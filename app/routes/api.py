"""
API endpoints
"""
from flask import Blueprint, jsonify, session
from app.auth import SessionManager

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Instance globale (injectée par __init__.py)
session_manager: SessionManager = None


def init_api(sess_mgr):
    """
    Initialise l'API avec les gestionnaires
    
    Args:
        sess_mgr: Gestionnaire de sessions
    """
    global session_manager
    session_manager = sess_mgr


@api_bp.route('/status', methods=['GET'])
def status():
    """Vérifie le statut de l'application"""
    return jsonify({
        'status': 'ok',
        'service': 'Secure LAN Chat'
    })


@api_bp.route('/session', methods=['GET'])
def get_session():
    """Récupère les informations de session"""
    if 'session_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    user_session = session_manager.get_session(session['session_id'])
    if not user_session:
        return jsonify({'error': 'Session invalide'}), 401
    
    return jsonify({
        'username': user_session['username'],
        'session_id': user_session['session_id'],
        'csrf_token': user_session['csrf_token'],
        'encryption_established': user_session.get('encryption_established', False)
    })


@api_bp.route('/users', methods=['GET'])
def get_users():
    """Récupère la liste des utilisateurs en ligne"""
    if 'session_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    sessions = session_manager.get_all_sessions()
    users = [
        {
            'username': s['username'],
            'encryption_ready': s.get('encryption_established', False)
        }
        for s in sessions
    ]
    
    return jsonify({'users': users})
