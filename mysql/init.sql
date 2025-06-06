CREATE TABLE usuario (
id INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(50) NOT NULL UNIQUE,
password VARCHAR(255) NOT NULL
);

INSERT INTO usuario (username, password) VALUES ('admin', 'adminItpj@rdin');

CREATE TABLE autorizacion_ingreso (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_visita VARCHAR(50) UNIQUE,
    identificacion VARCHAR(30),
    nombreresponsable VARCHAR(100),
    ocupacion VARCHAR(50),
    entidad VARCHAR(100),
    direccion_barrio VARCHAR(100),
    municipio VARCHAR(50),
    telefono VARCHAR(20),
    objetivovisita TEXT,
    numeropersonas INT,
    vinculacion TEXT,
    hora_llegada TIME,
    hora_salida TIME,
    fecha DATE,
    usuario_id INT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE asistencia_visita (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE,
    nombrecompleto VARCHAR(100),
    numero_documento VARCHAR(30),
    tipo_persona ENUM('Estudiante', 'Docente', 'Administrativo', 'Externo') NOT NULL,
    vinculacion_facultad ENUM(
        'INGENIERIA AMBIENTAL',
        'INGENIERIA CIVIL',
        'INGENIERIA FORESTAL',
        'INGENIERIA DE SISTEMAS',
        'INGENIERIA AGROINDUSTRIAL',
        'CONTADURIA PUBLICA',
        'ADMINISTRACION DE EMPRESAS',
        'NEGOCIOS INTERNACIONALES',
        'NO PERTENECE A NINGUNA'
    ),
    vinculacion_semestre ENUM('I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'No Aplica'),
    vinculacion_institucion VARCHAR(100),
    telefono VARCHAR(20),
    actividad_desarrollada ENUM('practica academica', 'turismo', 'reconocimiento'),
    codigo_visita VARCHAR(50),
    FOREIGN KEY (codigo_visita) REFERENCES autorizacion_ingreso(codigo_visita)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE estado_autorizacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    autorizacion_ingreso_id INT NOT NULL,
    estado ENUM('Aceptada', 'Rechazada', 'Pendiente') NOT NULL,
    motivo_estado TEXT,
    fecha_decision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (autorizacion_ingreso_id) REFERENCES autorizacion_ingreso(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);