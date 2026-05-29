#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pequeMundo.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import cuenta

print("=" * 60)
print("USUARIOS DEL SISTEMA")
print("=" * 60)

users = User.objects.all()
print(f"\nTotal de usuarios: {users.count()}\n")

if users.count() == 0:
    print("No hay usuarios en la base de datos")
else:
    for u in users:
        print(f"ID: {u.id}")
        print(f"  Usuario: {u.username}")
        print(f"  Email: {u.email}")
        print(f"  Activo: {u.is_active}")
        print(f"  Administrador: {u.is_staff}")
        print(f"  Superusuario: {u.is_superuser}")
        
        # Verificar si tiene cuenta de cliente
        try:
            cliente = cuenta.objects.get(usuario_cuenta=u.id)
            print(f"  Cuenta Cliente: SI")
            print(f"    - Nombre: {cliente.nombre}")
            print(f"    - Teléfono: {cliente.telefono}")
        except cuenta.DoesNotExist:
            print(f"  Cuenta Cliente: NO")
        
        print("-" * 60)

print("\n" + "=" * 60)
print("CUENTAS DE CLIENTE")
print("=" * 60)

cuentas = cuenta.objects.all()
print(f"\nTotal de cuentas de cliente: {cuentas.count()}\n")

for c in cuentas:
    print(f"ID Cuenta: {c.id}")
    print(f"  Nombre: {c.nombre}")
    print(f"  Usuario ID: {c.usuario_cuenta}")
    print(f"  Email: {c.correo}")
    print(f"  Teléfono: {c.telefono}")
    print(f"  Dirección: {c.direccion}")
    print("-" * 60)
