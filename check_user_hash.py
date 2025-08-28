# check_user_hash.py
from models import Usuario
from werkzeug.security import check_password_hash

email = "joaquinfritz16@gmail.com"   # reemplazá por el email del usuario que registraste por web
password_prueba = "123456"   # la contraseña que escribiste al registrar

u = Usuario.buscar_por_email(email)
if not u:
    print("❌ No se encontró el usuario en la DB:", email)
else:
    print("✅ Usuario encontrado:", u.nombre, u.email)
    print("repr(stored_password):", repr(u.password))
    print("len(stored_password):", len(u.password))
    print("check_password_hash(stored, correct):", check_password_hash(u.password, password_prueba))
    # prueba con strip por si hay espacios/newlines
    print("check_password_hash(stripped, correct):", check_password_hash(u.password.strip(), password_prueba))
    # comprobar si hay bytes nulos
    print("contains null bytes:", "\\x00" in repr(u.password))
