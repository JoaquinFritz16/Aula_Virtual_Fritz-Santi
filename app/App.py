import mysql.connector
from db import get_db_connection 
from functools import wraps
from flask import Flask, request, jsonify, render_template, redirect, session, url_for, flash

app = Flask(__name__)
app.secret_key = 'una_clave_segura_y_larga'
equipos_registrados = []
# Probamos que la base de datos funcione (funcion auxiliar para verificar)
@app.route('/test_db')
def test_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return f"Conexión exitosa a la base de datos: {result[0]}"
    except Exception as e:
        return f"Error en la conexión: {str(e)}"
# Este apartado es importantisimo para poder pedir el login siempre que sea necesario
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
@app.route('/login', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == "admin@copa.com" and password == "1234":
                session['user_email'] = email
                session['user_role'] = 'admin'
                return redirect('/')
        else:
                error = "Datos incorrectos (modo simulación)"
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Intentamos buscar al usuario en la base
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            user = cursor.fetchone()

            cursor.close()
            conn.close()

            # Si encontramos el usuario y coincide la contraseña
            if user and user['password'] == password:
                session['user_email'] = user['email']
                session['user_role'] = user['rol']
                session['user_id'] = user['id']
                return redirect('/')
            else:
                error = "Correo o contraseña incorrectos"
        except Exception as e:
            print("Error al conectar con la base de datos:", e)
        return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/')
def index():
    deportes = [
        {"id": 1, "name": "Futbol", "image": url_for('static', filename='images/futbol.png')},
        {"id": 2, "name": "Basquet", "image": url_for('static', filename='images/basquet.png')},
        {"id": 3, "name": "Voley", "image": url_for('static', filename='images/volley.png')}
    ]
    data = {
        "title": "Bienvenido a la aplicacion de la Copa!",
        "description": "Esta es una aplicacion de ejemplo para la Copa Renault.",
        "sports": deportes,
        "number_of_sports": len(deportes)
    }
    return render_template('index.html', data=data, deportes=deportes)

@app.route('/pedro')
@login_required
def pedro():
    data = {
        "title": "Pedro"
    }
    return render_template('pedro.html', data=data)
@app.route('/cantina')
# @login_required
def cantina():
    return render_template('cantina.html')

@app.route('/sponsors')
# @login_required
def sponsors():
    return render_template('sponsors.html')

@app.route('/fixtures')
@login_required
def fixtures():
    return render_template('fixtures.html')

@app.route('/futbol')
# @login_required
def futbol():
    return render_template('./deportes/futbol.html')

@app.route('/basquet')
# @login_required
def basquet():
    return render_template('./deportes/basquet.html')

@app.route('/voley')
# @login_required
def voley():
    return render_template('./deportes/voley.html')
@app.route('/registrar_equipo', methods=['GET', 'POST'])
@login_required

# Funcion clave para poder agregar equipos a la base de datos (dependiendo del usuario y de su id con su id de colegio)
def registrar_equipo():
    conn = get_db_connection()
    #Es 1000000 veces mas facil manejar diccionarios que tuplas
    cursor = conn.cursor(dictionary=True)

    user_id = session.get('user_id')
    cursor.execute("SELECT id_colegio FROM usuarios WHERE id = %s", (user_id,))
    usuario = cursor.fetchone()

    if not usuario or not usuario['id_colegio']:
        flash("No se encontró tu colegio", "danger")
        return render_template('registrar_equipo.html', error="No se encontró tu colegio")

    id_colegio = usuario['id_colegio']

    cursor.execute("SELECT estado FROM Colegios WHERE id_colegio = %s", (id_colegio,))
    colegio = cursor.fetchone()

    if not colegio or colegio['estado'] != 'aprobado':
        flash("Tu colegio aún no fue aprobado", "danger")
        return render_template('registrar_equipo.html')

    if request.method == 'POST':
        nombre_equipo = request.form.get('nombre')
        deporte = request.form.get('deporte')
        categoria = request.form.get('categoria')
        genero = request.form.get('genero')

        cursor.execute("""
            INSERT INTO Equipos (nombre, deporte, categoria, genero, id_colegio)
            VALUES (%s, %s, %s, %s, %s)
            """, (nombre_equipo, deporte, categoria, genero, id_colegio))
        conn.commit()

        flash("Equipo registrado correctamente", "success")
        return redirect(url_for('lista_equipos'))


    # Si es GET, mostrar formulario vacío
    return render_template('registrar_equipo.html')

# Luego del registro se muestran los equipos registrados
@app.route('/equipos')
@login_required
def lista_equipos():
    conn = get_db_connection()
    # Odio las tuplas
    cursor = conn.cursor(dictionary=True)

    user_id = session.get('user_id')
    cursor.execute("SELECT id_colegio FROM usuarios WHERE id = %s", (user_id,))
    usuario = cursor.fetchone()

    if not usuario or not usuario['id_colegio']:
        flash("No se encontró tu colegio", "danger")
        return redirect(url_for('home'))

    id_colegio = usuario['id_colegio']
    cursor.execute("SELECT * FROM Equipos WHERE id_colegio = %s", (id_colegio,))
    equipos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('equipos.html', equipos=equipos)

@app.route('/registrar_colegio', methods=['GET', 'POST'])
# Te diria que esta funcion es basicamente el esqueleto de la app para poder movernos NECESITAMOS que te registres como colegio
def registrar_colegio():
    if 'user_email' not in session:
        flash("Tenés que iniciar sesión para registrar un colegio")
        return redirect('/login')

    mensaje = None
    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificamos que no esté duplicado
        cursor.execute("SELECT * FROM Colegios WHERE nombre = %s AND direccion = %s", (nombre, direccion))
        colegio_existente = cursor.fetchone()

        if colegio_existente:
            mensaje = "Este colegio ya está registrado y pendiente de aprobación."
        else:
            cursor.execute("INSERT INTO Colegios (nombre, direccion) VALUES (%s, %s)", (nombre, direccion))
            conn.commit()
            mensaje = "Registro enviado. El colegio será aprobado manualmente."

        cursor.close()
        conn.close()

    return render_template('registrar_colegio.html', mensaje=mensaje)

# Casi tan importante como registrarte es ser aprobado
@app.route('/admin/colegios_pendientes')
def colegios_pendientes():
    if session.get('user_role') != 'admin':
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Colegios WHERE estado = 'pendiente'")
    colegios = cursor.fetchall()
    conn.close()

    return render_template('admin_colegios.html', colegios=colegios)

@app.route('/admin/aprobar_colegio/<int:id>', methods=['POST'])
@login_required
def aprobar_colegio(id):
    if session.get('user_role') != 'admin':
        return "No autorizado", 403
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Colegios SET estado = 'aprobado' WHERE id_colegio = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('colegios_pendientes'))

@app.route('/admin/rechazar_colegio/<int:id>', methods=['POST'])
@login_required
def rechazar_colegio(id):
    if session.get('user_role') != 'admin':
        return "No autorizado", 403
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Colegios SET estado = 'rechazado' WHERE id_colegio = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('colegios_pendientes'))
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        rol = request.form['rol']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar si el usuario ya existe
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return render_template('register.html', error="El usuario ya existe")

        # Insertar el nuevo usuario
        cursor.execute("INSERT INTO usuarios (email, password, rol) VALUES (%s, %s, %s)",
                        (email, password, rol))
        conn.commit()
        
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        
        user = cursor.fetchone()
        # Guardar sesión
        session['user_email'] = email
        session['user_role'] = rol  
        if user:
            session['user_id'] = user[0]
        
        cursor.close()
        conn.close()

        return redirect('/registrar_colegio')

    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)
