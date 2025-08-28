# test_login.py
from werkzeug.security import generate_password_hash, check_password_hash
from models import Usuario

print("=== PRUEBAS DE USUARIO ===")

# 1. Crear un usuario de prueba
password = "123456"
hashed = generate_password_hash(password)

print("Password original:", password)
print("Password encriptado:", hashed)

# Insertar usuario en la DB
Usuario.crear("TestUser", "test@example.com", hashed, "estudiante")
print("✅ Usuario creado en la base de datos")

# 2. Buscar al usuario
u = Usuario.buscar_por_email("test@example.com")
if u:
    print("✅ Usuario encontrado:", u.nombre, u.email)
else:
    print("❌ Usuario no encontrado")

# 3. Verificar la contraseña
if check_password_hash(u.password, "123456"):
    print("✅ Contraseña correcta")
else:
    print("❌ Contraseña incorrecta")
