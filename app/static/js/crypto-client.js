/**
 * Client-side cryptography pour le chiffrement de bout en bout
 * 
 * Note: Ce fichier utilise Web Crypto API pour l'implémentation ECDH et AES-GCM côté client.
 * La clé de chiffrement ne quitte JAMAIS le navigateur de l'utilisateur.
 */

class CryptoClient {
    constructor() {
        this.privateKey = null;
        this.publicKey = null;
        this.sharedSecret = null;
        this.encryptionKey = null;
        this.hmacKey = null;
    }

    /**
     * Génère une paire de clés ECDH
     * @returns {Promise<string>} Clé publique en base64
     */
    async generateKeyPair() {
        try {
            // Générer une paire de clés ECDH avec la courbe P-256
            const keyPair = await window.crypto.subtle.generateKey(
                {
                    name: 'ECDH',
                    namedCurve: 'P-256'
                },
                true,  // extractable
                ['deriveKey', 'deriveBits']
            );

            this.privateKey = keyPair.privateKey;
            this.publicKey = keyPair.publicKey;

            // Exporter la clé publique
            const exportedKey = await window.crypto.subtle.exportKey('raw', this.publicKey);
            const publicKeyB64 = this.arrayBufferToBase64(exportedKey);

            console.log('Paire de clés ECDH générée');
            return publicKeyB64;
        } catch (error) {
            console.error('Erreur lors de la génération de clés:', error);
            throw error;
        }
    }

    /**
     * Calcule le secret partagé et dérive les clés de chiffrement
     * @param {string} peerPublicKeyB64 - Clé publique du pair en base64
     */
    async computeSharedSecret(peerPublicKeyB64) {
        try {
            // Importer la clé publique du pair
            const peerPublicKeyBuffer = this.base64ToArrayBuffer(peerPublicKeyB64);
            const peerPublicKey = await window.crypto.subtle.importKey(
                'raw',
                peerPublicKeyBuffer,
                {
                    name: 'ECDH',
                    namedCurve: 'P-256'
                },
                false,
                []
            );

            // Dériver le secret partagé
            const sharedSecretBits = await window.crypto.subtle.deriveBits(
                {
                    name: 'ECDH',
                    public: peerPublicKey
                },
                this.privateKey,
                256  // 256 bits
            );

            this.sharedSecret = sharedSecretBits;

            // Dériver les clés de chiffrement et HMAC avec HKDF
            await this.deriveKeys();

            console.log('Secret partagé calculé et clés dérivées');
        } catch (error) {
            console.error('Erreur lors du calcul du secret partagé:', error);
            throw error;
        }
    }

    /**
     * Dérive les clés de chiffrement et HMAC depuis le secret partagé
     */
    async deriveKeys() {
        try {
            // Importer le secret partagé comme clé de base
            const baseKey = await window.crypto.subtle.importKey(
                'raw',
                this.sharedSecret,
                'HKDF',
                false,
                ['deriveKey']
            );

            const info = new TextEncoder().encode('chat_secure_keys');

            // Dériver la clé de chiffrement AES-256
            this.encryptionKey = await window.crypto.subtle.deriveKey(
                {
                    name: 'HKDF',
                    hash: 'SHA-256',
                    salt: new Uint8Array(0),
                    info: info
                },
                baseKey,
                {
                    name: 'AES-GCM',
                    length: 256
                },
                false,
                ['encrypt', 'decrypt']
            );

            // Dériver la clé HMAC
            const hmacKeyMaterial = await window.crypto.subtle.deriveKey(
                {
                    name: 'HKDF',
                    hash: 'SHA-256',
                    salt: new Uint8Array(32),  // Salt différent pour HMAC
                    info: info
                },
                baseKey,
                {
                    name: 'HMAC',
                    hash: 'SHA-256',
                    length: 256
                },
                true,
                ['sign', 'verify']
            );

            this.hmacKey = hmacKeyMaterial;

            console.log('Clés de chiffrement dérivées avec succès');
        } catch (error) {
            console.error('Erreur lors de la dérivation des clés:', error);
            throw error;
        }
    }

    /**
     * Chiffre un message avec AES-256-GCM
     * @param {string} plaintext - Message en clair
     * @returns {Promise<Object>} Données chiffrées {ciphertext, iv, tag}
     */
    async encrypt(plaintext) {
        try {
            if (!this.encryptionKey) {
                throw new Error('Clé de chiffrement non disponible');
            }

            // Générer un IV aléatoire (12 bytes pour GCM)
            const iv = window.crypto.getRandomValues(new Uint8Array(12));

            // Chiffrer le message
            const plaintextBuffer = new TextEncoder().encode(plaintext);
            const ciphertext = await window.crypto.subtle.encrypt(
                {
                    name: 'AES-GCM',
                    iv: iv,
                    tagLength: 128  // 128 bits pour le tag d'authentification
                },
                this.encryptionKey,
                plaintextBuffer
            );

            // GCM retourne ciphertext + tag
            // Séparer pour plus de clarté
            const ciphertextArray = new Uint8Array(ciphertext);
            const actualCiphertext = ciphertextArray.slice(0, -16);
            const tag = ciphertextArray.slice(-16);

            return {
                ciphertext: this.arrayBufferToBase64(actualCiphertext),
                iv: this.arrayBufferToBase64(iv),
                tag: this.arrayBufferToBase64(tag)
            };
        } catch (error) {
            console.error('Erreur lors du chiffrement:', error);
            throw error;
        }
    }

    /**
     * Déchiffre un message AES-256-GCM
     * @param {string} ciphertextB64 - Ciphertext en base64
     * @param {string} ivB64 - IV en base64
     * @param {string} tagB64 - Tag en base64
     * @returns {Promise<string>} Message en clair
     */
    async decrypt(ciphertextB64, ivB64, tagB64) {
        try {
            if (!this.encryptionKey) {
                throw new Error('Clé de chiffrement non disponible');
            }

            // Décoder depuis base64
            const ciphertext = this.base64ToArrayBuffer(ciphertextB64);
            const iv = this.base64ToArrayBuffer(ivB64);
            const tag = this.base64ToArrayBuffer(tagB64);

            // Reconstruire ciphertext + tag
            const fullCiphertext = new Uint8Array(ciphertext.byteLength + tag.byteLength);
            fullCiphertext.set(new Uint8Array(ciphertext), 0);
            fullCiphertext.set(new Uint8Array(tag), ciphertext.byteLength);

            // Déchiffrer
            const plaintextBuffer = await window.crypto.subtle.decrypt(
                {
                    name: 'AES-GCM',
                    iv: iv,
                    tagLength: 128
                },
                this.encryptionKey,
                fullCiphertext
            );

            return new TextDecoder().decode(plaintextBuffer);
        } catch (error) {
            console.error('Erreur lors du déchiffrement:', error);
            throw error;
        }
    }

    /**
     * Calcule HMAC d'un message
     * @param {string} message - Message à signer
     * @returns {Promise<string>} HMAC en base64
     */
    async computeHMAC(message) {
        try {
            if (!this.hmacKey) {
                throw new Error('Clé HMAC non disponible');
            }

            const messageBuffer = new TextEncoder().encode(message);
            const signature = await window.crypto.subtle.sign(
                'HMAC',
                this.hmacKey,
                messageBuffer
            );

            return this.arrayBufferToBase64(signature);
        } catch (error) {
            console.error('Erreur lors du calcul HMAC:', error);
            throw error;
        }
    }

    /**
     * Vérifie un HMAC
     * @param {string} message - Message original
     * @param {string} expectedHmacB64 - HMAC attendu en base64
     * @returns {Promise<boolean>} True si valide
     */
    async verifyHMAC(message, expectedHmacB64) {
        try {
            const computedHmac = await this.computeHMAC(message);
            return computedHmac === expectedHmacB64;
        } catch (error) {
            console.error('Erreur lors de la vérification HMAC:', error);
            return false;
        }
    }

    /**
     * Convertit ArrayBuffer en base64
     * @param {ArrayBuffer} buffer
     * @returns {string}
     */
    arrayBufferToBase64(buffer) {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
    }

    /**
     * Convertit base64 en ArrayBuffer
     * @param {string} base64
     * @returns {ArrayBuffer}
     */
    base64ToArrayBuffer(base64) {
        // Restaurer les caractères standard base64
        base64 = base64.replace(/-/g, '+').replace(/_/g, '/');

        // Ajouter le padding si nécessaire
        while (base64.length % 4) {
            base64 += '=';
        }

        const binary = atob(base64);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i);
        }
        return bytes.buffer;
    }

    /**
     * Vérifie si le chiffrement est prêt
     * @returns {boolean}
     */
    isReady() {
        return this.encryptionKey !== null && this.hmacKey !== null;
    }
}

// Rendre disponible globalement
if (typeof window !== 'undefined') {
    window.CryptoClient = CryptoClient;
}
