from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import Usuario, Curso, Tarea
from forms import LoginForm, RegistrationForm, CourseForm
from db import get_db_connection
app = Flask(__name__)
app.secret_key = "clave_secreta_segura"

# ---------------------------
# INDEX
# ---------------------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------------------
# REGISTER
# ---------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        nombre = form.username.data
        email = form.email.data
        password = generate_password_hash(form.password.data)
        rol = "estudiante"  # o según tu lógica

        Usuario.crear(nombre, email, password, rol)
        flash("✅ Usuario registrado correctamente", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)

# ---------------------------
# LOGIN
# ---------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.username.data
        password = form.password.data

        usuario = Usuario.buscar_por_email(email)
        if usuario and check_password_hash(usuario.password, password):
            session["usuario_id"] = usuario.id
            session["usuario_nombre"] = usuario.nombre
            flash("Bienvenido " + usuario.nombre, "success")
            return redirect(url_for("dashboard"))
        else:
            flash("❌ Credenciales incorrectas", "danger")

    return render_template("login.html", form=form)

# ---------------------------
# LOGOUT
# ---------------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("login"))

# ---------------------------
# DASHBOARD
# ---------------------------
@app.route("/dashboard")
def dashboard():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    usuario = Usuario.buscar_por_email(session["usuario_nombre"])  # o buscar_por_id si prefieres
    if usuario.rol == "docente":
        return render_template("dashboard_docente.html", usuario=usuario)
    else:
        return render_template("dashboard_estudiante.html", usuario=usuario)

# ---------------------------
# CURSOS
# ---------------------------
@app.route("/cursos")
def cursos():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conn = Curso.get_all(get_db_connection())
    return render_template("cursos.html", cursos=conn)

@app.route("/cursos/agregar", methods=["GET", "POST"])
def agregar_curso():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    form = CourseForm()
    if form.validate_on_submit():
        curso = Curso(nombre=form.title.data, descripcion=form.description.data, instructor_id=session["usuario_id"])
        conn = get_db_connection()
        curso.save(conn)
        conn.close()
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

# ---------------------------
# TAREAS
# ---------------------------
@app.route("/tareas/nueva", methods=["GET", "POST"])
def nueva_tarea():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    usuario = Usuario.buscar_por_email(session["usuario_nombre"])
    if usuario.rol != "docente":
        flash("❌ No tienes permiso para crear tareas", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        titulo = request.form["titulo"]
        descripcion = request.form["descripcion"]
        curso_id = request.form["curso_id"]
        Tarea.crear(titulo, descripcion, curso_id, usuario.id)
        flash("✅ Tarea creada correctamente", "success")
        return redirect(url_for("dashboard"))

    cursos = Curso.get_all(get_db_connection())
    return render_template("nueva_tarea.html", cursos=cursos)

# ---------------------------
# RUN APP
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
