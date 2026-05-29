import sqlite3
import os

db_path = r'C:\Users\USUARIO\OneDrive\Documents\GitHub\pequemundo\PequeMundo\db.sqlite3'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("USUARIOS DEL SISTEMA")
    print("=" * 70)
    
    cursor.execute('SELECT id, username, email, is_active FROM auth_user')
    rows = cursor.fetchall()
    
    print(f'Total usuarios: {len(rows)}\n')
    
    for r in rows:
        print(f'ID: {r[0]}')
        print(f'  Usuario: {r[1]}')
        print(f'  Email: {r[2]}')
        print(f'  Activo: {r[3]}')
        print('-' * 70)
    
    conn.close()
else:
    print(f'Base de datos no encontrada: {db_path}')
