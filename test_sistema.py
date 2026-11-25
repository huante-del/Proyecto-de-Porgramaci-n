"""
Suite de Pruebas Automáticas — Sistema de Gestión de Dispositivos en Red (Opción C).

Ejecución:
    python3 -m unittest discover -v
    python3 -m unittest test_sistema.py -v
"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from modelos import Dispositivo, EquipoPersonal, Responsable, Servidor
from sistema import Bitacora, RangoIP, SegmentoRed, SistemaRed, cargar, guardar


class TestModelosDispositivos(unittest.TestCase):
    """Pruebas unitarias para Responsable, Dispositivo, EquipoPersonal y Servidor."""

    def setUp(self) -> None:
        self.resp = Responsable(
            id_empleado="EMP-101",
            nombre="Diego Barba",
            correo="diego.barba@alumnos.udg.mx",
            departamento="Infraestructura TI",
        )

    def test_crear_responsable_y_actualizar_contacto(self) -> None:
        self.assertEqual(self.resp.id_empleado, "EMP-101")
        self.assertEqual(self.resp.nombre, "Diego Barba")
        self.resp.actualizar_contacto("nuevo@udg.mx")
        self.assertEqual(self.resp.correo, "nuevo@udg.mx")

    def test_responsable_invalido_lanza_error(self) -> None:
        with self.assertRaises(ValueError):
            Responsable("EMP-01", "   ")
        with self.assertRaises(ValueError):
            Responsable("", "Juan Pérez")
        with self.assertRaises(ValueError):
            self.resp.actualizar_contacto("correo-sin-arroba")

    def test_crear_equipo_personal_y_polimorfismo(self) -> None:
        equipo = EquipoPersonal(
            id_dispositivo="EQP-0001",
            nombre_host="laptop-dev",
            direccion_mac="00:1a:2b:3c:4d:5e",
            direccion_ip="192.168.10.15",
            responsable=self.resp,
            tipo_equipo="Laptop",
            sistema_operativo="Ubuntu 24.04",
        )
        self.assertTrue(equipo.validar_identificador())
        self.assertTrue(equipo.solicitar_acceso_vpn())
        self.assertEqual(equipo.direccion_mac, "00:1A:2B:3C:4D:5E")
        self.assertIn("Equipo Personal - Laptop", equipo.describir())
        self.assertIn("Ubuntu 24.04", equipo.describir())
        self.assertEqual(equipo.obtener_resumen()["tipo_clase"], "EquipoPersonal")

    def test_crear_servidor_y_polimorfismo(self) -> None:
        servidor = Servidor(
            id_dispositivo="SRV-0001",
            nombre_host="srv-db",
            direccion_mac="00:50:56:C0:00:08",
            direccion_ip="10.0.1.10",
            responsable="Administrador TI",
            rol_servidor="Base de Datos",
            puerto_servicio=5432,
            es_critico=True,
        )
        self.assertTrue(servidor.validar_identificador())
        self.assertIn("Servidor - Base de Datos", servidor.describir())
        self.assertIn("5432", servidor.describir())
        self.assertIn("CRÍTICO", servidor.ejecutar_diagnostico())
        self.assertEqual(servidor.obtener_resumen()["tipo_clase"], "Servidor")

    def test_rechaza_responsable_en_blanco(self) -> None:
        for resp_invalido in ("", "   ", None):
            with self.subTest(responsable=resp_invalido):
                with self.assertRaises(ValueError):
                    EquipoPersonal(
                        id_dispositivo="EQP-0002",
                        nombre_host="pc-test",
                        direccion_mac="AA:BB:CC:DD:EE:FF",
                        direccion_ip="192.168.1.10",
                        responsable=resp_invalido,  # type: ignore[arg-type]
                        tipo_equipo="Desktop",
                        sistema_operativo="Windows 11",
                    )

    def test_rechaza_formato_identificador_incorrecto(self) -> None:
        ids_invalidos = ["", "PC-99", "DEV-12", "DEV-12345", "XXX-0001", "DEV0001", "dev-0001"]
        for id_malo in ids_invalidos:
            with self.subTest(id_dispositivo=id_malo):
                with self.assertRaises(ValueError):
                    Servidor(
                        id_dispositivo=id_malo,
                        nombre_host="srv-bad",
                        direccion_mac="AA:BB:CC:DD:EE:01",
                        direccion_ip="10.0.1.20",
                        responsable=self.resp,
                        rol_servidor="Web",
                        puerto_servicio=80,
                    )

    def test_rechaza_puerto_servidor_fuera_de_rango(self) -> None:
        for puerto in (0, -1, 65536, True):
            with self.subTest(puerto=puerto):
                with self.assertRaises(ValueError):
                    Servidor(
                        id_dispositivo="SRV-0099",
                        nombre_host="srv-puerto",
                        direccion_mac="AA:BB:CC:DD:EE:02",
                        direccion_ip="10.0.1.25",
                        responsable=self.resp,
                        rol_servidor="API",
                        puerto_servicio=puerto,  # type: ignore[arg-type]
                    )


class TestSistemaRedRegistroYListado(unittest.TestCase):
    """Pruebas unitarias para registrar() (dispositivos y segmentos) y listar()."""

    def setUp(self) -> None:
        self.sistema = SistemaRed()
        self.equipo = EquipoPersonal(
            id_dispositivo="EQP-0001",
            nombre_host="laptop-1",
            direccion_mac="00:1A:2B:3C:4D:5E",
            direccion_ip="192.168.10.15",
            responsable="Diego Barba",
            tipo_equipo="Laptop",
            sistema_operativo="Ubuntu 24.04",
        )
        self.servidor = Servidor(
            id_dispositivo="SRV-0001",
            nombre_host="srv-web",
            direccion_mac="00:50:56:C0:00:08",
            direccion_ip="192.168.10.20",
            responsable="Emmanuel Huante",
            rol_servidor="Web",
            puerto_servicio=443,
            es_critico=True,
        )
        self.segmento = SegmentoRed(
            id_segmento="SEG-LAN1",
            nombre_segmento="Red Piso 1",
            capacidad_maxima=2,
            rango_ip=RangoIP("192.168.10.1", "192.168.10.254", "255.255.255.0"),
        )

    def test_registrar_dispositivos_y_segmento(self) -> None:
        self.assertTrue(self.sistema.registrar(self.equipo))
        self.assertTrue(self.sistema.registrar(self.servidor))
        self.assertTrue(self.sistema.registrar(self.segmento))

        self.assertIn("EQP-0001", self.sistema.dispositivos)
        self.assertIn("SRV-0001", self.sistema.dispositivos)
        self.assertIn("SEG-LAN1", self.sistema.segmentos)

    def test_registrar_duplicados_lanza_value_error(self) -> None:
        self.sistema.registrar(self.equipo)
        with self.assertRaises(ValueError):
            self.sistema.registrar(self.equipo)

        self.sistema.registrar(self.segmento)
        with self.assertRaises(ValueError):
            self.sistema.registrar(self.segmento)

    def test_registrar_tipo_invalido_lanza_type_error(self) -> None:
        with self.assertRaises(TypeError):
            self.sistema.registrar("no_es_un_objeto_valido")  # type: ignore[arg-type]

    def test_listar_imprime_y_retorna_descripciones(self) -> None:
        buffer_vacio = io.StringIO()
        with redirect_stdout(buffer_vacio):
            resultado_vacio = self.sistema.listar()
        self.assertEqual(resultado_vacio, [])
        self.assertIn("No hay dispositivos registrados", buffer_vacio.getvalue())

        self.sistema.registrar(self.equipo)
        self.sistema.registrar(self.servidor)

        buffer_con_datos = io.StringIO()
        with redirect_stdout(buffer_con_datos):
            resultado = self.sistema.listar()

        salida = buffer_con_datos.getvalue()
        self.assertEqual(len(resultado), 2)
        self.assertIn("EQP-0001", salida)
        self.assertIn("SRV-0001", salida)
        self.assertIn("Equipo Personal - Laptop", salida)
        self.assertIn("Servidor - Web", salida)


class TestContenedoresYAsignacion(unittest.TestCase):
    """Pruebas unitarias para RangoIP, SegmentoRed y SistemaRed.asignar()."""

    def setUp(self) -> None:
        self.sistema = SistemaRed()
        self.rango = RangoIP("192.168.10.1", "192.168.10.50", "255.255.255.0")
        self.segmento = SegmentoRed("SEG-01", "LAN Oficina", 2, self.rango)
        self.sistema.registrar(self.segmento)

        self.disp1 = EquipoPersonal(
            "EQP-0001", "pc-1", "AA:BB:CC:00:00:01", "192.168.10.10", "Ana", "Laptop", "Ubuntu"
        )
        self.disp2 = EquipoPersonal(
            "DEV-0002", "pc-2", "AA:BB:CC:00:00:02", "192.168.10.11", "Luis", "Desktop", "Windows"
        )
        self.disp3 = EquipoPersonal(
            "EQP-0003", "pc-3", "AA:BB:CC:00:00:03", "192.168.10.12", "Sofía", "Laptop", "Fedora"
        )
        self.disp_fuera_ip = Servidor(
            "SRV-0010", "srv-dmz", "AA:BB:CC:00:00:10", "10.0.0.5", "Admin", "Web", 443
        )

        for d in (self.disp1, self.disp2, self.disp3, self.disp_fuera_ip):
            self.sistema.registrar(d)

    def test_rango_ip(self) -> None:
        self.assertTrue(self.rango.ip_esta_en_rango("192.168.10.10"))
        self.assertFalse(self.rango.ip_esta_en_rango("10.0.0.1"))
        self.assertFalse(self.rango.ip_esta_en_rango("ip-invalida"))
        self.assertEqual(self.rango.obtener_total_direcciones(), 50)

    def test_asignacion_exitosa_y_ocupacion(self) -> None:
        self.assertTrue(self.sistema.asignar("EQP-0001", "SEG-01"))
        self.assertEqual(self.segmento.obtener_ocupacion_actual(), 1)
        self.assertTrue(self.segmento.verificar_capacidad())

        self.assertTrue(self.sistema.asignar("DEV-0002", "SEG-01"))
        self.assertEqual(self.segmento.obtener_ocupacion_actual(), 2)
        self.assertFalse(self.segmento.verificar_capacidad())

    def test_asignar_segmento_inexistente_rechaza(self) -> None:
        with self.assertRaises(ValueError):
            self.sistema.asignar("EQP-0001", "SEG-INEXISTENTE")

    def test_asignar_dispositivo_no_registrado_rechaza(self) -> None:
        with self.assertRaises(ValueError):
            self.sistema.asignar("DEV-9999", "SEG-01")

    def test_asignar_dispositivo_duplicado_en_segmento_rechaza(self) -> None:
        self.sistema.asignar("EQP-0001", "SEG-01")
        with self.assertRaises(ValueError):
            self.sistema.asignar("EQP-0001", "SEG-01")

    def test_asignar_superando_capacidad_rechaza(self) -> None:
        self.sistema.asignar("EQP-0001", "SEG-01")
        self.sistema.asignar("DEV-0002", "SEG-01")
        with self.assertRaises(ValueError):
            self.sistema.asignar("EQP-0003", "SEG-01")

    def test_asignar_ip_fuera_de_rango_rechaza(self) -> None:
        with self.assertRaises(ValueError):
            self.sistema.asignar("SRV-0010", "SEG-01")


class TestPersistenciaYArranqueLimpio(unittest.TestCase):
    """Pruebas unitarias para guardar(), cargar() y arranque limpio."""

    def test_guardar_y_cargar_estado_completo(self) -> None:
        sistema = SistemaRed()
        resp = Responsable("EMP-01", "Diego Barba", "diego@udg.mx", "TI")
        eq = EquipoPersonal(
            "EQP-0001", "host-eq", "00:11:22:33:44:55", "192.168.1.10", resp, "Laptop", "Ubuntu"
        )
        srv = Servidor(
            "SRV-0001", "host-srv", "00:11:22:33:44:66", "192.168.1.20", "Emmanuel", "DB", 5432, True
        )
        seg = SegmentoRed(
            "SEG-01", "Red Principal", 5, RangoIP("192.168.1.1", "192.168.1.100", "255.255.255.0")
        )

        sistema.registrar(eq)
        sistema.registrar(srv)
        sistema.registrar(seg)
        sistema.asignar("EQP-0001", "SEG-01")
        sistema.asignar("SRV-0001", "SEG-01")

        with tempfile.TemporaryDirectory() as tmpdir:
            ruta = os.path.join(tmpdir, "estado_test.json")
            guardar(sistema, ruta)
            self.assertTrue(os.path.exists(ruta))

            sistema_nuevo = SistemaRed()
            self.assertTrue(cargar(sistema_nuevo, ruta))
            self.assertEqual(len(sistema_nuevo.dispositivos), 2)
            self.assertEqual(len(sistema_nuevo.segmentos), 1)
            self.assertEqual(sistema_nuevo.segmentos["SEG-01"].obtener_ocupacion_actual(), 2)
            self.assertGreaterEqual(len(sistema_nuevo.bitacora.obtener_historial()), 5)
            self.assertIsInstance(sistema_nuevo.dispositivos["EQP-0001"], EquipoPersonal)
            self.assertIsInstance(sistema_nuevo.dispositivos["SRV-0001"], Servidor)

    def test_arranque_limpio_sin_archivo_previo(self) -> None:
        sistema = SistemaRed()
        with tempfile.TemporaryDirectory() as tmpdir:
            ruta_inexistente = os.path.join(tmpdir, "no_existe.json")
            self.assertFalse(cargar(sistema, ruta_inexistente))
            self.assertEqual(len(sistema.dispositivos), 0)
            self.assertEqual(len(sistema.segmentos), 0)


if __name__ == "__main__":
    unittest.main()
