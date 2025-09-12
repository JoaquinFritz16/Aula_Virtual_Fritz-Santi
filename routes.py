from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from models import Inscripcion, Curso, Lapiz, Usuario, Dictado, Tarea, Calificacion

routes = Blueprint("routes", __name__)



@routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("El usuario ya existe, usa otro correo", "danger")
            return redirect(url_for("routes.register"))

        
        hashed_pw = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
            (nombre, email, hashed_pw),
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Registro exitoso, ahora puedes iniciar sesión", "success")
        return redirect(url_for("routes.login"))

    return render_template("register.html")


@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["nombre"] = user["nombre"]
            flash("Bienvenido, " + user["nombre"], "success")
            return redirect(url_for("routes.dashboard"))
        else:
            flash("Credenciales incorrectas", "danger")

    return render_template("login.html")


@routes.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión", "info")
    return redirect(url_for("routes.login"))



@routes.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("routes.login"))

    return render_template("dashboard.html", nombre=session["nombre"])



@routes.route("/cursos")
def cursos():
    if "user_id" not in session:
        return redirect(url_for("routes.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cursos")
    cursos = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("cursos.html", cursos=cursos)


@routes.route("/cursos/crear", methods=["GET", "POST"])
def agregar_curso():
    if "user_id" not in session:
        return redirect(url_for("routes.login"))

    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO cursos (nombre, descripcion, instructor_id) VALUES (%s, %s, %s)",
            (nombre, descripcion, session["user_id"]),
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Curso agregado correctamente", "success")
        return redirect(url_for("routes.cursos"))

    return render_template("agregar_curso.html")


@routes.route("/cursos/editar/<int:id>", methods=["GET", "POST"])
def editar_curso(id):
    if "user_id" not in session:
        return redirect(url_for("routes.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]

        cursor.execute(
            "UPDATE cursos SET nombre = %s, descripcion = %s WHERE id = %s",
            (nombre, descripcion, id),
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Curso actualizado", "success")
        return redirect(url_for("routes.cursos"))

    cursor.execute("SELECT * FROM cursos WHERE id = %s", (id,))
    curso = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template("editar_curso.html", curso=curso)


@routes.route("/cursos/eliminar/<int:id>")
def eliminar_curso(id):
    if "user_id" not in session:
        return redirect(url_for("routes.login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cursos WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Curso eliminado", "danger")
    return redirect(url_for("routes.cursos"))

# Alumno solicita inscripción
@routes.route("/cursos/<int:curso_id>/inscribirse", methods=["POST"])
def inscribirse_curso(curso_id):
    if "user_id" not in session:
        return redirect(url_for("routes.login"))
    Inscripcion.inscribir(session["user_id"], curso_id)
    flash("Solicitud enviada, espera aprobación del docente", "info")
    return redirect(url_for("routes.cursos"))


# Profesor ve solicitudes pendientes
@routes.route("/cursos/<int:curso_id>/solicitudes")
def solicitudes_curso(curso_id):
    if "user_id" not in session:
        return redirect(url_for("routes.login"))
    pendientes = Inscripcion.obtener_pendientes_por_curso(curso_id)
    return render_template("solicitudes.html", pendientes=pendientes, curso_id=curso_id)


# Profesor acepta o rechaza
@routes.route("/inscripcion/<int:inscripcion_id>/<string:accion>")
def gestionar_inscripcion(inscripcion_id, accion):
    if accion in ["aceptado", "rechazado"]:
        Inscripcion.actualizar_estado(inscripcion_id, accion)
        flash(f"Inscripción {accion}", "success")
    return redirect(request.referrer or url_for("routes.cursos"))
@routes.route("/curso/nuevo", methods=["GET", "POST"])
def nuevo_curso():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        docente_id = session["user_id"]

        # Crear el curso y guardarlo
        curso = Curso(nombre=nombre, descripcion=descripcion, instructor_id=docente_id)
        curso.save()  # <--- ahora sí se guarda

        flash("Curso creado con éxito", "success")
        return redirect(url_for("cursos"))

    return render_template("curso_form.html")


@routes.route("/lapices")

def lapices():
    if "user_id" not in session:
        return redirect(url_for("login"))
    lista = Lapiz.get_all()
    return render_template("lapices.html", lapices=lista)

@routes.route("/lapices/agregar", methods=["GET", "POST"])
 # solo docentes pueden agregar
def agregar_lapiz():
    if "user_id" not in session:
        return redirect(url_for("login"))
    usuario = Usuario.buscar_por_id(session["usuario_id"])

    if request.method == "POST":
        titulo = request.form.get("titulo")
        descripcion = request.form.get("descripcion")
        imagen_url = request.form.get("imagen_url")

        nuevo = Lapiz(titulo, descripcion, imagen_url)
        nuevo.save(usuario.id)

        flash("✅ Lápiz agregado correctamente", "success")
        return redirect(url_for("routes.lapices"))

    return render_template("agregar_lapiz.html")


@routes.route("/dictados")

def dictados():
    if "user_id" not in session:
        return redirect(url_for("login"))
    lista = Dictado.get_all()
    return render_template("dictado.html", dictados=lista)

@routes.route("/dictados/agregar", methods=["GET", "POST"])
 # solo docentes pueden agregar
def agregar_dictado():
    if "user_id" not in session:
        return redirect(url_for("login"))
    usuario = Usuario.buscar_por_id(session["usuario_id"])

    if request.method == "POST":
        titulo = request.form.get("titulo")
        descripcion = request.form.get("descripcion")
        imagen_url = request.form.get("imagen_url")

        nuevo = Dictado(titulo, descripcion, imagen_url)
        nuevo.save(usuario.id)

        flash("Dictado agregado correctamente", "success")
        return redirect(url_for("routes.dictados"))

    return render_template("agregar_dictado.html")

@routes.route("/dictados/<int:dictado_id>")
def ver_dictado(dictado_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    usuario = Usuario.buscar_por_id(session["usuario_id"])

    # Obtener dictado
    dictado = Dictado.buscar_por_id(dictado_id)
    if not dictado:
        flash("Dictado no encontrado", "danger")
        return redirect(url_for("routes.dictados"))

    # Obtener tareas del dictado
    tareas = Tarea.obtener_por_dictado(dictado_id)

    # Si el usuario es estudiante, obtener calificaciones
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
