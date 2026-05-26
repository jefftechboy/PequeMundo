  document.addEventListener('DOMContentLoaded', () => {
    initEditProfileForm();
  });

  function initEditProfileForm() {
    const btn    = document.getElementById('editProfileBtn');
    const form   = document.getElementById('editProfileForm');
    const cancel = document.getElementById('editCancelBtn');
    const save   = document.getElementById('editSaveBtn');
    const msg    = document.getElementById('editProfileMsg');

    btn.addEventListener('click', () => {
      const user = getCurrentUser();
      if (user) {
        document.getElementById('editName').value = user.name || '';
        document.getElementById('editRut').value = user.rut || '';
        document.getElementById('editPassword').value = '';
        document.getElementById('editPasswordConfirm').value = '';
      }
      form.classList.add('open');
      btn.style.display = 'none';
      msg.className = 'edit-profile-msg';
      msg.style.display = 'none';
    });

    cancel.addEventListener('click', () => {
      form.classList.remove('open');
      btn.style.display = '';
    });

    save.addEventListener('click', () => {
      const name    = document.getElementById('editName').value.trim();
      const pwd     = document.getElementById('editPassword').value.trim();
      const pwdConf = document.getElementById('editPasswordConfirm').value.trim();
      msg.className = 'edit-profile-msg';
      msg.style.display = 'none';

      const rut = document.getElementById('editRut').value.trim();

      if (!name) {
        msg.textContent = 'El nombre no puede estar vacío.';
        msg.className = 'edit-profile-msg err';
        return;
      }

      if (rut && typeof validateRutFormat === 'function' && !validateRutFormat(rut)) {
        msg.textContent = 'El RUT no tiene un formato válido. Ej: 12345678-9';
        msg.className = 'edit-profile-msg err';
        return;
      }
      if (pwd && pwd.length < 6) {
        msg.textContent = 'La contraseña debe tener al menos 6 caracteres.';
        msg.className = 'edit-profile-msg err';
        return;
      }
      if (pwd && pwd !== pwdConf) {
        msg.textContent = 'Las contraseñas no coinciden.';
        msg.className = 'edit-profile-msg err';
        return;
      }

      const user = getCurrentUser();
      if (!user) return;

      const updated = { ...user, name, rut };
      if (pwd) updated.password = pwd;

      updateStoredUser(updated);

      document.getElementById('accountName').textContent = name;
      const rutEl = document.getElementById('accountRut');
      if (rutEl) rutEl.textContent = rut || 'No ingresado';
      msg.textContent = '¡Perfil actualizado correctamente!';
      msg.className = 'edit-profile-msg ok';

      document.getElementById('editPassword').value = '';
      document.getElementById('editPasswordConfirm').value = '';

      setTimeout(() => {
        form.classList.remove('open');
        btn.style.display = '';
      }, 1500);
    });
  }
