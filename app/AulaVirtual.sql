-- Eliminar y crear base de datos desde cero
DROP DATABASE IF EXISTS copa_renault;
CREATE DATABASE copa_renault;
USE copa_renault;

-- Tabla de colegios
CREATE TABLE Colegios (
  id_colegio INT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(255),
  direccion VARCHAR(255),
  estado ENUM('pendiente', 'aprobado', 'rechazado') DEFAULT 'pendiente'
);

-- Tabla de usuarios (asociados a colegios)
CREATE TABLE usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  rol VARCHAR(50) NOT NULL,
  id_colegio INT,
  FOREIGN KEY (id_colegio) REFERENCES Colegios(id_colegio)
);

-- Tabla de equipos
CREATE TABLE Equipos (
  id_equipo INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100),
  deporte VARCHAR(50),
  categoria VARCHAR(50),
  genero VARCHAR(20),
  id_colegio INT,
  FOREIGN KEY (id_colegio) REFERENCES Colegios(id_colegio)
);

-- Tabla de jugadores
CREATE TABLE Jugadores (
  dni INT PRIMARY KEY,
  id_equipo INT,
  mail VARCHAR(255),
  FOREIGN KEY (id_equipo) REFERENCES Equipos(id_equipo)
);

-- Tabla de directores técnicos
CREATE TABLE DT (
  dni INT PRIMARY KEY,
  name VARCHAR(100),
  surname VARCHAR(100),
  telefono INT,
  id_equipo INT,
  mail VARCHAR(255),
  FOREIGN KEY (id_equipo) REFERENCES Equipos(id_equipo)
);

-- Tabla de partidos
CREATE TABLE Partidos (
  id_partido INT PRIMARY KEY AUTO_INCREMENT,
  fecha DATETIME,
  equipo_local INT,
  equipo_visitante INT,
  resultado VARCHAR(100),
  cancha VARCHAR(100),
  FOREIGN KEY (equipo_local) REFERENCES Equipos(id_equipo),
  FOREIGN KEY (equipo_visitante) REFERENCES Equipos(id_equipo)
);
UPDATE usuarios SET id_colegio = 1 WHERE id = 1;

SELECT * FROM Colegios;
select * from usuarios;