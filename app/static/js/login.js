  function clearAuthError() {
    const error = document.getElementById('authError');
    if (error) {
      error.textContent = '';
      error.style.display = 'none';
    }
  }

  function setAuthError(message) {
    const error = document.getElementById('authError');
    if (error) {
      error.textContent = message;
      error.style.display = 'block';
    }
  }

  function initAuthToggle() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const authTitle = document.getElementById('authTitle');
    const authDescription = document.getElementById('authDescription');
    const switchToRegister = document.getElementById('switchToRegister');
    const switchToLogin = document.getElementById('switchToLogin');

    switchToRegister.addEventListener('click', () => {
      loginForm.classList.add('hidden');
      registerForm.classList.remove('hidden');
      authTitle.textContent = 'Crear cuenta';
      authDescription.textContent = 'Regístrate con tu correo para usar el carrito, pedidos y tu perfil.';
      switchToRegister.classList.add('hidden');
      switchToLogin.classList.remove('hidden');
      clearAuthError();
    });

    switchToLogin.addEventListener('click', () => {
      registerForm.classList.add('hidden');
      loginForm.classList.remove('hidden');
      authTitle.textContent = 'Iniciar sesión';
      authDescription.textContent = 'Accede a tu cuenta para seguir comprando, ver pedidos y experiencias personalizadas.';
      switchToRegister.classList.remove('hidden');
      switchToLogin.classList.add('hidden');
      clearAuthError();
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    redirectIfLoggedIn();
    initAuthPage();
    initAuthToggle();
  });
