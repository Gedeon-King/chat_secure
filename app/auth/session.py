"""
Gestionnaire de sessions sécurisées
"""
import uuid
import time
from typing import Dict, Optional
from app.crypto.utils import generate_random_bytes, encode_base64


class SessionManager:
    """
    Gestion des sessions utilisateur
    """
    
    def __init__(self, session_timeout: int = 1800):
        """
        Initialise le gestionnaire de sessions
        
        Args:
            session_timeout: Durée de vie d'une session en secondes (défaut 30 min)
        """
        self.sessions: Dict[str, dict] = {}
        self.session_timeout = session_timeout
    
    def create_session(self, username: str, socket_id: str) -> dict:
        """
        Crée une nouvelle session
        
        Args:
            username: Nom d'utilisateur
            socket_id: ID du socket
            
        Returns:
            Données de session
        """
        session_id = str(uuid.uuid4())
        csrf_token = encode_base64(generate_random_bytes(32))
        
        session_data = {
            'session_id': session_id,
            'username': username,
            'socket_id': socket_id,
            'connected': True,
            'created_at': time.time(),
            'last_activity': time.time(),
            'csrf_token': csrf_token,
            'public_key': None,
            'encryption_established': False
        }
        
        self.sessions[session_id] = session_data
        return session_data
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """
        Récupère une session
        
        Args:
            session_id: ID de session
            
        Returns:
            Données de session ou None
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Vérifier l'expiration
        if time.time() - session['last_activity'] > self.session_timeout:
            self.delete_session(session_id)
            return None
        
        return session
    
    def update_activity(self, session_id: str):
        """
        Met à jour l'activité d'une session
        
        Args:
            session_id: ID de session
        """
        if session_id in self.sessions:
            self.sessions[session_id]['last_activity'] = time.time()
    
    def set_public_key(self, session_id: str, public_key: str):
        """
        Enregistre la clé publique d'une session
        
        Args:
            session_id: ID de session
            public_key: Clé publique en base64
        """
        if session_id in self.sessions:
            self.sessions[session_id]['public_key'] = public_key
    
    def set_encryption_established(self, session_id: str):
        """
        Marque l'établissement du chiffrement
        
        Args:
            session_id: ID de session
        """
        if session_id in self.sessions:
            self.sessions[session_id]['encryption_established'] = True
    
    def delete_session(self, session_id: str):
        """
        Supprime une session
        
        Args:
            session_id: ID de session
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_all_sessions(self) -> list:
        """
        Récupère toutes les sessions actives
        
        Returns:
            Liste des sessions
        """
        # Nettoyer les sessions expirées
        self.cleanup_expired_sessions()
        return list(self.sessions.values())
    
    def cleanup_expired_sessions(self):
        """Nettoie les sessions expirées"""
        now = time.time()
        expired = [
            sid for sid, session in self.sessions.items()
            if now - session['last_activity'] > self.session_timeout
        ]
        
        for sid in expired:
            del self.sessions[sid]
    
    def get_session_by_socket(self, socket_id: str) -> Optional[dict]:
        """
        Récupère une session par son socket ID
        
        Args:
            socket_id: ID du socket
            
        Returns:
            Session ou None
        """
        for session in self.sessions.values():
            if session['socket_id'] == socket_id:
                return session
        return None
