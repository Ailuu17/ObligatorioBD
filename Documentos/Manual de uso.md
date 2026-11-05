# Manual de uso

## Sistema de Gestión del Torneo Interfacultades de Fútbol 5

### 1. Propósito y alcance

Este manual describe el uso del sistema desde un menú de opciones seleccionables. Está dirigido a los administradores del torneo, a los planilleros y a los jugadores.

Los nombres de las opciones que aparecen a continuación son descriptivos: se debe elegir la opción que muestre el menú, sin asumir números fijos.

### 2. Roles

| Rol | Acciones disponibles |
|---|---|
| Administrador | Gestionar jugadores, equipos, planteles, complejos, canchas, partidos y sanciones; consultar reportes. |
| Planillero | Registrar planillas, goles, tarjetas y capitanes; corregir o eliminar goles dentro del plazo permitido; marcar partidos como jugados y consultar partidos y posiciones. |
| Jugador | Consultar los partidos y sus estadísticas. No administra ningún dato del torneo. |

Cada usuario debe ingresar con la cuenta y el rol que le haya asignado la organización. Las opciones disponibles en el menú dependen del rol; si una opción no aparece, se debe solicitar acceso al administrador.

### 3. Preparación y ejecución local

#### Requisitos

- Python instalado.
- Servidor MySQL instalado y en ejecución.
- Acceso a la raíz del proyecto y a una cuenta MySQL con permisos para preparar la base.
- Paquete de Python `mysql-connector-python`.

#### Preparar la base de datos

1. Abra `BaseDeDatos/DataGrip.sql` en un entorno MySQL (por ejemplo MySQL Workbench o DataGrip).
2. Conéctese con una cuenta administradora de MySQL y ejecute el script completo una sola vez sobre una instalación limpia; respete el orden del archivo.
3. El script crea la base `obligatorio`, sus tablas, restricciones, disparadores, usuarios y datos de prueba. Si la base o sus tablas ya existen, la ejecución puede fallar; no vuelva a ejecutarlo sobre datos que quiera conservar. 
4. Desde PowerShell, instale el conector y configure la conexión. El programa lee variables de entorno; no carga un archivo `.env` automáticamente:

```powershell
python -m pip install mysql-connector-python
$env:DB_HOST = "localhost"
$env:DB_PORT = "3306"
$env:DB_NAME = "obligatorio"
$env:DB_USER = "<usuario MySQL>"
$env:DB_PASSWORD = "<contraseña MySQL>"
```

El script SQL contiene credenciales de ejemplo para sus cuentas de base de datos. Cámbielas antes de compartir o utilizar el sistema fuera de un entorno de prueba y no reutilice contraseñas de ejemplo.

#### Advertencia de seguridad

Esta versión es académica, las contraseñas de aplicación se almacenan en texto y se comparan directamente; el código también contiene un valor por defecto para la conexión a MySQL, que usa `root` si no se configura otra cuenta. Las contraseñas ingresadas en la consola no se ocultan.

La aplicación mantiene una sola conexión MySQL para todos los usuarios. El rol autenticado controla el menú, pero no cambia la cuenta MySQL utilizada; por eso los permisos `GRANT` se aplican según `DB_USER`, no según el rol de aplicación.

#### Iniciar el programa

Desde PowerShell, ubicado en la carpeta raíz del proyecto:

```powershell
python .\Programa\programa.py
```

Primero se establece la conexión a MySQL y luego se solicita el correo y la contraseña de una cuenta de aplicación existente en la tabla `login`.

### 4. Navegación por el menú

1. Lea las opciones disponibles en pantalla.
2. Seleccione la opción deseada según el texto e ingrese el número del menú que le corresponde.
3. Cuando se soliciten datos, complételos usando el formato indicado y confirme la operación.
4. Revise el mensaje de resultado. Si se informa un error de validación, corrija el dato solicitado antes de volver a confirmar.
5. Use la opción para volver al menú anterior o salir cuando termine de realizar las acciones que desea.

No cierre la ventana mientras una operación se está guardando. Al salir, espere a que el programa confirme el cierre.

### 5. Funciones del administrador

El menú de administración puede agrupar las opciones de la siguiente manera:

- **Jugadores:** consultar, dar de alta, modificar o dar de baja registros; al crear o editar un jugador, asociarlo con una facultad existente y su tipo (grado, posgrado, docente o funcionario). El programa no tiene un menú para administrar facultades.
- **Torneos:** la edición y los datos de ejemplo se preparan en el script SQL; el programa no tiene un menú para crear o modificar torneos.
- **Equipos y planteles:** crear equipos, inscribirlos en una edición, asignar capitán, agregar jugadores y números de camiseta.
- **Complejos, canchas y turnos:** registrar los lugares y franjas horarias disponibles para programar partidos.
- **Fixture y partidos:** crear y consultar fechas, equipos participantes, cancha, turno y estado del partido.
- **Sanciones:** consultar y gestionar sanciones. MySQL genera automáticamente una suspensión de una fecha por tarjeta roja y por cada grupo de tres amarillas acumuladas en el torneo; las sanciones disciplinarias siguen siendo registradas por el administrador.
- **Reportes:** elegir una consulta, indicar los filtros disponibles (por ejemplo, edición o fecha) y revisar los resultados en pantalla.

#### Orden sugerido para crear una nueva edición

1. Verificar que las facultades y la edición del torneo estén cargadas en la base de datos; el script incluye datos de ejemplo.
2. Registrar los jugadores.
3. Registrar los equipos e inscribirlos en esa edición.
4. Formar los planteles, asignar capitanes y números de camiseta.
5. Registrar complejos, canchas y turnos.
6. Programar los partidos y luego consultar los reportes necesarios.

El sistema rechaza datos que incumplan las reglas del torneo o las relaciones existentes. Por ejemplo, no se puede asociar un equipo o jugador que no esté registrado ni registrar dos veces el mismo enfrentamiento en una edición, aunque esté postergado. Para reprogramar un partido postergado, modifique el registro existente, cambie su fecha, turno o cancha y seleccione el estado `reprogramado`; la fecha del fixture original se conserva.

### 6. Funciones del planillero

Para cargar los datos de un partido:

1. Ingrese al menú de planillero y seleccione la consulta o el registro de planillas.
2. Elija el torneo y el partido disputado que corresponda.
3. Registre los jugadores que participaron, asociándolos al equipo correcto.
4. Registre cada gol con el jugador y el minuto. Indique si fue un autogol cuando el formulario lo permita.
5. Registre las tarjetas amarillas y rojas con el jugador, el color y el minuto.
6. Revise los datos cargados y confirme el registro.

El resultado del partido se calcula automáticamente a partir de los goles ingresados; no se debe cargar manualmente. MySQL impide incluir en la planilla a un jugador suspendido y exige que los goles y las tarjetas correspondan a jugadores que figuren en ella. El programa no valida que el equipo indicado para cada jugador sea uno de los dos equipos del partido ni que el jugador pertenezca a su plantel; el planillero debe comprobarlo antes de registrar la planilla.

Si el partido ya está marcado como jugado, el planillero puede modificar o eliminar goles durante las 48 horas posteriores al fin programado del turno. El programa calcula el plazo con la hora local del equipo donde se ejecuta; MySQL también lo verifica al guardar. Para evitar diferencias entre ambas validaciones, los relojes deben estar sincronizados.

### 7. Sanciones y reglas de los torneos

- Una tarjeta roja genera una suspensión de una fecha, y cada grupo de tres amarillas acumuladas en el torneo genera otra suspensión de una fecha. El conteo no se reinicia al cumplir una suspensión: se genera una nueva al llegar a 3, 6, 9, etc.
- La suspensión comienza en la fecha siguiente a la que corresponde la tarjeta. Si varias sanciones comienzan en la misma fecha, coinciden en esa fecha y no se trasladan a fechas consecutivas.
- Un jugador con una sanción vigente no puede incluirse en la planilla de un partido comprendido por esa sanción.
- El administrador registra manualmente las sanciones disciplinarias y puede ajustar una sanción si se corrige una tarjeta directamente en la base de datos. El sistema no recalcula automáticamente sanciones ante correcciones o eliminaciones manuales de tarjetas.
- Un partido solo puede marcarse como jugado una vez que su día y turno hayan pasado.
- Un partido jugado no se puede eliminar. La corrección de su resultado está limitada a las 48 horas posteriores al fin programado del turno.
- Una vez que el partido está jugado, no se puede cambiar su estado, fecha ni turno.
- Al programar partidos, se deben respetar la disponibilidad de equipos, turnos y canchas. No se debe asignar más de un partido a un equipo en una fecha ni más de un partido a una cancha en el mismo día y turno.

### 8. Reportes disponibles para consultas

El menú de reportes puede ofrecer las consultas previstas para el torneo:

- Tabla de posiciones por edición, ordenada por puntos, diferencia de goles y goles a favor. Se otorgan 3 puntos por victoria, 1 por empate y 0 por derrota.
- Tabla de goleadores.
- Tabla de Fair Play por equipo: 1 punto por tarjeta amarilla y 3 por tarjeta roja; un puntaje menor representa un mejor resultado.
- Promedio de goles por partido, por fecha y para toda la edición.
- Canchas y turnos más utilizados.
- Cantidad de jugadores por facultad y por tipo.
- Jugadores inscriptos en un plantel que nunca figuraron en una planilla.
- Cantidad de sanciones por equipo y por motivo.
- Porcentaje de partidos jugados vs. postergados. El porcentaje restante corresponde a partidos programados o reprogramados.
- Consultas adicionales: jugadores con más sanciones, facultades con más goles y jugador con más tarjetas.

Los resultados dependen de la información cargada y de los filtros seleccionados. Si no hay datos de partidos o planillas, algunos reportes pueden aparecer vacíos o incompletos.

### 9. Errores frecuentes

| Mensaje o situación | Qué hacer |
|---|---|
| No se puede conectar a MySQL | Verifique que el servidor esté activo y que la configuración de conexión sea correcta. |
| No se encuentra el registro seleccionado | Compruebe que el jugador, equipo, torneo, cancha o turno ya esté cargado. |
| No se puede guardar por una regla del torneo | Revise los datos ingresados y las restricciones indicadas en pantalla; por ejemplo, la elegibilidad del jugador o la disponibilidad de la cancha. |
| Un jugador no puede agregarse a la planilla | Confirme que no tenga una sanción vigente. Verifique manualmente que pertenezca a uno de los dos equipos participantes y a su plantel. |
| La opción no está disponible | Verifique que haya ingresado con el rol correcto o solicite permisos al administrador. |

### 10. Cierre de sesión

Seleccione la opción de volver o cerrar sesión y, luego, la opción de salir del programa. No comparta su cuenta ni deje una sesión abierta en un equipo compartido.
