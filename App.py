import os
from werkzeug.utils import secure_filename
from datetime import timedelta
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import Usuario, Curso, Tarea, Inscripcion, Notificacion, Calificacion, Lapiz, Dictado
from forms import LoginForm, RegistrationForm, CourseForm
from db import get_db_connection
app = Flask(__name__)
app.secret_key = "clave_secreta_segura"


UPLOAD_FOLDER = "uploads/tareas"
ALLOWED_EXTENSIONS = {"pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

from flask import send_from_directory

@app.route("/tareas/descargar/<filename>")
def descargar_tarea(filename):
    carpeta = "uploads/tareas"
    return send_from_directory(carpeta, filename, as_attachment=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Acceso requerido. Inicia sesión.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

def roles_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            from models import Usuario
            usuario = Usuario.buscar_por_id(session.get("usuario_id"))
            if not usuario or usuario.rol not in allowed_roles:
                flash("No tienes permisos para acceder a este recurso.", "danger")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        nombre = form.nombre.data
        email = form.email.data
        password = generate_password_hash(form.password.data)
        rol = "estudiante"
        Usuario.crear(nombre, email, password, rol)
        flash("Usuario registrado correctamente", "success")
        return redirect(url_for("login"))
    if form.errors:
        flash("Revisa los datos del formulario.", "danger")
    return render_template("register.html", form=form)
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        usuario = Usuario.buscar_por_email(email)
        if usuario and check_password_hash(usuario.password, password):
            session["usuario_id"] = usuario.id
            session["usuario_nombre"] = usuario.nombre
            flash(f"Bienvenido {usuario.nombre}", "success")
            return redirect(url_for("dashboard"))
        flash("Credenciales incorrectas", "danger")
    if form.errors:
        flash("Revisa los datos del formulario.", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    usuario = Usuario.buscar_por_id(session["usuario_id"])
    from models import Inscripcion, Calificacion, Notificacion

    if usuario.rol == "docente":
        # cursos que dicta
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cursos WHERE instructor_id = %s", (usuario.id,))
        cursos = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("dashboard_docente.html", usuario=usuario, cursos=cursos)


    cursos = Inscripcion.obtener_cursos_por_usuario(usuario.id)
    calificaciones = Calificacion.obtener_por_estudiante(usuario.id)
    notifs = Notificacion.obtener_no_leidas(usuario.id)
    notifs_count = len(notifs)

    return render_template(
        "dashboard_estudiante.html",
        usuario=usuario,
        cursos=cursos,
        calificaciones=calificaciones,
        notifs=notifs,
        notifs_count=notifs_count
    )

@app.route("/cursos")
@login_required
def cursos():
    usuario = Usuario.buscar_por_id(session["usuario_id"])
    if usuario.rol == "docente":
        cursos = Curso.obtener_por_docente(usuario.id)
    else:
        cursos = Curso.get_all() 
    return render_template("cursos.html", cursos=cursos, usuario=usuario)


@app.route("/cursos/<int:curso_id>")
@login_required
def curso_detalle(curso_id):
    usuario = Usuario.buscar_por_id(session["usuario_id"])
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cursos WHERE id=%s", (curso_id,))
    curso = cursor.fetchone()
    cursor.close()

    if usuario.rol == "docente" and curso["instructor_id"] == usuario.id:

        estudiantes = Inscripcion.obtener_estudiantes_por_curso(curso_id)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tareas WHERE curso_id=%s ORDER BY id DESC", (curso_id,))
        tareas = cursor.fetchall()
        cursor.close()
        return render_template("curso_docente.html", curso=curso, tareas=tareas, estudiantes=estudiantes)
    else:
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM inscripciones WHERE usuario_id=%s AND curso_id=%s", (usuario.id, curso_id))
        ok = cursor.fetchone()
        cursor.close()
        if not ok:
            flash("No estás inscrito en este curso.", "danger")
            return redirect(url_for("dashboard"))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tareas WHERE curso_id=%s ORDER BY fecha_entrega DESC", (curso_id,))
        tareas = cursor.fetchall()
        cursor.close()
        califs = Calificacion.obtener_resumen_por_curso_y_estudiante(curso_id, usuario.id)
        return render_template("curso_estudiante.html", curso=curso, tareas=tareas, calificaciones=califs)
@app.route("/cursos/<int:curso_id>/inscribir", methods=["POST"])
@login_required
@roles_required("docente","admin")
def curso_inscribir(curso_id):
    email = request.form.get("email")
    alumno = Usuario.buscar_por_email(email)
    if not alumno:
        flash("Alumno no encontrado", "danger")
        return redirect(url_for("curso_detalle", curso_id=curso_id))
    Inscripcion.inscribir(alumno.id, curso_id)
    Notificacion.crear(f"Fuiste inscrito/a en {curso_id} por el profesor", alumno.id, tipo="inscripcion", url_referencia=f"/cursos/{curso_id}")
    flash("Alumno inscrito correctamente", "success")
    return redirect(url_for("curso_detalle", curso_id=curso_id))


@app.route("/cursos/<int:curso_id>/calificar", methods=["POST"])
@login_required
@roles_required("docente","admin")
def curso_calificar(curso_id):
    estudiante_id = request.form.get("estudiante_id")
    tarea_id = request.form.get("tarea_id") or None
    valor = request.form.get("valor")
    comentarios = request.form.get("comentarios")
    Calificacion.crear(estudiante_id, curso_id, tarea_id, valor, comentarios)
    Notificacion.crear(f"Se cargó una nueva calificación en {curso_id}", estudiante_id, tipo="calificacion", url_referencia=f"/cursos/{curso_id}")
    flash("Calificación cargada", "success")
    return redirect(url_for("curso_detalle", curso_id=curso_id))


@app.route("/notificaciones")
@login_required
def ver_notificaciones():
    usuario = Usuario.buscar_por_id(session["usuario_id"])
    notifs = Notificacion.obtener_no_leidas(usuario.id)
    return render_template("notificaciones.html", notifs=notifs)

@app.route("/cursos/agregar", methods=["GET", "POST"])
@roles_required("docente")
def agregar_curso():
    form = CourseForm()
    if form.validate_on_submit():
        curso = Curso(
            nombre=form.title.data,
            descripcion=form.description.data,
            instructor_id=session["usuario_id"]
        )
        curso.save()  

        flash("Curso agregado correctamente", "success")
        return redirect(url_for("cursos"))

    return render_template("agregar_curso.html", form=form)


@app.route("/cursos/editar/<int:id>", methods=["GET", "POST"])
def editar_curso(id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursos = Curso.get_all(conn)
    curso = next((c for c in cursos if c["id"] == id), None)

    form = CourseForm()
    if request.method == "GET" and curso:
        form.title.data = curso["nombre"]
        form.description.data = curso["descripcion"]

    if form.validate_on_submit():
        c = Curso(id=id, nombre=form.title.data, descripcion=form.description.data, instructor_id=session["usuario_id"])
        c.save(conn)
        conn.close()
        flash("Curso actualizado correctamente", "success")
        return redirect(url_for("cursos"))

    return render_template("editar_curso.html", form=form, curso=curso)

@app.route("/cursos/eliminar/<int:id>")
def eliminar_curso(id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    Curso.delete(conn, id)
    conn.close()
    flash("Curso eliminado", "danger")
    return redirect(url_for("cursos"))



@app.route("/tareas/nueva", methods=["GET", "POST"])
@login_required
@roles_required("docente")
def nueva_tarea():
    usuario = Usuario.buscar_por_id(session["usuario_id"])

    if request.method == "POST":
        titulo = request.form["titulo"]
        descripcion = request.form["descripcion"]
        dictado_id = request.form.get("dictado_id") or None

        archivo_pdf = None
        if "archivo_pdf" in request.files:
            file = request.files["archivo_pdf"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                archivo_pdf = filename  

        Tarea.crear(titulo, descripcion, usuario.id, dictado_id, archivo_pdf)
        flash(" Tarea creada correctamente", "success")
        return redirect(url_for("dashboard"))

    cursos = Curso.obtener_por_docente(usuario.id)
    dictados = Dictado.get_all()  
    return render_template("nueva_tarea.html", cursos=cursos, dictados=dictados)

@app.route("/cursos/<int:curso_id>/inscribirse", methods=["POST"])
@login_required
@roles_required("estudiante")
def inscribirse_curso(curso_id):
    usuario_id = session['usuario_id']
    Inscripcion.inscribir(usuario_id, curso_id)
    Notificacion.crear(f"Te inscribiste en el curso {curso_id}", usuario_id, tipo="inscripcion", url_referencia=f"/cursos/{curso_id}")
    flash(" Inscripción exitosa", "success")
    return redirect(url_for("curso_detalle", curso_id=curso_id))
@app.route("/cursos/<int:curso_id>/notificar", methods=["POST"])
@login_required
@roles_required("docente","admin")
def enviar_notificacion(curso_id):
    usuario_id = request.form.get("usuario_id")
    mensaje = request.form.get("mensaje")
    Notificacion.crear(mensaje, usuario_id=usuario_id, tipo="mensaje", url_referencia=f"/cursos/{curso_id}")
    flash("Notificación enviada", "success")
    return redirect(url_for("curso_detalle", curso_id=curso_id))


@app.route("/lapices")
@login_required
def lapices():
    lista = Lapiz.get_all()
    return render_template("lapices.html", lapices=lista)


@app.route("/lapices/agregar", methods=["GET", "POST"])
@login_required
@roles_required("docente")
def agregar_lapiz():
    usuario = Usuario.buscar_por_id(session["usuario_id"])  # obtener usuario logueado
    
    if request.method == "POST":
        titulo = request.form.get("titulo")
        descripcion = request.form.get("descripcion")
        imagen_url = request.form.get("imagen_url")

        nuevo = Lapiz(titulo, descripcion, imagen_url)
        nuevo.save(usuario.id)  # guarda el lapiz con el id del docente
        
        flash(" Lápiz agregado correctamente", "success")
        return redirect(url_for("lapices"))

    return render_template("agregar_lapiz.html")


@app.route("/dictados")
@login_required
def dictados():
    lista = Dictado.get_all()
    return render_template("dictados.html", dictados=lista)


@app.route("/dictados/agregar", methods=["GET", "POST"])
@login_required
@roles_required("docente")
def agregar_dictado():
    usuario = Usuario.buscar_por_id(session["usuario_id"])  # obtener usuario logueado
    
    if request.method == "POST":
        titulo = request.form.get("titulo")
        descripcion = request.form.get("descripcion")
        imagen_url = request.form.get("imagen_url")

        nuevo = Dictado(titulo, descripcion, imagen_url)
        nuevo.save(usuario.id)  # guarda el lapiz con el id del docente
        
        flash("Dictado agregado correctamente", "success")
        return redirect(url_for("dictados"))

    return render_template("agregar_dictado.html")
@app.route("/dictados/<int:dictado_id>")
def ver_dictado(dictado_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    usuario = Usuario.buscar_por_id(session["usuario_id"])

   
    dictado = Dictado.buscar_por_id(dictado_id)
    if not dictado:
        flash("Dictado no encontrado", "danger")
        return redirect(url_for("dictados"))

    
    tareas = Tarea.obtener_por_dictado(dictado_id)

    
    calificaciones = {}
    if usuario.rol == "estudiante":
        calificaciones = Calificacion.obtener_resumen_por_dictado_y_estudiante(dictado_id, usuario.id)

    return render_template(
        "dictado_detalle.html",
        dictado=dictado,
        tareas=tareas,
        calificaciones=calificaciones,
        usuario=usuario
    )
@app.route("/dictados/<int:dictado_id>/inscribirse", methods=["POST"])
@login_required
@roles_required("estudiante")
def inscribirse_dictado(dictado_id):
    usuario_id = session['usuario_id']
    Inscripcion.inscribir(usuario_id, dictado_id=dictado_id)
    Notificacion.crear(
        f"Te inscribiste en el dictado {dictado_id}",
        usuario_id,
        tipo="inscripcion",
        url_referencia=f"/dictados/{dictado_id}"
    )
    flash(" Solicitud de inscripción enviada, espera aprobación del docente", "success")
    return redirect(url_for("ver_dictado", dictado_id=dictado_id))
@app.route("/dictados/<int:dictado_id>/solicitudes")
@login_required
@roles_required("docente")
def solicitudes_dictado(dictado_id):
    pendientes = Inscripcion.obtener_pendientes_por_dictado(dictado_id)
    return render_template("solicitudes_dictado.html", pendientes=pendientes, dictado_id=dictado_id)
@app.route("/inscripcion_dictado/<int:inscripcion_id>/<string:accion>")
@login_required
@roles_required("docente")
def gestionar_inscripcion_dictado(inscripcion_id, accion):
    if accion in ["aceptado", "rechazado"]:
        Inscripcion.actualizar_estado(inscripcion_id, accion)
        flash(f"Inscripción {accion}", "success")
    return redirect(request.referrer or url_for("dictados"))



if __name__ == "__main__":
    app.run(debug=True)

