-- Eliminar y crear base de datos desde cero
DROP DATABASE IF EXISTS aula_virtual;
CREATE DATABASE aula_virtual;
USE aula_virtual;

-- Tabla de instituciones educativas (similar a colegios)
CREATE TABLE Instituciones (
  id_institucion INT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(255) NOT NULL,
  direccion VARCHAR(255),
  estado ENUM('pendiente', 'aprobado', 'rechazado') DEFAULT 'pendiente'
);

-- Tabla de usuarios (asociados a instituciones)
CREATE TABLE Usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  rol ENUM('estudiante', 'instructor', 'administrador') NOT NULL,
  id_institucion INT,
  FOREIGN KEY (id_institucion) REFERENCES Instituciones(id_institucion)
);

-- Tabla de cursos
CREATE TABLE Cursos (
  id_curso INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(255) NOT NULL,
  descripcion TEXT,
  id_instructor INT,
  FOREIGN KEY (id_instructor) REFERENCES Usuarios(id)
);

-- Tabla de inscripciones a cursos (similar a equipos)
CREATE TABLE Inscripciones (
  id_inscripcion INT AUTO_INCREMENT PRIMARY KEY,
  id_estudiante INT,
  id_curso INT,
  fecha_inscripcion DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_estudiante) REFERENCES Usuarios(id),
  FOREIGN KEY (id_curso) REFERENCES Cursos(id_curso)
);

-- Tabla de contenidos (similar a jugadores)
CREATE TABLE Contenidos (
  id_contenido INT AUTO_INCREMENT PRIMARY KEY,
  titulo VARCHAR(255) NOT NULL,
  descripcion TEXT,
  archivo VARCHAR(255),
  id_curso INT,
  FOREIGN KEY (id_curso) REFERENCES Cursos(id_curso)
);

-- Tabla de evaluaciones (similar a directores técnicos)
CREATE TABLE Evaluaciones (
  id_evaluacion INT AUTO_INCREMENT PRIMARY KEY,
  titulo VARCHAR(255) NOT NULL,
  descripcion TEXT,
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  id_curso INT,
  FOREIGN KEY (id_curso) REFERENCES Cursos(id_curso)
);

-- Tabla de preguntas (similar a partidos)
CREATE TABLE Preguntas (
  id_pregunta INT AUTO_INCREMENT PRIMARY KEY,
  texto TEXT NOT NULL,
  id_evaluacion INT,
  FOREIGN KEY (id_evaluacion) REFERENCES Evaluaciones(id_evaluacion)
);

-- Tabla de respuestas
CREATE TABLE Respuestas (
  id_respuesta INT AUTO_INCREMENT PRIMARY KEY,
  texto TEXT NOT NULL,
  es_correcta BOOLEAN DEFAULT FALSE,
  id_pregunta INT,
  FOREIGN KEY (id_pregunta) REFERENCES Preguntas(id_pregunta)
);

-- Tabla de resultados de evaluaciones
CREATE TABLE ResultadosEvaluaciones (
  id_resultado INT AUTO_INCREMENT PRIMARY KEY,
  id_estudiante INT,
  id_evaluacion INT,
  calificacion DECIMAL(5,2),
  fecha_realizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_estudiante) REFERENCES Usuarios(id),
  FOREIGN KEY (id_evaluacion) REFERENCES Evaluaciones(id_evaluacion)
);

-- Insertar una institución
INSERT INTO Instituciones (nombre, direccion, estado) VALUES ('Instituto Educativo', 'Calle Principal 123', 'aprobado');

-- Insertar un usuario administrador
INSERT INTO Usuarios (email, password, rol, id_institucion) VALUES ('admin@instituto.edu', 'password123', 'administrador', 1);

-- Insertar un usuario instructor
INSERT INTO Usuarios (email, password, rol, id_institucion) VALUES ('instructor@instituto.edu', 'password123', 'instructor', 1);

-- Insertar un usuario estudiante
INSERT INTO Usuarios (email, password, rol, id_institucion) VALUES ('estudiante@instituto.edu', 'password123', 'estudiante', 1);

-- Insertar un curso
INSERT INTO Cursos (nombre, descripcion, id_instructor) VALUES ('Matemáticas', 'Curso de matemáticas básicas', 2);

-- Insertar una inscripción
INSERT INTO Inscripciones (id_estudiante, id_curso) VALUES (3, 1);

-- Insertar un contenido
INSERT INTO Contenidos (titulo, descripcion, archivo, id_curso) VALUES ('Introducción a las Matemáticas', 'Contenido introductorio', 'intro_matematicas.pdf', 1);

-- Insertar una evaluación
INSERT INTO Evaluaciones (titulo, descripcion, id_curso) VALUES ('Examen Parcial', 'Primer examen parcial del curso', 1);

-- Insertar una pregunta
INSERT INTO Preguntas (texto, id_evaluacion) VALUES ('¿Cuál es la suma de 2 + 2?', 1);

-- Insertar respuestas
INSERT INTO Respuestas (texto, es_correcta, id_pregunta) VALUES ('3', FALSE, 1);
INSERT INTO Respuestas (texto, es_correcta, id_pregunta) VALUES ('4', TRUE, 1);

-- Insertar un resultado de evaluación
INSERT INTO ResultadosEvaluaciones (id_estudiante, id_evaluacion, calificacion) VALUES (3, 1, 9.5);