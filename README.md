# Trabajo obligatorio - Base de Datos I
# Sistema de Gestión del Torneo Interfacultades de Fútbol 5

## Integrantes:
- Lara Canío
- Aileen Waller

## Descripción del proyecto

El sistema permite administrar el **Torneo Interfacultades de Fútbol 5**, centralizando la gestión de equipos, jugadores, partidos, resultados, sanciones y estadísticas.

La solución busca reemplazar el uso de planillas de cálculo y grupos de mensajería, evitando errores en la organización del torneo y mejorando la trazabilidad de la información.

## Objetivos

- Gestionar jugadores y equipos.
- Administrar planteles por edición del torneo.
- Organizar el fixture y programación de partidos.
- Registrar planillas de juego.
- Registrar goles y tarjetas.
- Administrar sanciones disciplinarias y suspensiones registradas.
- Generar reportes estadísticos para la organización del torneo.

---

## Arquitectura

La solución implementada es una aplicación interactiva de consola escrita en Python, conectada directamente a MySQL mediante `mysql-connector-python` y consultas SQL. No incluye una interfaz web ni ORM (ya que la letra no lo permitía).

---

## Roles del sistema

### Administrador
Puede realizar:

- ABM de jugadores.
- ABM de equipos.
- Gestión de planteles.
- ABM de complejos deportivos.
- ABM de canchas.
- ABM de partidos.
- Gestión de sanciones.
- Consulta de reportes.

### Planillero
Puede:

- Registrar planillas de partido.
- Registrar goles.
- Corregir o eliminar goles dentro del plazo permitido.
- Registrar tarjetas.
- Registrar capitanes y marcar partidos como jugados.
- Consultar partidos y la tabla de posiciones.

### Jugador
Puede consultar la tabla de posiciones, partidos, goles, tarjetas y sanciones.

---

## Funcionalidades principales

### Gestión de Jugadores

- Alta de jugadores.
- Modificación de datos.
- Baja y consulta de jugadores.
- Asociación a una facultad existente.

### Gestión de Equipos

- Creación de equipos.
- Asignación de capitán.
- Administración de planteles.
- Control de restricciones del torneo.

### Gestión del Torneo

- Inscripción de equipos.
- Programación de fechas.
- Gestión de partidos.
- La reprogramación modifica el registro del partido existente y conserva su fecha original del fixture.
- Control de disponibilidad de canchas y horarios.

### Registro de Partidos

- Registro de jugadores participantes.
- Registro de goles.
- Registro de tarjetas.
- Cálculo automático del resultado.

### Gestión de Sanciones

- La administración puede registrar, modificar, eliminar y consultar sanciones.
- Las sanciones por tarjeta roja o acumulación de amarillas no se generan
  automáticamente; deben registrarse desde la gestión de sanciones.
- Al agregar un jugador a una planilla, MySQL verifica que no esté suspendido.

### Reportes

- Tabla de posiciones.
- Tabla de goleadores.
- Ranking Fair Play.
- Promedio de goles.
- Uso de canchas y turnos.
- Estadísticas de jugadores por facultad.
- Jugadores nunca convocados.
- Sanciones por equipo y motivo.
- Porcentaje de partidos jugados vs. postergados.
- Consultas adicionales propuestas por el equipo.

---

## Modelo de Datos

La base de datos se construye sobre las entidades principales:

- Login
- Facultad
- Jugador
- Torneo
- Equipo
- Equipo_Jugador_Torneo
- Complejo
- Cancha
- Turno
- Partido
- Planilla_Partido
- Gol
- Tarjeta
- Sancion_Jugador

Definidas según el modelo propuesto en la consigna.

---

## Instalación y ejecución

### Requisitos

- Python 3.
- MySQL en ejecución.
- Una cuenta MySQL con permisos suficientes para crear la base y ejecutar el script.

### Instalar la dependencia

Desde PowerShell, en la carpeta raíz del proyecto:

```powershell
python -m pip install mysql-connector-python
```

### Crear la base y los datos de prueba

Abra `BaseDeDatos/DataGrip.sql` en MySQL Workbench, DataGrip u otra herramienta
compatible y ejecute el script completo sobre una instalación limpia. El script
crea la base `obligatorio`, las tablas, restricciones, disparadores, cuentas y
datos de ejemplo. No lo vuelva a ejecutar sobre una base que quiera conservar.

### Configurar la conexión

El programa lee las variables de entorno del proceso; no carga un archivo
`.env` automáticamente. En PowerShell, defínalas antes de iniciar el programa:

```powershell
$env:DB_HOST = "localhost"
$env:DB_PORT = "3306"
$env:DB_NAME = "obligatorio"
$env:DB_USER = "<usuario MySQL>"
$env:DB_PASSWORD = "<contraseña MySQL>"
```

La conexión a MySQL y el inicio de sesión dentro de la aplicación son pasos
distintos. La cuenta de aplicación y su rol se validan en la tabla `login`.
Cambie las credenciales de ejemplo del script antes de compartir o usar el
sistema fuera de un entorno de prueba.

### Ejecutar

```powershell
python .\Programa\programa.py
```

---

## Estructura del proyecto

```text
ObligatorioBD/
├── BaseDeDatos/
│   └── DataGrip.sql
├── Documentos/
│   ├── Bitácora.docx
│   ├── Manual de uso.md
│   └── Obligatorio BD - Segundo Semestre 2026.pdf
├── Programa/
│   └── programa.py
└── README.md
```

---

## Seguridad

La aplicación y la base de datos contemplan:

- Consultas SQL parametrizadas en el programa.
- Restricciones de integridad y disparadores MySQL.
- Menús de la aplicación diferenciados según el rol validado en la tabla `login`.
- El script SQL define cuentas MySQL con permisos distintos para sus roles.

Las credenciales incluidas en el script son de ejemplo y deben cambiarse antes
de usar o compartir el sistema fuera de un entorno de prueba.

---

## Datos de prueba

El sistema incluye datos de prueba para:

- Mínimo 6 equipos.
- Al menos 3 fechas disputadas.
- Goles registrados.
- Tarjetas registradas.
- Sanciones activas.

Según lo solicitado en la consigna.

---

## Documentación

El repositorio incluye:

- Script de creación de la base y datos iniciales: `BaseDeDatos/DataGrip.sql`.
- Bitácora del trabajo y manual de uso en `Documentos/`.
- Consigna del obligatorio en `Documentos/`.
