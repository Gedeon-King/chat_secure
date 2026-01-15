"""
Gestionnaire d'événements WebSocket
"""
from flask import request, session
from flask_socketio import emit, join_room, leave_room
import time
import uuid


def setup_socket_handlers(socketio, session_manager, validator):
    """
    Configure les gestionnaires d'événements SocketIO
    
    Args:
        socketio: Instance Flask-SocketIO
        session_manager: Gestionnaire de sessions
        validator: Validateur de messages
    """
    
    @socketio.on('connect')
    def handle_connect():
        """Gestion de la connexion WebSocket"""
        print(f"Client connecté: {request.sid}")
        
        # Vérifier si l'utilisateur est authentifié via la session Flask
        if 'session_id' not in session:
            print("Connexion refusée: pas de session")
            return False
        
        session_id = session['session_id']
        user_session = session_manager.get_session(session_id)
        
        if not user_session:
            print("Connexion refusée: session invalide")
            return False
        
        # Mettre à jour le socket ID
        user_session['socket_id'] = request.sid
        
        # Rejoindre la room de chat
        join_room('chat_room')
        
        # Notifier les autres utilisateurs
        emit('user_connected', {
            'username': user_session['username'],
            'timestamp': time.time()
        }, room='chat_room', skip_sid=request.sid)
        
        print(f"Utilisateur {user_session['username']} connecté")
        return True
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Gestion de la déconnexion WebSocket"""
        print(f"Client déconnecté: {request.sid}")
        
        # Trouver la session associée
        user_session = session_manager.get_session_by_socket(request.sid)
        
        if user_session:
            # Quitter la room
            leave_room('chat_room')
            
            # Notifier les autres utilisateurs
            emit('user_disconnected', {
                'username': user_session['username'],
                'timestamp': time.time()
            }, room='chat_room')
            
            print(f"Utilisateur {user_session['username']} déconnecté")
    
    @socketio.on('key_exchange')
    def handle_key_exchange(data):
        """
        Gestion de l'échange de clés ECDH
        
        Args:
            data: {'public_key': str}
        """
        if 'session_id' not in session:
            return {'success': False, 'error': 'Non authentifié'}
        
        session_id = session['session_id']
        user_session = session_manager.get_session(session_id)
        
        if not user_session:
            return {'success': False, 'error': 'Session invalide'}
        
        # Valider la clé publique
        public_key = data.get('public_key')
        if not validator.validate_public_key(public_key):
            return {'success': False, 'error': 'Clé publique invalide'}
        
        # Enregistrer la clé publique
        session_manager.set_public_key(session_id, public_key)
        session_manager.update_activity(session_id)
        
        # Broadcaster la clé publique aux autres utilisateurs
        emit('peer_public_key', {
            'username': user_session['username'],
            'public_key': public_key,
            'timestamp': time.time()
        }, room='chat_room', skip_sid=request.sid)
        
        print(f"Échange de clé pour {user_session['username']}")
        return {'success': True}
    
    @socketio.on('encryption_ready')
    def handle_encryption_ready():
        """Notification que le chiffrement est établi"""
        if 'session_id' not in session:
            return {'success': False}
        
        session_id = session['session_id']
        session_manager.set_encryption_established(session_id)
        session_manager.update_activity(session_id)
        
        return {'success': True}
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """
        Gestion de l'envoi de messages chiffrés
        
        Args:
            data: Message chiffré avec métadonnées
        """
        if 'session_id' not in session:
            return {'success': False, 'error': 'Non authentifié'}
        
        session_id = session['session_id']
        user_session = session_manager.get_session(session_id)
        
        if not user_session:
            return {'success': False, 'error': 'Session invalide'}
        
        # Vérifier que le chiffrement est établi
        if not user_session.get('encryption_established', False):
            return {'success': False, 'error': 'Chiffrement non établi'}
        
        # Valider la structure du message
        if not validator.validate_message_structure(data):
            return {'success': False, 'error': 'Structure de message invalide'}
        
        # Valider le timestamp (anti-replay)
        if not validator.validate_timestamp(data['timestamp']):
            return {'success': False, 'error': 'Timestamp invalide'}
        
        # Vérifier le nonce (anti-replay)
        if not validator.check_nonce(data['id']):
            return {'success': False, 'error': 'Message déjà reçu (replay attack)'}
        
        # Mettre à jour l'activité
        session_manager.update_activity(session_id)
        
        # Broadcaster le message chiffré
        emit('receive_message', data, room='chat_room', skip_sid=request.sid)
        
        return {'success': True}
    
    @socketio.on('typing')
    def handle_typing(data):
        """Gestion de l'indicateur de frappe"""
        if 'session_id' not in session:
            return
        
        session_id = session['session_id']
        user_session = session_manager.get_session(session_id)
        
        if user_session:
            emit('user_typing', {
                'username': user_session['username'],
                'is_typing': data.get('is_typing', False)
            }, room='chat_room', skip_sid=request.sid)
    
    @socketio.on('get_online_users')
    def handle_get_online_users():
        """Récupère la liste des utilisateurs en ligne"""
        sessions = session_manager.get_all_sessions()
        users = [
            {
                'username': s['username'],
                'encryption_ready': s.get('encryption_established', False)
            }
            for s in sessions
        ]
        return {'users': users}
