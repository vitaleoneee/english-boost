const csrf_token = Cookies.get('csrftoken')
const submitButton = document.getElementById('submitButton')
const contactForm = document.getElementById('contactForm')
contactForm.addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    fetch('ajax-send/', {
        method: 'POST',
        headers: {
            'X-CSRF-TOKEN': csrf_token,
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: formData
    })
        .then(() => {
                submitButton.textContent = 'Форма успешно отправлена!';
                submitButton.classList.add('disabled');
                contactForm.reset()
            }
        )
        .catch(() => {
                contactForm.reset()
                submitButton.textContent = 'Ошибка! Форма не может быть отправлена.';
            }
        )
})