"""
Utilitaires cryptographiques
"""
import os
import base64
import hmac
import hashlib


def generate_random_bytes(length: int) -> bytes:
    """
    Génère des bytes aléatoires cryptographiquement sécurisés
    
    Args:
        length: Nombre de bytes à générer
        
    Returns:
        bytes aléatoires
    """
    return os.urandom(length)


def encode_base64(data: bytes) -> str:
    """
    Encode des bytes en base64 URL-safe
    
    Args:
        data: Données à encoder
        
    Returns:
        String base64 URL-safe
    """
    return base64.urlsafe_b64encode(data).decode('utf-8')


def decode_base64(data: str) -> bytes:
    """
    Décode une string base64 URL-safe
    
    Args:
        data: String base64 à décoder
        
    Returns:
        Bytes décodés
    """
    return base64.urlsafe_b64decode(data.encode('utf-8'))


def compute_hmac(key: bytes, message: bytes) -> str:
    """
    Calcule HMAC-SHA256 d'un message
    
    Args:
        key: Clé HMAC
        message: Message à signer
        
    Returns:
        HMAC en base64
    """
    h = hmac.new(key, message, hashlib.sha256)
    return encode_base64(h.digest())


def verify_hmac(key: bytes, message: bytes, expected_hmac: str) -> bool:
    """
    Vérifie un HMAC
    
    Args:
        key: Clé HMAC
        message: Message original
        expected_hmac: HMAC attendu en base64
        
    Returns:
        True si valide, False sinon
    """
    computed = compute_hmac(key, message)
    return hmac.compare_digest(computed, expected_hmac)


def hash_password(password: str, salt: bytes = None) -> tuple:
    """
    Hash un mot de passe avec PBKDF2
    
    Args:
        password: Mot de passe en clair
        salt: Salt (généré si None)
        
    Returns:
        (hash, salt) en base64
    """
    if salt is None:
        salt = generate_random_bytes(32)
    
    # PBKDF2 avec 100000 itérations
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000,
        dklen=32
    )
    
    return encode_base64(key), encode_base64(salt)


def verify_password(password: str, expected_hash: str, salt: str) -> bool:
    """
    Vérifie un mot de passe hashé
    
    Args:
        password: Mot de passe à vérifier
        expected_hash: Hash attendu en base64
        salt: Salt en base64
        
    Returns:
        True si valide, False sinon
    """
    computed_hash, _ = hash_password(password, decode_base64(salt))
    return hmac.compare_digest(computed_hash, expected_hash)
