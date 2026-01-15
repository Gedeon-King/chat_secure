# Analyse de Sécurité - Secure LAN Chat

## 📊 Vue d'ensemble

Cette document analyse les mesures de sécurité implémentées et les vulnérabilités potentielles de l'application.

---

## 🔐 Mesures de sécurité implémentées

### 1. Chiffrement de bout en bout

#### ECDH (Elliptic Curve Diffie-Hellman)
- **Courbe** : P-256 (secp256r1)
- **Longueur de clé** : 256 bits
- **Implémentation** : Bibliothèque `cryptography` (Python) et Web Crypto API (JavaScript)
- **Protection** : Les clés privées ne quittent JAMAIS les terminaux

#### AES-256-GCM
- **Mode** : GCM (Galois/Counter Mode)
- **Longueur de clé** : 256 bits
- **IV** : 12 bytes, généré aléatoirement pour chaque message
- **Tag d'authentification** : 128 bits (intégré avec GCM)
- **Avantages** : AEAD (Authenticated Encryption with Associated Data)

#### HKDF (Key Derivation Function)
- **Fonction de hash** : SHA-256
- **Usage** : Dériver les clés de chiffrement et HMAC depuis le secret partagé ECDH
- **Longueur de sortie** : 64 bytes (32 pour AES, 32 pour HMAC)

#### HMAC-SHA256
- **Usage** : Signature des messages complets
- **Longueur** : 256 bits
- **Protection** : Intégrité et authenticité supplémentaires

---

### 2. Authentification

#### Secret partagé
- **Méthode** : PBKDF2-HMAC-SHA256
- **Itérations** : 100,000
- **Salt** : 32 bytes aléatoires
- **Stockage** : Hash uniquement (jamais le secret en clair)

#### Rate Limiting
- **Limite** : 5 tentatives de connexion
- **Fenêtre** : 5 minutes
- **Par IP** : Suivi des tentatives par adresse IP
- **Protection** : Anti-brute force

---

### 3. Protection réseau

#### Anti-replay
- **Timestamp** : Validation ±30 secondes
- **Nonces** : ID unique (UUID) pour chaque message
- **Cache** : Stockage des nonces récents (1000 derniers)

#### Validation des données
- **Whitelist** : Validation stricte de tous les champs
- **Sanitization** : Nettoyage des entrées utilisateur
- **Type checking** : Vérification des types de données

#### WebSocket sécurisé
- **Session** : Vérification de session pour chaque événement
- **CSRF tokens** : Protection contre les attaques CSRF
- **Origine** : Validation de l'origine en production

---

### 4. Sécurité web

#### Headers de sécurité
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: [politique stricte]
```

#### Sessions
- **Stockage** : Côté serveur (filesystem)
- **Cookies** : HttpOnly, SameSite=Lax
- **Expiration** : 30 minutes d'inactivité
- **Nettoyage** : Automatique des sessions expirées

---

## 🎯 Modèle de menaces (STRIDE)

### Spoofing (Usurpation d'identité)
- ✅ **Mitigé** : Secret partagé + authentification forte
- ⚠️ **Résiduel** : Si le secret est compromis

### Tampering (Falsification)
- ✅ **Mitigé** : Tag GCM + HMAC-SHA256
- ✅ **Détection** : Échec automatique du déchiffrement

### Repudiation (Répudiation)
- ⚠️ **Partiellement** : Pas de journalisation permanente (par design)
- ℹ️ **Note** : Volontaire pour la confidentialité

### Information Disclosure (Divulgation d'information)
- ✅ **Mitigé** : Chiffrement AES-256-GCM
- ✅ **Métadonnées** : Minimales (timestamps uniquement)

### Denial of Service (Déni de service)
- ⚠️ **Partiellement** : Rate limiting basique
- ⚠️ **Vulnérable** : Flood de connexions WebSocket

### Elevation of Privilege (Élévation de privilèges)
- ✅ **Mitigé** : Pas de notion de privilèges (chat 1-1)
- ✅ **Sessions** : Isolées et sécurisées

---

## ⚠️ Vulnérabilités résiduelles

### 1. Sécurité du secret partagé
**Risque** : Si le secret est faible ou compromis, toute la sécurité est inefficace

**Mitigation** :
- Exiger un secret fort (12+ caractères)
- Documenter la nécessité d'un canal sécurisé
- Permettre le changement de secret

### 2. Pas de TLS
**Risque** : Le trafic WebSocket n'est pas chiffré au niveau transport

**Mitigation** :
- Usage limité au LAN (risque réduit)
- Ajout de TLS recommandé pour production
- Utilisation de VPN en complément

### 3. Pas de vérification d'identité
**Risque** : Impossible de prouver l'identité réelle de l'interlocuteur

**Mitigation** :
- Vérification hors-bande (voix, vidéo)
- Échange de fingerprints des clés publiques (future amélioration)

### 4. Pas de forward secrecy parfaite
**Risque** : Si les clés sont compromises, tous les messages de la session peuvent être déchiffrés

**Mitigation** :
- Régénération périodique des clés (future amélioration)
- Sessions courtes recommandées

### 5. DoS sur le serveur
**Risque** : Le serveur peut être submergé de connexions

**Mitigation** :
- Rate limiting global (à implémenter)
- Limitation du nombre de connexions
- Monitoring des ressources

---

## 🧪 Scénarios de test

### Test 1 : MITM (Man-in-the-Middle)

**Objectif** : Vérifier qu'un attaquant ne peut pas intercepter et déchiffrer les messages

**Procédure** :
1. Lancer Wireshark sur le réseau
2. Établir une communication entre Alice et Bob
3. Capturer le trafic WebSocket
4. Tenter de déchiffrer les messages capturés

**Résultat attendu** :
- ✅ Les messages apparaissent chiffrés (base64)
- ✅ Impossible de déchiffrer sans les clés privées
- ✅ Le secret partagé n'est jamais transmis

### Test 2 : Replay Attack

**Objectif** : Vérifier qu'un ancien message ne peut pas être renvoyé

**Procédure** :
1. Capturer un message valide
2. Renvoyer le même message au serveur

**Résultat attendu** :
- ✅ Message rejeté (nonce déjà vu)
- ✅ Message rejeté (timestamp expiré après 30s)

### Test 3 : Falsification de message

**Objectif** : Vérifier qu'un message modifié est détecté

**Procédure** :
1. Intercepter un message chiffré
2. Modifier le ciphertext
3. Envoyer le message modifié

**Résultat attendu** :
- ✅ Tag GCM invalide
- ✅ Déchiffrement échoue
- ✅ Message rejeté

### Test 4 : Brute Force du secret

**Objectif** : Vérifier la protection anti-brute force

**Procédure** :
1. Tenter 10 connexions avec des secrets différents
2. Observer le blocage

**Résultat attendu** :
- ✅ Bloqué après 5 tentatives
- ✅ Déblocage après 5 minutes

### Test 5 : XSS (Cross-Site Scripting)

**Objectif** : Vérifier que les scripts injectés ne s'exécutent pas

**Procédure** :
1. Envoyer un message contenant `<script>alert('XSS')</script>`
2. Observer l'affichage

**Résultat attendu** :
- ✅ Le script est échappé et affiché comme texte
- ✅ Aucun code JavaScript n'est exécuté

---

## 📋 Recommandations

### Pour les utilisateurs

1. **Secret fort** : Minimum 12 caractères, alphanumérique + symboles
2. **Canal sécurisé** : Échanger le secret en personne ou par téléphone
3. **Vérification** : Vérifier que le chiffrement est établi avant d'envoyer des données sensibles
4. **Réseau de confiance** : Utiliser uniquement sur un LAN de confiance
5. **Sessions courtes** : Se déconnecter après utilisation

### Pour les administrateurs

1. **TLS** : Ajouter HTTPS/WSS en production
2. **Firewall** : Limiter l'accès au port 5000
3. **Monitoring** : Surveiller les connexions et les erreurs
4. **Logs** : Activer les logs pour détecter les anomalies
5. **Mises à jour** : Maintenir les dépendances à jour

### Améliorations futures

1. **Fingerprints** : Afficher et comparer les fingerprints des clés publiques
2. **Perfect Forward Secrecy** : Régénérer les clés périodiquement
3. **Multi-utilisateurs** : Support de groupes chiffrés
4. **Persistance** : Option de sauvegarde chiffrée de l'historique
5. **Audit** : Audit de sécurité professionnel

---

## ✅ Conformité

### OWASP Top 10 (2021)

| Vulnérabilité | État | Notes |
|---------------|------|-------|
| Broken Access Control | ✅ Protégé | Sessions et authentification |
| Cryptographic Failures | ✅ Protégé | AES-256-GCM, ECDH, HKDF |
| Injection | ✅ Protégé | Validation et sanitization |
| Insecure Design | ⚠️ Partiel | Pas de TLS (volontaire LAN) |
| Security Misconfiguration | ✅ Protégé | Headers sécurité, CSP |
| Vulnerable Components | ✅ Protégé | Dépendances à jour |
| Identification Failures | ✅ Protégé | Rate limiting, PBKDF2 |
| Software Integrity Failures | ✅ Protégé | Pas de CDN non vérifié |
| Logging Failures | ⚠️ Partiel | Logs minimaux (privacy) |
| SSRF | N/A | Pas de requêtes externes |

---

## 🎓 Conclusion

L'application implémente des mesures de sécurité robustes pour un chat en LAN :

✅ **Points forts** :
- Chiffrement de bout en bout solide (ECDH + AES-256-GCM)
- Protection contre les attaques courantes (MITM, replay, XSS)
- Architecture sécurité en profondeur

⚠️ **Limitations** :
- Pas de TLS (acceptable en LAN de confiance)
- Sécurité dépend du secret partagé
- Pas de forward secrecy parfaite

**Recommandation finale** : Cette application est appropriée pour des communications en LAN de confiance. Pour un usage professionnel ou sensible, un audit de sécurité par des experts est recommandé.

---

**Date d'analyse** : Janvier 2026  
**Version analysée** : 1.0.0
