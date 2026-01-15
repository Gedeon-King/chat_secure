"""
Chiffrement AES-256-GCM
"""
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .utils import generate_random_bytes, encode_base64, decode_base64


class AESGCMEncryption:
    """
    Gestion du chiffrement AES-256-GCM (Authenticated Encryption with Associated Data)
    """
    
    def __init__(self, key: bytes):
        """
        Initialise le chiffrement avec une clé
        
        Args:
            key: Clé de chiffrement (32 bytes pour AES-256)
        """
        if len(key) != 32:
            raise ValueError("La clé doit faire 32 bytes (256 bits)")
        
        self.aesgcm = AESGCM(key)
    
    def encrypt(self, plaintext: str, associated_data: bytes = None) -> dict:
        """
        Chiffre un message avec AES-256-GCM
        
        Args:
            plaintext: Message en clair
            associated_data: Données associées (optionnel, pour AAD)
            
        Returns:
            dict avec 'ciphertext', 'iv', 'tag' en base64
        """
        # Générer un IV aléatoire (12 bytes recommandé pour GCM)
        iv = generate_random_bytes(12)
        
        # Chiffrer le message
        plaintext_bytes = plaintext.encode('utf-8')
        ciphertext = self.aesgcm.encrypt(iv, plaintext_bytes, associated_data)
        
        # GCM retourne ciphertext + tag (16 derniers bytes)
        # On sépare pour plus de clarté
        actual_ciphertext = ciphertext[:-16]
        tag = ciphertext[-16:]
        
        return {
            'ciphertext': encode_base64(actual_ciphertext),
            'iv': encode_base64(iv),
            'tag': encode_base64(tag)
        }
    
    def decrypt(self, ciphertext_b64: str, iv_b64: str, tag_b64: str, 
                associated_data: bytes = None) -> str:
        """
        Déchiffre un message AES-256-GCM
        
        Args:
            ciphertext_b64: Ciphertext en base64
            iv_b64: IV en base64
            tag_b64: Tag d'authentification en base64
            associated_data: Données associées (optionnel)
            
        Returns:
            Message en clair
            
        Raises:
            cryptography.exceptions.InvalidTag: Si le tag est invalide
        """
        # Décoder depuis base64
        ciphertext = decode_base64(ciphertext_b64)
        iv = decode_base64(iv_b64)
        tag = decode_base64(tag_b64)
        
        # Reconstruire ciphertext + tag pour AESGCM
        full_ciphertext = ciphertext + tag
        
        # Déchiffrer et vérifier l'authenticité
        plaintext_bytes = self.aesgcm.decrypt(iv, full_ciphertext, associated_data)
        
        return plaintext_bytes.decode('utf-8')
    
    def encrypt_message(self, message: str) -> dict:
        """
        Chiffre un message (méthode simplifiée)
        
        Args:
            message: Message à chiffrer
            
        Returns:
            dict avec données chiffrées
        """
        return self.encrypt(message)
    
    def decrypt_message(self, encrypted_data: dict) -> str:
        """
        Déchiffre un message (méthode simplifiée)
        
        Args:
            encrypted_data: dict avec 'ciphertext', 'iv', 'tag'
            
        Returns:
            Message en clair
        """
        return self.decrypt(
            encrypted_data['ciphertext'],
            encrypted_data['iv'],
            encrypted_data['tag']
        )
