document.addEventListener('DOMContentLoaded', () => {
    // Processing all timers by the data-seconds attribute
    document.querySelectorAll('span[id^="timer-"]').forEach(timerSpan => {
        let seconds = parseInt(timerSpan.dataset.seconds);
        const interval = setInterval(() => {
            if (seconds <= 0) {
                clearInterval(interval);
                timerSpan.textContent = '';
                return;
            }
            const h = Math.floor(seconds / 3600);
            const m = Math.floor((seconds % 3600) / 60);
            const s = seconds % 60;
            let formatted = '';
            if (h > 0) formatted += h.toString().padStart(1, '0') + ':';
            formatted += m.toString().padStart(2, '0') + ':' + s.toString().padStart(2, '0');
            timerSpan.textContent = "До проверки: " + formatted;
            seconds--;
        }, 1000);
    });
});