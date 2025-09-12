from db import get_db_connection

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

    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        if self.id is None:
            print(f"Guardando curso: {self.nombre}, {self.descripcion}, instructor_id={self.instructor_id}")
            cursor.execute(
                "INSERT INTO cursos (nombre, descripcion, instructor_id) VALUES (%s, %s, %s)",
                (self.nombre, self.descripcion, self.instructor_id)
            )
            conn.commit()
            self.id = cursor.lastrowid
        else:  # actualizar curso existente
            cursor.execute(
                "UPDATE cursos SET nombre=%s, descripcion=%s, instructor_id=%s WHERE id=%s",
                (self.nombre, self.descripcion, self.instructor_id, self.id)
            )
            conn.commit()
            print(f"Curso guardado con id {self.id}")
        cursor.close()
        conn.close()


    # Obtener todos los cursos
    @staticmethod
    def get_all():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cursos")
        cursos = cursor.fetchall()
        cursor.close()
        conn.close()
        return cursos

    # Obtener cursos por docente
    @staticmethod
    def obtener_por_docente(docente_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cursos WHERE instructor_id = %s", (docente_id,))
        cursos = cursor.fetchall()
        cursor.close()
        conn.close()
        return cursos

    # Eliminar curso
    @staticmethod
    def delete(id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cursos WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
class Tarea:
    def __init__(self, id, titulo, descripcion, docente_id, dictado_id=None, archivo_pdf=None):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        
        self.docente_id = docente_id
        self.dictado_id = dictado_id
        self.archivo_pdf = archivo_pdf

    @classmethod
    def crear(cls, titulo, descripcion, docente_id, dictado_id=None, archivo_pdf=None):
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO tareas (titulo, descripcion,  docente_id, dictado_id, archivo_pdf) VALUES (%s, %s, %s, %s, %s)",
            (titulo, descripcion,  docente_id, dictado_id, archivo_pdf),
        )
        db.commit()
        cursor.close()


    # @classmethod
    # def obtener_por_curso(cls, curso_id):
    #     db = get_db_connection()
    #     cursor = db.cursor(dictionary=True)
    #     cursor.execute("SELECT * FROM tareas WHERE curso_id = %s", (curso_id,))
    #     rows = cursor.fetchall()
    #     cursor.close()
    #     return [cls(**row) for row in rows]
    @staticmethod
    def obtener_por_dictado(dictado_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tareas WHERE dictado_id=%s ORDER BY fecha_entrega DESC", (dictado_id,))
        tareas = cursor.fetchall()
        cursor.close()
        conn.close()
        return tareas

class Inscripcion:

    @staticmethod
    def inscribir(usuario_id, curso_id=None, dictado_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO inscripciones (usuario_id, curso_id, dictado_id, estado)
            VALUES (%s, %s, %s, 'pendiente')
            ON DUPLICATE KEY UPDATE estado='pendiente'
        """, (usuario_id, curso_id, dictado_id))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def actualizar_estado(inscripcion_id, nuevo_estado):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE inscripciones SET estado=%s WHERE id=%s", (nuevo_estado, inscripcion_id))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def obtener_pendientes_por_dictado(dictado_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT i.id, u.nombre, u.email
            FROM inscripciones i
            JOIN usuarios u ON u.id = i.usuario_id
            WHERE i.dictado_id=%s AND i.estado='pendiente'
        """, (dictado_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def obtener_pendientes_por_curso(curso_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT i.id, u.nombre, u.email 
            FROM inscripciones i
            JOIN usuarios u ON u.id = i.usuario_id
            WHERE i.curso_id = %s AND i.estado = 'pendiente'
        """, (curso_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def obtener_estudiantes_aceptados_curso(curso_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.* 
            FROM usuarios u
            JOIN inscripciones i ON u.id = i.usuario_id
            WHERE i.curso_id = %s AND i.estado = 'aceptado'
        """, (curso_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def obtener_estudiantes_aceptados_dictado(dictado_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.* 
            FROM usuarios u
            JOIN inscripciones i ON u.id = i.usuario_id
            WHERE i.dictado_id = %s AND i.estado = 'aceptado'
        """, (dictado_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def obtener_cursos_por_usuario(usuario_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.* 
            FROM cursos c
            JOIN inscripciones i ON c.id = i.curso_id
            WHERE i.usuario_id = %s AND i.estado = 'aceptado'
        """, (usuario_id,))
        cursos = cursor.fetchall()
        cursor.close()
        conn.close()
        return cursos

    @staticmethod
    def obtener_dictados_por_usuario(usuario_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT d.* 
            FROM dictados d
            JOIN inscripciones i ON d.id = i.dictado_id
            WHERE i.usuario_id = %s AND i.estado = 'aceptado'
        """, (usuario_id,))
        dictados = cursor.fetchall()
        cursor.close()
        conn.close()
        return dictados

class Calificacion:
    @staticmethod
    def crear(estudiante_id, dictado_id, tarea_id, valor, comentarios=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO calificaciones (estudiante_id, dictado_id, tarea_id, valor, comentarios) VALUES (%s,%s,%s,%s,%s)",
            (estudiante_id, dictado_id, tarea_id, valor, comentarios)
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
    def obtener_resumen_por_dictado_y_estudiante(dictado_id, estudiante_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.*, t.titulo AS tarea_titulo 
            FROM calificaciones c
            LEFT JOIN tareas t ON c.tarea_id = t.id
            WHERE c.dictado_id = %s AND c.estudiante_id = %s
        """, (dictado_id, estudiante_id))
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


class Lapiz:
    def __init__(self, titulo, descripcion, imagen_url, id=None):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.imagen_url = imagen_url

    def save(self, usuario_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        if self.id is None:
            cursor.execute(
                "INSERT INTO lapices (titulo, descripcion, imagen_url, instructor_id) VALUES (%s, %s, %s, %s)",
                (self.titulo, self.descripcion, self.imagen_url, usuario_id)
            )
            conn.commit()
            self.id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE lapices SET titulo=%s, descripcion=%s, imagen_url=%s WHERE id=%s",
                (self.titulo, self.descripcion, self.imagen_url, self.id)
            )
            conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_all():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM lapices")
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultados


class Dictado:
    def __init__(self, titulo, descripcion, imagen_url, id=None):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.imagen_url = imagen_url

    def save(self, usuario_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        if self.id is None:
            cursor.execute(
                "INSERT INTO dictados (titulo, descripcion, imagen_url, instructor_id) VALUES (%s, %s, %s, %s)",
                (self.titulo, self.descripcion, self.imagen_url, usuario_id)
            )
            conn.commit()
            self.id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE dictados SET titulo=%s, descripcion=%s, imagen_url=%s WHERE id=%s",
                (self.titulo, self.descripcion, self.imagen_url, self.id)
            )
            conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_all():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM dictados")
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultados
    
    
    @staticmethod
    def buscar_por_id(dictado_id):
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM dictados WHERE id=%s", (dictado_id,))
        dictado = cursor.fetchone()
        cursor.close()
        conn.close()
        return dictado