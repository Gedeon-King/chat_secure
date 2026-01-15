"""
Point d'entrée de l'application
"""

from app import create_app, socketio
import argparse


def main():
    """Lance l'application"""
    parser = argparse.ArgumentParser(description='Secure LAN Chat Application')
    parser.add_argument('--host', default='0.0.0.0', help='Adresse d\'écoute (défaut: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port d\'écoute (défaut: 5000)')
    parser.add_argument('--debug', action='store_true', help='Mode debug')
    
    args = parser.parse_args()
    
    app = create_app()
    
    print("=" * 60)
    print("🔒 Secure LAN Chat Application")
    print("=" * 60)
    print(f"Serveur lancé sur http://{args.host}:{args.port}")
    print(f"Mode debug: {'Activé' if args.debug else 'Désactivé'}")
    print("\n⚠️  IMPORTANT:")
    print("   - Partagez le secret avec votre interlocuteur AVANT de vous connecter")
    print("   - Le premier utilisateur à se connecter définit le secret partagé")
    print("   - Utilisez un canal sécurisé hors-bande pour échanger le secret")
    print("\n💡 Pour arrêter le serveur: Ctrl+C")
    print("=" * 60)
    
    socketio.run(app, 
                host=args.host, 
                port=args.port, 
                debug=args.debug)


if __name__ == '__main__':
    main()
