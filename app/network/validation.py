"""
Validation des données réseau
"""
import time
import re
from typing import Any, Optional


class MessageValidator:
    """
    Validation stricte des messages et données réseau
    """
    
    def __init__(self, replay_window: int = 30):
        """
        Initialise le validateur
        
        Args:
            replay_window: Fenêtre anti-replay en secondes
        """
        self.replay_window = replay_window
        self.seen_nonces = set()  # Protection anti-replay
    
    def validate_timestamp(self, timestamp: int) -> bool:
        """
        Valide un timestamp (protection anti-replay)
        
        Args:
            timestamp: Timestamp Unix à valider
            
        Returns:
            True si valide, False sinon
        """
        now = time.time()
        diff = abs(now - timestamp)
        return diff <= self.replay_window
    
    def validate_message_structure(self, message: dict) -> bool:
        """
        Valide la structure d'un message chiffré
        
        Args:
            message: Message à valider
            
        Returns:
            True si structure valide, False sinon
        """
        required_fields = ['id', 'sender', 'content', 'iv', 'tag', 'timestamp', 'hmac']
        
        # Vérifier que tous les champs requis sont présents
        if not all(field in message for field in required_fields):
            return False
        
        # Vérifier les types
        if not isinstance(message['id'], str):
            return False
        if not isinstance(message['sender'], str):
            return False
        if not isinstance(message['content'], str):
            return False
        if not isinstance(message['iv'], str):
            return False
        if not isinstance(message['tag'], str):
            return False
        if not isinstance(message['timestamp'], (int, float)):
            return False
        if not isinstance(message['hmac'], str):
            return False
        
        return True
    
    def validate_username(self, username: str) -> bool:
        """
        Valide un nom d'utilisateur
        
        Args:
            username: Nom d'utilisateur à valider
            
        Returns:
            True si valide, False sinon
        """
        if not username or not isinstance(username, str):
            return False
        
        # 3-20 caractères, alphanumérique + underscore
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
            return False
        
        return True
    
    def sanitize_string(self, value: str, max_length: int = 1000) -> str:
        """
        Nettoie une chaîne de caractères
        
        Args:
            value: Chaîne à nettoyer
            max_length: Longueur maximale
            
        Returns:
            Chaîne nettoyée
        """
        if not isinstance(value, str):
            return ""
        
        # Limiter la longueur
        value = value[:max_length]
        
        # Supprimer les caractères de contrôle dangereux
        value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
        
        return value.strip()
    
    def check_nonce(self, nonce: str) -> bool:
        """
        Vérifie si un nonce a déjà été vu (anti-replay)
        
        Args:
            nonce: Nonce à vérifier
            
        Returns:
            True si nouveau, False si déjà vu
        """
        if nonce in self.seen_nonces:
            return False
        
        self.seen_nonces.add(nonce)
        
        # Limiter la taille du cache (garder les 1000 derniers)
        if len(self.seen_nonces) > 1000:
            # Retirer les plus anciens (approximation)
            self.seen_nonces = set(list(self.seen_nonces)[-1000:])
        
        return True
    
    def validate_public_key(self, public_key: str) -> bool:
        """
        Valide une clé publique
        
        Args:
            public_key: Clé publique en base64 URL-safe (sans padding)
            
        Returns:
            True si valide, False sinon
        """
        if not public_key or not isinstance(public_key, str):
            return False
        
        # Vérifier que c'est du base64 URL-safe valide (sans padding obligatoire)
        # Accepte les caractères: A-Z, a-z, 0-9, -, _ (URL-safe)
        if not re.match(r'^[A-Za-z0-9_-]+$', public_key):
            return False
        
        # Vérifier une longueur raisonnable (clé ECDH P-256 = 65 bytes non compressée)
        # En base64 URL-safe: ~87 caractères (sans padding)
        # Accepter une petite marge
        if len(public_key) < 80 or len(public_key) > 100:
            return False
        
        return True
