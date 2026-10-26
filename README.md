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
- Gestionar sanciones automáticas y disciplinarias.
- Generar reportes estadísticos para la organización del torneo.

---

## Arquitectura

### Backend
- Python
- API REST

### Base de Datos
- MySQL

### Frontend
- (Falta elegir)

### Herramientas
- Git
- GitHub
- Docker 
- Docker Compose 

> La consigna no permite utilizar ORM.

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
- Registrar tarjetas.

No posee permisos de administración general.

---

## Funcionalidades principales

### Gestión de Jugadores

- Alta de jugadores.
- Modificación de datos.
- Baja lógica o física (según implementación).
- Asociación a facultades.

### Gestión de Equipos

- Creación de equipos.
- Asignación de capitán.
- Administración de planteles.
- Control de restricciones del torneo.

### Gestión del Torneo

- Inscripción de equipos.
- Programación de fechas.
- Gestión de partidos.
- Control de disponibilidad de canchas y horarios.

### Registro de Partidos

- Registro de jugadores participantes.
- Registro de goles.
- Registro de tarjetas.
- Cálculo automático del resultado.

### Gestión de Sanciones

- Suspensiones por tarjeta roja.
- Suspensiones por acumulación de amarillas.
- Sanciones disciplinarias definidas por la organización.

### Reportes

- Tabla de posiciones.
- Tabla de goleadores.
- Ranking Fair Play.
- Promedio de goles.
- Uso de canchas y turnos.
- Estadísticas de jugadores por facultad.
- Jugadores nunca convocados.
- Sanciones por equipo y motivo.
- Porcentaje de partidos jugados, postergados y cancelados.
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

### 1. Clonar el repositorio

```bash
git clone https://github.com/usuario/repositorio.git
cd repositorio
```

### 2. Crear la base de datos

```sql
CREATE DATABASE torneo_interfacultades;
```

### 3. Ejecutar scripts SQL

```bash
/database/schema.sql
/database/data.sql
```

### 4. Configurar variables de entorno

Crear archivo `.env`

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=torneo_interfacultades
DB_USER=root
DB_PASSWORD=password
```

### 5. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 6. Ejecutar la aplicación

```bash
python app.py
```

---

## Estructura del proyecto

```Txt
ObligatorioBD/
│
├── backend/
│   ├── 
│   ├── 
│   ├── 
│   ├── 
│   └── 
│
├── frontend/
│
├── BaseDeDatos/
│   ├── 
│   ├── 
│   ├── 
│   └── 
│
├── docs/
│   ├── 
│   ├── 
│   └── 
│
├── 
├── 
└── README.md
```

---

## Seguridad

La aplicación contempla:

- Validaciones en frontend.
- Validaciones en backend.
- Restricciones de integridad en la base de datos.
- Gestión de permisos por rol.
- Usuarios de base de datos con privilegios diferenciados.

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

- Script completo de creación de base de datos.
- Datos iniciales.
- Informe.
- Bitácora del trabajo.
- Manual de instalación y ejecución.