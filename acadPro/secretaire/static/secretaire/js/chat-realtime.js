// Script pour rendre le chat en temps réel
document.addEventListener('DOMContentLoaded', function() 
{
    // Référence au conteneur des messages
    const chatBody = document.getElementById('chat-body');
    // ID de l'étudiant avec qui on converse (récupéré de l'URL)
    const urlParts = window.location.pathname.split('/');
    const etudiantId = urlParts[urlParts.length - 2]; // Avant-dernier segment de l'URL
    const matriculeEleve = urlParts[urlParts.length - 1]; // Dernier segment de l'URL
    
    // Dernier ID de message pour ne récupérer que les nouveaux
    let lastMessageId = getLastMessageId();
    
    // Faire défiler jusqu'au bas de la conversation lors du chargement
    chatBody.scrollTop = chatBody.scrollHeight;
    
    // Fonction pour récupérer le dernier ID de message affiché
    function getLastMessageId() {
        const messages = chatBody.querySelectorAll('.message');
        if (messages.length === 0) return 0;
        // On pourrait stocker l'ID du message dans un attribut data-*
        // Pour cette démo, on va supposer qu'on peut récupérer l'ID du dernier message
        return messages.length; // Simplifié pour l'exemple
    }
    
    // Fonction pour ajouter un nouveau message au chat
    function appendMessage(message) {
        // Vérifier si le message n'est pas déjà affiché
        if (document.querySelector(`[data-message-id="${message.id}"]`)) {
            return;
        }
        
        const messageWrapper = document.createElement('div');
        
        // Si l'expéditeur est l'élève courant (matricule), c'est un message envoyé
        if (message.expediteur_matricule === matriculeEleve) {
            messageWrapper.className = 'message-wrapper';
            messageWrapper.innerHTML = `
                <div class="message sent" style="margin-bottom: 10px; background-color:rgb(134, 160, 176)!important;" data-message-id="${message.id}">
                    <div class="message-content">${message.contenu}</div>
                    <div class="message-time">${message.date_envoi}</div>
                </div>
                <div class="dropdown">
                    <a class="dropdown-toggle" href="#" role="button" data-toggle="dropdown" aria-expanded="false">...</a>
                    <div class="dropdown-menu dropdown-menu-right">
                        <a class="dropdown-item" href="#"><i class="fas fa-times text-orange-red"></i> Supprimer</a>
                        <a class="dropdown-item" href="#"><i class="fas fa-cogs text-dark-pastel-green"></i> Modifier</a>
                    </div>
                </div>
            `;
        } else {
            // Sinon c'est un message reçu
            messageWrapper.className = 'message received';
            messageWrapper.setAttribute('data-message-id', message.id);
            messageWrapper.innerHTML = `
                <div class="message-content">${message.contenu}</div>
                <div class="message-time">${message.date_envoi}</div>
            `;
        }
        
        chatBody.appendChild(messageWrapper);
        chatBody.scrollTop = chatBody.scrollHeight;
    }
    
    // Fonction pour récupérer les nouveaux messages du serveur
    function fetchNewMessages() {
        fetch(`/api/messages/${etudiantId}/${matriculeEleve}/?since=${lastMessageId}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(message => {
                    appendMessage(message);
                });
                // Mettre à jour le dernier ID
                lastMessageId = data.last_id;
                
                // Marquer les messages comme lus
                if (data.messages.length > 0) {
                    markMessagesAsRead();
                }
            }
        })
        .catch(error => console.error('Erreur lors de la récupération des messages:', error));
    }
    
    // Fonction pour marquer les messages comme lus
    function markMessagesAsRead() {
        fetch(`/api/messages/${etudiantId}/${matriculeEleve}/read/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'same-origin'
        });
    }
    
    // Fonction pour envoyer un message
    const messageForm = document.querySelector('.chat-footer');
    const messageInput = document.getElementById('messageInput');
    
    messageForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = messageInput.value.trim();
        if (!message) return;
        
        // Envoyer le message via AJAX
        fetch(`/api/messages/${etudiantId}/${matriculeEleve}/send/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ message: message }),
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Ajouter le message envoyé à l'interface
                appendMessage({
                    id: data.message_id,
                    contenu: message,
                    date_envoi: data.date_envoi,
                    expediteur_matricule: matriculeEleve
                });
                
                // Vider le champ de saisie
                messageInput.value = '';
            }
        })
        .catch(error => console.error('Erreur lors de l\'envoi du message:', error));
    });
    
    // Fonction utilitaire pour obtenir les cookies (pour le CSRF)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Lancer la vérification périodique des nouveaux messages
    setInterval(fetchNewMessages, 3000); // Toutes les 1 secondes
    
    // Vérifier les nouveaux messages immédiatement au chargement
    fetchNewMessages();
});