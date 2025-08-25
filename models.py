# models.py
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
        else:  # actualizar existente
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