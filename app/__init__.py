"""
Initialisation de l'application Flask
"""
from flask import Flask
from flask_socketio import SocketIO
from flask_session import Session
import os

from app.config import Config
from app.auth import AuthManager, SessionManager
from app.network import setup_socket_handlers, MessageValidator


# Instances globales
socketio = SocketIO()
flask_session = Session()
auth_manager = AuthManager()
session_manager = SessionManager()
validator = MessageValidator()


def create_app(config_class=Config):
    """
    Factory pour créer l'application Flask
    
    Args:
        config_class: Classe de configuration
        
    Returns:
        Instance Flask configurée
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Créer le dossier de sessions si nécessaire
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
    
    # Initialiser les extensions
    flask_session.init_app(app)
    socketio.init_app(app, 
                     cors_allowed_origins="*",  # En LAN, accepter toutes les origines
                     async_mode='threading',
                     logger=False,
                     engineio_logger=False)
    
    # Enregistrer les blueprints
    from app.routes import main_bp, api_bp
    from app.routes.main import init_routes
    from app.routes.api import init_api
    
    # Initialiser les routes avec les gestionnaires
    init_routes(auth_manager, session_manager, validator)
    init_api(session_manager)
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    
    # Configurer les gestionnaires WebSocket
    setup_socket_handlers(socketio, session_manager, validator)
    
    # Headers de sécurité
    @app.after_request
    def security_headers(response):
        """Ajoute des headers de sécurité"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # CSP pour empêcher les scripts inline malveillants (sauf nos propres scripts)
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.socket.io; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com;"
        return response
    
    return app
