"""
Configuration de l'application Flask
Paramètres de sécurité et de session
"""
import os
from datetime import timedelta

class Config:
    """Configuration principale de l'application"""
    
    # Clé secrète pour Flask (régénérée à chaque démarrage pour sécurité maximale)
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    
    # Configuration de la session
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_SECURE = False  # True en production avec HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'flask_session')
    
    # Protection CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 heure
    
    # Configuration SocketIO
    SOCKETIO_ASYNC_MODE = 'threading'
    SOCKETIO_PING_TIMEOUT = 60
    SOCKETIO_PING_INTERVAL = 25
    
    # Paramètres de sécurité
    MAX_CONTENT_LENGTH = 16 * 1024  # 16 KB max pour les messages
    REPLAY_WINDOW = 30  # Fenêtre anti-replay en secondes
    
    # Rate limiting
    LOGIN_ATTEMPTS_LIMIT = 5
    LOGIN_ATTEMPTS_WINDOW = 300  # 5 minutes
    
    # Secret partagé (hash - à définir lors de l'authentification)
    SHARED_SECRET_HASH = None
