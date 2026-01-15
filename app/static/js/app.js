/**
 * Gestion du chat en temps réel avec SocketIO
 * Intègre le chiffrement de bout en bout
 */

// Vérifier qu'on est sur la page de chat
if (window.location.pathname === '/chat') {
    // Récupérer les données de l'app
    const appData = document.getElementById('appData');
    const username = appData.dataset.username;
    const csrfToken = appData.dataset.csrfToken;

    // Initialiser le client de cryptographie
    const cryptoClient = new CryptoClient();

    // Connexion Socket.IO
    const socket = io({
        transports: ['websocket', 'polling']
    });

    // Éléments DOM
    const messagesContainer = document.getElementById('messagesContainer');
    const messageForm = document.getElementById('messageForm');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const connectionStatus = document.getElementById('connectionStatus');
    const encryptionBadge = document.getElementById('encryptionBadge');
    const typingIndicator = document.getElementById('typingIndicator');

    // État
    let isEncryptionReady = false;
    let isTyping = false;
    let typingTimeout = null;

    /**
     * Mise à jour du statut de connexion
     */
    function updateConnectionStatus(status, text) {
        const statusDot = connectionStatus.querySelector('.status-dot');
        const statusText = connectionStatus;

        statusDot.className = 'status-dot status-' + status;

        if (text) {
            statusText.innerHTML = `<span class="status-dot status-${status}"></span> ${text}`;
        }
    }

    /**
     * Mise à jour du badge de chiffrement
     */
    function updateEncryptionBadge(ready) {
        if (ready) {
            encryptionBadge.innerHTML = '🔒 Chiffrement actif';
            encryptionBadge.className = 'badge bg-success me-2';
        } else {
            encryptionBadge.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Établissement...';
            encryptionBadge.className = 'badge bg-warning me-2';
        }
    }

    /**
     * Afficher un message dans le chat
     */
    function displayMessage(sender, content, timestamp, isSent = false) {
        // Supprimer le message de bienvenue si présent
        const welcome = messagesContainer.querySelector('.messages-welcome');
        if (welcome) {
            welcome.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isSent ? 'message-sent' : 'message-received'}`;

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';

        if (!isSent) {
            const senderSpan = document.createElement('div');
            senderSpan.className = 'message-sender';
            senderSpan.textContent = sender;
            bubbleDiv.appendChild(senderSpan);
        }

        const contentP = document.createElement('div');
        contentP.textContent = content;
        bubbleDiv.appendChild(contentP);

        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';
        metaDiv.textContent = formatTimestamp(timestamp);
        bubbleDiv.appendChild(metaDiv);

        messageDiv.appendChild(bubbleDiv);
        messagesContainer.appendChild(messageDiv);

        // Scroll vers le bas
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    /**
     * Afficher un message système
     */
    function displaySystemMessage(text) {
        const welcome = messagesContainer.querySelector('.messages-welcome');
        if (welcome) {
            const infoDiv = welcome.querySelector('.encryption-info small');
            if (infoDiv) {
                infoDiv.textContent = text;
            }
        }
    }

    /**
     * Événement: Connexion établie
     */
    socket.on('connect', async () => {
        console.log('WebSocket connecté');
        updateConnectionStatus('connected', 'Connecté');

        try {
            // Générer la paire de clés ECDH
            displaySystemMessage('🔐 Génération de clés ECDH...');
            const publicKey = await cryptoClient.generateKeyPair();

            // Envoyer la clé publique au serveur
            socket.emit('key_exchange', { public_key: publicKey }, (response) => {
                if (response.success) {
                    console.log('Clé publique envoyée');
                    displaySystemMessage('🔐 En attente de la clé du pair...');
                } else {
                    console.error('Erreur lors de l\'échange de clés:', response.error);
                }
            });
        } catch (error) {
            console.error('Erreur lors de la génération de clés:', error);
            alert('Erreur lors de l\'établissement du chiffrement');
        }
    });

    /**
     * Événement: Clé publique du pair reçue
     */
    socket.on('peer_public_key', async (data) => {
        console.log('Clé publique du pair reçue:', data.username);
        displaySystemMessage('🔐 Calcul du secret partagé...');

        try {
            // Calculer le secret partagé et dériver les clés
            await cryptoClient.computeSharedSecret(data.public_key);

            // Marquer le chiffrement comme établi
            isEncryptionReady = true;
            socket.emit('encryption_ready');

            // Mettre à jour l'interface
            updateEncryptionBadge(true);
            displaySystemMessage('✅ Chiffrement établi ! Vous pouvez maintenant envoyer des messages sécurisés.');

            // Activer le champ de saisie
            messageInput.disabled = false;
            sendButton.disabled = false;
            messageInput.focus();

            console.log('Chiffrement de bout en bout établi');
        } catch (error) {
            console.error('Erreur lors du calcul du secret:', error);
            alert('Erreur lors de l\'établissement du chiffrement');
        }
    });

    /**
     * Événement: Message reçu
     */
    socket.on('receive_message', async (data) => {
        console.log('Message chiffré reçu');

        try {
            // Vérifier HMAC
            const messageStr = JSON.stringify({
                id: data.id,
                sender: data.sender,
                content: data.content,
                iv: data.iv,
                tag: data.tag,
                timestamp: data.timestamp
            });

            const isValid = await cryptoClient.verifyHMAC(messageStr, data.hmac);
            if (!isValid) {
                console.error('HMAC invalide - message rejeté');
                return;
            }

            // Déchiffrer le message
            const plaintext = await cryptoClient.decrypt(data.content, data.iv, data.tag);

            // Afficher le message
            displayMessage(data.sender, plaintext, data.timestamp, false);
        } catch (error) {
            console.error('Erreur lors du déchiffrement du message:', error);
            displayMessage('Système', '❌ Erreur de déchiffrement', Date.now() / 1000, false);
        }
    });

    /**
     * Événement: Utilisateur connecté
     */
    socket.on('user_connected', (data) => {
        console.log('Utilisateur connecté:', data.username);
        displaySystemMessage(`👋 ${data.username} vient de se connecter`);
    });

    /**
     * Événement: Utilisateur déconnecté
     */
    socket.on('user_disconnected', (data) => {
        console.log('Utilisateur déconnecté:', data.username);
        updateConnectionStatus('disconnected', 'Pair déconnecté');
        isEncryptionReady = false;
        updateEncryptionBadge(false);
        messageInput.disabled = true;
        sendButton.disabled = true;
    });

    /**
     * Événement: Indicateur de frappe
     */
    socket.on('user_typing', (data) => {
        if (data.is_typing) {
            typingIndicator.querySelector('.typing-text').textContent = `${data.username} est en train d'écrire...`;
            typingIndicator.style.display = 'flex';
        } else {
            typingIndicator.style.display = 'none';
        }
    });

    /**
     * Événement: Déconnexion
     */
    socket.on('disconnect', () => {
        console.log('WebSocket déconnecté');
        updateConnectionStatus('disconnected', 'Déconnecté');
        messageInput.disabled = true;
        sendButton.disabled = true;
    });

    /**
     * Gestion de la frappe (indicateur)
     */
    messageInput.addEventListener('input', () => {
        if (!isTyping && isEncryptionReady) {
            isTyping = true;
            socket.emit('typing', { is_typing: true });
        }

        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(() => {
            isTyping = false;
            socket.emit('typing', { is_typing: false });
        }, 1000);
    });

    /**
     * Gestion de l'envoi de messages
     */
    messageForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const message = messageInput.value.trim();
        if (!message || !isEncryptionReady) return;

        try {
            // Chiffrer le message
            const encrypted = await cryptoClient.encrypt(message);

            // Créer l'objet message
            const messageData = {
                id: crypto.randomUUID(),
                sender: username,
                content: encrypted.ciphertext,
                iv: encrypted.iv,
                tag: encrypted.tag,
                timestamp: Date.now() / 1000
            };

            // Calculer HMAC
            const messageStr = JSON.stringify({
                id: messageData.id,
                sender: messageData.sender,
                content: messageData.content,
                iv: messageData.iv,
                tag: messageData.tag,
                timestamp: messageData.timestamp
            });

            messageData.hmac = await cryptoClient.computeHMAC(messageStr);

            // Envoyer le message
            socket.emit('send_message', messageData, (response) => {
                if (response.success) {
                    // Afficher le message envoyé
                    displayMessage(username, message, messageData.timestamp, true);

                    // Réinitialiser le champ
                    messageInput.value = '';

                    // Arrêter l'indicateur de frappe
                    if (isTyping) {
                        isTyping = false;
                        socket.emit('typing', { is_typing: false });
                    }
                } else {
                    console.error('Erreur lors de l\'envoi:', response.error);
                    alert('Erreur lors de l\'envoi du message');
                }
            });
        } catch (error) {
            console.error('Erreur lors du chiffrement:', error);
            alert('Erreur lors du chiffrement du message');
        }
    });

    // Fonction formatTimestamp (si pas déjà définie)
    if (typeof formatTimestamp === 'undefined') {
        function formatTimestamp(timestamp) {
            const date = new Date(timestamp * 1000);
            const now = new Date();
            const diff = Math.floor((now - date) / 1000);

            if (diff < 60) return 'À l\'instant';
            if (diff < 3600) return `Il y a ${Math.floor(diff / 60)} min`;
            if (diff < 86400) return `Il y a ${Math.floor(diff / 3600)} h`;

            return date.toLocaleDateString('fr-FR', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }
}
