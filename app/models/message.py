"""
Modèle de message
"""
import uuid
import time
from typing import Optional


class Message:
    """
    Structure d'un message chiffré
    """
    
    def __init__(self, sender: str, content: str, iv: str, tag: str, 
                 hmac: str, message_id: str = None, timestamp: float = None):
        """
        Initialise un message
        
        Args:
            sender: Nom de l'expéditeur
            content: Contenu chiffré (base64)
            iv: IV pour déchiffrement (base64)
            tag: Tag d'authentification (base64)
            hmac: HMAC du message (base64)
            message_id: ID unique (généré si None)
            timestamp: Timestamp Unix (généré si None)
        """
        self.id = message_id or str(uuid.uuid4())
        self.sender = sender
        self.content = content
        self.iv = iv
        self.tag = tag
        self.timestamp = timestamp or time.time()
        self.hmac = hmac
    
    def to_dict(self) -> dict:
        """
        Convertit le message en dictionnaire
        
        Returns:
            Dictionnaire représentant le message
        """
        return {
            'id': self.id,
            'sender': self.sender,
            'content': self.content,
            'iv': self.iv,
            'tag': self.tag,
            'timestamp': self.timestamp,
            'hmac': self.hmac
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """
        Crée un message depuis un dictionnaire
        
        Args:
            data: Dictionnaire contenant les données du message
            
        Returns:
            Instance de Message
        """
        return cls(
            sender=data['sender'],
            content=data['content'],
            iv=data['iv'],
            tag=data['tag'],
            hmac=data['hmac'],
            message_id=data.get('id'),
            timestamp=data.get('timestamp')
        )
