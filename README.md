# Secure LAN Chat Application

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## 🔒 Description

Application web de chat sécurisé permettant à deux utilisateurs sur un réseau local (LAN) de communiquer de manière confidentielle avec chiffrement de bout en bout.

### Caractéristiques principales

✅ **Chiffrement de bout en bout** : ECDH + AES-256-GCM  
✅ **Authentification** : Secret partagé avec protection anti-brute force  
✅ **Protection réseau** : Anti-MITM, anti-replay, validation stricte  
✅ **Interface moderne** : UI responsive avec dark mode  
✅ **Communication temps réel** : WebSocket avec Socket.IO  
✅ **Architecture propre** : Code modulaire et maintenable  

## 🏗️ Architecture

```
app/
├── crypto/          # Modules cryptographiques (ECDH, AES-GCM)
├── auth/            # Authentification et sessions
├── network/         # WebSocket et validation
├── routes/          # Routes Flask
├── models/          # Modèles de données
├── static/          # CSS, JavaScript, assets
└── templates/       # Templates HTML
```

### Stack technologique

- **Backend** : Flask, Flask-SocketIO, cryptography
- **Frontend** : HTML5, CSS3, JavaScript (Web Crypto API)
- **Communication** : WebSocket (Socket.IO)
- **Chiffrement** : ECDH (P-256) + AES-256-GCM + HMAC-SHA256

## 📋 Prérequis

- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)
- Navigateur web moderne (Chrome, Firefox, Edge, Safari)
- Deux machines sur le même réseau local

## 🚀 Installation

### 1. Cloner ou télécharger le projet

```bash
cd chat_secure
```

### 2. Créer un environnement virtuel (recommandé)

```bash
python -m venv venv
```

**Activer l'environnement virtuel :**

- Windows :
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```

- Linux/Mac :
  ```bash
  source venv/bin/activate
  ```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

## 💻 Utilisation

### Lancement du serveur

Sur la machine qui hébergera le serveur :

```bash
python run.py
```

Par défaut, le serveur démarre sur `http://0.0.0.0:5000`

**Options disponibles :**

```bash
python run.py --host 0.0.0.0 --port 5000 --debug
```

- `--host` : Adresse d'écoute (défaut : 0.0.0.0)
- `--port` : Port d'écoute (défaut : 5000)
- `--debug` : Mode debug (ne pas utiliser en production)

### Connexion au chat

#### Sur la machine serveur :

1. Ouvrir un navigateur
2. Aller à `http://localhost:5000`
3. Entrer un pseudonyme
4. Entrer un secret partagé (minimum 6 caractères)
5. Cliquer sur "Se connecter"

**⚠️ IMPORTANT** : Le premier utilisateur à se connecter définit le secret partagé.

#### Sur la machine client :

1. Trouver l'adresse IP du serveur
   - Windows : `ipconfig`
   - Linux/Mac : `ifconfig` ou `ip addr`

2. Ouvrir un navigateur
3. Aller à `http://<IP_SERVEUR>:5000`
4. Entrer un pseudonyme **différent**
5. Entrer le **même secret partagé**
6. Cliquer sur "Se connecter"

### Échange de clés et communication

1. Une fois connectés, l'échange de clés ECDH se fait **automatiquement**
2. Un badge vert "🔒 Chiffrement actif" apparaît quand le chiffrement est établi
3. Vous pouvez maintenant échanger des messages chiffrés de bout en bout

## 🔐 Sécurité

### Mécanismes de protection

| Menace | Protection |
|--------|-----------|
| MITM | Secret partagé pré-établi + ECDH authentifié |
| Replay Attack | Validation timestamp (±30s) + nonces uniques |
| Interception | AES-256-GCM avec clés éphémères |
| Falsification | Tag GCM + HMAC-SHA256 |
| CSRF | Tokens CSRF par session |
| Brute Force | Rate limiting (5 tentatives / 5 min) |
| XSS | Sanitization + CSP headers |

### Protocole de chiffrement

1. **Échange de clés** : ECDH avec courbe P-256
2. **Dérivation** : HKDF-SHA256 (clé chiffrement + clé HMAC)
3. **Chiffrement** : AES-256-GCM (AEAD)
4. **Intégrité** : HMAC-SHA256 sur message complet
5. **Anti-replay** : Timestamp + ID unique (UUID)

### Bonnes pratiques

⚠️ **Secret partagé** :
- Échanger le secret via un canal sécurisé hors-bande (appel vocal, SMS, en personne)
- Ne JAMAIS envoyer le secret via email ou messagerie non chiffrée
- Utiliser un secret fort (minimum 12 caractères, alphanumérique + symboles)

⚠️ **Réseau** :
- Utiliser uniquement sur un réseau local de confiance
- Ne PAS exposer directement à Internet sans couches additionnelles (VPN, TLS, etc.)
- Vérifier que le firewall autorise le port 5000

## 🧪 Tests

### Exécuter les tests unitaires

```bash
pytest tests/ -v
```

### Tests de couverture

```bash
pytest tests/ --cov=app --cov-report=html
```

Le rapport sera généré dans `htmlcov/index.html`

### Tests manuels de sécurité

Voir `docs/security_analysis.md` pour les scénarios de test.

## 📚 Documentation

- **Manuel utilisateur** : `docs/user_manual.md`
- **Analyse de sécurité** : `docs/security_analysis.md`
- **Architecture** : `docs/architecture.md`

## 🎨 Interface

L'application offre :
- Design moderne avec effet glassmorphism
- Mode sombre automatique
- Interface responsive (mobile et desktop)
- Animations fluides
- Indicateurs de statut en temps réel
- Indicateur de frappe

## 🐛 Dépannage

### Le serveur ne démarre pas

- Vérifier que le port 5000 n'est pas déjà utilisé
- Vérifier que les dépendances sont installées : `pip install -r requirements.txt`

### Impossible de se connecter depuis une autre machine

- Vérifier l'adresse IP du serveur
- Vérifier que le firewall autorise le port 5000
- Vérifier que les deux machines sont sur le même réseau

### Le chiffrement ne s'établit pas

- Rafraîchir la page (F5)
- Vérifier la console JavaScript (F12) pour les erreurs
- S'assurer que le navigateur supporte Web Crypto API

### "Secret partagé incorrect"

- Vérifier que vous utilisez exactement le même secret que le premier utilisateur
- Attention à la casse (majuscules/minuscules)
- Si bloqué par rate limiting, attendre 5 minutes

## 🤝 Contribution

Ce projet est à but éducatif. Pour toute amélioration :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit les changements (`git commit -m 'Ajout fonctionnalité'`)
4. Push (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

## 📄 Licence

MIT License - voir le fichier LICENSE pour plus de détails.

## ⚠️ Avertissement

Cette application est conçue pour des communications en réseau local. Elle n'est **PAS** destinée à être exposée directement sur Internet sans couches de sécurité supplémentaires (TLS, VPN, etc.).

Pour un usage professionnel ou sensible, faites auditer le code par des experts en sécurité.

## 🙏 Remerciements

Développé avec ❤️ en utilisant :
- Flask et Flask-SocketIO
- Cryptography library
- Bootstrap 5
- Socket.IO

---

**Version** : 1.0.0  
**Auteur** : Secure Chat Team  
**Date** : Janvier 2026
