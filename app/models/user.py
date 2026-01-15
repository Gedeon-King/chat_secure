"""
Modèle d'utilisateur
"""
from typing import Optional


class User:
    """
    Structure d'un utilisateur
    """
    
    def __init__(self, session_id: str, username: str, socket_id: str = None):
        """
        Initialise un utilisateur
        
        Args:
            session_id: ID de session unique
            username: Pseudonyme de l'utilisateur
            socket_id: ID du socket WebSocket
        """
        self.session_id = session_id
        self.username = username
        self.socket_id = socket_id
        self.connected = False
        self.public_key: Optional[str] = None
        self.encryption_ready = False
    
    def to_dict(self) -> dict:
        """
        Convertit l'utilisateur en dictionnaire
        
        Returns:
            Dictionnaire représentant l'utilisateur
        """
        return {
            'session_id': self.session_id,
            'username': self.username,
            'socket_id': self.socket_id,
            'connected': self.connected,
            'public_key': self.public_key,
            'encryption_ready': self.encryption_ready
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """
        Crée un utilisateur depuis un dictionnaire
        
        Args:
            data: Dictionnaire contenant les données utilisateur
            
        Returns:
            Instance de User
        """
        user = cls(
            session_id=data['session_id'],
            username=data['username'],
            socket_id=data.get('socket_id')
        )
        user.connected = data.get('connected', False)
        user.public_key = data.get('public_key')
        user.encryption_ready = data.get('encryption_ready', False)
        return user
