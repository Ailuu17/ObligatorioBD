# Manual de uso

## Sistema de Gestión del Torneo Interfacultades de Fútbol 5

### 1. Propósito y alcance

Este manual describe el uso del sistema desde un menú de opciones seleccionables. Está dirigido a los administradores del torneo, a los planilleros y a los jugadores.

Los nombres de las opciones que aparecen a continuación son descriptivos: se debe elegir la opción que muestre el menú, sin asumir números fijos.

> Verificar los pasos de ejecución y las opciones cuando el programa.py esté implementado.

### 2. Roles

| Rol | Acciones previstas |
|---|---|
| Administrador | Gestionar los datos del torneo, organizar equipos y planteles, programar partidos, administrar sanciones y consultar reportes. |
| Planillero | Consultar los partidos y registrar sus planillas, los jugadores participantes, los goles y las tarjetas. No administra los datos generales del torneo. |
| Jugador | Consultar los partidos y sus estadísticas. No administra ningún dato del torneo. |

Cada usuario debe ingresar con la cuenta y el rol que le haya asignado la organización. Las opciones disponibles en el menú dependen del rol; si una opción no aparece, se debe solicitar acceso al administrador.

### 3. Preparación y ejecución local

#### Requisitos

- Python instalado.
- Servidor MySQL instalado y en ejecución.
- Acceso a la raíz del proyecto y a una cuenta MySQL con permisos para preparar la base.

#### Preparar la base de datos

1. Abra `BaseDeDatos/DataGrip.sql` en un entorno MySQL (por ejemplo MySQL Workbench o DataGrip).
2. Conéctese con una cuenta administradora de MySQL y ejecute el script completo (es importante ejecutarlo en el orden que está escrito, no lo desordenes) una sola vez sobre una instalación limpia.
3. El script crea la base `obligatorio`, sus tablas, restricciones, disparadores, usuarios y datos de prueba. Si la base o sus tablas ya existen, la ejecución puede fallar; no vuelva a ejecutarlo sobre datos que quiera conservar. 
4. Configure la conexión del programa con los datos del servidor y una cuenta autorizada. 

El script SQL contiene credenciales de ejemplo para sus cuentas de base de datos. Cámbielas antes de compartir o utilizar el sistema fuera de un entorno de prueba y no reutilice contraseñas de ejemplo.

#### Iniciar el programa

Desde PowerShell, ubicado en la carpeta raíz del proyecto:

```powershell
python .\Backend\Backend.py
```

El programa mostrará la pantalla inicial.

### 4. Navegación por el menú

1. Lea las opciones disponibles en pantalla.
2. Seleccione la opción deseada según el texto e ingrese el número del menú que le corresponde.
3. Cuando se soliciten datos, complételos usando el formato indicado y confirme la operación.
4. Revise el mensaje de resultado. Si se informa un error de validación, corrija el dato solicitado antes de volver a confirmar.
5. Use la opción para volver al menú anterior o salir cuando termine de realizar las acciones que desea.

No cierre la ventana mientras una operación se está guardando. Al salir, espere a que el programa confirme el cierre.

### 5. Funciones del administrador

El menú de administración puede agrupar las opciones de la siguiente manera:

- **Facultades y jugadores:** consultar, dar de alta, modificar o dar de baja registros; asociar cada jugador con su facultad y tipo (grado, posgrado, docente o funcionario).
- **Torneos:** crear o consultar una edición, indicando año, semestre, fechas y estado (inscripción, en curso o finalizado).
- **Equipos y planteles:** crear equipos, inscribirlos en una edición, asignar capitán, agregar jugadores y números de camiseta.
- **Complejos, canchas y turnos:** registrar los lugares y franjas horarias disponibles para programar partidos.
- **Fixture y partidos:** crear y consultar fechas, equipos participantes, cancha, turno y estado del partido.
- **Sanciones:** consultar las sanciones vigentes y registrar sanciones disciplinarias cuando corresponda.
- **Reportes:** elegir una consulta, indicar los filtros disponibles (por ejemplo, edición o fecha) y revisar los resultados en pantalla.

#### Orden sugerido para crear una nueva edición

1. Registrar las facultades y los jugadores.
2. Crear la edición del torneo.
3. Registrar los equipos e inscribirlos en esa edición.
4. Formar los planteles, asignar capitanes y números de camiseta.
5. Registrar complejos, canchas y turnos.
6. Programar los partidos y luego consultar los reportes necesarios.

El sistema rechaza datos que incumplan las reglas del torneo o las relaciones existentes. Por ejemplo, no se puede asociar un equipo o jugador que no esté registrado, ni programar dos veces el mismo enfrentamiento en una edición, salvo que el anterior haya sido pospuesto.

### 6. Funciones del planillero

Para registrar un partido:

1. Ingrese al menú de planillero y seleccione la consulta o el registro de planillas.
2. Elija el torneo y el partido disputado que corresponda.
3. Registre los jugadores que participaron, asociándolos al equipo correcto.
4. Registre cada gol con el jugador y el minuto. Indique si fue un autogol cuando el formulario lo permita.
5. Registre las tarjetas amarillas y rojas con el jugador, el color y el minuto.
6. Revise los datos cargados y confirme el registro.

El resultado del partido se calcula automaticamente a partir de los goles ingresados; no se debe cargar manualmente. Solo pueden figurar jugadores de los dos equipos del partido que pertenezcan al plantel y no estén suspendidos. Los goles y las tarjetas deben corresponder a jugadores incluidos en la planilla.

### 7. Sanciones y reglas de los torneos

- Una tarjeta roja o la acumulación de tres tarjetas amarillas en la edición genera una suspensión automática de una fecha.
- La suspensión se cumple en la fecha siguiente del torneo. Un jugador suspendido no puede incluirse en la planilla de un partido que se abarque por esa sanción.
- La organización puede registrar sanciones disciplinarias de varias fechas.
- Un partido solo puede marcarse como jugado una vez que su día y turno hayan pasado.
- Un partido jugado no se puede eliminar. La corrección de su resultado está limitada a las 48 horas posteriores a su disputa.
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
- Porcentaje de partidos jugados frente a postergados.
- Consultas adicionales: jugadores con más sanciones, facultades con más goles y jugador con más tarjetas.

Los resultados dependen de la información cargada y de los filtros seleccionados. Si no hay datos de partidos o planillas, algunos reportes pueden aparecer vacíos o incompletos.

### 9. Errores frecuentes

| Mensaje o situación | Qué hacer |
|---|---|
| No se puede conectar a MySQL | Verifique que el servidor esté activo y que la configuración de conexión sea correcta. |
| No se encuentra el registro seleccionado | Compruebe que el jugador, equipo, torneo, cancha o turno ya esté cargado. |
| No se puede guardar por una regla del torneo | Revise los datos ingresados y las restricciones indicadas en pantalla; por ejemplo, la elegibilidad del jugador o la disponibilidad de la cancha. |
| Un jugador no puede agregarse a la planilla | Confirme que integre uno de los dos planteles participantes y que no esté suspendido. |
| La opción no está disponible | Verifique que haya ingresado con el rol correcto o solicite permisos al administrador. |

### 10. Cierre de sesión

Seleccione la opción de volver o cerrar sesión y, luego, la opción de salir del programa. No comparta su cuenta ni deje una sesión abierta en un equipo compartido.
