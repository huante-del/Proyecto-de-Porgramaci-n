"""
Script Principal de Demostración y Pruebas — Hito 2 (Opción C: Dispositivos en red).

Autores:
- Diego Barba Mier Y Concha (225996364)
- Jesús Emmanuel Huante Jiménez (222479008)

Este script ejecuta de principio a fin:
1. La creación y registro válido de instancias de `EquipoPersonal` y `Servidor` (con `Responsable`).
2. El listado polimórfico mediante `sistema.listar()` e invocación de `describir()`.
3. Las pruebas de validación ("rompiendo" las reglas del registro) para demostrar que
   el programa rechaza entradas inválidas con mensajes claros y sin errores nativos inesperados.
4. Las pruebas de contenedores (`SegmentoRed`), asignación (`asignar`) con sus validaciones,
   y persistencia (`guardar`, `cargar` y arranque limpio sin archivo previo).
"""

import os
from modelos import Dispositivo, EquipoPersonal, Servidor, Responsable
from sistema import SistemaRed, SegmentoRed, RangoIP, guardar, cargar


def imprimir_encabezado(titulo: str) -> None:
    """Imprime un separador visual con formato claro en consola."""
    print("\n" + "=" * 78)
    print(f" {titulo}")
    print("=" * 78)


def ejecutar_pruebas_diego(sistema: SistemaRed) -> None:
    """
    Ejecuta las pruebas completas del modelado de dispositivos, polimorfismo,
    operaciones base (`registrar` y `listar`) y validaciones de registro.
    """
    imprimir_encabezado("1. REGISTRO EXITOSO DE DISPOSITIVOS (EquipoPersonal y Servidor)")

    # Creación de objetos Responsable
    resp_diego = Responsable(
        id_empleado="EMP-101",
        nombre="Diego Barba",
        correo="diego.barba@alumnos.udg.mx",
        departamento="Infraestructura TI",
    )
    resp_emmanuel = Responsable(
        id_empleado="EMP-102",
        nombre="Emmanuel Huante",
        correo="emmanuel.huante@alumnos.udg.mx",
        departamento="Redes y Seguridad",
    )

    # Creación de Equipos Personales (Clase Hija 1)
    laptop_dev = EquipoPersonal(
        id_dispositivo="EQP-0001",
        nombre_host="laptop-diego-dev",
        direccion_mac="00:1A:2B:3C:4D:5E",
        direccion_ip="192.168.10.15",
        responsable=resp_diego,
        tipo_equipo="Laptop",
        sistema_operativo="Ubuntu 24.04 LTS",
    )

    workstation_admin = EquipoPersonal(
        id_dispositivo="DEV-0002",
        nombre_host="ws-redes-01",
        direccion_mac="AA:BB:CC:DD:EE:01",
        direccion_ip="192.168.10.20",
        responsable="Carlos Mendoza (Soporte N2)",  # También soporta string directo como dueño
        tipo_equipo="Workstation",
        sistema_operativo="Windows 11 Pro",
    )

    # Creación de Servidores (Clase Hija 2)
    servidor_bd = Servidor(
        id_dispositivo="SRV-0001",
        nombre_host="srv-postgres-prod",
        direccion_mac="00:50:56:C0:00:08",
        direccion_ip="10.0.1.10",
        responsable=resp_emmanuel,
        rol_servidor="Base de Datos",
        puerto_servicio=5432,
        es_critico=True,
    )

    servidor_web = Servidor(
        id_dispositivo="SRV-0002",
        nombre_host="srv-nginx-front",
        direccion_mac="00:50:56:C0:00:09",
        direccion_ip="10.0.1.11",
        responsable=resp_diego,
        rol_servidor="Servidor Web",
        puerto_servicio=443,
        es_critico=False,
    )

    for disp in (laptop_dev, workstation_admin, servidor_bd, servidor_web):
        sistema.registrar(disp)
        print(f"[OK] Registrado correctamente: {disp.id_dispositivo} ({disp.nombre_host})")

    # -----------------------------------------------------------------
    # DEMOSTRACIÓN DE POLIMORFISMO Y LISTAR()
    # -----------------------------------------------------------------
    imprimir_encabezado("2. LISTADO POLIMÓRFICO DE DISPOSITIVOS (sistema.listar() -> describir())")
    sistema.listar()

    print("\n  [Métodos específicos de las clases hijas]:")
    print(f"  - Solicitud VPN ({laptop_dev.id_dispositivo}): {'Aprobada' if laptop_dev.solicitar_acceso_vpn() else 'Rechazada'}")
    print(f"  - {servidor_bd.ejecutar_diagnostico()}")

    # -----------------------------------------------------------------
    # PRUEBAS DE VALIDACIONES (ROMPIENDO REGLAS DE NEGOCIO - TABLA 5)
    # -----------------------------------------------------------------
    imprimir_encabezado("3. PRUEBAS DE VALIDACIÓN Y RECHAZOS EN REGISTRO (Tabla 5 - Hito 1)")

    # Caso 1: Registrar un dispositivo dejando el responsable o dueño en blanco
    print("\n[Prueba 3.1] Intentar registrar un dispositivo con el responsable en blanco:")
    try:
        equipo_sin_dueno = EquipoPersonal(
            id_dispositivo="EQP-0099",
            nombre_host="pc-huerfana",
            direccion_mac="11:22:33:44:55:66",
            direccion_ip="192.168.10.99",
            responsable="   ",  # En blanco
            tipo_equipo="Desktop",
            sistema_operativo="Debian 12",
        )
        sistema.registrar(equipo_sin_dueno)
    except ValueError as err:
        print(f"  -> [RECHAZO CONTROLADO]: {err}")

    # Caso 2: Registrar un dispositivo cuyo identificador tiene un formato incorrecto
    print("\n[Prueba 3.2] Intentar registrar un dispositivo con formato de identificador incorrecto ('PC-99'):")
    try:
        equipo_id_malo = Servidor(
            id_dispositivo="PC-99",  # Formato inválido (se espera DEV-/SRV-/EQP- + 4 dígitos)
            nombre_host="srv-mal-id",
            direccion_mac="11:22:33:44:55:77",
            direccion_ip="10.0.1.99",
            responsable=resp_diego,
            rol_servidor="Cache Redis",
            puerto_servicio=6379,
        )
        sistema.registrar(equipo_id_malo)
    except ValueError as err:
        print(f"  -> [RECHAZO CONTROLADO]: {err}")

    # Caso 3: Registrar un equipo con un identificador previamente guardado en el sistema
    print("\n[Prueba 3.3] Intentar registrar un dispositivo con identificador duplicado ('SRV-0001'):")
    try:
        servidor_duplicado = Servidor(
            id_dispositivo="SRV-0001",  # Ya fue registrado arriba
            nombre_host="srv-clonado",
            direccion_mac="99:88:77:66:55:44",
            direccion_ip="10.0.1.50",
            responsable=resp_emmanuel,
            rol_servidor="Servidor DNS",
            puerto_servicio=53,
        )
        sistema.registrar(servidor_duplicado)
    except ValueError as err:
        print(f"  -> [RECHAZO CONTROLADO]: {err}")


def ejecutar_pruebas_emmanuel(sistema: SistemaRed) -> None:
    """
    Ejecuta las pruebas completas de contenedores (`SegmentoRed`), asignación (`asignar`),
    validaciones de asignación, persistencia (`guardar`, `cargar`) y arranque limpio.
    """
    imprimir_encabezado("4. CONTENEDORES, ASIGNACIÓN Y PERSISTENCIA (Sección de Emmanuel Huante)")

    rango_lan = RangoIP("192.168.10.1", "192.168.10.254", "255.255.255.0")
    segmento_lan = SegmentoRed(
        id_segmento="SEG-LAN1",
        nombre_segmento="Segmento Corporativo Piso 1",
        capacidad_maxima=2,
        rango_ip=rango_lan,
    )
    sistema.registrar(segmento_lan)
    print(
        f"[OK] Contenedor creado y registrado en el sistema mediante registrar(): "
        f"{segmento_lan.id_segmento} ('{segmento_lan.nombre_segmento}', cupo máx: {segmento_lan.capacidad_maxima})"
    )

    # Asignaciones válidas (llenando el cupo máximo de 2)
    sistema.asignar("EQP-0001", "SEG-LAN1")
    print("[OK] Dispositivo EQP-0001 asignado exitosamente a SEG-LAN1.")
    sistema.asignar("DEV-0002", "SEG-LAN1")
    print("[OK] Dispositivo DEV-0002 asignado exitosamente a SEG-LAN1.")

    # Validaciones de asignación
    print("\n[Prueba 4.1] Asignar dispositivo a segmento inexistente ('SEG-NOEXISTE'):")
    try:
        sistema.asignar("EQP-0001", "SEG-NOEXISTE")
    except ValueError as err:
        print(f"  -> [RECHAZO CONTROLADO]: {err}")

    print("\n[Prueba 4.2] Asignar dispositivo no registrado ('DEV-9999'):")
    try:
        sistema.asignar("DEV-9999", "SEG-LAN1")
    except ValueError as err:
        print(f"  -> [RECHAZO CONTROLADO]: {err}")

    print("\n[Prueba 4.3] Asignar dispositivo duplicado en el mismo segmento ('EQP-0001'):")
    try:
        sistema.asignar("EQP-0001", "SEG-LAN1")
    except ValueError as err:
        print(f"  -> [RECHAZO CONTROLADO]: {err}")

    print("\n[Prueba 4.4] Superar cupo máximo del segmento ('SEG-LAN1' ya tiene 2/2):")
    extra = EquipoPersonal(
        id_dispositivo="EQP-0003",
        nombre_host="laptop-extra",
        direccion_mac="AA:BB:CC:DD:EE:03",
        direccion_ip="192.168.10.30",
        responsable="Ana López",
        tipo_equipo="Laptop",
        sistema_operativo="Fedora 40",
    )
    sistema.registrar(extra)
    try:
        sistema.asignar("EQP-0003", "SEG-LAN1")
    except ValueError as err:
        print(f"  -> [RECHAZO CONTROLADO]: {err}")

    # Persistencia: guardar, recargar en un sistema nuevo y arranque limpio
    ruta_datos = "estado_red.json"
    guardar(sistema, ruta_datos)
    print(f"\n[OK] Estado guardado en '{ruta_datos}'.")

    sistema_recargado = SistemaRed()
    cargo_ok = cargar(sistema_recargado, ruta_datos)
    print(
        f"[OK] Estado recargado en nueva instancia (cargar={cargo_ok}): "
        f"{len(sistema_recargado.dispositivos)} dispositivos, "
        f"{len(sistema_recargado.segmentos)} segmento(s)."
    )

    sistema_limpio = SistemaRed()
    archivo_inexistente = "archivo_que_no_existe.json"
    if os.path.exists(archivo_inexistente):
        os.remove(archivo_inexistente)
    arranque_limpio = cargar(sistema_limpio, archivo_inexistente)
    print(f"[OK] Arranque limpio sin archivo previo (cargar={arranque_limpio}): sin errores.")


def main() -> None:
    """Punto de entrada principal de las pruebas del sistema de red."""
    sistema = SistemaRed()
    ejecutar_pruebas_diego(sistema)
    ejecutar_pruebas_emmanuel(sistema)

    imprimir_encabezado("5. HISTORIAL DE LA BITÁCORA DEL SISTEMA")
    for evento in sistema.bitacora.obtener_historial():
        print(f"  * {evento}")
    print("=" * 78 + "\n")


if __name__ == "__main__":
    main()

