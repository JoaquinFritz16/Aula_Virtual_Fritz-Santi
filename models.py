from db import get_db_connection

class Usuario:
    def __init__(self, id, nombre, email, password, rol):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password = password
        self.rol = rol

    @staticmethod
    def crear(nombre, email, password, rol):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s, %s, %s, %s)",
            (nombre, email, password, rol)
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def buscar_por_email(email):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return Usuario(**row)
        return None
    @staticmethod
    def buscar_por_id(user_id):
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE id=%s", (user_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row:
                return Usuario(**row)
            return None

class Curso:
    def __init__(self, id=None, nombre="", descripcion="", instructor_id=None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.instructor_id = instructor_id

    def save(self, conn):
        cursor = conn.cursor()
        if self.id is None:  # crear nuevo
            cursor.execute(
                "INSERT INTO cursos (nombre, descripcion, instructor_id) VALUES (%s, %s, %s)",
                (self.nombre, self.descripcion, self.instructor_id)
            )
            conn.commit()
            self.id = cursor.lastrowid
        else:  
            cursor.execute(
                "UPDATE cursos SET nombre=%s, descripcion=%s, instructor_id=%s WHERE id=%s",
                (self.nombre, self.descripcion, self.instructor_id, self.id)
            )
            conn.commit()
        
    @staticmethod
    def get_all(conn):
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cursos")
        return cursor.fetchall()

    @staticmethod
    def delete(conn, id):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cursos WHERE id=%s", (id,))
        conn.commit()
class Tarea:
    def __init__(self, id, titulo, descripcion, curso_id, docente_id):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.curso_id = curso_id
        self.docente_id = docente_id

    @classmethod
    def crear(cls, titulo, descripcion, curso_id, docente_id):
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO tareas (titulo, descripcion, curso_id, docente_id) VALUES (%s, %s, %s, %s)",
            (titulo, descripcion, curso_id, docente_id),
        )
        db.commit()
        cursor.close()

    @classmethod
    def obtener_por_curso(cls, curso_id):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tareas WHERE curso_id = %s", (curso_id,))
        rows = cursor.fetchall()
        cursor.close()
        return [cls(**row) for row in rows]

class Inscripcion:
    @staticmethod
    def inscribir(usuario_id, curso_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT IGNORE INTO inscripciones (usuario_id, curso_id) VALUES (%s, %s)", (usuario_id, curso_id))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def obtener_cursos_por_usuario(usuario_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.* FROM cursos c
            JOIN inscripciones i ON c.id = i.curso_id
            WHERE i.usuario_id = %s
        """, (usuario_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def obtener_estudiantes_por_curso(curso_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.* FROM usuarios u
            JOIN inscripciones i ON u.id = i.usuario_id
            WHERE i.curso_id = %s
        """, (curso_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

class Calificacion:
    @staticmethod
    def crear(estudiante_id, curso_id, tarea_id, valor, comentarios=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO calificaciones (estudiante_id, curso_id, tarea_id, valor, comentarios) VALUES (%s,%s,%s,%s,%s)",
            (estudiante_id, curso_id, tarea_id, valor, comentarios)
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def obtener_por_estudiante(estudiante_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM calificaciones WHERE estudiante_id = %s", (estudiante_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def obtener_resumen_por_curso_y_estudiante(curso_id, estudiante_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.*, t.titulo AS tarea_titulo FROM calificaciones c
            LEFT JOIN tareas t ON c.tarea_id = t.id
            WHERE c.curso_id=%s AND c.estudiante_id=%s
        """, (curso_id, estudiante_id))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

class Notificacion:
    @staticmethod
    def crear(mensaje, usuario_id=None, tipo=None, url_referencia=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notificaciones (usuario_id, tipo, mensaje, url_referencia) VALUES (%s,%s,%s,%s)",
            (usuario_id, tipo, mensaje, url_referencia)
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def obtener_no_leidas(usuario_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM notificaciones WHERE (usuario_id = %s OR usuario_id IS NULL) AND leido = 0 ORDER BY creado DESC", (usuario_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def marcar_como_leida(notif_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE notificaciones SET leido=1 WHERE id=%s", (notif_id,))
        conn.commit()
        cursor.close()
        conn.close()