document.addEventListener('DOMContentLoaded', function () {
    const chatBody = document.getElementById('chat-body');
    const etudiantId = chatBody.dataset.etudiantId;

    // Dernier ID de message pour ne récupérer que les nouveaux
    let lastMessageId = getLastMessageId();

    // Défilement automatique
    chatBody.scrollTop = chatBody.scrollHeight;

    function getLastMessageId() {
        const messages = chatBody.querySelectorAll('.message');
        if (messages.length === 0) return 0;
        const last = messages[messages.length - 1];
        return parseInt(last.getAttribute('data-message-id')) || 0;
    }

    function appendMessage(message) {
        if (document.querySelector(`[data-message-id="${message.id}"]`)) return;

        const messageWrapper = document.createElement('div');
        messageWrapper.setAttribute('data-message-id', message.id);

        if (message.expediteur_matricule === chatBody.dataset.matricule) {
            messageWrapper.className = 'message-wrapper';
            messageWrapper.innerHTML = `
                <div class="message sent" style="margin-bottom: 10px; background-color: rgb(134, 160, 176) !important;">
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
            messageWrapper.className = 'message received';
            messageWrapper.innerHTML = `
                <div class="message-content">${message.contenu}</div>
                <div class="message-time">${message.date_envoi}</div>
            `;
        }

        chatBody.appendChild(messageWrapper);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function fetchNewMessages() {
        fetch(`/api/messages/${etudiantId}/?since=${lastMessageId}`, {
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
                data.messages.forEach(message => appendMessage(message));
                lastMessageId = data.last_id;
                markMessagesAsRead();
            }
        })
        .catch(error => console.error('Erreur récupération messages:', error));
    }

    function markMessagesAsRead() {
        fetch(`/api/messages/${etudiantId}/read/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'same-origin'
        });
    }

    // Envoi de message
    const messageForm = document.querySelector('.chat-footer');
    const messageInput = document.getElementById('messageInput');

    if (messageForm) {
        messageForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const message = messageInput.value.trim();
            if (!message) return;

            fetch(`/api/messages/${etudiantId}/send/`, {
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
                    appendMessage({
                        id: data.message_id,
                        contenu: message,
                        date_envoi: data.date_envoi,
                        expediteur_matricule: chatBody.dataset.matricule
                    });
                    messageInput.value = '';
                } else {
                    console.error("Erreur d'envoi:", data.error);
                }
            })
            .catch(error => console.error("Erreur d'envoi:", error));
        });
    }

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

    setInterval(fetchNewMessages, 3000);
    fetchNewMessages();
});
