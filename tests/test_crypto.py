"""
Tests unitaires pour le module crypto
"""
import pytest
from app.crypto import ECDHKeyExchange, AESGCMEncryption, generate_random_bytes, encode_base64, decode_base64


class TestCryptoUtils:
    """Tests des utilitaires cryptographiques"""
    
    def test_generate_random_bytes(self):
        """Test de génération de bytes aléatoires"""
        random_data = generate_random_bytes(32)
        assert len(random_data) == 32
        assert isinstance(random_data, bytes)
        
        # Vérifier qu'on obtient des valeurs différentes
        random_data2 = generate_random_bytes(32)
        assert random_data != random_data2
    
    def test_base64_encoding(self):
        """Test d'encodage/décodage base64"""
        original = b"Hello, World!"
        encoded = encode_base64(original)
        decoded = decode_base64(encoded)
        
        assert isinstance(encoded, str)
        assert decoded == original


class TestECDHKeyExchange:
    """Tests de l'échange de clés ECDH"""
    
    def test_keypair_generation(self):
        """Test de génération de paire de clés"""
        ecdh = ECDHKeyExchange()
        public_key_b64 = ecdh.generate_keypair()
        
        assert isinstance(public_key_b64, str)
        assert ecdh.private_key is not None
        assert ecdh.public_key is not None
    
    def test_shared_secret_computation(self):
        """Test du calcul du secret partagé entre deux parties"""
        # Alice génère sa paire de clés
        alice = ECDHKeyExchange()
        alice_public = alice.generate_keypair()
        
        # Bob génère sa paire de clés
        bob = ECDHKeyExchange()
        bob_public = bob.generate_keypair()
        
        # Ils échangent leurs clés publiques et calculent le secret partagé
        alice.compute_shared_secret(bob_public)
        bob.compute_shared_secret(alice_public)
        
        # Les secrets partagés doivent être identiques
        assert alice.shared_secret == bob.shared_secret
    
    def test_key_derivation(self):
        """Test de dérivation de clés"""
        alice = ECDHKeyExchange()
        alice.generate_keypair()
        
        bob = ECDHKeyExchange()
        bob_public = bob.generate_keypair()
        
        alice.compute_shared_secret(bob_public)
        keys = alice.derive_keys()
        
        assert 'encryption_key' in keys
        assert 'hmac_key' in keys
        assert len(keys['encryption_key']) == 32  # 256 bits
        assert len(keys['hmac_key']) == 32  # 256 bits
        
        # Vérifier que les clés peuvent être récupérées
        assert alice.get_encryption_key() == keys['encryption_key']
        assert alice.get_hmac_key() == keys['hmac_key']


class TestAESGCMEncryption:
    """Tests du chiffrement AES-GCM"""
    
    @pytest.fixture
    def encryption_key(self):
        """Génère une clé de chiffrement pour les tests"""
        return generate_random_bytes(32)
    
    def test_encryption_decryption(self, encryption_key):
        """Test de chiffrement/déchiffrement"""
        cipher = AESGCMEncryption(encryption_key)
        
        original_message = "Ceci est un message secret 🔒"
        
        # Chiffrer
        encrypted = cipher.encrypt(original_message)
        
        assert 'ciphertext' in encrypted
        assert 'iv' in encrypted
        assert 'tag' in encrypted
        
        # Déchiffrer
        decrypted = cipher.decrypt(
            encrypted['ciphertext'],
            encrypted['iv'],
            encrypted['tag']
        )
        
        assert decrypted == original_message
    
    def test_different_iv_per_encryption(self, encryption_key):
        """Vérifier que chaque chiffrement utilise un IV différent"""
        cipher = AESGCMEncryption(encryption_key)
        
        message = "Test message"
        
        encrypted1 = cipher.encrypt(message)
        encrypted2 = cipher.encrypt(message)
        
        # Les IVs doivent être différents
        assert encrypted1['iv'] != encrypted2['iv']
        # Les ciphertexts doivent aussi être différents
        assert encrypted1['ciphertext'] != encrypted2['ciphertext']
    
    def test_tampered_message_detection(self, encryption_key):
        """Vérifier que la modification d'un message est détectée"""
        cipher = AESGCMEncryption(encryption_key)
        
        original_message = "Message authentique"
        encrypted = cipher.encrypt(original_message)
        
        # Modifier le ciphertext
        tampered_ciphertext = encode_base64(b"AAAA" + decode_base64(encrypted['ciphertext'])[4:])
        
        # Le déchiffrement doit échouer
        with pytest.raises(Exception):
            cipher.decrypt(tampered_ciphertext, encrypted['iv'], encrypted['tag'])
    
    def test_wrong_key_fails(self, encryption_key):
        """Vérifier qu'une mauvaise clé ne peut pas déchiffrer"""
        cipher1 = AESGCMEncryption(encryption_key)
        message = "Secret message"
        encrypted = cipher1.encrypt(message)
        
        # Essayer de déchiffrer avec une autre clé
        wrong_key = generate_random_bytes(32)
        cipher2 = AESGCMEncryption(wrong_key)
        
        with pytest.raises(Exception):
            cipher2.decrypt(encrypted['ciphertext'], encrypted['iv'], encrypted['tag'])


class TestEndToEndEncryption:
    """Tests de chiffrement de bout en bout"""
    
    def test_full_key_exchange_and_encryption(self):
        """Test complet: échange de clés + chiffrement/déchiffrement"""
        # Alice et Bob génèrent leurs clés
        alice = ECDHKeyExchange()
        alice_public = alice.generate_keypair()
        
        bob = ECDHKeyExchange()
        bob_public = bob.generate_keypair()
        
        # Échange de clés
        alice.compute_shared_secret(bob_public)
        bob.compute_shared_secret(alice_public)
        
        # Dérivation des clés
        alice_keys = alice.derive_keys()
        bob_keys = bob.derive_keys()
        
        # Vérifier que les clés dérivées sont identiques
        assert alice_keys['encryption_key'] == bob_keys['encryption_key']
        assert alice_keys['hmac_key'] == bob_keys['hmac_key']
        
        # Alice chiffre un message
        alice_cipher = AESGCMEncryption(alice.get_encryption_key())
        message = "Hello Bob! This is Alice 👋"
        encrypted = alice_cipher.encrypt(message)
        
        # Bob déchiffre le message
        bob_cipher = AESGCMEncryption(bob.get_encryption_key())
        decrypted = bob_cipher.decrypt(
            encrypted['ciphertext'],
            encrypted['iv'],
            encrypted['tag']
        )
        
        assert decrypted == message
        
        # Bob répond
        response = "Hi Alice! Message received 🔒"
        encrypted_response = bob_cipher.encrypt(response)
        
        # Alice déchiffre la réponse
        decrypted_response = alice_cipher.decrypt(
            encrypted_response['ciphertext'],
            encrypted_response['iv'],
            encrypted_response['tag']
        )
        
        assert decrypted_response == response


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
