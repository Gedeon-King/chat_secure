"""
Échange de clés ECDH (Elliptic Curve Diffie-Hellman)
"""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from .utils import encode_base64, decode_base64


class ECDHKeyExchange:
    """
    Gestion de l'échange de clés ECDH
    """
    
    def __init__(self):
        """Initialise l'échange de clés"""
        self.private_key = None
        self.public_key = None
        self.shared_secret = None
        self.derived_keys = None
        
    def generate_keypair(self):
        """
        Génère une paire de clés ECDH (courbe secp256r1)
        
        Returns:
            Clé publique en base64
        """
        # Générer la paire de clés avec courbe secp256r1 (NIST P-256)
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()
        
        # Sérialiser la clé publique
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
        
        return encode_base64(public_bytes)
    
    def compute_shared_secret(self, peer_public_key_b64: str):
        """
        Calcule le secret partagé avec la clé publique du pair
        
        Args:
            peer_public_key_b64: Clé publique du pair en base64
        """
        # Désérialiser la clé publique du pair
        peer_public_bytes = decode_base64(peer_public_key_b64)
        peer_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
            ec.SECP256R1(),
            peer_public_bytes
        )
        
        # Calculer le secret partagé
        self.shared_secret = self.private_key.exchange(
            ec.ECDH(),
            peer_public_key
        )
        
    def derive_keys(self, info: bytes = b'chat_secure_keys'):
        """
        Dérive les clés de chiffrement et HMAC depuis le secret partagé avec HKDF
        
        Args:
            info: Information contextuelle pour HKDF
            
        Returns:
            dict avec 'encryption_key' et 'hmac_key'
        """
        if not self.shared_secret:
            raise ValueError("Le secret partagé n'a pas été calculé")
        
        # Dériver 64 bytes: 32 pour AES-256, 32 pour HMAC
        kdf = HKDF(
            algorithm=hashes.SHA256(),
            length=64,
            salt=None,
            info=info
        )
        
        derived = kdf.derive(self.shared_secret)
        
        self.derived_keys = {
            'encryption_key': derived[:32],  # 32 bytes pour AES-256
            'hmac_key': derived[32:]         # 32 bytes pour HMAC
        }
        
        return self.derived_keys
    
    def get_encryption_key(self) -> bytes:
        """Retourne la clé de chiffrement"""
        if not self.derived_keys:
            raise ValueError("Les clés n'ont pas été dérivées")
        return self.derived_keys['encryption_key']
    
    def get_hmac_key(self) -> bytes:
        """Retourne la clé HMAC"""
        if not self.derived_keys:
            raise ValueError("Les clés n'ont pas été dérivées")
        return self.derived_keys['hmac_key']
