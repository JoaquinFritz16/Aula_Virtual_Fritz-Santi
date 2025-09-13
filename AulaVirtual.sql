-- Active: 1756120724278@@127.0.0.1@3306@aula_virtual
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
CREATE TABLE IF NOT EXISTS dictados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255),
    descripcion TEXT,
    imagen_url VARCHAR(255),
    instructor_id INT
);
CREATE TABLE IF NOT EXISTS cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    instructor_id INT,
    FOREIGN KEY (instructor_id) REFERENCES usuarios(id) ON DELETE SET NULL
);
CREATE TABLE if not exists tareas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    descripcion TEXT,
    docente_id INT NOT NULL,
    dictado_id int,
    FOREIGN KEY (docente_id) REFERENCES usuarios(id),
    FOREIGN KEY (dictado_id) REFERENCES dictados(id)
);

CREATE TABLE IF NOT EXISTS inscripciones (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  dictado_id INT NOT NULL,
  fecha_inscripcion DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY ux_inscripcion (usuario_id, dictado_id),
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  FOREIGN KEY (dictado_id) REFERENCES dictados(id) ON DELETE CASCADE
);


ALTER TABLE tareas
  ADD COLUMN tipo ENUM('tarea','examen') DEFAULT 'tarea',
  ADD COLUMN fecha_entrega DATETIME NULL;


CREATE TABLE IF NOT EXISTS calificaciones (
  id INT AUTO_INCREMENT PRIMARY KEY,
  estudiante_id INT NOT NULL,
  dictado_id INT NOT NULL,
  tarea_id INT NULL,
  valor DECIMAL(5,2) NOT NULL,
  comentarios TEXT,
  fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (estudiante_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  FOREIGN KEY (dictado_id) REFERENCES dictados(id) ON DELETE CASCADE,
  FOREIGN KEY (tarea_id) REFERENCES tareas(id) ON DELETE SET NULL
);


CREATE TABLE IF NOT EXISTS notificaciones (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NULL, 
  tipo VARCHAR(50),
  mensaje TEXT NOT NULL,
  leido TINYINT(1) DEFAULT 0,
  creado DATETIME DEFAULT CURRENT_TIMESTAMP,
  url_referencia VARCHAR(255) NULL,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

insert into usuarios (nombre, email, password, rol) values
('Admin', 'admin@example.com', 'admin123', 'admin');
select * from usuarios;
INSERT INTO usuarios (nombre, email, password, rol) 
VALUES ('ProfesorX', 'profx@mail.com', 'scrypt:32768:8:1$vtmaXXXm9TjC933n$6b6f33377d0513831a72df9c3b40d666824ff5bc8c2fd855d61d5d5cfa6ea2c57af2eb3c1e830e158a7378e837437d6986724530b3439ce91851f274f0bfbd6f', 'docente');

UPDATE usuarios
SET password = 'scrypt:32768:8:1$L6t1hog6g6RfshDK$c558266acf825a4588086ebb6355780c4a8423b85f1d2c9c2f5d541242f944b705212d7310eaa045d6b932e4bf726a54562e6669673d60a1bafc501128ebe844'
WHERE email = 'admin@example.com';

ALTER TABLE inscripciones
ADD COLUMN estado ENUM('pendiente','aceptado','rechazado') DEFAULT 'pendiente';
ALTER TABLE cursos
ADD COLUMN docente_id INT,
ADD FOREIGN KEY (docente_id) REFERENCES usuarios(id);
select * from cursos;

CREATE TABLE IF NOT EXISTS lapices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255),
    descripcion TEXT,
    imagen_url VARCHAR(255),
    instructor_id INT
);
select * from lapices;

select * from dictados;


ALTER TABLE tareas ADD COLUMN archivo_pdf VARCHAR(255) NULL;
DESCRIBE calificaciones;
