function scrollToBottom() {
    var chatContainer = document.getElementById("messagesContainer");
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

userInfoModal.addEventListener('show.bs.modal', function () {
    const header = document.getElementById('chatHeader');
    document.getElementById('modalFullName').innerText = document.getElementById('chatName').innerText;
    document.getElementById('modalAvatar').src = document.getElementById('chatAvatar').src;
    document.getElementById('modalBio').innerText = header.getAttribute('data-bio');
    document.getElementById('modalJoined').innerText = header.getAttribute('data-joined');
    document.getElementById('modalFriendsSince').innerText = header.getAttribute('data-friends-since');
});

(function() {
    // ========== SEARCH FILTER ==========
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        function filterFriends() {
            const query = searchInput.value.trim().toLowerCase();
            const contactItems = document.querySelectorAll('.contact-item');
            let visibleCount = 0;
            contactItems.forEach(item => {
                const nameSpan = item.querySelector('.contact-name');
                if (!nameSpan) return;
                const friendName = nameSpan.innerText.toLowerCase();
                if (query === '' || friendName.includes(query)) {
                    item.style.display = '';
                    visibleCount++;
                } else {
                    item.style.display = 'none';
                }
            });
            let noResultsMsg = document.getElementById('noSearchResults');
            if (visibleCount === 0) {
                if (!noResultsMsg) {
                    const contactsList = document.querySelector('.contacts-list');
                    noResultsMsg = document.createElement('div');
                    noResultsMsg.id = 'noSearchResults';
                    noResultsMsg.className = 'no-contacts';
                    noResultsMsg.innerHTML = '<i class="bi bi-search"></i> No matching friends found';
                    contactsList.appendChild(noResultsMsg);
                }
            } else if (noResultsMsg) {
                noResultsMsg.remove();
            }
        }
        searchInput.addEventListener('input', filterFriends);
    }

    // ========== CHAT SENDING LOGIC (for the right panel) ==========
    const sendBtn = document.getElementById('sendBtn');
    const messageInput = document.getElementById('messageInput');
    const fileInput = document.getElementById('fileInput');
    const messagesContainer = document.getElementById('messagesContainer');

    // Helper to get CSRF token
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

    async function sendMessage(text, imageDataUrl = null) {
        const friendshipId = document.getElementById('friendshipId').value;
        const url = `/chat/image-message/${friendshipId}/`;
        const formData = new FormData();
        formData.append('text_message', text || '');

        if (imageDataUrl) {
            // Convert data URL to Blob
            const blob = await fetch(imageDataUrl).then(r => r.blob());
            formData.append('image', blob, 'image.jpg');
        }

        const csrftoken = getCookie('csrftoken');
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                body: formData,
            });
            if (response.ok) {
                // Reload the page to show the new message (or you can append dynamically)
                // window.location.reload();
            } else {
                console.error('Send failed');
            }
        } catch (err) {
            console.error('Error sending message:', err);
        }
    }

    // Image preview modal logic
    let pendingImageFile = null;
    const previewModal = new bootstrap.Modal(document.getElementById('imagePreviewModal'));
    const previewImage = document.getElementById('previewImage');
    const captionInput = document.getElementById('captionInput');
    const sendImageBtn = document.getElementById('sendImageBtn');

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                pendingImageFile = file;
                const reader = new FileReader();
                reader.onload = function(ev) {
                    previewImage.src = ev.target.result;
                    captionInput.value = '';
                    previewModal.show();
                };
                reader.readAsDataURL(file);
            }
            fileInput.value = '';
        });
    }

    if (sendImageBtn) {
        sendImageBtn.addEventListener('click', async () => {
            if (!pendingImageFile) return;

            // Disable button and show spinner
            const originalText = sendImageBtn.innerHTML;
            sendImageBtn.disabled = true;
            sendImageBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Sending...';

            const caption = captionInput.value.trim();
            const reader = new FileReader();

            reader.onload = async function(ev) {
                try {
                    await sendMessage(caption, ev.target.result);
                    // sendMessage will reload the page on success, so no need to hide modal here
                    previewModal.hide();
                    pendingImageFile = null;
                } catch (error) {
                    console.error('Send failed:', error);
                    // Re-enable button on error
                    sendImageBtn.disabled = false;
                    sendImageBtn.innerHTML = originalText;
                    alert('Failed to send message. Please try again.');
                }
            };

            reader.onerror = function() {
                sendImageBtn.disabled = false;
                sendImageBtn.innerHTML = originalText;
                alert('Error reading image file.');
            };

            reader.readAsDataURL(pendingImageFile);
        });
    }

    // Mobile back button
    const backBtn = document.getElementById('backBtn');
    const panels = document.getElementById('panels');
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            panels.classList.remove('show-chat');
        });
    }
    // If on mobile and a friend is selected, show chat panel
    if (window.innerWidth <= 768 && document.querySelector('.chat-panel .chat-header h6')?.innerText !== 'Select a friend') {
        panels.classList.add('show-chat');
    }
})();