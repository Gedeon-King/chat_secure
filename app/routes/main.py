"""
Routes principales de l'application
"""
from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from app.auth import AuthManager, SessionManager
from app.network import MessageValidator

main_bp = Blueprint('main', __name__)

# Instances globales (injectées par __init__.py)
auth_manager: AuthManager = None
session_manager: SessionManager = None
validator: MessageValidator = None


def init_routes(auth_mgr, sess_mgr, valid):
    """
    Initialise les routes avec les gestionnaires
    
    Args:
        auth_mgr: Gestionnaire d'authentification
        sess_mgr: Gestionnaire de sessions
        valid: Validateur de messages
    """
    global auth_manager, session_manager, validator
    auth_manager = auth_mgr
    session_manager = sess_mgr
    validator = valid


@main_bp.route('/')
def index():
    """Page d'accueil - Redirection vers login ou chat"""
    if 'session_id' in session:
        # Vérifier si la session est valide
        user_session = session_manager.get_session(session.get('session_id'))
        if user_session:
            return redirect(url_for('main.chat'))
    
    return redirect(url_for('main.login'))


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if request.method == 'POST':
        # Récupérer les données du formulaire
        username = request.form.get('username', '').strip()
        shared_secret = request.form.get('shared_secret', '')
        
        # Valider le nom d'utilisateur
        if not validator.validate_username(username):
            flash('Nom d\'utilisateur invalide (3-20 caractères alphanumériques)', 'error')
            return render_template('login.html')
        
        # Vérifier le secret partagé
        client_ip = request.remote_addr
        if not auth_manager.verify_secret(shared_secret, client_ip):
            flash('Secret partagé incorrect ou trop de tentatives. Réessayez plus tard.', 'error')
            return render_template('login.html')
        
        # Créer la session utilisateur
        user_session = session_manager.create_session(username, None)
        
        # Stocker l'ID de session dans la session Flask
        session['session_id'] = user_session['session_id']
        session['username'] = username
        session.permanent = False
        
        flash(f'Bienvenue {username} !', 'success')
        return redirect(url_for('main.chat'))
    
    return render_template('login.html')


@main_bp.route('/chat')
def chat():
    """Interface de chat (nécessite authentification)"""
    if 'session_id' not in session:
        flash('Vous devez vous connecter d\'abord', 'error')
        return redirect(url_for('main.login'))
    
    # Vérifier la validité de la session
    user_session = session_manager.get_session(session['session_id'])
    if not user_session:
        session.clear()
        flash('Session expirée', 'error')
        return redirect(url_for('main.login'))
    
    return render_template('chat.html', 
                          username=user_session['username'],
                          csrf_token=user_session['csrf_token'])


@main_bp.route('/logout')
def logout():
    """Déconnexion"""
    if 'session_id' in session:
        session_manager.delete_session(session['session_id'])
    
    session.clear()
    flash('Vous êtes déconnecté', 'info')
    return redirect(url_for('main.login'))
