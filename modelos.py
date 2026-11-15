"""
Módulo de Modelos de Dispositivos y Responsables (Opción C: Dispositivos en red).

Autor de esta sección: Diego Barba Mier Y Concha (225996364)
Incluye:
- Clase Responsable
- Clase Base Dispositivo (con encapsulamiento, validaciones y polimorfismo)
- Clase Hija EquipoPersonal
- Clase Hija Servidor
"""

import re
from typing import Union


class Responsable:
    """
    Representa al empleado o dueño responsable de un dispositivo en la red.
    """

    def __init__(
        self,
        id_empleado: str,
        nombre: str,
        correo: str = "",
        departamento: str = ""
    ) -> None:
        """
        Inicializa un nuevo Responsable validando que sus datos clave no estén vacíos.

        Args:
            id_empleado (str): Identificador del empleado (ej. 'EMP-01').
            nombre (str): Nombre completo del responsable.
            correo (str, opcional): Correo electrónico de contacto.
            departamento (str, opcional): Departamento al que pertenece.

        Raises:
            ValueError: Si el nombre o id_empleado están en blanco.
        """
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError(
                "Error de validación: El nombre del responsable o dueño es un campo obligatorio y no puede dejarse en blanco."
            )
        if not isinstance(id_empleado, str) or not id_empleado.strip():
            raise ValueError(
                "Error de validación: El identificador del empleado responsable es obligatorio."
            )

        self._id_empleado: str = id_empleado.strip()
        self._nombre: str = nombre.strip()
        self._correo: str = correo.strip() if isinstance(correo, str) else ""
        self._departamento: str = departamento.strip() if isinstance(departamento, str) else ""

    @property
    def id_empleado(self) -> str:
        """Devuelve el identificador del empleado."""
        return self._id_empleado

    @property
    def nombre(self) -> str:
        """Devuelve el nombre del responsable."""
        return self._nombre

    @property
    def correo(self) -> str:
        """Devuelve el correo electrónico del responsable."""
        return self._correo

    @property
    def departamento(self) -> str:
        """Devuelve el departamento del responsable."""
        return self._departamento

    def actualizar_contacto(self, correo: str) -> None:
        """
        Actualiza el correo electrónico de contacto del responsable.

        Args:
            correo (str): Nuevo correo electrónico.

        Raises:
            ValueError: Si el correo está vacío o no tiene un formato básico válido.
        """
        if not isinstance(correo, str) or not correo.strip() or "@" not in correo:
            raise ValueError("El correo proporcionado no es válido.")
        self._correo = correo.strip()

    def obtener_resumen(self) -> dict:
        """
        Retorna un diccionario con los datos del responsable para serialización.

        Returns:
            dict: Datos del responsable.
        """
        return {
            "id_empleado": self._id_empleado,
            "nombre": self._nombre,
            "correo": self._correo,
            "departamento": self._departamento,
        }

    def __str__(self) -> str:
        """Representación en cadena del responsable."""
        depto = f" ({self._departamento})" if self._departamento else ""
        return f"{self._nombre} [{self._id_empleado}]{depto}"


class Dispositivo:
    """
    Clase base que define los datos y comportamientos comunes para cualquier
    máquina o equipo conectado a la infraestructura de red.
    """

    # Formato esperado: Prefijo DEV-, SRV- o EQP- seguido de 4 dígitos (8 caracteres en total)
    PATRON_ID = re.compile(r"^(DEV|SRV|EQP)-\d{4}$")

    def __init__(
        self,
        id_dispositivo: str,
        nombre_host: str,
        direccion_mac: str,
        direccion_ip: str,
        responsable: Union["Responsable", str],
    ) -> None:
        """
        Inicializa un dispositivo de red aplicando las validaciones de negocio.

        Args:
            id_dispositivo (str): Identificador único (ej. 'DEV-0001', 'SRV-1024', 'EQP-0010').
            nombre_host (str): Nombre de host del equipo en la red.
            direccion_mac (str): Dirección física MAC del dispositivo.
            direccion_ip (str): Dirección IPv4 asignada al dispositivo.
            responsable (Responsable | str): Objeto Responsable o nombre del dueño responsable.

        Raises:
            ValueError: Si el responsable está en blanco, si el identificador tiene
                        un formato incorrecto o si algún dato obligatorio falta.
        """
        # 1. Validación de responsable o dueño obligatorio (Tabla 5 del Hito 1)
        self._validar_y_asignar_responsable(responsable)

        # 2. Asignación y validación del identificador (Tabla 5 del Hito 1)
        if not isinstance(id_dispositivo, str) or not id_dispositivo.strip():
            raise ValueError(
                "Rechazado: El identificador del dispositivo no puede estar vacío. "
                "Se espera una longitud exacta de 8 caracteres con estructura 'PREFIJO-0000' "
                "(prefijos válidos: DEV-, SRV-, EQP- seguidos de 4 dígitos, ej. DEV-0001)."
            )
        self._id_dispositivo: str = id_dispositivo.strip()
        if not self.validar_identificador():
            raise ValueError(
                f"Rechazado: El identificador '{self._id_dispositivo}' tiene un formato incorrecto. "
                "Se espera una longitud exacta de 8 caracteres con la estructura 'PREFIJO-0000', "
                "donde el prefijo sea 'DEV-', 'SRV-' o 'EQP-' seguido de 4 dígitos numéricos (ej. DEV-0001)."
            )

        # 3. Validación de atributos básicos del dispositivo
        if not isinstance(nombre_host, str) or not nombre_host.strip():
            raise ValueError("Rechazado: El campo 'nombre_host' es obligatorio y no puede estar en blanco.")
        if not isinstance(direccion_mac, str) or not direccion_mac.strip():
            raise ValueError("Rechazado: El campo 'direccion_mac' es obligatorio y no puede estar en blanco.")
        if not isinstance(direccion_ip, str) or not direccion_ip.strip():
            raise ValueError("Rechazado: El campo 'direccion_ip' es obligatorio y no puede estar en blanco.")

        self._nombre_host: str = nombre_host.strip()
        self._direccion_mac: str = direccion_mac.strip().upper()
        self._direccion_ip: str = direccion_ip.strip()

    def _validar_y_asignar_responsable(self, responsable: Union["Responsable", str]) -> None:
        """
        Valida que el responsable o dueño no esté en blanco y lo almacena encapsulado.

        Args:
            responsable (Responsable | str): Instancia de Responsable o cadena con el nombre.

        Raises:
            ValueError: Si el responsable es None o cadena vacía.
        """
        if responsable is None:
            raise ValueError(
                "Rechazado: El campo responsable o dueño es obligatorio y no puede dejarse en blanco."
            )
        if isinstance(responsable, str):
            if not responsable.strip():
                raise ValueError(
                    "Rechazado: El campo responsable o dueño es obligatorio y no puede dejarse en blanco."
                )
            self._responsable: Union[Responsable, str] = responsable.strip()
        elif isinstance(responsable, Responsable):
            if not responsable.nombre.strip():
                raise ValueError(
                    "Rechazado: El campo responsable o dueño es obligatorio y no puede dejarse en blanco."
                )
            self._responsable = responsable
        else:
            raise ValueError(
                "Rechazado: El responsable debe ser un nombre válido (str) o una instancia de la clase Responsable."
            )

    @property
    def id_dispositivo(self) -> str:
        """Devuelve el identificador único del dispositivo."""
        return self._id_dispositivo

    @property
    def nombre_host(self) -> str:
        """Devuelve el nombre de host del dispositivo."""
        return self._nombre_host

    @property
    def direccion_mac(self) -> str:
        """Devuelve la dirección MAC del dispositivo."""
        return self._direccion_mac

    @property
    def direccion_ip(self) -> str:
        """Devuelve la dirección IP del dispositivo."""
        return self._direccion_ip

    @property
    def responsable(self) -> Union[Responsable, str]:
        """Devuelve el responsable asignado al dispositivo."""
        return self._responsable

    @property
    def nombre_responsable(self) -> str:
        """Devuelve el nombre legible del responsable sin importar si es objeto o str."""
        if isinstance(self._responsable, Responsable):
            return str(self._responsable)
        return self._responsable

    def validar_identificador(self) -> bool:
        """
        Verifica si el identificador del dispositivo cumple con el formato oficial:
        Prefijo 'DEV-', 'SRV-' o 'EQP-' seguido de exactamente 4 dígitos (8 caracteres).

        Returns:
            bool: True si el formato es válido, False en caso contrario.
        """
        if not isinstance(self._id_dispositivo, str):
            return False
        return bool(self.PATRON_ID.match(self._id_dispositivo))

    def obtener_resumen(self) -> dict:
        """
        Genera un diccionario con el resumen del estado y atributos del dispositivo.
        Útil para inspección y para la persistencia de datos.

        Returns:
            dict: Diccionario con los atributos principales del dispositivo.
        """
        resp_data = (
            self._responsable.obtener_resumen()
            if isinstance(self._responsable, Responsable)
            else self._responsable
        )
        return {
            "tipo_clase": "Dispositivo",
            "id_dispositivo": self._id_dispositivo,
            "nombre_host": self._nombre_host,
            "direccion_mac": self._direccion_mac,
            "direccion_ip": self._direccion_ip,
            "responsable": resp_data,
        }

    def describir(self) -> str:
        """
        Método polimórfico que devuelve una descripción legible del dispositivo.
        Las clases hijas sobrescriben este método para añadir sus detalles específicos.

        Returns:
            str: Descripción formateada del dispositivo.
        """
        return (
            f"[Dispositivo Base] ID: {self._id_dispositivo} | Host: {self._nombre_host} | "
            f"IP: {self._direccion_ip} | MAC: {self._direccion_mac} | "
            f"Responsable: {self.nombre_responsable}"
        )

    def __str__(self) -> str:
        """Retorna la descripción polimórfica al convertir el objeto a cadena."""
        return self.describir()


class EquipoPersonal(Dispositivo):
    """
    Representa una computadora de uso individual (ej. Laptop, Desktop, Workstation)
    asociada a su respectivo sistema operativo. Hereda de Dispositivo.
    """

    def __init__(
        self,
        id_dispositivo: str,
        nombre_host: str,
        direccion_mac: str,
        direccion_ip: str,
        responsable: Union[Responsable, str],
        tipo_equipo: str,
        sistema_operativo: str,
    ) -> None:
        """
        Inicializa un EquipoPersonal.

        Args:
            id_dispositivo (str): Identificador único (ej. 'EQP-0001' o 'DEV-0001').
            nombre_host (str): Nombre del host en la red.
            direccion_mac (str): Dirección MAC del equipo.
            direccion_ip (str): Dirección IP asignada.
            responsable (Responsable | str): Dueño o responsable del equipo.
            tipo_equipo (str): Tipo de equipo personal (ej. 'Laptop', 'Desktop').
            sistema_operativo (str): Sistema operativo instalado (ej. 'Ubuntu 24.04', 'Windows 11').

        Raises:
            ValueError: Si algún campo obligatorio o validación de la clase base falla.
        """
        super().__init__(
            id_dispositivo=id_dispositivo,
            nombre_host=nombre_host,
            direccion_mac=direccion_mac,
            direccion_ip=direccion_ip,
            responsable=responsable,
        )
        if not isinstance(tipo_equipo, str) or not tipo_equipo.strip():
            raise ValueError("Rechazado: El campo 'tipo_equipo' es obligatorio para un EquipoPersonal.")
        if not isinstance(sistema_operativo, str) or not sistema_operativo.strip():
            raise ValueError("Rechazado: El campo 'sistema_operativo' es obligatorio para un EquipoPersonal.")

        self._tipo_equipo: str = tipo_equipo.strip()
        self._sistema_operativo: str = sistema_operativo.strip()

    @property
    def tipo_equipo(self) -> str:
        """Devuelve el tipo de equipo personal."""
        return self._tipo_equipo

    @property
    def sistema_operativo(self) -> str:
        """Devuelve el sistema operativo del equipo personal."""
        return self._sistema_operativo

    def solicitar_acceso_vpn(self) -> bool:
        """
        Evalúa si el equipo personal cumple con los requisitos para acceso VPN
        (identificador válido, IP asignada y responsable registrado).

        Returns:
            bool: True si el acceso VPN es concedido.
        """
        return bool(self.validar_identificador() and self._direccion_ip and self._responsable)

    def obtener_resumen(self) -> dict:
        """
        Sobrescribe obtener_resumen() añadiendo los atributos propios de EquipoPersonal.

        Returns:
            dict: Resumen completo del equipo personal.
        """
        resumen = super().obtener_resumen()
        resumen.update(
            {
                "tipo_clase": "EquipoPersonal",
                "tipo_equipo": self._tipo_equipo,
                "sistema_operativo": self._sistema_operativo,
            }
        )
        return resumen

    def describir(self) -> str:
        """
        Implementación polimórfica de describir() para EquipoPersonal.

        Returns:
            str: Descripción detallada del equipo personal y su sistema operativo.
        """
        vpn_str = "Habilitada" if self.solicitar_acceso_vpn() else "Denegada"
        return (
            f"[Equipo Personal - {self._tipo_equipo}] ID: {self._id_dispositivo} | "
            f"Host: {self._nombre_host} | SO: {self._sistema_operativo} | "
            f"IP: {self._direccion_ip} | MAC: {self._direccion_mac} | "
            f"VPN: {vpn_str} | Responsable: {self.nombre_responsable}"
        )


class Servidor(Dispositivo):
    """
    Modela una máquina centralizada dedicada a proveer un servicio en específico
    dentro de la infraestructura de red. Hereda de Dispositivo.
    """

    def __init__(
        self,
        id_dispositivo: str,
        nombre_host: str,
        direccion_mac: str,
        direccion_ip: str,
        responsable: Union[Responsable, str],
        rol_servidor: str,
        puerto_servicio: int,
        es_critico: bool = False,
    ) -> None:
        """
        Inicializa un Servidor.

        Args:
            id_dispositivo (str): Identificador único (ej. 'SRV-0001').
            nombre_host (str): Nombre del host servidor.
            direccion_mac (str): Dirección MAC del servidor.
            direccion_ip (str): Dirección IP del servidor.
            responsable (Responsable | str): Administrador responsable del servidor.
            rol_servidor (str): Función principal (ej. 'Base de Datos', 'Servidor Web', 'DNS').
            puerto_servicio (int): Puerto TCP/UDP principal en el que escucha (1 - 65535).
            es_critico (bool, opcional): Indica si el servidor es de misión crítica.

        Raises:
            ValueError: Si los datos base son inválidos o el puerto está fuera de rango (1-65535).
        """
        super().__init__(
            id_dispositivo=id_dispositivo,
            nombre_host=nombre_host,
            direccion_mac=direccion_mac,
            direccion_ip=direccion_ip,
            responsable=responsable,
        )
        if not isinstance(rol_servidor, str) or not rol_servidor.strip():
            raise ValueError("Rechazado: El campo 'rol_servidor' es obligatorio para un Servidor.")
        if not isinstance(puerto_servicio, int) or isinstance(puerto_servicio, bool) or not (1 <= puerto_servicio <= 65535):
            raise ValueError(
                "Rechazado: El 'puerto_servicio' debe ser un número entero válido entre 1 y 65535."
            )

        self._rol_servidor: str = rol_servidor.strip()
        self._puerto_servicio: int = puerto_servicio
        self._es_critico: bool = bool(es_critico)

    @property
    def rol_servidor(self) -> str:
        """Devuelve el rol del servidor."""
        return self._rol_servidor

    @property
    def puerto_servicio(self) -> int:
        """Devuelve el puerto principal del servicio."""
        return self._puerto_servicio

    @property
    def es_critico(self) -> bool:
        """Indica si el servidor es crítico para la infraestructura."""
        return self._es_critico

    def ejecutar_diagnostico(self) -> str:
        """
        Ejecuta una verificación de estado simulada sobre el servidor y su puerto.

        Returns:
            str: Reporte del diagnóstico del servidor.
        """
        nivel = "CRÍTICO" if self._es_critico else "ESTÁNDAR"
        return (
            f"Diagnóstico OK -> Servidor '{self._nombre_host}' ({self._rol_servidor}) "
            f"activo en {self._direccion_ip}:{self._puerto_servicio} [Prioridad: {nivel}]"
        )

    def obtener_resumen(self) -> dict:
        """
        Sobrescribe obtener_resumen() añadiendo los atributos propios de Servidor.

        Returns:
            dict: Resumen completo del servidor.
        """
        resumen = super().obtener_resumen()
        resumen.update(
            {
                "tipo_clase": "Servidor",
                "rol_servidor": self._rol_servidor,
                "puerto_servicio": self._puerto_servicio,
                "es_critico": self._es_critico,
            }
        )
        return resumen

    def describir(self) -> str:
        """
        Implementación polimórfica de describir() para Servidor.

        Returns:
            str: Descripción detallada del servidor, su rol, puerto y criticidad.
        """
        etiqueta_critico = "SÍ (Alta Disponibilidad)" if self._es_critico else "NO"
        return (
            f"[Servidor - {self._rol_servidor}] ID: {self._id_dispositivo} | "
            f"Host: {self._nombre_host} | Puerto: {self._puerto_servicio} | "
            f"Crítico: {etiqueta_critico} | IP: {self._direccion_ip} | "
            f"MAC: {self._direccion_mac} | Responsable: {self.nombre_responsable}"
        )

