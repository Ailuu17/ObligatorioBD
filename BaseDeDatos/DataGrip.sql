Create database obligatorio default character set utf8 collate utf8_spanish_ci;
use obligatorio;

-- Creación de tablas

Create table login(
    correo VARCHAR(70) PRIMARY KEY,
    contraseña VARCHAR(120) NOT NULL,
    rol VARCHAR(20) NOT NULL,
    CHECK ( rol in('administrador', 'planillero', 'jugador') )
);

Create table facultad(
    id_facultad INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

Create table jugador(
    ci INT PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL,
    apellido VARCHAR(40) NOT NULL,
    email VARCHAR(70) NOT NULL UNIQUE,
    fecha_nacimiento date NOT NULL,
    id_facultad INT NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    CHECK ( tipo in('grado', 'posgrado', 'docente', 'funcionario') ),
    FOREIGN KEY (id_facultad) REFERENCES facultad(id_facultad)
);

Create table torneo(
    id_torneo INT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    año INT NOT NULL,
    semestre INT NOT NULL,
    fecha_inicio date NOT NULL,
    fecha_fin date NOT NULL,
    estado VARCHAR(15) NOT NULL,
    CHECK ( semestre in(1, 2) ),
    CHECK ( estado in ('inscripción', 'en curso', 'finalizado') ),
    CHECK (fecha_inicio <= fecha_fin),
    UNIQUE(año, semestre)
);

CREATE TABLE equipo(
    id_equipo INT PRIMARY KEY,
    nombre VARCHAR(70) NOT NULL,
    id_facultad INT NOT NULL,
    FOREIGN KEY (id_facultad) REFERENCES facultad(id_facultad),
    UNIQUE (nombre)
);

-- Relaciona un equipo existente con el torneo que va a jugar y declara su capitán
CREATE TABLE equipo_torneo(
    id_equipo INT,
    id_torneo INT,
    ci_capitan INT NOT NULL,
    PRIMARY KEY (id_equipo,id_torneo),
    FOREIGN KEY (id_equipo) REFERENCES equipo(id_equipo),
    FOREIGN KEY (id_torneo) REFERENCES torneo(id_torneo),
    FOREIGN KEY (ci_capitan) REFERENCES jugador(ci),
    UNIQUE (ci_capitan,id_torneo)
);

-- Relaciona cada jugador con su respectivo equipo y les asigna su número de camiseta
Create table equipo_jugador_torneo(
    id_equipo INT NOT NULL,
    ci_jugador INT NOT NULL,
    id_torneo INT NOT NULL,
    numero_camiseta INT NOT NULL,
    CHECK (numero_camiseta > 0 AND numero_camiseta < 100),
    UNIQUE(ci_jugador, id_torneo),
    UNIQUE(id_equipo, id_torneo, numero_camiseta),
    PRIMARY KEY (id_equipo, ci_jugador, id_torneo),
    FOREIGN KEY (id_equipo, id_torneo) REFERENCES equipo_torneo(id_equipo, id_torneo),
    FOREIGN KEY (ci_jugador) REFERENCES jugador(ci)
);

Create table complejo(
    id_complejo INT PRIMARY KEY,
    nombre VARCHAR(70) NOT NULL,
    dirección VARCHAR(100) NOT NULL,
    departamento VARCHAR(20) NOT NULL
);

Create table cancha(
    nombre_cancha VARCHAR(70),
    id_complejo INT,
    superficie VARCHAR(10) NOT NULL,
    techada boolean NOT NULL,
    CHECK (superficie in ('sintético', 'parquet')),
    PRIMARY KEY (nombre_cancha, id_complejo),
    FOREIGN KEY (id_complejo) REFERENCES complejo(id_complejo)
);

Create table turno(
    id_turno INT PRIMARY KEY,
    hora_inicio time NOT NULL,
    hora_fin time NOT NULL,
    CHECK (hora_inicio < hora_fin)
);

Create table partido(
    id_partido INT,
    id_torneo INT,
    numero_fecha INT NOT NULL,
    id_equipo_local INT NOT NULL,
    id_equipo_visitante INT NOT NULL,
    dia date NOT NULL,
    id_turno INT NOT NULL,
    nombre_cancha VARCHAR(70) NOT NULL,
    id_complejo INT NOT NULL,
    estado VARCHAR(15) NOT NULL,
    UNIQUE(dia, id_turno, nombre_cancha, id_complejo),
    CHECK ( estado in ('programado', 'jugado', 'postergado', 'reprogramado')),
    CHECK (id_equipo_local != id_equipo_visitante),
    CHECK (numero_fecha > 0),
    PRIMARY KEY (id_partido, id_torneo),
    FOREIGN KEY (id_torneo) REFERENCES torneo(id_torneo),
    FOREIGN KEY (id_equipo_local, id_torneo) REFERENCES equipo_torneo(id_equipo, id_torneo),
    FOREIGN KEY (id_equipo_visitante, id_torneo) REFERENCES equipo_torneo(id_equipo, id_torneo),
    FOREIGN KEY (id_turno) REFERENCES turno(id_turno),
    FOREIGN KEY (nombre_cancha, id_complejo) REFERENCES cancha(nombre_cancha, id_complejo)
);

-- Registra los jugadores que realmente jugaron ese partido (hay 10 jugadores y juegan 5)
Create table planilla_partido(
    id_partido INT,
    id_torneo INT NOT NULL,
    ci_jugador INT,
    id_equipo INT NOT NULL,
    PRIMARY KEY (id_partido, id_torneo, ci_jugador),
    FOREIGN KEY (id_partido, id_torneo) REFERENCES partido(id_partido, id_torneo),
    FOREIGN KEY (ci_jugador) REFERENCES jugador(ci),
    FOREIGN KEY (id_equipo, id_torneo) REFERENCES equipo_torneo(id_equipo, id_torneo)
);

Create table gol(
    id_gol INT PRIMARY KEY,
    id_partido INT NOT NULL,
    id_torneo INT NOT NULL,
    ci_jugador INT NOT NULL,
    minuto INT NOT NULL,
    autogol boolean NOT NULL DEFAULT FALSE,
    CHECK (minuto >= 0),
    FOREIGN KEY (id_partido, id_torneo) REFERENCES partido(id_partido, id_torneo),
    FOREIGN KEY (ci_jugador) REFERENCES jugador(ci)
);

Create table tarjeta(
    id_tarjeta INT PRIMARY KEY,
    id_partido INT NOT NULL,
    id_torneo INT NOT NULL,
    ci_jugador INT NOT NULL,
    minuto INT NOT NULL,
    color VARCHAR(10) NOT NULL,
    CHECK ( color in('rojo', 'amarillo','roja', 'amarilla') ),
    CHECK (minuto >= 0),
    FOREIGN KEY (id_partido, id_torneo) REFERENCES partido(id_partido, id_torneo),
    FOREIGN KEY (ci_jugador) REFERENCES jugador(ci)
);

Create table sancion_jugador(
    id_sancion INT AUTO_INCREMENT PRIMARY KEY,
    ci_jugador INT NOT NULL,
    id_torneo INT NOT NULL,
    motivo VARCHAR(25) NOT NULL,
    numero_fecha_sancion INT NOT NULL,
    numero_fecha_inicio_sancion INT NOT NULL,
    cantidad_fechas_sancionadas INT NOT NULL,
    CHECK ( motivo in('roja', 'acumulación de amarillas', 'disciplinaria') ),
    CHECK (cantidad_fechas_sancionadas > 0),
    FOREIGN KEY (id_torneo) REFERENCES torneo(id_torneo),
    FOREIGN KEY (ci_jugador) REFERENCES jugador(ci)
);

-- Fue creada para registrar cualquier cambio de capitán que se de en el partido
Create Table capitan_partido(
    id_partido INT,
    id_torneo INT,
    id_equipo INT,
    ci_jugador INT NOT NULL,
    minuto_inicio INT,
    PRIMARY KEY (id_partido, id_torneo, id_equipo, minuto_inicio),
    FOREIGN KEY (id_partido,id_torneo) REFERENCES partido(id_partido,id_torneo),
    FOREIGN KEY (ci_jugador) REFERENCES jugador(ci),
    FOREIGN KEY (id_equipo,id_torneo) REFERENCES equipo_torneo(id_equipo,id_torneo),
    FOREIGN KEY (id_equipo, ci_jugador, id_torneo) REFERENCES equipo_jugador_torneo (id_equipo, ci_jugador, id_torneo)
);

-- Creación de usuarios válidos para ingresar al sistema
CREATE USER 'admin@ucu.edu.uy' IDENTIFIED BY 'ADMIN123';
CREATE USER 'planilla@ucu.edu.uy' IDENTIFIED BY 'PLANILLERO123';
CREATE USER 'jugador@correo.ucu.edu.uy' IDENTIFIED BY 'JUGADOR123';


-- Gestionamos los permisos de cada usuario según corresponda a su rol
-- Administrador: todos los permisos
GRANT ALL PRIVILEGES
ON obligatorio.*
TO 'admin@ucu.edu.uy';

-- Planillero: permiso para consultar, registrar y actualizar datos en ciertas tablas
GRANT SELECT
ON obligatorio.partido
TO 'planilla@ucu.edu.uy';
GRANT SELECT
ON obligatorio.turno
TO 'planilla@ucu.edu.uy';
GRANT SELECT
ON obligatorio.gol
TO 'planilla@ucu.edu.uy';
GRANT SELECT
ON obligatorio.equipo
TO 'planilla@ucu.edu.uy';
GRANT SELECT
ON obligatorio.equipo_jugador_torneo
TO 'planilla@ucu.edu.uy';
GRANT SELECT
ON obligatorio.jugador
TO 'planilla@ucu.edu.uy';
GRANT SELECT
ON obligatorio.capitan_partido
TO 'planilla@ucu.edu.uy';
GRANT INSERT
ON obligatorio.planilla_partido
TO 'planilla@ucu.edu.uy';
GRANT INSERT
ON obligatorio.gol
TO 'planilla@ucu.edu.uy';
GRANT INSERT
ON obligatorio.tarjeta
TO 'planilla@ucu.edu.uy';
GRANT INSERT
ON obligatorio.capitan_partido
TO 'planilla@ucu.edu.uy';
GRANT UPDATE (ci_jugador, minuto, autogol)
ON obligatorio.gol
TO 'planilla@ucu.edu.uy';
GRANT UPDATE
ON obligatorio.planilla_partido
TO 'planilla@ucu.edu.uy';
GRANT DELETE
ON obligatorio.gol
TO 'planilla@ucu.edu.uy';

-- Jugador: solo tiene permitido consultar ciertas tablas
GRANT SELECT
ON obligatorio.partido
TO 'jugador@correo.ucu.edu.uy';
GRANT SELECT
ON obligatorio.gol
TO 'jugador@correo.ucu.edu.uy';
GRANT SELECT
ON obligatorio.tarjeta
TO 'jugador@correo.ucu.edu.uy';
GRANT SELECT
ON obligatorio.sancion_jugador
TO 'jugador@correo.ucu.edu.uy';


-- Definimos los triggers necesarios para la insercción de los datos (el nombre de cada uno describe lo que hace)

DELIMITER //

CREATE TRIGGER trigger_misma_facultad
BEFORE INSERT
ON equipo_jugador_torneo
FOR EACH ROW
BEGIN

    DECLARE facultad_jugador INT;
    DECLARE facultad_equipo INT;

    SELECT id_facultad
    INTO facultad_jugador
    FROM jugador
    WHERE ci = NEW.ci_jugador;

    SELECT id_facultad
    INTO facultad_equipo
    FROM equipo
    WHERE id_equipo = NEW.id_equipo;

    IF facultad_jugador != facultad_equipo THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El jugador no pertenece a la facultad del equipo';
    END IF;

END; //

DELIMITER ;

DELIMITER //

CREATE TRIGGER trigger_max_docentes_funcionarios
BEFORE INSERT
ON equipo_jugador_torneo
FOR EACH ROW
BEGIN

    DECLARE tipo_jugador VARCHAR(20);
    DECLARE cantidad INT;

    SELECT tipo
    INTO tipo_jugador
    FROM jugador
    WHERE ci = NEW.ci_jugador;

    IF tipo_jugador IN ('docente','funcionario') THEN

        SELECT COUNT(*)
        INTO cantidad
        FROM equipo_jugador_torneo ejt
        JOIN jugador j ON ejt.ci_jugador = j.ci
        WHERE ejt.id_equipo = NEW.id_equipo
        AND ejt.id_torneo = NEW.id_torneo
        AND j.tipo IN ('docente','funcionario');

        IF cantidad = 2 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El equipo ya tiene 2 docentes/funcionarios';
        END IF;

    END IF;

END;//

DELIMITER ;

DELIMITER //

CREATE TRIGGER trigger_max_jugadores
BEFORE INSERT
ON equipo_jugador_torneo
FOR EACH ROW
BEGIN
    DECLARE cantidad INT;

    SELECT COUNT(*)
    INTO cantidad
    FROM equipo_jugador_torneo
    WHERE id_equipo = NEW.id_equipo
      AND id_torneo = NEW.id_torneo;

    IF cantidad >= 10 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'El equipo ya tiene el máximo de 10 jugadores';
    END IF;

END;//

DELIMITER ;

DELIMITER //

CREATE TRIGGER trigger_min_jugadores
BEFORE DELETE
ON equipo_jugador_torneo
FOR EACH ROW
BEGIN
    DECLARE cantidad INT;

    SELECT COUNT(*)
    INTO cantidad
    FROM equipo_jugador_torneo
    WHERE id_equipo = OLD.id_equipo
      AND id_torneo = OLD.id_torneo;

    IF cantidad <= 5 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'El equipo debe tener al menos 5 jugadores';
    END IF;

END//

DELIMITER ;

DELIMITER //

CREATE TRIGGER trigger_plantel_inscripcion_insert
BEFORE INSERT
ON equipo_jugador_torneo
FOR EACH ROW
BEGIN

    DECLARE estado_torneo VARCHAR(20);

    SELECT estado
    INTO estado_torneo
    FROM torneo
    WHERE id_torneo = NEW.id_torneo;

    IF estado_torneo != 'inscripción' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El plantel solo puede modificarse durante la inscripción';
    END IF;

END;//

DELIMITER ;

DELIMITER //

CREATE TRIGGER trigger_plantel_inscripcion_delete
BEFORE DELETE
ON equipo_jugador_torneo
FOR EACH ROW
BEGIN

    DECLARE estado_torneo VARCHAR(20);

    SELECT estado
    INTO estado_torneo
    FROM torneo
    WHERE id_torneo = OLD.id_torneo;

    IF estado_torneo != 'inscripción' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El plantel solo puede modificarse durante la inscripción';
    END IF;

END;//

DELIMITER ;

DELIMITER //

CREATE TRIGGER trigger_plantel_inscripcion_update
BEFORE UPDATE
ON equipo_jugador_torneo
FOR EACH ROW
BEGIN

    DECLARE estado_torneo VARCHAR(20);

    SELECT estado
    INTO estado_torneo
    FROM torneo
    WHERE id_torneo = NEW.id_torneo;

    IF estado_torneo != 'inscripción' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El plantel solo puede modificarse durante la inscripción';
    END IF;

END;//

DELIMITER ;

DELIMITER //

CREATE TRIGGER trigger_suspendido_planilla
BEFORE INSERT
ON planilla_partido
FOR EACH ROW
BEGIN

    DECLARE fecha_partido INT;
    DECLARE cantidad INT;

    SELECT numero_fecha
    INTO fecha_partido
    FROM partido
    WHERE id_partido = NEW.id_partido
      AND id_torneo = NEW.id_torneo;

    SELECT COUNT(*)
    INTO cantidad
    FROM sancion_jugador
    WHERE ci_jugador = NEW.ci_jugador
      AND id_torneo = NEW.id_torneo
      AND fecha_partido BETWEEN numero_fecha_inicio_sancion AND numero_fecha_inicio_sancion + cantidad_fechas_sancionadas -1;

    IF cantidad > 0 THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Jugador suspendido';

    END IF;

END;//

DELIMITER ;

DELIMITER //

CREATE TRIGGER trigger_gol_planilla
BEFORE INSERT
ON gol
FOR EACH ROW
BEGIN

    DECLARE cantidad INT;

    SELECT COUNT(*)
    INTO cantidad
    FROM planilla_partido
    WHERE id_partido = NEW.id_partido
      AND id_torneo = NEW.id_torneo
      AND ci_jugador = NEW.ci_jugador;

    IF cantidad = 0 THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Jugador no figura en planilla';

    END IF;

END;//

DELIMITER ;

DELIMITER //

CREATE TRIGGER trigger_gol_plazo_update
BEFORE UPDATE
ON gol
FOR EACH ROW
BEGIN

    DECLARE estado_partido VARCHAR(15);
    DECLARE fecha_partido DATE;
    DECLARE hora_fin TIME;
    DECLARE cantidad INT;

    SELECT p.estado, p.dia, t.hora_fin
    INTO estado_partido, fecha_partido, hora_fin
    FROM partido p
    JOIN turno t ON p.id_turno = t.id_turno
    WHERE p.id_partido = OLD.id_partido
      AND p.id_torneo = OLD.id_torneo;

    IF estado_partido <> 'jugado'
       OR NOW() < TIMESTAMP(fecha_partido, hora_fin)
       OR NOW() > DATE_ADD(TIMESTAMP(fecha_partido, hora_fin), INTERVAL 48 HOUR) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El resultado solo se puede corregir dentro de las 48 horas posteriores al fin del turno';
    END IF;

    SELECT COUNT(*)
    INTO cantidad
    FROM planilla_partido
    WHERE id_partido = NEW.id_partido
      AND id_torneo = NEW.id_torneo
      AND ci_jugador = NEW.ci_jugador;

    IF cantidad = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Jugador no figura en planilla';
    END IF;

END;//

DELIMITER ;

DELIMITER //

CREATE TRIGGER trigger_gol_plazo_delete
BEFORE DELETE
ON gol
FOR EACH ROW
BEGIN

    DECLARE estado_partido VARCHAR(15);
    DECLARE fecha_partido DATE;
    DECLARE hora_fin TIME;

    SELECT p.estado, p.dia, t.hora_fin
    INTO estado_partido, fecha_partido, hora_fin
    FROM partido p
    JOIN turno t ON p.id_turno = t.id_turno
    WHERE p.id_partido = OLD.id_partido
      AND p.id_torneo = OLD.id_torneo;

    IF estado_partido <> 'jugado'
       OR NOW() < TIMESTAMP(fecha_partido, hora_fin)
       OR NOW() > DATE_ADD(TIMESTAMP(fecha_partido, hora_fin), INTERVAL 48 HOUR) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El resultado solo se puede corregir dentro de las 48 horas posteriores al fin del turno';
    END IF;

END;//

DELIMITER ;

DELIMITER //

CREATE TRIGGER trigger_no_reprogramar_jugado
BEFORE UPDATE
ON partido
FOR EACH ROW
BEGIN

    IF OLD.estado = 'jugado'
       AND (NEW.estado <> OLD.estado OR NEW.dia <> OLD.dia OR NEW.id_turno <> OLD.id_turno) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'No se puede cambiar el estado, la fecha o el turno de un partido jugado';
    END IF;

END;//

DELIMITER ;

DELIMITER //

CREATE TRIGGER trigger_tarjeta_planilla
BEFORE INSERT
ON tarjeta
FOR EACH ROW
BEGIN

    DECLARE cantidad INT;

    SELECT COUNT(*)
    INTO cantidad
    FROM planilla_partido
    WHERE id_partido = NEW.id_partido
      AND id_torneo = NEW.id_torneo
      AND ci_jugador = NEW.ci_jugador;

    IF cantidad = 0 THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Jugador no figura en planilla';

    END IF;

END;//

DELIMITER ;

DELIMITER //

CREATE TRIGGER trigger_no_borrar_jugado
BEFORE DELETE
ON partido
FOR EACH ROW
BEGIN

    IF OLD.estado = 'jugado' THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'No se puede borrar un partido jugado';

    END IF;

END;//

DELIMITER ;



-- Insertamos los valores en cada una de las tablas

INSERT INTO facultad VALUES
(1,'Facultad de Ingeniería y Tecnologías - MVD'),
(2,'Facultad de Ciencias Empresariales - MVD'),
(3,'Facultad de Derecho y Artes Liberales - MVD'),
(4,'Facultad de Psicología y Bienestar Humano - MVD'),
(5,'Facultad de Salud - MVD'),
(6,'Facultad de Ingeniería y Tecnologías - PDE');

INSERT INTO torneo VALUES
(1,'Torneo Interfacultades de Fútbol 5 2026',2026,2,'2026-08-03','2026-11-30','inscripción');

INSERT INTO complejo VALUES
(1,' Sacré Cœur (Central)','Av. 8 de Octubre 2738','Montevideo'),
(2,'Candelaria','Av. Roosevelt y Florencia (Parada 7 y 1/2)','Maldonado');

INSERT INTO cancha VALUES
('Cancha A',1,'sintético',true),
('Cancha B',1,'sintético',false),
('Cancha C',2,'parquet',true);

INSERT INTO turno VALUES
(1,'18:00:00','19:00:00'),
(2,'19:00:00','20:00:00'),
(3,'20:00:00','21:00:00'),
(4,'21:00:00','22:00:00'),
(5,'22:00:00','23:00:00');

INSERT INTO login VALUES
('admin@ucu.edu.uy','ADMIN123','administrador'),
('planilla@ucu.edu.uy','PLANILLERO123','planillero'),
('jugador@correo.ucu.edu.uy','JUGADOR123','jugador');

INSERT INTO equipo VALUES
(1,'Ingenieros FC',1),
(2,'Business United',2),
(3,'DereClub',3),
(4,'PsicoTeam',4),
(5,'Salud FC',5),
(6, 'Inge26',6);

INSERT INTO jugador VALUES
(12345678,'Juan','Pérez','juanperez@correo.ucu.edu.uy','2000-05-10',1,'grado'),
(11111111,'Martín','Silva','martinsilva@correo.ucu.edu.uy','2001-03-12',1,'grado'),
(12121212,'Diego','López','diegolopez@correo.ucu.edu.uy','1999-11-01',1,'posgrado'),
(10041004,'Pablo','Gómez','pablogomez@ucu.edu.uy','1985-01-07',1,'docente'),
(15151515,'Nicolás','Suárez','nicosuarez@correo.ucu.edu.uy','2002-06-11',1,'grado'),
(89785876,'Andrés','Rodríguez','andresrodriguez@correo.ucu.edu.uy','2001-09-05',1,'grado'),
(78965412,'Ricardo','Fernandez','ricardofernandez@correo.ucu.edu.uy','2002-04-15',1,'grado'),
(36985214,'Alvaro','Mendez','alvaromendez@correo.ucu.edu.uy','2003-02-11',1,'grado'),
(74125896,'Fernando','Santos','fernandosantos@correo.ucu.edu.uy','1997-05-01',1,'posgrado'),
(78932145,'Daniel','Acosta','danielacosta@ucu.edu.uy','1989-08-22',1,'funcionario'),
(87456321,'Luis','Fernández','luisfernandez@correo.ucu.edu.uy','2000-04-10',2,'grado'),
(22222222,'Santiago','Méndez','santiagomendez@correo.ucu.edu.uy','2002-01-10',2,'grado'),
(23100130,'Facundo','Ruiz','facundoruiz@correo.ucu.edu.uy','2001-08-20',2,'grado'),
(50000000,'Carlos','Díaz','carlosdiaz@ucu.edu.uy','1988-02-01',2,'docente'),
(20000000,'Joaquín','Torres','joaquintorres@correo.ucu.edu.uy','1999-12-03',2,'posgrado'),
(10000000,'Mateo','Viera','mateoviera@correo.ucu.edu.uy','1995-05-15',2,'grado'),
(70000000,'Pedro','Silva','pedrosilva@correo.ucu.edu.uy','2002-03-11',2,'grado'),
(30000000,'Ignacio','Costa','ignaciocosta@correo.ucu.edu.uy','2001-04-17',2,'grado'),
(40000000,'Emilio','Rey','emiliorey@correo.ucu.edu.uy','1998-09-02',2,'posgrado'),
(54000000,'Hector','Pintos','hectorpintos@ucu.edu.uy','1991-07-12',2,'funcionario'),
(60000000,'Agustín','Sosa','agustinsosa@correo.ucu.edu.uy','2000-01-20',3,'grado'),
(12312345,'Bruno','Pérez','brunoperez@correo.ucu.edu.uy','2001-07-10',3,'grado'),
(80000000,'Tomás','Rey','tomasrey@correo.ucu.edu.uy','1998-12-12',3,'posgrado'),
(90000000,'Javier','Costa','javiercosta@ucu.edu.uy','1984-11-01',3,'docente'),
(33333333,'Rodrigo','Acosta','rodrigoacosta@correo.ucu.edu.uy','2002-03-04',3,'grado'),
(44444444,'Gonzalo','Martins','gonzalomartins@ucu.edu.uy','1990-02-11',3,'funcionario'),
(55555555,'Martin','Castro','martincastro@correo.ucu.edu.uy','2001-01-10',3,'grado'),
(66666666,'Jorge','Lemos','jorgelemos@correo.ucu.edu.uy','2002-05-04',3,'grado'),
(77777777,'Federico','Curbelo','fedecurbelo@correo.ucu.edu.uy','1999-11-17',3,'posgrado'),
(88888888,'German','Pena','germanpena@ucu.edu.uy','1990-10-11',3,'grado'),
(99999999,'Lucía','Martínez','luciamartinez@correo.ucu.edu.uy','2000-02-15',4,'grado'),
(57777777,'Valentina','Pereira','valepereira@correo.ucu.edu.uy','2001-06-11',4,'grado'),
(47777777,'Camila','Suárez','camilasuarez@correo.ucu.edu.uy','1998-11-23',4,'posgrado'),
(45555555,'Mariana','Silva','marianasilva@ucu.edu.uy','1986-07-01',4,'docente'),
(49999999,'Florencia','Rodríguez','florenciarodriguez@correo.ucu.edu.uy','2002-05-01',4,'grado'),
(40000007,'Paula','López','paulalopez@ucu.edu.uy','1994-04-10',4,'funcionario'),
(44747444,'Victoria','Suarez','victoriasuarez@correo.ucu.edu.uy','2002-06-16',4,'grado'),
(78787333,'Antonella','Mora','antonellamora@correo.ucu.edu.uy','2001-08-01',4,'grado'),
(98789878,'Natalia','Costa','nataliacosta@correo.ucu.edu.uy','1999-03-19',4,'posgrado'),
(15951595,'Gabriela','Perez','gabrielaperez@correo.ucu.edu.uy','1991-12-13',4,'grado'),
(56786780,'Federico','Mora','federico.mora@correo.ucu.edu.uy','2000-09-09',5,'grado'),
(51111111,'Matías','Lima','matias.lima@correo.ucu.edu.uy','2001-08-08',5,'grado'),
(50333333,'Sebastián','Ortiz','sebastian.ortiz@correo.ucu.edu.uy','1997-02-02',5,'posgrado'),
(54545222,'Ricardo','Núñez','ricardo.nuñez@ucu.edu.uy','1982-03-03',5,'docente'),
(50055005,'Álvaro','Gil','alvaro.gil@correo.ucu.edu.uy','2002-10-10',5,'grado'),
(56767676,'César','Pardo','cesar.pardo@correo.ucu.edu.uy','1992-05-05',5,'posgrado'),
(58889999,'Leonardo','Suarez','leonardo.suarez@correo.ucu.edu.uy','2002-07-20',5,'grado'),
(58787872,'Nicolas','Silva','nicolas.silva@correo.ucu.edu.uy','2001-11-10',5,'grado'),
(57872451,'Diego','Fuentes','diego.fuentes@correo.ucu.edu.uy','1998-08-14',5,'posgrado'),
(50105010,'Mauricio','Lemos','mauricio.lemos@ucu.edu.uy','1992-05-09',5,'funcionario'),
(20202020,'Sofía','García','sofia.garcia@correo.ucu.edu.uy','2000-01-01',6,'grado'),
(68955786,'Martina','Pintos','martina.pintos@correo.ucu.edu.uy','2001-02-02',6,'grado'),
(60606060,'Micaela','Romero','micaela.romero@correo.ucu.edu.uy','1999-09-09',6,'posgrado'),
(67676767,'Ana','Morales','ana.morales@correo.ucu.edu.uy','1987-04-04',6,'grado'),
(11111777,'Julieta','Santos','julieta.santos@correo.ucu.edu.uy','2002-07-07',6,'grado'),
(77771111,'Paola','Castro','paola.castro@ucu.edu.uy','1993-08-08',6,'funcionario'),
(78555691,'Valeria','Torres','valeria.torres@correo.ucu.edu.uy','2002-04-14',6,'grado'),
(88899978,'Melina','Gomez','melina.gomez@correo.ucu.edu.uy','2001-06-28',6,'grado'),
(67854555,'Luciana','Silva','luciana.silva@correo.ucu.edu.uy','1999-01-21',6,'posgrado'),
(99879996,'Patricia','Ruiz','patricia.ruiz@correo.ucu.edu.uy','1990-03-04',6,'grado');

INSERT INTO equipo_torneo VALUES
(1,1,12345678),
(2,1,87456321),
(3,1,12312345),
(4,1,99999999),
(5,1,56786780),
(6,1,20202020);

INSERT INTO equipo_jugador_torneo VALUES
(1,12345678,1,10),
(1,11111111,1,7),
(1,12121212,1,8),
(1,10041004,1,1),
(1,15151515,1,11),
(1,89785876,1,5),
(1,78965412,1,23),
(1,36985214,1,28),
(1,74125896,1,24),
(1,78932145,1,18),
(2,87456321,1,10),
(2,22222222,1,7),
(2,23100130,1,8),
(2,50000000,1,1),
(2,20000000,1,11),
(2,10000000,1,5),
(2,70000000,1,9),
(2,30000000,1,22),
(2,40000000,1,27),
(2,54000000,1,16),
(3,60000000,1,10),
(3,12312345,1,7),
(3,80000000,1,8),
(3,90000000,1,1),
(3,33333333,1,11),
(3,44444444,1,5),
(3,55555555,1,9),
(3,66666666,1,22),
(3,77777777,1,27),
(3,88888888,1,16),
(4,99999999,1,10),
(4,57777777,1,7),
(4,47777777,1,8),
(4,45555555,1,1),
(4,49999999,1,11),
(4,40000007,1,5),
(4,44747444,1,9),
(4,78787333,1,22),
(4,98789878,1,27),
(4,15951595,1,16),
(5,56786780,1,10),
(5,51111111,1,7),
(5,50333333,1,8),
(5,54545222,1,1),
(5,50055005,1,11),
(5,56767676,1,5),
(5,58889999,1,9),
(5,58787872,1,22),
(5,57872451,1,27),
(5,50105010,1,16),
(6,20202020,1,10),
(6,68955786,1,7),
(6,60606060,1,8),
(6,67676767,1,1),
(6,11111777,1,11),
(6,77771111,1,5),
(6,78555691,1,9),
(6,88899978,1,22),
(6,67854555,1,27),
(6,99879996,1,16);

UPDATE torneo
SET estado = 'en curso'
WHERE id_torneo = 1;

INSERT INTO partido VALUES
(1,1,1,1,2,'2026-09-10',1,'Cancha A',1,'jugado'),
(2,1,1,3,4,'2026-09-10',2,'Cancha B',1,'jugado'),
(3,1,1,5,6,'2026-09-10',3,'Cancha C',2,'jugado'),
(4,1,2,1,3,'2026-09-17',1,'Cancha A',1,'jugado'),
(5,1,2,2,5,'2026-09-17',2,'Cancha B',1,'jugado'),
(6,1,2,4,6,'2026-09-17',3,'Cancha C',2,'jugado'),
(7,1,3,1,4,'2026-09-24',1,'Cancha A',1,'jugado'),
(8,1,3,2,6,'2026-09-24',2,'Cancha B',1,'jugado'),
(9,1,3,3,5,'2026-09-24',3,'Cancha C',2,'postergado'),
(10,1,4,4,5,'2026-10-01',1,'Cancha A',1,'postergado'),
(11,1,4,2,3,'2026-10-01',2,'Cancha B',1,'programado'),
(12,1,4,1,6,'2026-10-01',3,'Cancha C',2,'programado'),
(13,1,5,4,5,'2026-10-08',1,'Cancha A',1,'reprogramado');

INSERT INTO planilla_partido VALUES
(1,1,12345678,1),
(1,1,11111111,1),
(1,1,12121212,1),
(1,1,10041004,1),
(1,1,78965412,1),
(1,1,15151515,1),
(1,1,87456321,2),
(1,1,22222222,2),
(1,1,23100130,2),
(1,1,50000000,2),
(1,1,20000000,2),
(1,1,70000000,2);

INSERT INTO tarjeta VALUES
(1,1,1 ,10041004,12,'amarilla'),
(2,1,1 ,10041004,22,'amarilla'),
(3,1,1 ,10041004,31,'amarilla'),
(4,1,1, 50000000,3,'amarilla');

INSERT INTO sancion_jugador VALUES
(1,10041004,1,'acumulación de amarillas',1,2,1),
(2,88888888,1,'roja',1,2,1),
(3,57872451,1,'acumulación de amarillas',1,2,1);

INSERT INTO capitan_partido VALUES
(1,1,1,12345678,0),
(1,1,1,15151515,32),
(1,1,2,87456321,0),
(1,1,2,70000000,28);

INSERT INTO gol VALUES
(1,1,1,12345678,8,false),
(2,1,1,11111111,12,false),
(3,1,1,12121212,21,false),
(4,1,1,87456321,27,true),
(5,1,1,22222222,35,true);

INSERT INTO planilla_partido VALUES
(2,1,60000000,3),
(2,1,12312345,3),
(2,1,88888888,3),
(2,1,90000000,3),
(2,1,33333333,3),
(2,1,44444444,3),
(2,1,99999999,4),
(2,1,57777777,4),
(2,1,47777777,4),
(2,1,45555555,4),
(2,1,49999999,4),
(2,1,40000007,4);

INSERT INTO tarjeta VALUES
(5,2,1, 88888888,15,'roja');

INSERT INTO sancion_jugador VALUES
(4,54000000,1,'disciplinaria',2,3,2),
(5,15951595,1,'disciplinaria',2,3,2);

INSERT INTO capitan_partido VALUES
(2,1,3,12312345,0),
(2,1,3,44444444,30),
(2,1,4,99999999,0),
(2,1,4, 40000007,25);

INSERT INTO gol VALUES
(6,2,1,60000000,11,false),
(7,2,1,12312345,29,false),
(8,2,1,99999999,38,false);

INSERT INTO planilla_partido VALUES
(3,1,56786780,5),
(3,1,57872451,5),
(3,1,50333333,5),
(3,1,54545222,5),
(3,1,50055005,5),
(3,1,50105010,5),
(3,1,20202020,6),
(3,1,68955786,6),
(3,1,60606060,6),
(3,1,67676767,6),
(3,1,11111777,6),
(3,1,88899978,6);

INSERT INTO tarjeta VALUES
(6,3,1, 57872451,23,'amarilla'),
(7,3,1, 57872451,27,'amarilla'),
(8,3,1, 57872451,38,'amarilla');

INSERT INTO sancion_jugador VALUES
(6,47777777,1,'roja',3,4,1),
(7,49999999,1,'disciplinaria',3,4,2),
(8,77771111,1,'roja',3,4,1);

INSERT INTO capitan_partido VALUES
(3,1,5,56786780,0),
(3,1,5,50105010 ,35),
(3,1,6,20202020,0),
(3,1,6,88899978,45);

INSERT INTO gol VALUES
(9,3,1,56786780,13,false),
(10,3,1,20202020,44,false);

INSERT INTO planilla_partido VALUES
(4,1,12345678,1),
(4,1,11111111,1),
(4,1,12121212,1),
(4,1,78965412,1),
(4,1,89785876,1),
(4,1,12312345,3),
(4,1,33333333,3),
(4,1,44444444,3),
(4,1,66666666,3),
(4,1,77777777,3);

INSERT INTO tarjeta VALUES
(9,4,1, 77777777,40,'amarilla');

INSERT INTO capitan_partido VALUES
(4,1,1,12345678,0),
(4,1,3,12312345,0);

INSERT INTO gol VALUES
(11,4,1,12345678,5,false),
(12,4,1,11111111,7,false),
(13,4,1,12121212,12,false),
(14,4,1,89785876,40,false),
(15,4,1,12312345,45,false);

INSERT INTO planilla_partido VALUES
(5,1,87456321,2),
(5,1,22222222,2),
(5,1,10000000,2),
(5,1,54000000,2),
(5,1,30000000,2),
(5,1,56786780,5),
(5,1,51111111,5),
(5,1,50333333,5),
(5,1,58889999,5),
(5,1,58787872,5);

INSERT INTO tarjeta VALUES
(10,5,1,10000000,27,'amarilla');

INSERT INTO capitan_partido VALUES
(5,1,2,87456321,0),
(5,1,5,56786780,0);

INSERT INTO gol VALUES
(16,5,1,87456321,10,false),
(17,5,1,22222222,12,false),
(18,5,1,56786780,18,false),
(19,5,1,51111111,22,false);

INSERT INTO planilla_partido VALUES
(6,1,99999999,4),
(6,1,57777777,4),
(6,1,78787333,4),
(6,1,98789878,4),
(6,1,15951595,4),
(6,1,20202020,6),
(6,1,68955786,6),
(6,1,60606060,6),
(6,1,88899978,6),
(6,1,67854555,6);

INSERT INTO tarjeta VALUES
(11,6,1,98789878,14,'amarilla');

INSERT INTO capitan_partido VALUES
(6,1,4,99999999,0),
(6,1,6,20202020,0);

INSERT INTO gol VALUES
(20,6,1,20202020,47,false);

INSERT INTO planilla_partido VALUES
(7,1,12345678,1),
(7,1,11111111,1),
(7,1,12121212,1),
(7,1,15151515,1),
(7,1,89785876,1),
(7,1,57777777,4),
(7,1,49999999,4),
(7,1,78787333,4),
(7,1,98789878,4),
(7,1,47777777,4);

INSERT INTO tarjeta VALUES
(12,7,1,47777777,40,'roja');

INSERT INTO capitan_partido VALUES
(7,1,1,12345678,0),
(7,1,4,57777777,0);

INSERT INTO gol VALUES
(21,7,1,12345678,7,false),
(22,7,1,11111111,25,true),
(23,7,1,15151515,40,false);

INSERT INTO planilla_partido VALUES
(8,1,87456321,2),
(8,1,22222222,2),
(8,1,23100130,2),
(8,1,70000000,2),
(8,1,40000000,2),
(8,1,20202020,6),
(8,1,68955786,6),
(8,1,60606060,6),
(8,1,77771111,6),
(8,1,78555691,6);

INSERT INTO tarjeta VALUES
(13,8,1,78555691,22,'amarilla'),
(14,8,1,77771111,21, 'roja');

INSERT INTO capitan_partido VALUES
(8,1,2,87456321,0),
(8,1,6,20202020,0);

INSERT INTO gol VALUES
(24,8,1,87456321,1,false),
(25,8,1,22222222,6,false),
(26,8,1,20202020,9,false),
(27,8,1,68955786,30,false),
(28,8,1,60606060,48,false);

DELIMITER //

CREATE TRIGGER trigger_gol_plazo_insert
BEFORE INSERT
ON gol
FOR EACH ROW
BEGIN

    DECLARE estado_partido VARCHAR(15);
    DECLARE fecha_partido DATE;
    DECLARE hora_fin TIME;

    SELECT p.estado, p.dia, t.hora_fin
    INTO estado_partido, fecha_partido, hora_fin
    FROM partido p
    JOIN turno t ON p.id_turno = t.id_turno
    WHERE p.id_partido = NEW.id_partido
      AND p.id_torneo = NEW.id_torneo;

    IF estado_partido != 'jugado'
       OR NOW() < TIMESTAMP(fecha_partido, hora_fin)
       OR NOW() > DATE_ADD(TIMESTAMP(fecha_partido, hora_fin), INTERVAL 48 HOUR) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El resultado solo se puede cargar dentro de las 48 horas posteriores al fin del turno';
    END IF;

END;//

DELIMITER ;

DELIMITER //

CREATE TRIGGER trigger_sancion_automatica_tarjeta
AFTER INSERT
ON tarjeta
FOR EACH ROW
BEGIN

    DECLARE fecha_sancion INT;
    DECLARE cantidad_amarillas INT;

    SELECT numero_fecha
    INTO fecha_sancion
    FROM partido
    WHERE id_partido = NEW.id_partido
      AND id_torneo = NEW.id_torneo;

    IF NEW.color IN ('roja', 'rojo') THEN
        INSERT INTO sancion_jugador (
            ci_jugador, id_torneo, motivo, numero_fecha_sancion,
            numero_fecha_inicio_sancion, cantidad_fechas_sancionadas
        )
        VALUES (
            NEW.ci_jugador, NEW.id_torneo, 'roja',
            fecha_sancion, fecha_sancion + 1, 1
        );
    ELSEIF NEW.color IN ('amarilla', 'amarillo') THEN
        SELECT COUNT(*)
        INTO cantidad_amarillas
        FROM tarjeta
        WHERE ci_jugador = NEW.ci_jugador
          AND id_torneo = NEW.id_torneo
          AND color IN ('amarilla', 'amarillo');

        IF MOD(cantidad_amarillas, 3) = 0 THEN
            INSERT INTO sancion_jugador (
                ci_jugador, id_torneo, motivo, numero_fecha_sancion,
                numero_fecha_inicio_sancion, cantidad_fechas_sancionadas
            )
            VALUES (
                NEW.ci_jugador, NEW.id_torneo, 'acumulación de amarillas',
                fecha_sancion, fecha_sancion + 1, 1
            );
        END IF;
    END IF;

END;//

DELIMITER ;

-- Realizamos las consultas que se pedían 

-- 1: Cantidad de jugadores por facultad y por tipo 
-- Por facultad:
SELECT f.nombre, COUNT(*) AS cantidad_jugadores
FROM facultad f
JOIN jugador j
    ON f.id_facultad = j.id_facultad
GROUP BY f.id_facultad, f.nombre
ORDER BY cantidad_jugadores DESC;

-- Por tipo:
SELECT tipo, COUNT(*) AS cantidad
FROM jugador
GROUP BY tipo;


-- 2: Cantidad de sanciones por equipo y por motivo
-- Por motivo:
SELECT motivo, COUNT(*) AS cantidad
FROM sancion_jugador
GROUP BY motivo;

-- Por equipo:
SELECT e.nombre AS equipo, COUNT(*) AS cantidad_sanciones
FROM sancion_jugador s
JOIN equipo_jugador_torneo ejt
    ON s.ci_jugador = ejt.ci_jugador
   AND s.id_torneo = ejt.id_torneo
JOIN equipo e
    ON ejt.id_equipo = e.id_equipo
GROUP BY e.id_equipo, e.nombre
ORDER BY cantidad_sanciones DESC;


-- 3: Tabla de goleadores
SELECT j.ci, j.nombre, j.apellido, COUNT(*) AS goles
FROM gol g
JOIN jugador j
    ON g.ci_jugador = j.ci
GROUP BY j.ci, j.nombre, j.apellido
ORDER BY goles DESC
LIMIT 10;


-- 4: Jugadores inscriptos en un plantel que nunca figuraron en una planilla de juego
SELECT j.ci, j.nombre, j.apellido
FROM jugador j
JOIN equipo_jugador_torneo ejt
    ON j.ci = ejt.ci_jugador
WHERE NOT EXISTS (
    SELECT *
    FROM planilla_partido pp
    WHERE pp.ci_jugador = j.ci
);


-- 5: Canchas y turnos más utilizados
-- Canchas:
SELECT nombre_cancha, COUNT(*) AS cantidad_usos
FROM partido
WHERE estado = 'jugado'
GROUP BY nombre_cancha
ORDER BY cantidad_usos DESC;

-- Turnos:
SELECT t.id_turno, t.hora_inicio, t.hora_fin, COUNT(*) AS cantidad_usos
FROM partido p
JOIN turno t
    ON p.id_turno = t.id_turno
WHERE p.estado = 'jugado'
GROUP BY t.id_turno, t.hora_inicio, t.hora_fin
ORDER BY cantidad_usos DESC;


-- 6: Promedio de goles por partido en cada fecha y en toda la edición
-- Por fecha:
SELECT p.numero_fecha, COUNT(g.id_gol) * 1.0 / COUNT(DISTINCT p.id_partido) AS promedio_goles
FROM partido p
LEFT JOIN gol g
    ON p.id_partido = g.id_partido
   AND p.id_torneo = g.id_torneo
WHERE p.estado = 'jugado'
GROUP BY p.numero_fecha
ORDER BY p.numero_fecha;

-- En toda la edición
SELECT COUNT(g.id_gol) * 1.0 / COUNT(DISTINCT p.id_partido) AS promedio_goles_torneo
FROM partido p
LEFT JOIN gol g
    ON p.id_partido = g.id_partido
   AND p.id_torneo = g.id_torneo
WHERE p.estado = 'jugado';


-- 7: Porcentaje de partidos jugados vs. postergados/cancelados
-- Por los cambios que realizamos, postergados y cancelados son lo mismo y la base de datos
-- solo considera postergados, ni cancelados
-- El 23,07692% que falta para completar el 100% es de los programados y reprogramados
-- Porcentaje de jugados
SELECT
    COUNT(*) * 100.0 /
    (SELECT COUNT(*) FROM partido) AS porcentaje_jugados
FROM partido
WHERE estado = 'jugado';

-- Porcentaje de postergados
SELECT
    COUNT(*) * 100.0 /
    (SELECT COUNT(*) FROM partido) AS porcentaje_postergados
FROM partido
WHERE estado = 'postergado';


-- 8: Tabla de fair play por equipo
SELECT e.nombre,
    SUM(
        CASE
            WHEN t.color = 'amarilla' THEN 1
            WHEN t.color = 'roja' THEN 3
        END
    ) AS puntaje_fair_play
FROM tarjeta t
JOIN equipo_jugador_torneo ejt
    ON t.ci_jugador = ejt.ci_jugador
   AND t.id_torneo = ejt.id_torneo
JOIN equipo e
    ON ejt.id_equipo = e.id_equipo
GROUP BY e.id_equipo, e.nombre
ORDER BY puntaje_fair_play ASC;


-- 9: Tabla de posiciones por edición del torneo
-- Como había que juntar muchísimos datos, hicimos las partes de las consultas sueltas y con ayuda de la IA las fuimos juntando para que funcione correctamente.
-- Asumimos como puntaje: 3 por victoria, 1 por empate y 0 por derrota.
-- La posicion de cada equipo se determina por el orden de las filas.
SELECT t.nombre AS torneo, t.año, t.semestre, e.nombre AS equipo,
       -- Contamos los partidos jugados
       COUNT(r.id_partido) AS partidos_jugados,
       -- Contamos los partidos ganados, empatados y perdidos
       COUNT(CASE WHEN r.goles_favor > r.goles_contra THEN 1 END) AS partidos_ganados,
       COUNT(CASE WHEN r.goles_favor = r.goles_contra THEN 1 END) AS partidos_empatados,
       COUNT(CASE WHEN r.goles_favor < r.goles_contra THEN 1 END) AS partidos_perdidos,
       CASE
           WHEN COUNT(r.id_partido) = 0 THEN 0
           ELSE SUM(r.goles_favor)
       END AS goles_favor,
       CASE
           WHEN COUNT(r.id_partido) = 0 THEN 0
           ELSE SUM(r.goles_contra)
       END AS goles_contra,
       CASE
           WHEN COUNT(r.id_partido) = 0 THEN 0
           ELSE SUM(r.goles_favor) - SUM(r.goles_contra)
       END AS diferencia_goles,
       -- Indicamos cuantos puntos se obtienen en cada caso y sumamos para obtener el total de puntos del equipo
       SUM(CASE
               WHEN r.goles_favor > r.goles_contra THEN 3
               WHEN r.goles_favor = r.goles_contra THEN 1
               ELSE 0
           END) AS puntos
FROM equipo_torneo et
JOIN torneo t
    ON t.id_torneo = et.id_torneo
JOIN equipo e
    ON e.id_equipo = et.id_equipo
LEFT JOIN (
    -- Calculamos el resultado de cada partido para cada equipo que jugó
    SELECT p.id_torneo, p.id_partido, et.id_equipo,
           -- Contamos los goles a favor
           COUNT(CASE
                     WHEN (g.autogol = FALSE AND pp.id_equipo = et.id_equipo)
                       OR (g.autogol = TRUE AND (
                              (et.id_equipo = p.id_equipo_local AND pp.id_equipo = p.id_equipo_visitante)
                           OR (et.id_equipo = p.id_equipo_visitante AND pp.id_equipo = p.id_equipo_local)
                       ))
                     THEN 1
                 END) AS goles_favor,

           -- Contamos los goles en contra
           COUNT(CASE
                     WHEN (g.autogol = FALSE AND (
                              (et.id_equipo = p.id_equipo_local AND pp.id_equipo = p.id_equipo_visitante)
                           OR (et.id_equipo = p.id_equipo_visitante AND pp.id_equipo = p.id_equipo_local)
                       ))
                       OR (g.autogol = TRUE AND pp.id_equipo = et.id_equipo)
                     THEN 1
                 END) AS goles_contra
    FROM partido p
    JOIN equipo_torneo et
        ON et.id_torneo = p.id_torneo
        AND (et.id_equipo = p.id_equipo_local OR et.id_equipo = p.id_equipo_visitante)
    LEFT JOIN gol g
        ON g.id_partido = p.id_partido
        AND g.id_torneo = p.id_torneo
    -- Usamos el equipo de la planilla del partido para identificar al goleador.
    LEFT JOIN planilla_partido pp
        ON pp.id_partido = g.id_partido
       AND pp.id_torneo = g.id_torneo
       AND pp.ci_jugador = g.ci_jugador
    WHERE p.estado = 'jugado'
    GROUP BY p.id_torneo, p.id_partido, et.id_equipo
) r
    ON r.id_torneo = et.id_torneo
   AND r.id_equipo = et.id_equipo
GROUP BY t.id_torneo, t.nombre, t.año, t.semestre, e.id_equipo, e.nombre
ORDER BY t.id_torneo, puntos DESC, diferencia_goles DESC, goles_favor DESC, equipo;


-- Realizamos las 3 consultas a elección nuestra 

-- 1: Top 10 jugadores con más sanciones
SELECT j.ci, j.nombre, j.apellido, COUNT(*) AS cantidad_sanciones
FROM sancion_jugador s
JOIN jugador j
    ON s.ci_jugador = j.ci
GROUP BY j.ci, j.nombre, j.apellido
ORDER BY cantidad_sanciones DESC
LIMIT 10;


-- 2: Top 3 facultades con más goles
SELECT f.nombre, COUNT(*) AS goles
FROM gol g
JOIN jugador j
    ON g.ci_jugador = j.ci
JOIN facultad f
    ON j.id_facultad = f.id_facultad
GROUP BY f.id_facultad, f.nombre
ORDER BY goles DESC
LIMIT 3;


-- 3: Jugador con más tarjetas sacadas
SELECT j.ci, j.nombre, j.apellido, COUNT(*) AS cantidad_tarjetas
FROM tarjeta t
JOIN jugador j
    ON t.ci_jugador = j.ci
GROUP BY j.ci, j.nombre, j.apellido
ORDER BY cantidad_tarjetas DESC
LIMIT 1;
