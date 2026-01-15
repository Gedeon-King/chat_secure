"""
Gestionnaire d'authentification
"""
import time
from typing import Optional, Dict
from app.crypto.utils import hash_password, verify_password


class AuthManager:
    """
    Gestion de l'authentification avec secret partagé
    """
    
    def __init__(self):
        """Initialise le gestionnaire d'authentification"""
        self.shared_secret_hash = None
        self.shared_secret_salt = None
        self.login_attempts: Dict[str, list] = {}  # IP -> [timestamps]
        self.max_attempts = 5
        self.attempt_window = 300  # 5 minutes
    
    def set_shared_secret(self, secret: str):
        """
        Définit le secret partagé (première connexion)
        
        Args:
            secret: Secret partagé en clair
        """
        self.shared_secret_hash, self.shared_secret_salt = hash_password(secret)
    
    def verify_secret(self, secret: str, client_ip: str = None) -> bool:
        """
        Vérifie le secret partagé
        
        Args:
            secret: Secret à vérifier
            client_ip: IP du client (pour rate limiting)
            
        Returns:
            True si valide, False sinon
        """
        # Vérifier le rate limiting
        if client_ip and not self._check_rate_limit(client_ip):
            return False
        
        # Si pas encore de secret défini, c'est la première connexion
        if not self.shared_secret_hash:
            self.set_shared_secret(secret)
            return True
        
        # Vérifier le secret
        is_valid = verify_password(
            secret,
            self.shared_secret_hash,
            self.shared_secret_salt
        )
        
        # Enregistrer la tentative
        if client_ip:
            self._record_attempt(client_ip)
        
        return is_valid
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """
        Vérifie le rate limiting pour une IP
        
        Args:
            client_ip: IP à vérifier
            
        Returns:
            True si autorisé, False si trop de tentatives
        """
        now = time.time()
        
        # Nettoyer les anciennes tentatives
        if client_ip in self.login_attempts:
            self.login_attempts[client_ip] = [
                t for t in self.login_attempts[client_ip]
                if now - t < self.attempt_window
            ]
        else:
            self.login_attempts[client_ip] = []
        
        # Vérifier le nombre de tentatives
        return len(self.login_attempts[client_ip]) < self.max_attempts
    
    def _record_attempt(self, client_ip: str):
        """
        Enregistre une tentative de connexion
        
        Args:
            client_ip: IP du client
        """
        if client_ip not in self.login_attempts:
            self.login_attempts[client_ip] = []
        self.login_attempts[client_ip].append(time.time())
    
    def reset_secret(self):
        """Réinitialise le secret partagé"""
        self.shared_secret_hash = None
        self.shared_secret_salt = None
        self.login_attempts.clear()
