# Manuel Utilisateur - Secure LAN Chat

## 📖 Guide d'utilisation

Ce manuel vous guide pas à pas dans l'utilisation de l'application de chat sécurisé.

---

## 1️⃣ Prérequis

Avant de commencer, assurez-vous d'avoir :

- ✅ Python 3.9 ou supérieur installé
- ✅ Deux ordinateurs sur le même réseau local (WiFi ou Ethernet)
- ✅ Un navigateur web moderne (Chrome, Firefox, Edge recommandés)
- ✅ Un secret partagé que vous et votre interlocuteur connaissez

---

## 2️⃣ Installation

### Sur la machine qui hébergera le serveur :

1. **Ouvrir un terminal/PowerShell**

2. **Naviguer vers le dossier de l'application**
   ```bash
   cd chemin/vers/chat_secure
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

---

## 3️⃣ Démarrage du serveur

1. **Lancer le serveur**
   ```bash
   python run.py
   ```

2. **Noter l'adresse IP affichée**
   - Le serveur affiche : `Serveur lancé sur http://0.0.0.0:5000`
   - Trouvez votre adresse IP locale :
     - Windows : Ouvrir CMD et taper `ipconfig`
     - Chercher "Adresse IPv4" (ex: `192.168.1.10`)

3. **Gardez le terminal ouvert** (le serveur doit rester actif)

---

## 4️⃣ Connexion au chat

### 👤 Premier utilisateur (sur la machine serveur) :

1. Ouvrir un navigateur web

2. Aller à : `http://localhost:5000`

3. Remplir le formulaire :
   - **Nom d'utilisateur** : Choisissez un pseudonyme (3-20 caractères)
   - **Secret partagé** : Entrez un secret (minimum 6 caractères)
     - ⚠️ Ce secret sera utilisé par tous les participants
     - Choisissez quelque chose de fort et mémorisable
     - **Exemple** : `MaReunion2026!`

4. Cliquer sur **"Se connecter"**

5. Vous êtes maintenant sur l'interface de chat
   - Un message indique : "🔐 En attente de la clé du pair..."

### 👥 Deuxième utilisateur (sur une autre machine) :

1. Ouvrir un navigateur web

2. Aller à : `http://[IP_SERVEUR]:5000`
   - Remplacez `[IP_SERVEUR]` par l'adresse IP notée plus tôt
   - **Exemple** : `http://192.168.1.10:5000`

3. Remplir le formulaire :
   - **Nom d'utilisateur** : Choisissez un pseudonyme **différent**
   - **Secret partagé** : Entrez **exactement le même secret** que le premier utilisateur

4. Cliquer sur **"Se connecter"**

---

## 5️⃣ Établissement du chiffrement

Une fois les deux utilisateurs connectés :

1. **Échange automatique de clés ECDH**
   - Les deux navigateurs génèrent des clés cryptographiques
   - Les clés publiques sont échangées via le serveur
   - Un secret partagé est calculé localement

2. **Indicateurs de progression** :
   - "🔐 Génération de clés ECDH..."
   - "🔐 En attente de la clé du pair..."
   - "🔐 Calcul du secret partagé..."
   - "✅ Chiffrement établi !"

3. **Confirmation visuelle** :
   - Le badge passe au vert : **"🔒 Chiffrement actif"**
   - Le champ de saisie des messages devient actif
   - Vous pouvez maintenant commencer à discuter

---

## 6️⃣ Envoi de messages

1. **Taper votre message** dans le champ de saisie

2. **Indicateur de frappe** :
   - Les trois points s'affichent chez l'autre utilisateur
   - Indique que vous êtes en train d'écrire

3. **Envoyer le message** :
   - Cliquer sur le bouton d'envoi (icône avion) OU
   - Appuyer sur **Entrée**

4. **Chiffrement automatique** :
   - Votre message est chiffré localement avec AES-256-GCM
   - Le serveur ne voit que le message chiffré
   - L'autre utilisateur le déchiffre localement

5. **Affichage** :
   - Vos messages apparaissent à droite (bulles violettes)
   - Les messages reçus apparaissent à gauche (bulles claires)

---

## 7️⃣ Interface utilisateur

### Header (en haut)

- **Avatar** : Première lettre de votre pseudo
- **Statut de connexion** :
  - 🟡 Connexion... (jaune)
  - 🟢 Connecté (vert)
  - 🔴 Déconnecté (rouge)
- **Badge de chiffrement** :
  - ⚠️ Orange : Établissement du chiffrement
  - ✅ Vert : Chiffrement actif
- **Bouton Déconnexion** : Se déconnecter du chat
- **Toggle thème** : Basculer entre mode clair et sombre

### Zone de messages

- **Messages envoyés** : Alignés à droite, fond violet
- **Messages reçus** : Alignés à gauche, fond clair/sombre
- **Horodatage** : Affiché sous chaque message
- **Scroll automatique** : Vers le dernier message

### Zone de saisie (en bas)

- **Champ de texte** : Écrire vos messages
- **Bouton d'envoi** : Icône avion pour envoyer

---

## 8️⃣ Fonctionnalités

### 🌙 Mode sombre

- Cliquer sur l'icône en bas à droite (🌙 ou ☀️)
- Le thème est sauvegardé automatiquement
- Fonctionne aussi sur la page de connexion

### ⌨️ Indicateur de frappe

- S'affiche automatiquement quand l'autre personne écrit
- Disparaît après 1 seconde d'inactivité

### 📱 Design responsive

- L'interface s'adapte automatiquement :
  - Ordinateur de bureau (grand écran)
  - Tablette (écran moyen)
  - Téléphone (petit écran)

---

## 9️⃣ Déconnexion

### Méthode 1 : Bouton Déconnexion

1. Cliquer sur le bouton **"🚪 Déconnexion"** dans le header
2. Confirmer si demandé
3. Vous êtes redirigé vers la page de connexion

### Méthode 2 : Fermer l'onglet

- Simplement fermer l'onglet du navigateur
- La session expire automatiquement après 30 minutes

---

## 🔟 Sécurité et bonnes pratiques

### ✅ À FAIRE

- ✅ Échanger le secret partagé **avant** de vous connecter
- ✅ Utiliser un canal sécurisé pour partager le secret :
  - Appel téléphonique
  - SMS
  - En personne
  - Messagerie chiffrée (Signal, WhatsApp)
- ✅ Choisir un secret fort (12+ caractères, mélange de lettres, chiffres, symboles)
- ✅ Vérifier le badge "🔒 Chiffrement actif" avant d'envoyer des messages sensibles
- ✅ Fermer la session quand vous avez terminé

### ❌ À ÉVITER

- ❌ Ne JAMAIS envoyer le secret par email
- ❌ Ne pas utiliser de secrets évidents ("password", "123456")
- ❌ Ne pas réutiliser le même secret pour plusieurs sessions importantes
- ❌ Ne pas laisser de session ouverte sans surveillance
- ❌ Ne pas utiliser sur un réseau WiFi public non sécurisé

---

## 🛠️ Résolution de problèmes

### Problème : "Secret partagé incorrect"

**Solutions** :
1. Vérifier que vous utilisez **exactement** le même secret
2. Attention à la casse (majuscules/minuscules)
3. Vérifier qu'il n'y a pas d'espaces en trop
4. Si bloqué : attendre 5 minutes (protection anti-brute force)

### Problème : Le chiffrement ne s'établit pas

**Solutions** :
1. Rafraîchir la page (F5)
2. Vérifier votre connexion Internet/réseau
3. Ouvrir la console du navigateur (F12) pour voir les erreurs
4. Essayer avec un autre navigateur

### Problème : Les messages n'apparaissent pas

**Solutions** :
1. Vérifier le badge : doit être "🔒 Chiffrement actif"
2. Rafraîchir la page
3. Vérifier que l'autre utilisateur est bien connecté

### Problème : Impossible de se connecter à `http://[IP]:5000`

**Solutions** :
1. Vérifier que le serveur est bien démarré
2. Vérifier l'adresse IP (utiliser `ipconfig` ou `ifconfig`)
3. Vérifier que les deux machines sont sur le même réseau
4. Désactiver temporairement le firewall pour tester
5. Essayer avec `http://localhost:5000` si sur la même machine

---

## 📞 Support

Pour toute question ou problème :

1. Consulter d'abord ce manuel
2. Vérifier le README technique
3. Consulter `docs/security_analysis.md`

---

## 🎯 Résumé rapide

1. **Installer** : `pip install -r requirements.txt`
2. **Démarrer** : `python run.py`
3. **Se connecter** : Ouvrir `http://[IP]:5000`
4. **Secret** : Même secret pour les deux utilisateurs
5. **Attendre** : Établissement automatique du chiffrement
6. **Discuter** : Messages chiffrés de bout en bout

---

**Bon chat sécurisé ! 🔒💬**
