function syncSelectAllCheckbox() {
    const selectAll = document.getElementById('select-all');
    if (!selectAll) {
        return;
    }

    const checkboxes = document.querySelectorAll('input[name="selected_words"]');
    const checkedCheckboxes = document.querySelectorAll('input[name="selected_words"]:checked');

    selectAll.checked = checkboxes.length > 0 && checkedCheckboxes.length === checkboxes.length;
    selectAll.indeterminate = checkedCheckboxes.length > 0 && checkedCheckboxes.length < checkboxes.length;
}

document.addEventListener('change', function (event) {
    const target = event.target;
    if (!(target instanceof HTMLInputElement)) {
        return;
    }

    if (target.id === 'select-all') {
        const checkboxes = document.querySelectorAll('input[name="selected_words"]');
        checkboxes.forEach(cb => cb.checked = target.checked);
        target.indeterminate = false;
        return;
    }

    if (target.name === 'selected_words') {
        syncSelectAllCheckbox();
    }
});

document.addEventListener('DOMContentLoaded', syncSelectAllCheckbox);
document.body.addEventListener('htmx:afterSwap', syncSelectAllCheckbox);
