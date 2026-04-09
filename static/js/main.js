// Avatar handling
const avatarInput = document.getElementById('avatarInput');
const avatarImg = document.getElementById('avatarImg');
avatarInput.addEventListener('change', function (e) {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function (ev) {
            avatarImg.src = ev.target.result;
        };
        reader.readAsDataURL(file);
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});