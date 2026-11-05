# -*- coding: utf-8 -*-
"""
================================================================================
                    SISTEMA DE GESTIÓN TORNEO DE FÚTBOL UCU
                    Base de Datos 1 - Obligatorio BD
================================================================================
Integrantes: Lara Canío y Aileen Waller

Aclaraciones:
El código fue realizado por Antigravity pero con las idicaciones que nosotras le fuimos dando.
A medida que se iba generando el código lo fuimos revisando y modificando para que cumpla con la
consigna correctamente, para que los cálculos funcionen y devuelvan lo esperado, y aprovechamos
que la IA es mucho más eficiente que un programador promedio para generar el código (además
considerando que no tenemos conocimientos avanzados de programación y que lógicamente programar todo
esto a mano, corregirlo y revisarlo nos habría llevado semanas). Obviamente esto no significa que
no entendamos el código. Lo entendemos a la perfección dadas las constantes correcciones que le
fuimos haciendo y esperamos demostrarlo en la defensa oral del proyecto.

Módulos y Roles implementados:
  1. Administrador:
     - Alta, Baja y Modificación de Jugadores (Validación CI de 8 dígitos y fecha MySQL)
     - Alta, Baja y Modificación de Equipos
     - Alta, Baja y Modificación de Complejos
     - Alta, Baja y Modificación de Canchas
     - Alta, Baja y Modificación de Partidos (Verificación de turno existente, local != visitante)
     - Alta, Baja y Modificación de Sanciones
     - Gestión de Planteles (Inscripción de equipos, asignación y baja de jugadores)
     - Reportes y Estadísticas Oficiales
  2. Planillero:
     - Registrar Planilla de Partido
     - Registrar Gol (Restricción de 48hs posteriores al partido)
     - Registrar Tarjeta
     - Registrar Capitán de Partido
     - Finalizar Partido (Solo se puede marcar como jugado si ya pasó la fecha y hora)
  3. Jugador:
     - Solo Consultas: Partidos (lista completa desde jugados hasta programados con resultado),
       Goles, Tarjetas y Sanciones.

SEGURIDAD Y PROTECCIÓN:
  - 100% Consultas preparadas / parametrizadas (%s) contra SQL Injection.
  - Formateo automático de fechas a formato MySQL (YYYY-MM-DD).
  - Validación de existencia de turnos y clave foráneas.
  - Validación de que el resultado solo sea modificable durante 48 horas tras jugarse.
  - Validación de que un partido solo pueda marcarse como jugado si ya finalizó.
================================================================================
"""

import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta, time, date

# ==============================================================================
# CONFIGURACIÓN DE CONEXIÓN A LA BASE DE DATOS
# ==============================================================================
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "Luc14n4.C0l37151107"),
    "database": os.environ.get("DB_NAME", "obligatorio")
}


def obtener_conexion():
    """Establece y retorna la conexión a la base de datos."""
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        return conexion
    except Error as err:
        print(f"\n[ERROR DE CONEXIÓN A MYSQL]: {err}")
        opc = input("¿Desea ingresar las credenciales de conexión manualmente? (s/n): ").strip().lower()
        if opc == 's':
            DB_CONFIG["host"] = input("Host (Enter para 'localhost'): ").strip() or "localhost"
            DB_CONFIG["user"] = input("Usuario (Enter para 'root'): ").strip() or "root"
            DB_CONFIG["password"] = input("Contraseña: ")
            DB_CONFIG["database"] = input("Base de datos (Enter para 'obligatorio'): ").strip() or "obligatorio"
            try:
                conexion = mysql.connector.connect(**DB_CONFIG)
                print("¡Conexión establecida exitosamente!")
                return conexion
            except Error as err2:
                print(f"[ERROR]: Falló la conexión: {err2}")
        return None


# ==============================================================================
# FUNCIONES AUXILIARES: VALIDACIONES, ENTRADA DE DATOS Y FECHAS
# ==============================================================================
def imprimir_titulo(texto):
    print("\n" + "=" * 70)
    print(f" {texto.center(68)} ")
    print("=" * 70)


def imprimir_subtitulo(texto):
    print("\n" + "-" * 55)
    print(f" {texto} ")
    print("-" * 55)


def imprimir_tabla(encabezados, filas):
    """Muestra una lista de tuplas formateada como tabla ASCII dinámica."""
    if not filas:
        print("\n [No se encontraron registros]")
        return

    str_filas = [[str(item) if item is not None else "NULL" for item in fila] for fila in filas]
    anchos = [len(str(h)) for h in encabezados]

    for fila in str_filas:
        for i, val in enumerate(fila):
            anchos[i] = max(anchos[i], len(val))

    separador = "+-" + "-+-".join("-" * w for w in anchos) + "-+"
    formato_fila = "| " + " | ".join(f"{{:<{w}}}" for w in anchos) + " |"

    print("\n" + separador)
    print(formato_fila.format(*encabezados))
    print(separador)
    for fila in str_filas:
        print(formato_fila.format(*fila))
    print(separador + "\n")


def pedir_ci(mensaje="Cédula de Identidad (8 dígitos)"):
    """
    Solicita una cédula de identidad y verifica que tenga exactamente 8 dígitos numéricos.
    """
    while True:
        entrada = input(f"{mensaje}: ").strip()
        if entrada.isdigit() and len(entrada) == 8:
            return int(entrada)
        print("  -> Error: La cédula debe tener exactamente 8 dígitos numéricos (ej: 12345678).")


def formatear_fecha(entrada):
    """
    Parsea una fecha ingresada en múltiples formatos habituales
    y la formatea al formato estándar que MySQL entiende (YYYY-MM-DD).
    """
    formatos = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%y", "%d-%m-%y"]
    for fmt in formatos:
        try:
            return datetime.strptime(entrada.strip(), fmt).date().strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def pedir_fecha(mensaje, opcional=False):
    """
    Solicita una fecha por consola y la retorna garantizando el formato YYYY-MM-DD para MySQL.
    """
    while True:
        entrada = input(f"{mensaje} (DD/MM/AAAA o AAAA-MM-DD): ").strip()
        if opcional and not entrada:
            return None
        fecha_mysql = formatear_fecha(entrada)
        if fecha_mysql:
            return fecha_mysql
        print("  -> Error: Formato de fecha no válido. Ingrese una fecha válida (ej: 15/09/2026 o 2026-09-15).")


def pedir_entero(mensaje, minimo=None, maximo=None, sugerido=None, opcional=False):
    """Solicita un número entero por consola con validación de rango opcional."""
    sug_txt = f" [{sugerido}]" if sugerido is not None else ""
    while True:
        entrada = input(f"{mensaje}{sug_txt}: ").strip()
        if opcional and entrada == "":
            return None
        if sugerido is not None and entrada == "":
            return sugerido
        try:
            val = int(entrada)
            if minimo is not None and val < minimo:
                print(f"  -> El valor debe ser mayor o igual a {minimo}.")
                continue
            if maximo is not None and val > maximo:
                print(f"  -> El valor debe ser menor o igual a {maximo}.")
                continue
            return val
        except ValueError:
            print("  -> Ingrese un número entero válido.")


def pedir_texto(mensaje, opcional=False, longitud_maxima=None):
    """Solicita texto validando longitud y obligatoriedad."""
    while True:
        entrada = input(f"{mensaje}: ").strip()
        if not entrada and not opcional:
            print("  -> Este campo es obligatorio.")
            continue
        if longitud_maxima and len(entrada) > longitud_maxima:
            print(f"  -> El texto no puede superar {longitud_maxima} caracteres.")
            continue
        return entrada


def pedir_opcion(mensaje, opciones_validas):
    """Solicita al usuario elegir entre una lista de opciones válidas."""
    opcs_str = "/".join(opciones_validas)
    while True:
        entrada = input(f"{mensaje} ({opcs_str}): ").strip().lower()
        for opc in opciones_validas:
            if entrada == opc.lower():
                return opc
        print(f"  -> Opción inválida. Opciones disponibles: {opcs_str}")


def obtener_siguiente_id(conexion, tabla, columna):
    """Obtiene el siguiente ID correlativo para tablas con clave numérica manual."""
    cursor = conexion.cursor()
    cursor.execute(f"SELECT COALESCE(MAX(`{columna}`), 0) + 1 FROM `{tabla}`")
    siguiente = cursor.fetchone()[0]
    cursor.close()
    return siguiente


def parse_fecha_hora(p_dia, t_hora):
    """Convierte el par (p_dia, t_hora) de MySQL en un objeto datetime de Python."""
    if isinstance(p_dia, str):
        p_dia = datetime.strptime(p_dia, "%Y-%m-%d").date()
    elif isinstance(p_dia, datetime):
        p_dia = p_dia.date()

    if isinstance(t_hora, timedelta):
        return datetime.combine(p_dia, time.min) + t_hora
    elif isinstance(t_hora, time):
        return datetime.combine(p_dia, t_hora)
    elif isinstance(t_hora, str):
        partes = [int(p) for p in t_hora.split(":")]
        return datetime.combine(p_dia, time(partes[0], partes[1], partes[2] if len(partes) > 2 else 0))
    return datetime.combine(p_dia, time(0, 0, 0))


# ==============================================================================
# CAPA DE ACCESO A DATOS (SEGURO CONTRA SQL INJECTION)
# ==============================================================================
def ejecutar_consulta(conexion, sql, params=()):
    """
    Ejecuta una consulta SELECT parametrizada.
    Retorna (encabezados, filas).
    """
    cursor = conexion.cursor()
    try:
        cursor.execute(sql, params)
        encabezados = [desc[0] for desc in cursor.description] if cursor.description else []
        filas = cursor.fetchall()
        return encabezados, filas
    except Error as err:
        print(f"\n[ERROR BD]: {err.msg}")
        return [], []
    finally:
        cursor.close()


def ejecutar_dml(conexion, sql, params=(), mensaje_exito="Operación completada con éxito."):
    """
    Ejecuta una sentencia INSERT / UPDATE / DELETE parametrizada con COMMIT.
    Captura y exhibe amigablemente los errores de TRIGGERS, CHECKS y FOREIGN KEYS.
    """
    cursor = conexion.cursor()
    try:
        cursor.execute(sql, params)
        conexion.commit()
        print(f"\n✓ {mensaje_exito}")
        return True
    except Error as err:
        conexion.rollback()
        print(f"\n✗ [ERROR DE BASE DE DATOS]: {err.msg}")
        return False
    finally:
        cursor.close()


# ==============================================================================
# REGLAS DE NEGOCIO TEMPORALES
# ==============================================================================
def verificar_partido_ya_paso(conexion, id_partido, id_torneo):
    """
    Regla: Un partido solo se puede marcar como jugado si ya pasó.
    Verifica que la fecha y hora de finalización del partido sean anteriores al momento actual.
    """
    sql = """
        SELECT p.dia, t.hora_fin, p.estado
        FROM partido p
        JOIN turno t ON p.id_turno = t.id_turno
        WHERE p.id_partido = %s AND p.id_torneo = %s
    """
    _, rows = ejecutar_consulta(conexion, sql, (id_partido, id_torneo))
    if not rows:
        print("✗ Partido no encontrado.")
        return False

    p_dia, hora_fin, estado_act = rows[0]
    dt_fin = parse_fecha_hora(p_dia, hora_fin)
    ahora = datetime.now()

    if ahora < dt_fin:
        print(f"\n✗ RESTRICCIÓN TEMPORAL:")
        print(f"  El partido NO se puede marcar como 'jugado' porque aún no se ha disputado / finalizado.")
        print(f"  Fecha y hora programada de fin: {dt_fin.strftime('%d/%m/%Y %H:%M')}")
        print(f"  Fecha y hora actual del sistema: {ahora.strftime('%d/%m/%Y %H:%M')}")
        return False

    return True


def verificar_resultado_es_modificable(conexion, id_partido, id_torneo):
    """
    Regla: El resultado solo sea modificable durante las 48 horas desde que se jugó.
    Si el partido está en estado 'jugado' y pasaron más de 48 horas desde su finalización,
    bloquea la modificación de goles / resultado.
    """
    sql = """
        SELECT p.estado, p.dia, t.hora_fin
        FROM partido p
        JOIN turno t ON p.id_turno = t.id_turno
        WHERE p.id_partido = %s AND p.id_torneo = %s
    """
    _, rows = ejecutar_consulta(conexion, sql, (id_partido, id_torneo))
    if not rows:
        print("✗ Partido no encontrado.")
        return False

    estado, p_dia, hora_fin = rows[0]
    if estado == 'jugado':
        dt_fin = parse_fecha_hora(p_dia, hora_fin)
        ahora = datetime.now()
        horas_transcurridas = (ahora - dt_fin).total_seconds() / 3600.0

        if horas_transcurridas > 48:
            print(f"\n✗ RESTRICCIÓN DE SEGURIDAD (PLAZO 48 HORAS EXPIRADO):")
            print(f"  El resultado solo es modificable durante las 48 horas posteriores a disputarse el partido.")
            print(f"  Fecha de juego: {dt_fin.strftime('%d/%m/%Y %H:%M')}")
            print(f"  Han transcurrido {horas_transcurridas:.1f} horas desde que finalizó (Límite máximo: 48 horas).")
            return False

    return True


def pedir_turno_existente(conexion, mensaje="ID Turno"):
    """
    Verificación obligatoria: Confirma que el turno exista en la BD antes de registrar o editar un partido.
    """
    sql = "SELECT id_turno, hora_inicio, hora_fin FROM turno ORDER BY hora_inicio"
    _, turnos = ejecutar_consulta(conexion, sql)
    print("\nTurnos registrados en la base de datos:")
    for t_id, h_ini, h_fin in turnos:
        print(f"  Turno {t_id}: de {h_ini} a {h_fin}")

    ids_validos = [t[0] for t in turnos]
    while True:
        t_sel = pedir_entero(mensaje)
        if t_sel in ids_validos:
            return t_sel
        print(f"  -> Error: El turno {t_sel} NO existe en la base de datos. Elija uno de la lista.")


# ==============================================================================
# AUTENTICACIÓN / LOGIN CON PROTECCIÓN SQL INJECTION
# ==============================================================================
def autenticar_usuario(conexion):
    """
    Inicia sesión verificando credenciales en la tabla 'login'.
    Utiliza consultas parametrizadas (%s) para neutralizar completamente SQL Injection.
    """
    imprimir_titulo("INICIO DE SESIÓN - TORNEO UCU")
    print("Ingrese sus credenciales registradas en la base de datos.")

    correo = input("Correo electrónico: ").strip()
    contrasena = input("Contraseña: ").strip()

    # Consulta parametrizada
    sql = """
        SELECT correo, rol
        FROM login
        WHERE correo = %s
          AND contraseña = %s
    """
    encabezados, filas = ejecutar_consulta(conexion, sql, (correo, contrasena))

    if filas:
        correo_logueado, rol = filas[0]
        print(f"\n✓ Inicio de sesión exitoso. Usuario: [{correo_logueado}] | Rol: [{rol.upper()}]")
        return correo_logueado, rol
    else:
        print("\n✗ Correo o contraseña incorrectos.")
        return None, None


# ==============================================================================
# MÓDULO ADMINISTRADOR: JUGADORES, EQUIPOS, COMPLEJOS, CANCHAS, PARTIDOS, SANCIONES, PLANTELES Y REPORTES
# ==============================================================================
def admin_alta_jugador(conexion):
    print("\n--- Alta de Jugador ---")
    ci = pedir_ci("Cédula de Identidad (exactamente 8 dígitos)")
    nombre = pedir_texto("Nombre", longitud_maxima=30)
    apellido = pedir_texto("Apellido", longitud_maxima=40)
    email = pedir_texto("Email", longitud_maxima=70)
    fnac = pedir_fecha("Fecha de Nacimiento")

    _, facs = ejecutar_consulta(conexion, "SELECT id_facultad, nombre FROM facultad")
    print("\nFacultades registradas:")
    for f_id, f_nom in facs:
        print(f"  {f_id} - {f_nom}")
    id_facultad = pedir_entero("ID Facultad asignada")
    tipo = pedir_opcion("Tipo de integrante", ["grado", "posgrado", "docente", "funcionario"])

    sql = """
        INSERT INTO jugador (ci, nombre, apellido, email, fecha_nacimiento, id_facultad, tipo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    ejecutar_dml(conexion, sql, (ci, nombre, apellido, email, fnac, id_facultad, tipo),
                 "Jugador dado de alta exitosamente.")


def admin_baja_jugador(conexion):
    print("\n--- Baja de Jugador ---")
    ci = pedir_ci("Cédula del jugador a eliminar (8 dígitos)")
    confirmar = input(f"¿Confirma dar de baja al jugador con CI {ci}? (s/n): ").strip().lower()
    if confirmar == 's':
        sql = "DELETE FROM jugador WHERE ci = %s"
        ejecutar_dml(conexion, sql, (ci,), "Jugador eliminado exitosamente.")


def admin_modificacion_jugador(conexion):
    print("\n--- Modificación de Jugador ---")
    ci = pedir_ci("Cédula del jugador a modificar (8 dígitos)")
    sql_sel = "SELECT ci, nombre, apellido, email, fecha_nacimiento, id_facultad, tipo FROM jugador WHERE ci = %s"
    _, rows = ejecutar_consulta(conexion, sql_sel, (ci,))
    if not rows:
        print("✗ Jugador no encontrado.")
        return

    j = rows[0]
    print(f"Modificando jugador: {j[1]} {j[2]} (Presione Enter para mantener valor actual)")
    nombre = input(f"Nombre [{j[1]}]: ").strip() or j[1]
    apellido = input(f"Apellido [{j[2]}]: ").strip() or j[2]
    email = input(f"Email [{j[3]}]: ").strip() or j[3]
    fnac_in = input(f"Fecha Nacimiento [{j[4]}]: ").strip()
    fnac = formatear_fecha(fnac_in) if fnac_in else str(j[4])
    fac_in = input(f"ID Facultad [{j[5]}]: ").strip()
    id_facultad = int(fac_in) if fac_in else j[5]
    tipo_in = input(f"Tipo (grado/posgrado/docente/funcionario) [{j[6]}]: ").strip().lower()
    tipo = tipo_in if tipo_in in ['grado', 'posgrado', 'docente', 'funcionario'] else j[6]

    sql = """
        UPDATE jugador
        SET nombre = %s, apellido = %s, email = %s, fecha_nacimiento = %s, id_facultad = %s, tipo = %s
        WHERE ci = %s
    """
    ejecutar_dml(conexion, sql, (nombre, apellido, email, fnac, id_facultad, tipo, ci),
                 "Jugador modificado exitosamente.")


def admin_consultar_jugadores(conexion):
    sql = """
        SELECT j.ci AS CI, j.nombre AS Nombre, j.apellido AS Apellido,
               j.email AS Email, j.fecha_nacimiento AS 'F. Nac.',
               f.nombre AS Facultad, j.tipo AS Tipo
        FROM jugador j
        JOIN facultad f ON j.id_facultad = f.id_facultad
        ORDER BY j.apellido, j.nombre
    """
    headers, rows = ejecutar_consulta(conexion, sql)
    imprimir_tabla(headers, rows)


def menu_gestion_jugadores(conexion):
    while True:
        imprimir_subtitulo("GESTIÓN DE JUGADORES (ABM)")
        print("1. Alta Jugador (CI 8 dígitos)")
        print("2. Baja Jugador")
        print("3. Modificación Jugador")
        print("4. Consultar / Listar Jugadores")
        print("0. Volver")
        opc = input("Seleccione una opción: ").strip()
        if opc == "1":
            admin_alta_jugador(conexion)
        elif opc == "2":
            admin_baja_jugador(conexion)
        elif opc == "3":
            admin_modificacion_jugador(conexion)
        elif opc == "4":
            admin_consultar_jugadores(conexion)
        elif opc == "0":
            break


def admin_alta_equipo(conexion):
    print("\n--- Alta de Equipo ---")
    sug_id = obtener_siguiente_id(conexion, "equipo", "id_equipo")
    id_equipo = pedir_entero("ID Equipo", sugerido=sug_id)
    nombre = pedir_texto("Nombre del equipo", longitud_maxima=70)

    _, facs = ejecutar_consulta(conexion, "SELECT id_facultad, nombre FROM facultad")
    print("\nFacultades registradas:")
    for f_id, f_nom in facs:
        print(f"  {f_id} - {f_nom}")
    id_facultad = pedir_entero("ID Facultad asignada")

    sql = "INSERT INTO equipo (id_equipo, nombre, id_facultad) VALUES (%s, %s, %s)"
    ejecutar_dml(conexion, sql, (id_equipo, nombre, id_facultad), "Equipo registrado con éxito.")


def admin_baja_equipo(conexion):
    print("\n--- Baja de Equipo ---")
    id_equipo = pedir_entero("ID Equipo a eliminar")
    confirmar = input(f"¿Confirma dar de baja el equipo {id_equipo}? (s/n): ").strip().lower()
    if confirmar == 's':
        sql = "DELETE FROM equipo WHERE id_equipo = %s"
        ejecutar_dml(conexion, sql, (id_equipo,), "Equipo eliminado con éxito.")


def admin_modificacion_equipo(conexion):
    print("\n--- Modificación de Equipo ---")
    id_equipo = pedir_entero("ID Equipo a modificar")
    _, rows = ejecutar_consulta(conexion, "SELECT id_equipo, nombre, id_facultad FROM equipo WHERE id_equipo = %s", (id_equipo,))
    if not rows:
        print("✗ Equipo no encontrado.")
        return
    eq = rows[0]
    nombre = input(f"Nuevo Nombre [{eq[1]}]: ").strip() or eq[1]
    fac_in = input(f"Nuevo ID Facultad [{eq[2]}]: ").strip()
    id_facultad = int(fac_in) if fac_in else eq[2]

    sql = "UPDATE equipo SET nombre = %s, id_facultad = %s WHERE id_equipo = %s"
    ejecutar_dml(conexion, sql, (nombre, id_facultad, id_equipo), "Equipo modificado con éxito.")


def admin_consultar_equipos(conexion):
    sql = """
        SELECT e.id_equipo AS ID, e.nombre AS Equipo, f.nombre AS Facultad
        FROM equipo e
        JOIN facultad f ON e.id_facultad = f.id_facultad
        ORDER BY e.id_equipo
    """
    headers, rows = ejecutar_consulta(conexion, sql)
    imprimir_tabla(headers, rows)


def menu_gestion_equipos(conexion):
    while True:
        imprimir_subtitulo("GESTIÓN DE EQUIPOS (ABM)")
        print("1. Alta Equipo")
        print("2. Baja Equipo")
        print("3. Modificación Equipo")
        print("4. Consultar / Listar Equipos")
        print("0. Volver")
        opc = input("Seleccione una opción: ").strip()
        if opc == "1":
            admin_alta_equipo(conexion)
        elif opc == "2":
            admin_baja_equipo(conexion)
        elif opc == "3":
            admin_modificacion_equipo(conexion)
        elif opc == "4":
            admin_consultar_equipos(conexion)
        elif opc == "0":
            break


def admin_alta_complejo(conexion):
    print("\n--- Alta de Complejo ---")
    sug_id = obtener_siguiente_id(conexion, "complejo", "id_complejo")
    id_complejo = pedir_entero("ID Complejo", sugerido=sug_id)
    nombre = pedir_texto("Nombre del complejo", longitud_maxima=70)
    direccion = pedir_texto("Dirección", longitud_maxima=100)
    depto = pedir_texto("Departamento", longitud_maxima=20)

    sql = "INSERT INTO complejo (id_complejo, nombre, dirección, departamento) VALUES (%s, %s, %s, %s)"
    ejecutar_dml(conexion, sql, (id_complejo, nombre, direccion, depto), "Complejo registrado con éxito.")


def admin_baja_complejo(conexion):
    print("\n--- Baja de Complejo ---")
    id_complejo = pedir_entero("ID Complejo a eliminar")
    confirmar = input(f"¿Confirma dar de baja el complejo {id_complejo}? (s/n): ").strip().lower()
    if confirmar == 's':
        sql = "DELETE FROM complejo WHERE id_complejo = %s"
        ejecutar_dml(conexion, sql, (id_complejo,), "Complejo eliminado con éxito.")


def admin_modificacion_complejo(conexion):
    print("\n--- Modificación de Complejo ---")
    id_complejo = pedir_entero("ID Complejo a modificar")
    _, rows = ejecutar_consulta(conexion, "SELECT id_complejo, nombre, dirección, departamento FROM complejo WHERE id_complejo = %s", (id_complejo,))
    if not rows:
        print("✗ Complejo no encontrado.")
        return
    c = rows[0]
    nombre = input(f"Nombre [{c[1]}]: ").strip() or c[1]
    direccion = input(f"Dirección [{c[2]}]: ").strip() or c[2]
    depto = input(f"Departamento [{c[3]}]: ").strip() or c[3]

    sql = "UPDATE complejo SET nombre = %s, dirección = %s, departamento = %s WHERE id_complejo = %s"
    ejecutar_dml(conexion, sql, (nombre, direccion, depto, id_complejo), "Complejo actualizado con éxito.")


def admin_consultar_complejos(conexion):
    sql = "SELECT id_complejo AS ID, nombre AS Complejo, dirección AS Dirección, departamento AS Dpto FROM complejo ORDER BY id_complejo"
    headers, rows = ejecutar_consulta(conexion, sql)
    imprimir_tabla(headers, rows)


def menu_gestion_complejos(conexion):
    while True:
        imprimir_subtitulo("GESTIÓN DE COMPLEJOS (ABM)")
        print("1. Alta Complejo")
        print("2. Baja Complejo")
        print("3. Modificación Complejo")
        print("4. Consultar / Listar Complejos")
        print("0. Volver")
        opc = input("Seleccione una opción: ").strip()
        if opc == "1":
            admin_alta_complejo(conexion)
        elif opc == "2":
            admin_baja_complejo(conexion)
        elif opc == "3":
            admin_modificacion_complejo(conexion)
        elif opc == "4":
            admin_consultar_complejos(conexion)
        elif opc == "0":
            break


def admin_alta_cancha(conexion):
    print("\n--- Alta de Cancha ---")
    admin_consultar_complejos(conexion)
    nombre_cancha = pedir_texto("Nombre de la cancha (ej: Cancha A)", longitud_maxima=70)
    id_complejo = pedir_entero("ID Complejo al que pertenece")
    superficie = pedir_opcion("Superficie", ["sintético", "parquet"])
    techada_opc = pedir_opcion("¿Es techada?", ["si", "no"])
    techada = True if techada_opc == "si" else False

    sql = "INSERT INTO cancha (nombre_cancha, id_complejo, superficie, techada) VALUES (%s, %s, %s, %s)"
    ejecutar_dml(conexion, sql, (nombre_cancha, id_complejo, superficie, techada), "Cancha registrada con éxito.")


def admin_baja_cancha(conexion):
    print("\n--- Baja de Cancha ---")
    nombre_cancha = pedir_texto("Nombre de la cancha a eliminar")
    id_complejo = pedir_entero("ID Complejo")
    confirmar = input(f"¿Confirma dar de baja la cancha '{nombre_cancha}' del complejo {id_complejo}? (s/n): ").strip().lower()
    if confirmar == 's':
        sql = "DELETE FROM cancha WHERE nombre_cancha = %s AND id_complejo = %s"
        ejecutar_dml(conexion, sql, (nombre_cancha, id_complejo), "Cancha eliminada con éxito.")


def admin_modificacion_cancha(conexion):
    print("\n--- Modificación de Cancha ---")
    nombre_cancha = pedir_texto("Nombre de la cancha a modificar")
    id_complejo = pedir_entero("ID Complejo")
    _, rows = ejecutar_consulta(conexion, "SELECT superficie, techada FROM cancha WHERE nombre_cancha = %s AND id_complejo = %s", (nombre_cancha, id_complejo))
    if not rows:
        print("✗ Cancha no encontrada.")
        return
    sup_act, tech_act = rows[0]
    superficie = pedir_opcion(f"Superficie [{sup_act}]", ["sintético", "parquet"])
    techada_opc = pedir_opcion(f"¿Es techada? [{'si' if tech_act else 'no'}]", ["si", "no"])
    techada = True if techada_opc == "si" else False

    sql = "UPDATE cancha SET superficie = %s, techada = %s WHERE nombre_cancha = %s AND id_complejo = %s"
    ejecutar_dml(conexion, sql, (superficie, techada, nombre_cancha, id_complejo), "Cancha modificada con éxito.")


def admin_consultar_canchas(conexion):
    sql = """
        SELECT ca.nombre_cancha AS Cancha, c.id_complejo AS 'ID Comp.', c.nombre AS Complejo,
               ca.superficie AS Superficie, IF(ca.techada = 1, 'Sí', 'No') AS Techada
        FROM cancha ca
        JOIN complejo c ON ca.id_complejo = c.id_complejo
        ORDER BY c.id_complejo, ca.nombre_cancha
    """
    headers, rows = ejecutar_consulta(conexion, sql)
    imprimir_tabla(headers, rows)


def menu_gestion_canchas(conexion):
    while True:
        imprimir_subtitulo("GESTIÓN DE CANCHAS (ABM)")
        print("1. Alta Cancha")
        print("2. Baja Cancha")
        print("3. Modificación Cancha")
        print("4. Consultar / Listar Canchas")
        print("0. Volver")
        opc = input("Seleccione una opción: ").strip()
        if opc == "1":
            admin_alta_cancha(conexion)
        elif opc == "2":
            admin_baja_cancha(conexion)
        elif opc == "3":
            admin_modificacion_cancha(conexion)
        elif opc == "4":
            admin_consultar_canchas(conexion)
        elif opc == "0":
            break


def admin_alta_partido(conexion):
    print("\n--- Alta de Partido (Programar Encuentro) ---")
    id_torneo = pedir_entero("ID Torneo")
    sug_partido = obtener_siguiente_id(conexion, "partido", "id_partido")
    id_partido = pedir_entero("ID Partido", sugerido=sug_partido)
    nro_fecha = pedir_entero("Número de Fecha del fixture", minimo=1)

    # Validar que local != visitante
    id_local = pedir_entero("ID Equipo Local")
    while True:
        id_visitante = pedir_entero("ID Equipo Visitante")
        if id_visitante != id_local:
            break
        print("  -> Error: El equipo local debe ser distinto al equipo visitante.")

    # REGLAS DEL TORNEO (PDF PÁGS. 1-2):
    # 1. Ambos equipos deben pertenecer a la misma edición del torneo
    sql_check_et = "SELECT id_equipo FROM equipo_torneo WHERE id_torneo = %s AND id_equipo = %s"
    _, r_loc = ejecutar_consulta(conexion, sql_check_et, (id_torneo, id_local))
    if not r_loc:
        print(f"✗ El equipo local ({id_local}) no está inscripto en la edición {id_torneo} del torneo.")
        return

    _, r_vis = ejecutar_consulta(conexion, sql_check_et, (id_torneo, id_visitante))
    if not r_vis:
        print(f"✗ El equipo visitante ({id_visitante}) no está inscripto en la edición {id_torneo} del torneo.")
        return

    # 2. Ambos equipos deben tener al menos 5 jugadores en su plantel
    sql_check_min = "SELECT COUNT(*) FROM equipo_jugador_torneo WHERE id_torneo = %s AND id_equipo = %s"
    _, r_c_loc = ejecutar_consulta(conexion, sql_check_min, (id_torneo, id_local))
    cant_loc = r_c_loc[0][0] if r_c_loc else 0
    if cant_loc < 5:
        print(f"✗ El equipo local ({id_local}) tiene {cant_loc} jugadores en su plantel (mínimo reglamentario: 5).")
        return

    _, r_c_vis = ejecutar_consulta(conexion, sql_check_min, (id_torneo, id_visitante))
    cant_vis = r_c_vis[0][0] if r_c_vis else 0
    if cant_vis < 5:
        print(f"✗ El equipo visitante ({id_visitante}) tiene {cant_vis} jugadores en su plantel (mínimo reglamentario: 5).")
        return

    # 3. Ningún equipo juegue más de un partido en la misma fecha del torneo
    sql_fecha = """
        SELECT id_partido FROM partido
        WHERE id_torneo = %s AND numero_fecha = %s
          AND (id_equipo_local IN (%s, %s) OR id_equipo_visitante IN (%s, %s))
          AND estado != 'postergado'
    """
    _, r_f = ejecutar_consulta(conexion, sql_fecha, (id_torneo, nro_fecha, id_local, id_visitante, id_local, id_visitante))
    if r_f:
        print(f"✗ Conflicto de fixture: Uno de los equipos ya tiene un partido programado en la fecha N° {nro_fecha} de este torneo.")
        return

    # 4. No se enfrenten dos veces en la misma edición (liga a una sola rueda), salvo postergado
    sql_duelo = """
        SELECT id_partido, estado FROM partido
        WHERE id_torneo = %s
          AND ((id_equipo_local = %s AND id_equipo_visitante = %s)
            OR (id_equipo_local = %s AND id_equipo_visitante = %s))
          AND estado != 'postergado'
    """
    _, r_d = ejecutar_consulta(conexion, sql_duelo, (id_torneo, id_local, id_visitante, id_visitante, id_local))
    if r_d:
        print("✗ Ambos equipos ya tienen un partido registrado entre sí en esta edición del torneo (liga a una sola rueda).")
        return

    dia = pedir_fecha("Día del encuentro")

    # Confirmar que el turno exista
    id_turno = pedir_turno_existente(conexion, "ID Turno")

    nombre_cancha = pedir_texto("Nombre Cancha")
    id_complejo = pedir_entero("ID Complejo")
    estado = pedir_opcion("Estado inicial", ["programado", "postergado", "reprogramado", "jugado"])

    if estado == 'jugado':
        # Validar si ya pasó
        dt_fin = parse_fecha_hora(dia, "23:59:00")
        sql_t = "SELECT hora_fin FROM turno WHERE id_turno = %s"
        _, r_t = ejecutar_consulta(conexion, sql_t, (id_turno,))
        if r_t:
            dt_fin = parse_fecha_hora(dia, r_t[0][0])
        if datetime.now() < dt_fin:
            print("✗ No se puede programar directamente como 'jugado': el horario del partido aún no ha pasado.")
            estado = "programado"

    sql = """
        INSERT INTO partido (id_partido, id_torneo, numero_fecha, id_equipo_local, id_equipo_visitante,
                             dia, id_turno, nombre_cancha, id_complejo, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    ejecutar_dml(conexion, sql, (id_partido, id_torneo, nro_fecha, id_local, id_visitante,
                                 dia, id_turno, nombre_cancha, id_complejo, estado),
                 "Partido programado exitosamente.")


def admin_baja_partido(conexion):
    print("\n--- Baja de Partido ---")
    print("[NOTA]: La base de datos mediante trigger impedirá borrar un partido en estado 'jugado'.")
    id_partido = pedir_entero("ID Partido a eliminar")
    id_torneo = pedir_entero("ID Torneo")
    confirmar = input(f"¿Confirma eliminar el partido {id_partido} del torneo {id_torneo}? (s/n): ").strip().lower()
    if confirmar == 's':
        sql = "DELETE FROM partido WHERE id_partido = %s AND id_torneo = %s"
        ejecutar_dml(conexion, sql, (id_partido, id_torneo), "Partido eliminado exitosamente.")


def admin_modificacion_partido(conexion):
    print("\n--- Modificación de Partido ---")
    id_partido = pedir_entero("ID Partido")
    id_torneo = pedir_entero("ID Torneo")

    sql = """
        SELECT dia, id_turno, nombre_cancha, id_complejo, estado, id_equipo_local, id_equipo_visitante
        FROM partido
        WHERE id_partido = %s AND id_torneo = %s
    """
    _, rows = ejecutar_consulta(conexion, sql, (id_partido, id_torneo))
    if not rows:
        print("✗ Partido no encontrado.")
        return
    p_dia, p_turno, p_cancha, p_comp, p_est, p_loc, p_vis = rows[0]

    print(f"Datos actuales: Fecha: {p_dia} | Turno: {p_turno} | Cancha: {p_cancha} (Complejo {p_comp}) | Estado: {p_est}")

    dia_in = input(f"Nuevo Día (DD/MM/AAAA) [{p_dia}]: ").strip()
    dia = formatear_fecha(dia_in) if dia_in else str(p_dia)

    cambiar_turno = input(f"¿Desea cambiar el turno {p_turno}? (s/n): ").strip().lower()
    if cambiar_turno == 's':
        id_turno = pedir_turno_existente(conexion, "Nuevo ID Turno")
    else:
        id_turno = p_turno

    cancha_in = input(f"Nueva Cancha [{p_cancha}]: ").strip()
    nombre_cancha = cancha_in if cancha_in else p_cancha

    comp_in = input(f"Nuevo Complejo [{p_comp}]: ").strip()
    id_complejo = int(comp_in) if comp_in else p_comp

    nuevo_estado = pedir_opcion(f"Nuevo Estado [{p_est}]", ["programado", "jugado", "postergado", "reprogramado"])

    if nuevo_estado == 'jugado' and p_est != 'jugado':
        if not verificar_partido_ya_paso(conexion, id_partido, id_torneo):
            return

    sql_upd = """
        UPDATE partido
        SET dia = %s, id_turno = %s, nombre_cancha = %s, id_complejo = %s, estado = %s
        WHERE id_partido = %s AND id_torneo = %s
    """
    ejecutar_dml(conexion, sql_upd, (dia, id_turno, nombre_cancha, id_complejo, nuevo_estado, id_partido, id_torneo),
                 "Partido modificado exitosamente.")


def admin_consultar_partidos(conexion):
    sql = """
        SELECT p.id_partido AS ID, p.id_torneo AS Torneo, p.numero_fecha AS Fecha,
               el.nombre AS Local, ev.nombre AS Visitante,
               p.dia AS Dia, t.hora_inicio AS Hora, p.nombre_cancha AS Cancha,
               p.estado AS Estado
        FROM partido p
        JOIN equipo el ON p.id_equipo_local = el.id_equipo
        JOIN equipo ev ON p.id_equipo_visitante = ev.id_equipo
        JOIN turno t ON p.id_turno = t.id_turno
        ORDER BY p.id_torneo, p.numero_fecha, p.dia
    """
    headers, rows = ejecutar_consulta(conexion, sql)
    imprimir_tabla(headers, rows)


def menu_gestion_partidos(conexion):
    while True:
        imprimir_subtitulo("GESTIÓN DE PARTIDOS / FIXTURE (ABM)")
        print("1. Alta Partido (Verificación de turnos y local != visitante)")
        print("2. Baja Partido (Trigger: no permite borrar jugados)")
        print("3. Modificación Partido")
        print("4. Consultar / Listar Partidos")
        print("0. Volver")
        opc = input("Seleccione una opción: ").strip()
        if opc == "1":
            admin_alta_partido(conexion)
        elif opc == "2":
            admin_baja_partido(conexion)
        elif opc == "3":
            admin_modificacion_partido(conexion)
        elif opc == "4":
            admin_consultar_partidos(conexion)
        elif opc == "0":
            break


def admin_alta_sancion(conexion):
    print("\n--- Alta de Sanción ---")
    sug_id = obtener_siguiente_id(conexion, "sancion_jugador", "id_sancion")
    id_sancion = pedir_entero("ID Sanción", sugerido=sug_id)
    ci_jugador = pedir_ci("Cédula del jugador sancionado (8 dígitos)")
    id_torneo = pedir_entero("ID Torneo")
    motivo = pedir_opcion("Motivo", ["roja", "acumulación de amarillas", "disciplinaria"])
    fecha_sanc = pedir_entero("Número de fecha en que ocurrió la sanción", minimo=1)
    fecha_ini = pedir_entero("Número de fecha desde que comienza a cumplir", minimo=1)
    cant_fechas = pedir_entero("Cantidad de fechas de suspensión", minimo=1)

    sql = """
        INSERT INTO sancion_jugador (id_sancion, ci_jugador, id_torneo, motivo,
                                     numero_fecha_sancion, numero_fecha_inicio_sancion, cantidad_fechas_sancionadas)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    ejecutar_dml(conexion, sql, (id_sancion, ci_jugador, id_torneo, motivo, fecha_sanc, fecha_ini, cant_fechas),
                 "Sanción registrada correctamente.")


def admin_baja_sancion(conexion):
    print("\n--- Baja de Sanción ---")
    id_sancion = pedir_entero("ID Sanción a eliminar")
    confirmar = input(f"¿Confirma dar de baja la sanción {id_sancion}? (s/n): ").strip().lower()
    if confirmar == 's':
        sql = "DELETE FROM sancion_jugador WHERE id_sancion = %s"
        ejecutar_dml(conexion, sql, (id_sancion,), "Sanción eliminada con éxito.")


def admin_modificacion_sancion(conexion):
    print("\n--- Modificación de Sanción ---")
    id_sancion = pedir_entero("ID Sanción a modificar")
    _, rows = ejecutar_consulta(conexion, "SELECT motivo, numero_fecha_inicio_sancion, cantidad_fechas_sancionadas FROM sancion_jugador WHERE id_sancion = %s", (id_sancion,))
    if not rows:
        print("✗ Sanción no encontrada.")
        return
    motivo_act, ini_act, cant_act = rows[0]
    motivo = pedir_opcion(f"Nuevo Motivo [{motivo_act}]", ["roja", "acumulación de amarillas", "disciplinaria"])
    ini_in = input(f"Nueva Fecha de Inicio [{ini_act}]: ").strip()
    fecha_ini = int(ini_in) if ini_in else ini_act
    cant_in = input(f"Nueva Cantidad de Fechas [{cant_act}]: ").strip()
    cant_fechas = int(cant_in) if cant_in else cant_act

    sql = """
        UPDATE sancion_jugador
        SET motivo = %s, numero_fecha_inicio_sancion = %s, cantidad_fechas_sancionadas = %s
        WHERE id_sancion = %s
    """
    ejecutar_dml(conexion, sql, (motivo, fecha_ini, cant_fechas, id_sancion), "Sanción actualizada con éxito.")


def admin_consultar_sanciones(conexion):
    sql = """
        SELECT s.id_sancion AS ID, s.ci_jugador AS CI,
               CONCAT(j.nombre, ' ', j.apellido) AS Jugador,
               s.id_torneo AS Torneo, s.motivo AS Motivo,
               s.numero_fecha_sancion AS 'Fecha Sanc.',
               s.numero_fecha_inicio_sancion AS 'Inicio Sanc.',
               s.cantidad_fechas_sancionadas AS 'Cant. Fechas'
        FROM sancion_jugador s
        JOIN jugador j ON s.ci_jugador = j.ci
        ORDER BY s.id_sancion DESC
    """
    headers, rows = ejecutar_consulta(conexion, sql)
    imprimir_tabla(headers, rows)


def menu_gestion_sanciones(conexion):
    while True:
        imprimir_subtitulo("GESTIÓN DE SANCIONES (ABM)")
        print("1. Alta Sanción")
        print("2. Baja Sanción")
        print("3. Modificación Sanción")
        print("4. Consultar / Listar Sanciones")
        print("0. Volver")
        opc = input("Seleccione una opción: ").strip()
        if opc == "1":
            admin_alta_sancion(conexion)
        elif opc == "2":
            admin_baja_sancion(conexion)
        elif opc == "3":
            admin_modificacion_sancion(conexion)
        elif opc == "4":
            admin_consultar_sanciones(conexion)
        elif opc == "0":
            break


def menu_gestion_planteles(conexion):
    while True:
        imprimir_subtitulo("GESTIÓN DE PLANTELES E INSCRIPCIONES")
        print("1. Inscribir Equipo en Torneo (Asignar Capitán)")
        print("2. Alta de Jugador en Plantel (Triggers: misma facultad, cupos, máx 10)")
        print("3. Baja de Jugador en Plantel (Triggers: mín 5 jugadores, inscripción)")
        print("4. Modificación de Camiseta de Jugador en Plantel")
        print("5. Consultar Planteles por Torneo y Equipo")
        print("0. Volver")

        opc = input("Seleccione una opción: ").strip()

        if opc == "1":
            print("\n--- Inscribir Equipo en Torneo ---")
            id_torneo = pedir_entero("ID Torneo")
            id_equipo = pedir_entero("ID Equipo")
            ci_capitan = pedir_ci("CI Jugador Capitán (8 dígitos)")
            sql = "INSERT INTO equipo_torneo (id_equipo, id_torneo, ci_capitan) VALUES (%s, %s, %s)"
            ejecutar_dml(conexion, sql, (id_equipo, id_torneo, ci_capitan), "Equipo inscripto en torneo con éxito.")

        elif opc == "2":
            print("\n--- Alta de Jugador en Plantel ---")
            id_torneo = pedir_entero("ID Torneo")
            id_equipo = pedir_entero("ID Equipo")
            ci_jugador = pedir_ci("CI Jugador (8 dígitos)")
            camiseta = pedir_entero("Número de Camiseta (1 a 99)", minimo=1, maximo=99)

            sql = """
                INSERT INTO equipo_jugador_torneo (id_equipo, ci_jugador, id_torneo, numero_camiseta)
                VALUES (%s, %s, %s, %s)
            """
            ejecutar_dml(conexion, sql, (id_equipo, ci_jugador, id_torneo, camiseta),
                         "Jugador incorporado al plantel correctamente.")

        elif opc == "3":
            print("\n--- Baja de Jugador en Plantel ---")
            id_torneo = pedir_entero("ID Torneo")
            id_equipo = pedir_entero("ID Equipo")
            ci_jugador = pedir_ci("CI Jugador (8 dígitos)")

            confirmar = input(f"¿Confirma dar de baja al jugador {ci_jugador} del plantel {id_equipo}? (s/n): ").strip().lower()
            if confirmar == 's':
                sql = "DELETE FROM equipo_jugador_torneo WHERE id_equipo = %s AND ci_jugador = %s AND id_torneo = %s"
                ejecutar_dml(conexion, sql, (id_equipo, ci_jugador, id_torneo), "Jugador quitado del plantel.")

        elif opc == "4":
            print("\n--- Modificación de Camiseta ---")
            id_torneo = pedir_entero("ID Torneo")
            id_equipo = pedir_entero("ID Equipo")
            ci_jugador = pedir_ci("CI Jugador (8 dígitos)")
            nueva_camiseta = pedir_entero("Nuevo Número de Camiseta (1 a 99)", minimo=1, maximo=99)

            sql = """
                UPDATE equipo_jugador_torneo
                SET numero_camiseta = %s
                WHERE id_equipo = %s AND ci_jugador = %s AND id_torneo = %s
            """
            ejecutar_dml(conexion, sql, (nueva_camiseta, id_equipo, ci_jugador, id_torneo), "Camiseta actualizada.")

        elif opc == "5":
            id_torneo = pedir_entero("ID Torneo")
            sql = """
                SELECT ejt.id_equipo AS 'ID Eq.', e.nombre AS Equipo,
                       ejt.ci_jugador AS CI, CONCAT(j.nombre, ' ', j.apellido) AS Jugador,
                       ejt.numero_camiseta AS Dorsal, j.tipo AS Tipo
                FROM equipo_jugador_torneo ejt
                JOIN equipo e ON ejt.id_equipo = e.id_equipo
                JOIN jugador j ON ejt.ci_jugador = j.ci
                WHERE ejt.id_torneo = %s
                ORDER BY e.nombre, ejt.numero_camiseta
            """
            headers, rows = ejecutar_consulta(conexion, sql, (id_torneo,))
            imprimir_tabla(headers, rows)

        elif opc == "0":
            break


def consultar_tabla_posiciones(conexion, id_torneo=None):
    """
    Muestra la Tabla de Posiciones oficial según la edición del torneo seleccionada.
    Considera:
      - PJ: Partidos Jugados
      - PG: Partidos Ganados (3 puntos c/u)
      - PE: Partidos Empatados (1 punto c/u)
      - PP: Partidos Perdidos (0 puntos c/u)
      - GF: Goles a Favor
      - GC: Goles en Contra
      - DG: Diferencia de Goles (GF - GC)
      - Pts: Puntos totales obtenidos
    Criterio de ordenación oficial:
      1° Puntos (Pts DESC)
      2° Diferencia de Goles (DG DESC)
      3° Goles a Favor (GF DESC)
      4° Nombre del Equipo (Equipo ASC)
    """
    imprimir_subtitulo("TABLA DE POSICIONES OFICIAL POR EDICIÓN DEL TORNEO")

    if id_torneo is None:
        sql_torneos = "SELECT id_torneo, nombre, año, semestre, estado FROM torneo ORDER BY id_torneo"
        _, torneos = ejecutar_consulta(conexion, sql_torneos)
        if not torneos:
            print("✗ No se encontraron ediciones de torneo registradas.")
            return

        print("\nEdiciones de Torneo disponibles:")
        for t_id, t_nom, t_anio, t_sem, t_est in torneos:
            print(f"  Torneo ID [{t_id}]: {t_nom} ({t_anio} - Semestre {t_sem}) [Estado: {t_est}]")

        id_torneo = pedir_entero("Ingrese el ID del Torneo a consultar", sugerido=torneos[0][0])

    # Consultar datos informativos del torneo
    sql_info = "SELECT nombre, año, semestre, estado FROM torneo WHERE id_torneo = %s"
    _, t_info = ejecutar_consulta(conexion, sql_info, (id_torneo,))
    if not t_info:
        print("✗ Torneo no encontrado.")
        return

    nom_torneo, anio_t, sem_t, est_t = t_info[0]

    # Consulta oficial de tabla de posiciones basada en DataGrip.sql
    sql_tabla = """
        SELECT e.nombre AS equipo,
               COUNT(r.id_partido) AS pj,
               COUNT(CASE WHEN r.goles_favor > r.goles_contra THEN 1 END) AS pg,
               COUNT(CASE WHEN r.goles_favor = r.goles_contra THEN 1 END) AS pe,
               COUNT(CASE WHEN r.goles_favor < r.goles_contra THEN 1 END) AS pp,
               COALESCE(SUM(r.goles_favor), 0) AS gf,
               COALESCE(SUM(r.goles_contra), 0) AS gc,
               COALESCE(SUM(r.goles_favor) - SUM(r.goles_contra), 0) AS dg,
               COALESCE(SUM(CASE
                       WHEN r.goles_favor > r.goles_contra THEN 3
                       WHEN r.goles_favor = r.goles_contra THEN 1
                       ELSE 0
                   END), 0) AS pts
        FROM equipo_torneo et
        JOIN torneo t ON t.id_torneo = et.id_torneo
        JOIN equipo e ON e.id_equipo = et.id_equipo
        LEFT JOIN (
            SELECT p.id_torneo, p.id_partido, et.id_equipo,
                   COUNT(CASE
                             WHEN (g.autogol = FALSE AND pp.id_equipo = et.id_equipo)
                               OR (g.autogol = TRUE AND (
                                      (et.id_equipo = p.id_equipo_local AND pp.id_equipo = p.id_equipo_visitante)
                                   OR (et.id_equipo = p.id_equipo_visitante AND pp.id_equipo = p.id_equipo_local)
                               ))
                             THEN 1
                         END) AS goles_favor,
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
            LEFT JOIN planilla_partido pp
                ON pp.id_partido = g.id_partido
               AND pp.id_torneo = g.id_torneo
               AND pp.ci_jugador = g.ci_jugador
            WHERE p.estado = 'jugado'
            GROUP BY p.id_torneo, p.id_partido, et.id_equipo
        ) r
            ON r.id_torneo = et.id_torneo
           AND r.id_equipo = et.id_equipo
        WHERE et.id_torneo = %s
        GROUP BY t.id_torneo, t.nombre, e.id_equipo, e.nombre
        ORDER BY pts DESC, dg DESC, gf DESC, e.nombre ASC
    """
    _, filas = ejecutar_consulta(conexion, sql_tabla, (id_torneo,))

    print(f"\n--- {nom_torneo} ({anio_t} - Semestre {sem_t}) | Estado: {est_t.upper()} ---")
    headers = ["Pos.", "Equipo", "PJ", "PG", "PE", "PP", "GF", "GC", "DG", "Pts"]
    filas_pos = []
    for idx, r in enumerate(filas, 1):
        filas_pos.append([f"{idx}°", r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8]])

    imprimir_tabla(headers, filas_pos)
    print("Reglamento de puntuación: Victoria = 3 pts | Empate = 1 pto | Derrota = 0 pts")
    print("Criterio de desempate: 1° Puntos -> 2° Diferencia de Goles -> 3° Goles a Favor -> 4° Alfabético")


def submenu_reportes(conexion):
    while True:
        imprimir_subtitulo("REPORTES Y ESTADÍSTICAS OFICIALES")
        print("1. Tabla de Posiciones por Edición del Torneo")
        print("2. Cantidad de jugadores por facultad")
        print("3. Cantidad de jugadores por tipo (grado, posgrado, docente, etc.)")
        print("4. Top 10 Máximos Goleadores")
        print("5. Jugadores sin minutos (que no figuran en ninguna planilla)")
        print("6. Canchas más utilizadas")
        print("7. Turnos más solicitados")
        print("8. Promedio de goles por fecha y por torneo")
        print("9. Porcentaje de partidos jugados vs. postergados")
        print("10. Tabla Fair Play de equipos")
        print("11. Ranking de sanciones y tarjetas")
        print("0. Volver")

        opc = input("Seleccione un reporte: ").strip()

        if opc == "1":
            consultar_tabla_posiciones(conexion)

        elif opc == "2":
            sql = """
                SELECT f.nombre AS Facultad, COUNT(*) AS Cantidad_Jugadores
                FROM facultad f
                JOIN jugador j ON f.id_facultad = j.id_facultad
                GROUP BY f.id_facultad, f.nombre
                ORDER BY Cantidad_Jugadores DESC
            """
            headers, rows = ejecutar_consulta(conexion, sql)
            imprimir_tabla(headers, rows)

        elif opc == "3":
            sql = "SELECT tipo AS 'Tipo de Integrante', COUNT(*) AS Cantidad FROM jugador GROUP BY tipo ORDER BY Cantidad DESC"
            headers, rows = ejecutar_consulta(conexion, sql)
            imprimir_tabla(headers, rows)

        elif opc == "4":
            sql = """
                SELECT j.ci AS CI, j.nombre AS Nombre, j.apellido AS Apellido, COUNT(*) AS Goles
                FROM gol g
                JOIN jugador j ON g.ci_jugador = j.ci
                WHERE g.autogol = FALSE
                GROUP BY j.ci, j.nombre, j.apellido
                ORDER BY Goles DESC
                LIMIT 10
            """
            headers, rows = ejecutar_consulta(conexion, sql)
            imprimir_tabla(headers, rows)

        elif opc == "5":
            sql = """
                SELECT j.ci AS CI, j.nombre AS Nombre, j.apellido AS Apellido, f.nombre AS Facultad
                FROM jugador j
                JOIN facultad f ON j.id_facultad = f.id_facultad
                JOIN equipo_jugador_torneo ejt ON j.ci = ejt.ci_jugador
                WHERE NOT EXISTS (
                    SELECT 1 FROM planilla_partido pp WHERE pp.ci_jugador = j.ci
                )
                ORDER BY j.apellido, j.nombre
            """
            headers, rows = ejecutar_consulta(conexion, sql)
            imprimir_tabla(headers, rows)

        elif opc == "6":
            sql = """
                SELECT nombre_cancha AS Cancha, COUNT(*) AS Cantidad_Usos
                FROM partido
                WHERE estado = 'jugado'
                GROUP BY nombre_cancha
                ORDER BY Cantidad_Usos DESC
            """
            headers, rows = ejecutar_consulta(conexion, sql)
            imprimir_tabla(headers, rows)

        elif opc == "7":
            sql = """
                SELECT t.id_turno AS 'ID Turno', t.hora_inicio AS Inicio, t.hora_fin AS Fin,
                       COUNT(*) AS Cantidad_Partidos
                FROM partido p
                JOIN turno t ON p.id_turno = t.id_turno
                WHERE p.estado = 'jugado'
                GROUP BY t.id_turno, t.hora_inicio, t.hora_fin
                ORDER BY Cantidad_Partidos DESC
            """
            headers, rows = ejecutar_consulta(conexion, sql)
            imprimir_tabla(headers, rows)

        elif opc == "8":
            print("\n--- Promedio de Goles por Fecha ---")
            sql_fechas = """
                SELECT p.numero_fecha AS Fecha,
                       ROUND(COUNT(g.id_gol) * 1.0 / COUNT(DISTINCT p.id_partido), 2) AS Promedio_Goles
                FROM partido p
                LEFT JOIN gol g ON p.id_partido = g.id_partido AND p.id_torneo = g.id_torneo
                WHERE p.estado = 'jugado'
                GROUP BY p.numero_fecha
                ORDER BY p.numero_fecha
            """
            h1, r1 = ejecutar_consulta(conexion, sql_fechas)
            imprimir_tabla(h1, r1)

            print("\n--- Promedio General del Torneo ---")
            sql_gral = """
                SELECT ROUND(COUNT(g.id_gol) * 1.0 / COUNT(DISTINCT p.id_partido), 2) AS Promedio_Goles_Torneo
                FROM partido p
                LEFT JOIN gol g ON p.id_partido = g.id_partido AND p.id_torneo = g.id_torneo
                WHERE p.estado = 'jugado'
            """
            h2, r2 = ejecutar_consulta(conexion, sql_gral)
            imprimir_tabla(h2, r2)

        elif opc == "9":
            sql = """
                SELECT
                    ROUND(SUM(CASE WHEN estado = 'jugado' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS Porcentaje_Jugados,
                    ROUND(SUM(CASE WHEN estado = 'postergado' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS Porcentaje_Postergados,
                    ROUND(SUM(CASE WHEN estado = 'programado' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS Porcentaje_Programados
                FROM partido
            """
            headers, rows = ejecutar_consulta(conexion, sql)
            imprimir_tabla(headers, rows)

        elif opc == "10":
            sql = """
                SELECT e.nombre AS Equipo,
                       SUM(CASE WHEN t.color IN ('amarilla', 'amarillo') THEN 1
                                WHEN t.color IN ('roja', 'rojo') THEN 3 ELSE 0 END) AS Puntaje_Fair_Play
                FROM tarjeta t
                JOIN equipo_jugador_torneo ejt ON t.ci_jugador = ejt.ci_jugador AND t.id_torneo = ejt.id_torneo
                JOIN equipo e ON ejt.id_equipo = e.id_equipo
                GROUP BY e.id_equipo, e.nombre
                ORDER BY Puntaje_Fair_Play ASC
            """
            headers, rows = ejecutar_consulta(conexion, sql)
            imprimir_tabla(headers, rows)

        elif opc == "11":
            print("\n--- Top 10 Jugadores con más Sanciones ---")
            sql_sanc = """
                SELECT j.ci AS CI, j.nombre AS Nombre, j.apellido AS Apellido, COUNT(*) AS Cantidad_Sanciones
                FROM sancion_jugador s
                JOIN jugador j ON s.ci_jugador = j.ci
                GROUP BY j.ci, j.nombre, j.apellido
                ORDER BY Cantidad_Sanciones DESC
                LIMIT 10
            """
            h, r = ejecutar_consulta(conexion, sql_sanc)
            imprimir_tabla(h, r)

            print("\n--- Top 3 Facultades con más Goles ---")
            sql_fac = """
                SELECT f.nombre AS Facultad, COUNT(*) AS Total_Goles
                FROM gol g
                JOIN jugador j ON g.ci_jugador = j.ci
                JOIN facultad f ON j.id_facultad = f.id_facultad
                WHERE g.autogol = FALSE
                GROUP BY f.id_facultad, f.nombre
                ORDER BY Total_Goles DESC
                LIMIT 3
            """
            h_f, r_f = ejecutar_consulta(conexion, sql_fac)
            imprimir_tabla(h_f, r_f)

            print("\n--- Jugador con más Tarjetas ---")
            sql_tarj = """
                SELECT j.ci AS CI, j.nombre AS Nombre, j.apellido AS Apellido, COUNT(*) AS Cantidad_Tarjetas
                FROM tarjeta t
                JOIN jugador j ON t.ci_jugador = j.ci
                GROUP BY j.ci, j.nombre, j.apellido
                ORDER BY Cantidad_Tarjetas DESC
                LIMIT 1
            """
            h_t, r_t = ejecutar_consulta(conexion, sql_tarj)
            imprimir_tabla(h_t, r_t)

        elif opc == "0":
            break


def menu_administrador(conexion, usuario):
    while True:
        imprimir_titulo(f"PANEL DEL ADMINISTRADOR ({usuario})")
        print("1. Gestión de Jugadores (Alta, Baja, Modificación, Consultar)")
        print("2. Gestión de Equipos (Alta, Baja, Modificación, Consultar)")
        print("3. Gestión de Complejos (Alta, Baja, Modificación, Consultar)")
        print("4. Gestión de Canchas (Alta, Baja, Modificación, Consultar)")
        print("5. Gestión de Partidos (Alta, Baja, Modificación, Consultar)")
        print("6. Gestión de Sanciones (Alta, Baja, Modificación, Consultar)")
        print("7. Gestión de Planteles")
        print("8. Reportes y Estadísticas del Torneo")
        print("0. Cerrar Sesión")

        opc = input("\nSeleccione una opción: ").strip()

        if opc == "1":
            menu_gestion_jugadores(conexion)
        elif opc == "2":
            menu_gestion_equipos(conexion)
        elif opc == "3":
            menu_gestion_complejos(conexion)
        elif opc == "4":
            menu_gestion_canchas(conexion)
        elif opc == "5":
            menu_gestion_partidos(conexion)
        elif opc == "6":
            menu_gestion_sanciones(conexion)
        elif opc == "7":
            menu_gestion_planteles(conexion)
        elif opc == "8":
            submenu_reportes(conexion)
        elif opc == "0":
            print("\nCerrando sesión de Administrador...")
            break
        else:
            print("Opción inválida. Intente nuevamente.")


# ==============================================================================
# MÓDULO PLANILLERO: REGISTRAR PLANILLA, GOL, TARJETA, CAPITÁN Y FINALIZAR PARTIDO
# ==============================================================================
def planillero_registrar_planilla(conexion):
    imprimir_subtitulo("REGISTRAR PLANILLA DE PARTIDO")
    id_partido = pedir_entero("ID Partido")
    id_torneo = pedir_entero("ID Torneo")
    ci_jugador = pedir_ci("CI Jugador (8 dígitos)")
    id_equipo = pedir_entero("ID Equipo al que defiende")

    # Trigger de suspensión activo en MySQL
    sql = """
        INSERT INTO planilla_partido (id_partido, id_torneo, ci_jugador, id_equipo)
        VALUES (%s, %s, %s, %s)
    """
    ejecutar_dml(conexion, sql, (id_partido, id_torneo, ci_jugador, id_equipo),
                 "Jugador registrado en la planilla del partido.")


def planillero_registrar_gol(conexion):
    imprimir_subtitulo("REGISTRAR GOL")
    id_partido = pedir_entero("ID Partido")
    id_torneo = pedir_entero("ID Torneo")

    # Regla: el resultado solo es modificable durante las 48 horas desde que se jugó
    if not verificar_resultado_es_modificable(conexion, id_partido, id_torneo):
        return

    sug_id = obtener_siguiente_id(conexion, "gol", "id_gol")
    id_gol = pedir_entero("ID Gol", sugerido=sug_id)
    ci_jugador = pedir_ci("CI Jugador que convirtió (8 dígitos)")
    minuto = pedir_entero("Minuto del gol", minimo=0)
    auto_opc = pedir_opcion("¿Fue autogol?", ["si", "no"])
    autogol = True if auto_opc == "si" else False

    # Trigger de BD: el jugador debe figurar en la planilla del partido
    sql = """
        INSERT INTO gol (id_gol, id_partido, id_torneo, ci_jugador, minuto, autogol)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    ejecutar_dml(conexion, sql, (id_gol, id_partido, id_torneo, ci_jugador, minuto, autogol),
                 "Gol registrado exitosamente.")


def planillero_registrar_tarjeta(conexion):
    imprimir_subtitulo("REGISTRAR TARJETA")
    id_partido = pedir_entero("ID Partido")
    id_torneo = pedir_entero("ID Torneo")
    ci_jugador = pedir_ci("CI Jugador sancionado (8 dígitos)")
    minuto = pedir_entero("Minuto de la infracción", minimo=0)
    color = pedir_opcion("Color de tarjeta", ["amarilla", "roja"])

    sug_id = obtener_siguiente_id(conexion, "tarjeta", "id_tarjeta")
    id_tarjeta = pedir_entero("ID Tarjeta", sugerido=sug_id)

    # Trigger de BD: el jugador debe figurar en la planilla del partido
    sql = """
        INSERT INTO tarjeta (id_tarjeta, id_partido, id_torneo, ci_jugador, minuto, color)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    ejecutar_dml(conexion, sql, (id_tarjeta, id_partido, id_torneo, ci_jugador, minuto, color),
                 "Tarjeta registrada exitosamente.")


def planillero_registrar_capitan(conexion):
    imprimir_subtitulo("REGISTRAR CAPITÁN DE PARTIDO")
    id_partido = pedir_entero("ID Partido")
    id_torneo = pedir_entero("ID Torneo")
    id_equipo = pedir_entero("ID Equipo")
    ci_jugador = pedir_ci("CI Jugador Capitán (8 dígitos)")
    minuto_inicio = pedir_entero("Minuto desde el cual porta el brazalete", minimo=0)

    sql = """
        INSERT INTO capitan_partido (id_partido, id_torneo, id_equipo, ci_jugador, minuto_inicio)
        VALUES (%s, %s, %s, %s, %s)
    """
    ejecutar_dml(conexion, sql, (id_partido, id_torneo, id_equipo, ci_jugador, minuto_inicio),
                 "Capitán asignado correctamente.")


def planillero_finalizar_partido(conexion):
    imprimir_subtitulo("FINALIZAR PARTIDO (MARCAR COMO JUGADO)")
    id_partido = pedir_entero("ID Partido")
    id_torneo = pedir_entero("ID Torneo")

    # Regla: solo se puede marcar como jugado si ya pasó
    if not verificar_partido_ya_paso(conexion, id_partido, id_torneo):
        return

    confirmar = input(f"¿Confirma marcar el partido {id_partido} como 'jugado'? (s/n): ").strip().lower()
    if confirmar == 's':
        sql = "UPDATE partido SET estado = 'jugado' WHERE id_partido = %s AND id_torneo = %s"
        ejecutar_dml(conexion, sql, (id_partido, id_torneo), "Partido marcado como 'jugado' exitosamente.")


def planillero_consultar_partidos(conexion):
    sql = """
        SELECT p.id_partido AS ID, p.id_torneo AS Torneo, p.numero_fecha AS Fecha,
               el.nombre AS Local, ev.nombre AS Visitante,
               p.dia AS Dia, t.hora_inicio AS Hora, p.nombre_cancha AS Cancha,
               p.estado AS Estado
        FROM partido p
        JOIN equipo el ON p.id_equipo_local = el.id_equipo
        JOIN equipo ev ON p.id_equipo_visitante = ev.id_equipo
        JOIN turno t ON p.id_turno = t.id_turno
        ORDER BY p.dia DESC, t.hora_inicio
    """
    headers, rows = ejecutar_consulta(conexion, sql)
    imprimir_tabla(headers, rows)


def menu_planillero(conexion, usuario):
    while True:
        imprimir_titulo(f"PANEL DEL PLANILLERO ({usuario})")
        print("1. Registrar Planilla")
        print("2. Registrar Gol (Control 48hs activado)")
        print("3. Registrar Tarjeta")
        print("4. Registrar Capitán de Partido")
        print("5. Finalizar Partido (Solo si ya pasó la fecha y hora)")
        print("6. Consultar Partidos")
        print("7. Consultar Tabla de Posiciones por Edición")
        print("0. Cerrar Sesión")

        opc = input("\nSeleccione una opción: ").strip()

        if opc == "1":
            planillero_registrar_planilla(conexion)
        elif opc == "2":
            planillero_registrar_gol(conexion)
        elif opc == "3":
            planillero_registrar_tarjeta(conexion)
        elif opc == "4":
            planillero_registrar_capitan(conexion)
        elif opc == "5":
            planillero_finalizar_partido(conexion)
        elif opc == "6":
            planillero_consultar_partidos(conexion)
        elif opc == "7":
            consultar_tabla_posiciones(conexion)
        elif opc == "0":
            print("\nCerrando sesión de Planillero...")
            break
        else:
            print("Opción inválida. Intente nuevamente.")


# ==============================================================================
# MÓDULO JUGADOR: SOLO CONSULTAR GOLES, SANCIONES, TARJETAS Y PARTIDOS
# ==============================================================================
def jugador_consultar_partidos(conexion):
    """
    Muestra la lista completa de partidos desde jugados (con resultado de goles),
    hasta postergados, reprogramados y programados.
    """
    imprimir_subtitulo("LISTA COMPLETA DE PARTIDOS (DESDE JUGADOS HASTA PROGRAMADOS)")
    sql = """
        SELECT p.id_partido AS ID,
               p.numero_fecha AS 'Fecha N°',
               el.nombre AS Local,
               CASE
                   WHEN p.estado = 'jugado' THEN
                       (SELECT COUNT(*) FROM gol g
                        JOIN planilla_partido pp ON g.id_partido = pp.id_partido AND g.id_torneo = pp.id_torneo AND g.ci_jugador = pp.ci_jugador
                        WHERE g.id_partido = p.id_partido AND g.id_torneo = p.id_torneo
                          AND ((g.autogol = FALSE AND pp.id_equipo = p.id_equipo_local)
                               OR (g.autogol = TRUE AND pp.id_equipo = p.id_equipo_visitante)))
                   ELSE '-'
               END AS 'G. Loc.',
               CASE
                   WHEN p.estado = 'jugado' THEN
                       (SELECT COUNT(*) FROM gol g
                        JOIN planilla_partido pp ON g.id_partido = pp.id_partido AND g.id_torneo = pp.id_torneo AND g.ci_jugador = pp.ci_jugador
                        WHERE g.id_partido = p.id_partido AND g.id_torneo = p.id_torneo
                          AND ((g.autogol = FALSE AND pp.id_equipo = p.id_equipo_visitante)
                               OR (g.autogol = TRUE AND pp.id_equipo = p.id_equipo_local)))
                   ELSE '-'
               END AS 'G. Vis.',
               ev.nombre AS Visitante,
               p.dia AS Día,
               t.hora_inicio AS Hora,
               p.nombre_cancha AS Cancha,
               UPPER(p.estado) AS Estado
        FROM partido p
        JOIN equipo el ON p.id_equipo_local = el.id_equipo
        JOIN equipo ev ON p.id_equipo_visitante = ev.id_equipo
        JOIN turno t ON p.id_turno = t.id_turno
        ORDER BY FIELD(p.estado, 'jugado', 'reprogramado', 'postergado', 'programado'), p.dia, t.hora_inicio
    """
    headers, rows = ejecutar_consulta(conexion, sql)
    imprimir_tabla(headers, rows)


def jugador_consultar_goles(conexion):
    """Muestra la tabla de goleadores y la lista completa de todos los goles registrados."""
    imprimir_subtitulo("CONSULTA DE GOLES DEL TORNEO")
    print("--- Tabla de Goleadores ---")
    sql_top = """
        SELECT j.ci AS CI, j.nombre AS Nombre, j.apellido AS Apellido, COUNT(*) AS Total_Goles
        FROM gol g
        JOIN jugador j ON g.ci_jugador = j.ci
        WHERE g.autogol = FALSE
        GROUP BY j.ci, j.nombre, j.apellido
        ORDER BY Total_Goles DESC
    """
    h1, r1 = ejecutar_consulta(conexion, sql_top)
    imprimir_tabla(h1, r1)

    print("--- Lista Completa de Goles Registrados ---")
    sql_goles = """
        SELECT g.id_gol AS 'ID Gol',
               p.numero_fecha AS 'Fecha N°',
               p.id_partido AS 'ID Partido',
               CONCAT(el.nombre, ' vs ', ev.nombre) AS Partido,
               g.minuto AS Minuto,
               CONCAT(j.nombre, ' ', j.apellido) AS Jugador,
               IF(g.autogol = 1, 'Sí (Autogol)', 'No') AS Autogol
        FROM gol g
        JOIN jugador j ON g.ci_jugador = j.ci
        JOIN partido p ON g.id_partido = p.id_partido AND g.id_torneo = p.id_torneo
        JOIN equipo el ON p.id_equipo_local = el.id_equipo
        JOIN equipo ev ON p.id_equipo_visitante = ev.id_equipo
        ORDER BY p.numero_fecha ASC, g.id_partido ASC, g.minuto ASC
    """
    h2, r2 = ejecutar_consulta(conexion, sql_goles)
    imprimir_tabla(h2, r2)


def jugador_consultar_tarjetas(conexion):
    """Muestra la lista completa de tarjetas amarillas y rojas registradas."""
    imprimir_subtitulo("CONSULTA DE TARJETAS REGISTRADAS")
    sql = """
        SELECT t.id_tarjeta AS 'ID Tarjeta',
               p.numero_fecha AS 'Fecha N°',
               p.id_partido AS 'ID Partido',
               CONCAT(el.nombre, ' vs ', ev.nombre) AS Partido,
               t.minuto AS Minuto,
               CONCAT(j.nombre, ' ', j.apellido) AS Jugador,
               UPPER(t.color) AS Tarjeta
        FROM tarjeta t
        JOIN jugador j ON t.ci_jugador = j.ci
        JOIN partido p ON t.id_partido = p.id_partido AND t.id_torneo = p.id_torneo
        JOIN equipo el ON p.id_equipo_local = el.id_equipo
        JOIN equipo ev ON p.id_equipo_visitante = ev.id_equipo
        ORDER BY p.numero_fecha ASC, t.id_partido ASC, t.minuto ASC
    """
    headers, rows = ejecutar_consulta(conexion, sql)
    imprimir_tabla(headers, rows)


def jugador_consultar_sanciones(conexion):
    """Muestra la lista completa de sanciones y suspensiones activas."""
    imprimir_subtitulo("CONSULTA DE SANCIONES Y SUSPENSIONES")
    sql = """
        SELECT s.ci_jugador AS CI, CONCAT(j.nombre, ' ', j.apellido) AS Jugador,
               s.motivo AS Motivo,
               s.numero_fecha_sancion AS 'Fecha Ocurrida',
               s.numero_fecha_inicio_sancion AS 'Comienza en Fecha N°',
               s.cantidad_fechas_sancionadas AS 'Cant. Fechas Suspensión'
        FROM sancion_jugador s
        JOIN jugador j ON s.ci_jugador = j.ci
        ORDER BY s.numero_fecha_inicio_sancion DESC
    """
    headers, rows = ejecutar_consulta(conexion, sql)
    imprimir_tabla(headers, rows)


def menu_jugador(conexion, usuario):
    while True:
        imprimir_titulo(f"PANEL DEL JUGADOR ({usuario}) - MODO CONSULTA")
        print("1. Consultar Tabla de Posiciones por Edición del Torneo")
        print("2. Consultar Partidos (Lista completa desde jugados hasta programados)")
        print("3. Consultar Goles")
        print("4. Consultar Tarjetas")
        print("5. Consultar Sanciones")
        print("0. Cerrar Sesión")

        opc = input("\nSeleccione una opción: ").strip()

        if opc == "1":
            consultar_tabla_posiciones(conexion)
        elif opc == "2":
            jugador_consultar_partidos(conexion)
        elif opc == "3":
            jugador_consultar_goles(conexion)
        elif opc == "4":
            jugador_consultar_tarjetas(conexion)
        elif opc == "5":
            jugador_consultar_sanciones(conexion)
        elif opc == "0":
            print("\nCerrando sesión de Jugador...")
            break
        else:
            print("Opción inválida. Intente nuevamente.")


# ==============================================================================
# FUNCIÓN PRINCIPAL / BUCLE DE APLICACIÓN
# ==============================================================================
def main():
    imprimir_titulo("SISTEMA DE GESTIÓN DE TORNEOS DE FÚTBOL UCU")
    print("Conectando con la base de datos MySQL 'obligatorio'...")

    conexion = obtener_conexion()
    if not conexion:
        print("\nNo se pudo establecer conexión con la base de datos. Fin del programa.")
        return

    print("✓ Conexión establecida con éxito.")

    try:
        while True:
            correo, rol = autenticar_usuario(conexion)
            if not correo:
                reintentar = input("\n¿Desea reintentar el inicio de sesión? (s/n): ").strip().lower()
                if reintentar != 's':
                    print("\n¡Hasta pronto!")
                    break
                continue

            # Redirección estricta según el rol
            if rol == "administrador":
                menu_administrador(conexion, correo)
            elif rol == "planillero":
                menu_planillero(conexion, correo)
            elif rol == "jugador":
                menu_jugador(conexion, correo)
            else:
                print(f"Rol '{rol}' no reconocido por el sistema.")

            opc = input("\n¿Desea iniciar sesión con otro usuario? (s/n): ").strip().lower()
            if opc != 's':
                print("\nGracias por utilizar el Sistema de Gestión de Torneos UCU. ¡Hasta luego!")
                break

    except KeyboardInterrupt:
        print("\n\nOperación interrumpida por el usuario. Saliendo...")
    finally:
        if conexion.is_connected():
            conexion.close()
            print("Conexión a la base de datos cerrada de forma segura.")


if __name__ == "__main__":
    main()
