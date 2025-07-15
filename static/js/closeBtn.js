document.addEventListener('DOMContentLoaded', () => {
    const closeBtn = document.getElementById('close-messages-btn');
    const messagesWrapper = document.getElementById('messages-wrapper');
    if (closeBtn && messagesWrapper) {
        closeBtn.addEventListener('click', () => {
            messagesWrapper.style.display = 'none';
        });
    }
});