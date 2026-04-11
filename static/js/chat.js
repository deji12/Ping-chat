function scrollToBottom() {
    var chatContainer = document.getElementById("messagesContainer");
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// ─── User Info Modal ───────────────────────────────────────────────────────────
const userInfoModalEl = document.getElementById('userInfoModal');
if (userInfoModalEl) {
    userInfoModalEl.addEventListener('show.bs.modal', function () {
        const header = document.getElementById('chatHeader2');
        if (!header) return;
        document.getElementById('modalFullName').innerText = document.getElementById('chatName').innerText;
        document.getElementById('modalAvatar').src = document.getElementById('chatAvatar').src;
        document.getElementById('modalBio').innerText = header.getAttribute('data-bio');
        document.getElementById('modalJoined').innerText = header.getAttribute('data-joined');
        document.getElementById('modalFriendsSince').innerText = header.getAttribute('data-friends-since');
    });
}

(function () {

    // ─── Search Filter ─────────────────────────────────────────────────────────
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            const query = this.value.trim().toLowerCase();
            const contactItems = document.querySelectorAll('.contact-item');
            let visibleCount = 0;
            contactItems.forEach(item => {
                const nameSpan = item.querySelector('.contact-name');
                if (!nameSpan) return;
                const match = query === '' || nameSpan.innerText.toLowerCase().includes(query);
                item.style.display = match ? '' : 'none';
                if (match) visibleCount++;
            });
            let noMsg = document.getElementById('noSearchResults');
            if (visibleCount === 0) {
                if (!noMsg) {
                    noMsg = document.createElement('div');
                    noMsg.id = 'noSearchResults';
                    noMsg.className = 'no-contacts';
                    noMsg.innerHTML = '<i class="bi bi-search"></i> No matching friends found';
                    document.querySelector('.contacts-list').appendChild(noMsg);
                }
            } else if (noMsg) {
                noMsg.remove();
            }
        });
    }

    // ─── Reply State ───────────────────────────────────────────────────────────
    window.pendingReply = null; // { id, senderName, text, hasImage }

    const replyBar        = document.getElementById('replyBar');
    const replyBarSender  = document.getElementById('replyBarSender');
    const replyBarText    = document.getElementById('replyBarText');
    const cancelReplyBtn  = document.getElementById('cancelReplyBtn');

    function showReplyBar(reply) {
        window.pendingReply = reply;
        if (!replyBar) return;
        replyBarSender.textContent = reply.senderName;
        
        // ✅ Show image thumbnail in reply bar if applicable
        if (reply.hasImage && reply.imageUrl) {
            replyBarText.innerHTML = `
                <span class="d-flex align-items-center gap-2">
                    <img src="${reply.imageUrl}" style="width:28px;height:28px;object-fit:cover;border-radius:3px;">
                    <span>${reply.text || '📷 Photo'}</span>
                </span>`;
        } else {
            replyBarText.textContent = reply.text || '📷 Photo';
        }
        
        replyBar.style.display = 'flex';
        document.getElementById('messageInput')?.focus();
    }

    window.clearReply = function clearReply() {
        window.pendingReply = null;
        if (replyBar) replyBar.style.display = 'none';
        const hiddenReplyId = document.getElementById('replyToIdImage');
        if (hiddenReplyId) hiddenReplyId.value = '';
    }

    if (cancelReplyBtn) cancelReplyBtn.addEventListener('click', clearReply);

    // ─── Context Menu ──────────────────────────────────────────────────────────
    const ctxMenu   = document.getElementById('msgContextMenu');
    const ctxReply  = document.getElementById('ctxReply');
    let ctxTarget   = null;   // the .message-row element

    function hideCtxMenu() {
        if (ctxMenu) ctxMenu.style.display = 'none';
        ctxTarget = null;
    }

    document.addEventListener('click', hideCtxMenu);
    document.addEventListener('keydown', e => { if (e.key === 'Escape') hideCtxMenu(); });

    const messagesContainer = document.getElementById('messagesContainer');
    if (messagesContainer) {
        messagesContainer.addEventListener('contextmenu', function (e) {
            const row = e.target.closest('.message-row');
            if (!row) return;
            e.preventDefault();
            ctxTarget = row;
            ctxMenu.style.display = 'block';
            // Position near cursor, keep within viewport
            const x = Math.min(e.clientX, window.innerWidth  - ctxMenu.offsetWidth  - 8);
            const y = Math.min(e.clientY, window.innerHeight - ctxMenu.offsetHeight - 8);
            ctxMenu.style.left = x + 'px';
            ctxMenu.style.top  = y + 'px';
        });
    }

    if (ctxReply) {
        ctxReply.addEventListener('click', function () {
            if (!ctxTarget) return;
            console.log('ctxTarget dataset:', ctxTarget.dataset);  // ADD THIS
            const reply = {
                id:         ctxTarget.dataset.messageId,
                senderName: ctxTarget.dataset.senderName,
                text:       ctxTarget.dataset.text,
                hasImage:   ctxTarget.dataset.hasImage === 'true',
                imageUrl:   ctxTarget.dataset.imageUrl || null, 
            };
            showReplyBar(reply);
            hideCtxMenu();
        });
    }

    // ─── Click reply-quote to scroll to original ───────────────────────────────
    document.addEventListener('click', function (e) {
        const quote = e.target.closest('.reply-quote');
        if (!quote) return;
        const targetId = quote.dataset.scrollTo;
        if (!targetId) return;
        const targetEl = document.querySelector(`.message-row[data-message-id="${targetId}"]`);
        if (targetEl) {
            targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
            // Brief highlight
            targetEl.querySelector('.message-bubble')?.classList.add('highlight-flash');
            setTimeout(() => {
                targetEl.querySelector('.message-bubble')?.classList.remove('highlight-flash');
            }, 1200);
        }
    });

    // ─── Helpers ───────────────────────────────────────────────────────────────
    function getCookie(name) {
        let val = null;
        if (document.cookie) {
            document.cookie.split(';').forEach(c => {
                c = c.trim();
                if (c.startsWith(name + '=')) val = decodeURIComponent(c.slice(name.length + 1));
            });
        }
        return val;
    }

    function buildReplyQuoteHTML(replyPreview, isSent) {
        if (!replyPreview) return '';
        
        let contentHTML = '';
        if (replyPreview.has_image && replyPreview.image_url) {
            // Show thumbnail + caption if any
            contentHTML = `
                <div class="reply-text d-flex align-items-center gap-2">
                    <img src="${replyPreview.image_url}" 
                         style="width:40px;height:40px;object-fit:cover;border-radius:4px;flex-shrink:0;">
                    <span>${replyPreview.text ? escapeHtml(replyPreview.text) : '📷 Photo'}</span>
                </div>`;
        } else {
            contentHTML = `<div class="reply-text">${escapeHtml(replyPreview.text || '(image)')}</div>`;
        }

        return `
            <div class="reply-quote" data-scroll-to="${replyPreview.id}">
                <div class="reply-sender">${escapeHtml(replyPreview.sender_name)}</div>
                ${contentHTML}
            </div>`;
    }

    function escapeHtml(str) {
        return String(str)
            .replace(/&/g,'&amp;').replace(/</g,'&lt;')
            .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    // ─── add_message (used by WebSocket) ──────────────────────────────────────
    window.add_message = function (message, currentUserId) {
        const sentAt      = new Date(message.sent_at);
        const displayTime = sentAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const isSent      = message.sender_id === String(currentUserId);
        const replyQuote  = buildReplyQuoteHTML(message.reply_preview, isSent);
        const senderName  = isSent ? 'You' : (message.sender_name || 'Friend');
        const text        = message.message || '';
        const hasImage    = message.message_type === 'image_text';

        let html = `
            <div class="message-row"
                 data-message-id="${message.message_id || ''}"
                 data-sender-name="${escapeHtml(senderName)}"
                 data-text="${escapeHtml(text.slice(0, 80))}"
                 data-has-image="${hasImage}"
                 data-image-url="${hasImage && message.image_url ? message.image_url : ''}">
              <div class="message-bubble ${isSent ? 'sent' : 'received'}">
                ${replyQuote}
                ${isSent ? '' : `<div class="message-sender">${escapeHtml(senderName)}</div>`}
                <div class="message-text">${escapeHtml(text)}</div>`;

        if (hasImage && message.image_url) {
            html += `<img src="${message.image_url}" class="message-image" onclick="window.open(this.src)" alt="image">`;
        }

        html += `
                <div class="message-meta">
                  <span>${displayTime}</span>
                  ${isSent ? '<i class="bi bi-check2-all"></i>' : ''}
                </div>
              </div>
            </div>`;

        messagesContainer.innerHTML += html;
        scrollToBottom();
    };

    // ─── Image send (via HTTP) ─────────────────────────────────────────────────
    async function sendImageMessage(text, imageDataUrl, replyToId) {
        const friendshipId = document.getElementById('friendshipId')?.value;
        if (!friendshipId) return;
        const url      = `/chat/image-message/${friendshipId}/`;
        const formData = new FormData();
        formData.append('text_message', text || '');
        if (replyToId) formData.append('reply_to_id', replyToId);

        if (imageDataUrl) {
            const blob = await fetch(imageDataUrl).then(r => r.blob());
            formData.append('image', blob, 'image.jpg');
        }

        const resp = await fetch(url, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            body: formData,
        });
        if (!resp.ok) throw new Error('Send failed');
    }

    // ─── Image Preview Modal ───────────────────────────────────────────────────
    let pendingImageFile = null;
    const previewModal   = document.getElementById('imagePreviewModal')
                            ? new bootstrap.Modal(document.getElementById('imagePreviewModal')) : null;
    const previewImage   = document.getElementById('previewImage');
    const captionInput   = document.getElementById('captionInput');
    const sendImageBtn   = document.getElementById('sendImageBtn');
    const fileInput      = document.getElementById('fileInput');

    if (fileInput) {
        fileInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                pendingImageFile = file;
                const reader = new FileReader();
                reader.onload = ev => {
                    previewImage.src  = ev.target.result;
                    captionInput.value = '';
                    previewModal?.show();
                };
                reader.readAsDataURL(file);
            }
            fileInput.value = '';
        });
    }

    if (sendImageBtn) {
        sendImageBtn.addEventListener('click', async () => {
            if (!pendingImageFile) return;
            const orig = sendImageBtn.innerHTML;
            sendImageBtn.disabled = true;
            sendImageBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Sending...';

            const caption   = captionInput?.value.trim() || '';
            const replyToId = window.pendingReply?.id || null;

            const reader = new FileReader();
            reader.onload = async ev => {
                try {
                    await sendImageMessage(caption, ev.target.result, replyToId);
                    previewModal?.hide();
                    pendingImageFile = null;
                    clearReply();
                } catch {
                    alert('Failed to send. Please try again.');
                    sendImageBtn.disabled = false;
                    sendImageBtn.innerHTML = orig;
                }
            };
            reader.onerror = () => {
                sendImageBtn.disabled = false;
                sendImageBtn.innerHTML = orig;
                alert('Error reading image file.');
            };
            reader.readAsDataURL(pendingImageFile);
        });
    }

    // ─── Mobile back button ────────────────────────────────────────────────────
    const backBtn = document.getElementById('backBtn');
    const panels  = document.getElementById('panels');
    if (backBtn) backBtn.addEventListener('click', () => panels?.classList.remove('show-chat'));
    if (window.innerWidth <= 768 && document.querySelector('.chat-panel .chat-header h6')?.innerText !== 'Select a friend') {
        panels?.classList.add('show-chat');
    }

})();