from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

routes = Blueprint("routes", __name__)

# ---------------------------
#  USUARIOS
# ---------------------------

@routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # verificar si ya existe
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("El usuario ya existe, usa otro correo", "danger")
            return redirect(url_for("routes.register"))

        # registrar nuevo usuario
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


# ---------------------------
#  DASHBOARD
# ---------------------------

@routes.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("routes.login"))

    return render_template("dashboard.html", nombre=session["nombre"])


# ---------------------------
#  CURSOS
# ---------------------------

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


@routes.route("/cursos/agregar", methods=["GET", "POST"])
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
