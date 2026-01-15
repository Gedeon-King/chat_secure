# 🚀 Quick Start Guide - Secure LAN Chat

## Démarrage rapide en 3 minutes

### 1️⃣ Installation (1 minute)

```powershell
# Naviguer vers le dossier
cd chat_secure

# Installer les dépendances
pip install -r requirements.txt
```

### 2️⃣ Lancement du serveur (30 secondes)

```powershell
python run.py
```

Vous verrez :
```
============================================================
🔒 Secure LAN Chat Application
============================================================
Serveur lancé sur http://0.0.0.0:5000
Mode debug: Désactivé

⚠️  IMPORTANT:
   - Partagez le secret avec votre interlocuteur AVANT de vous connecter
   - Le premier utilisateur à se connecter définit le secret partagé
   - Utilisez un canal sécurisé hors-bande pour échanger le secret

💡 Pour arrêter le serveur: Ctrl+C
============================================================
```

### 3️⃣ Connexion (1 minute)

#### Machine Serveur:
1. Ouvrir `http://localhost:5000`
2. Pseudonyme: `Alice`
3. Secret: `MaReunion2026!`
4. ✅ Se connecter

#### Machine Client:
1. Trouver l'IP du serveur: `ipconfig` (Windows)
2. Ouvrir `http://[IP]:5000` (ex: `http://192.168.1.10:5000`)
3. Pseudonyme: `Bob`
4. Secret: `MaReunion2026!` (le même!)
5. ✅ Se connecter

### 4️⃣ Chat sécurisé! 🎉

- Attendez le badge vert: **"🔒 Chiffrement actif"**
- Commencez à discuter en toute sécurité!

---

## 🆘 Problèmes courants

### "No module named pytest"
```powershell
pip install -r requirements.txt
```

### "Port déjà utilisé"
```powershell
python run.py --port 5001
```

### "Impossible de se connecter"
- Vérifier firewall Windows (autoriser port 5000)
- Vérifier que les deux machines sont sur le même réseau
- Essayer avec `ipconfig` pour obtenir la bonne IP

---

## 📖 Documentation complète

- **README.md** - Guide technique complet
- **docs/user_manual.md** - Manuel utilisateur détaillé
- **docs/security_analysis.md** - Analyse de sécurité

---

**C'est tout! Profitez de votre chat sécurisé! 🔒💬**
