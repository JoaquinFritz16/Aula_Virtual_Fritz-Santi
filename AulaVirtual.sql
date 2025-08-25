drop database if exists aula_virtual;
create database aula_virtual;
USE aula_virtual;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    rol VARCHAR(50)
);
CREATE TABLE IF NOT EXISTS cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    instructor_id INT,
    FOREIGN KEY (instructor_id) REFERENCES usuarios(id) ON DELETE SET NULL
);
CREATE TABLE tareas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    descripcion TEXT,
    curso_id INT NOT NULL,
    docente_id INT NOT NULL,
    FOREIGN KEY (curso_id) REFERENCES cursos(id),
    FOREIGN KEY (docente_id) REFERENCES usuarios(id)
);
