document.getElementById('select-all').addEventListener('change', function () {
    const checkboxes = document.querySelectorAll('input[name="selected_words"]');
    checkboxes.forEach(cb => cb.checked = this.checked);
});