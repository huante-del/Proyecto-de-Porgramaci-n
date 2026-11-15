"""
Módulo de Gestión de Contenedores, Bitácora y Sistema Principal (Opción C: Dispositivos en red).

Reparto de Trabajo en este archivo:
- Diego Barba Mier Y Concha (225996364):
    * Implementación completa de `registrar(objeto)` y `listar()` en `SistemaRed`.
    * Validaciones de registro (campos vacíos, formato de identificador y duplicados).
- Jesús Emmanuel Huante Jiménez (222479008):
    * Cimientos y esqueletos guiados (`# TODO`) para `RangoIP`, `SegmentoRed`, `Bitacora`,
      `asignar(identificador, clave)`, `guardar(sistema, ruta)` y `cargar(sistema, ruta)`.
"""

from typing import Optional
from modelos import Dispositivo, EquipoPersonal, Servidor, Responsable


# =====================================================================
# SECCIÓN DE EMMANUEL HUANTE: Cimientos de RangoIP, SegmentoRed y Bitacora
# =====================================================================


class RangoIP:
    """
    Representa el rango de direcciones IPv4 y máscara de subred asociado por
    composición (TIENE-UNA) a un SegmentoRed.

    [Responsabilidad de: Jesús Emmanuel Huante Jiménez]
    """

    def __init__(self, ip_inicio: str, ip_fin: str, mascara_subred: str) -> None:
        """
        Inicializa un RangoIP con sus atributos encapsulados.

        Args:
            ip_inicio (str): Primera dirección IP del rango (ej. '192.168.1.1').
            ip_fin (str): Última dirección IP del rango (ej. '192.168.1.254').
            mascara_subred (str): Máscara de subred (ej. '255.255.255.0').
        """
        self._ip_inicio: str = ip_inicio
        self._ip_fin: str = ip_fin
        self._mascara_subred: str = mascara_subred

    @property
    def ip_inicio(self) -> str:
        """Devuelve la IP inicial del rango."""
        return self._ip_inicio

    @property
    def ip_fin(self) -> str:
        """Devuelve la IP final del rango."""
        return self._ip_fin

    @property
    def mascara_subred(self) -> str:
        """Devuelve la máscara de subred."""
        return self._mascara_subred

    def ip_esta_en_rango(self, ip: str) -> bool:
        """
        Verifica si una dirección IP se encuentra dentro del rango definido.

        Args:
            ip (str): Dirección IP a evaluar.

        Returns:
            bool: True si la IP está en el rango, False en caso contrario.
        """
        # TODO (Emmanuel): Implementar la verificación de si `ip` está entre `_ip_inicio` y `_ip_fin`
        # Sugerencia: Puedes usar el módulo estándar `ipaddress.ip_address(ip)` de Python:
        #   return ip_address(self._ip_inicio) <= ip_address(ip) <= ip_address(self._ip_fin)
        raise NotImplementedError("TODO (Emmanuel): Implementar RangoIP.ip_esta_en_rango(ip)")

    def obtener_total_direcciones(self) -> int:
        """
        Calcula el total de direcciones disponibles dentro del rango.

        Returns:
            int: Cantidad total de direcciones IP en el rango.
        """
        # TODO (Emmanuel): Calcular y retornar la cantidad de direcciones entre `_ip_inicio` y `_ip_fin`
        # Sugerencia: int(ip_address(self._ip_fin)) - int(ip_address(self._ip_inicio)) + 1
        raise NotImplementedError("TODO (Emmanuel): Implementar RangoIP.obtener_total_direcciones()")


class SegmentoRed:
    """
    Clase Contenedor que controla el cupo máximo de direcciones disponibles
    para un grupo de conexiones (Dispositivos) en la red.

    [Responsabilidad de: Jesús Emmanuel Huante Jiménez]
    """

    def __init__(
        self,
        id_segmento: str,
        nombre_segmento: str,
        capacidad_maxima: int,
        rango_ip: Optional[RangoIP] = None,
    ) -> None:
        """
        Inicializa un SegmentoRed con sus atributos encapsulados.

        Args:
            id_segmento (str): Clave única del segmento (ej. 'SEG-LAN1').
            nombre_segmento (str): Nombre descriptivo del segmento (ej. 'Red Corporativa Piso 1').
            capacidad_maxima (int): Límite máximo de dispositivos que puede alojar.
            rango_ip (RangoIP, opcional): Objeto RangoIP compuesto en este segmento.
        """
        # TODO (Emmanuel): Si deseas agregar validaciones adicionales al crear el segmento
        # (ej. que capacidad_maxima > 0 e id_segmento no esté vacío), hazlo aquí.
        self._id_segmento: str = id_segmento
        self._nombre_segmento: str = nombre_segmento
        self._capacidad_maxima: int = capacidad_maxima
        self._rango_ip: Optional[RangoIP] = rango_ip
        self._dispositivos: list[Dispositivo] = []

    @property
    def id_segmento(self) -> str:
        """Devuelve la clave/identificador del segmento de red."""
        return self._id_segmento

    @property
    def nombre_segmento(self) -> str:
        """Devuelve el nombre del segmento de red."""
        return self._nombre_segmento

    @property
    def capacidad_maxima(self) -> int:
        """Devuelve la capacidad máxima de dispositivos del segmento."""
        return self._capacidad_maxima

    @property
    def rango_ip(self) -> Optional[RangoIP]:
        """Devuelve el objeto RangoIP asociado al segmento."""
        return self._rango_ip

    @property
    def dispositivos(self) -> list[Dispositivo]:
        """Devuelve una copia de la lista de dispositivos asignados al segmento."""
        return list(self._dispositivos)

    def obtener_ocupacion_actual(self) -> int:
        """
        Retorna la cantidad de dispositivos actualmente asignados al segmento.

        Returns:
            int: Número de dispositivos en `self._dispositivos`.
        """
        # TODO (Emmanuel): Retornar `len(self._dispositivos)`
        raise NotImplementedError("TODO (Emmanuel): Implementar SegmentoRed.obtener_ocupacion_actual()")

    def verificar_capacidad(self) -> bool:
        """
        Verifica si el segmento de red aún tiene cupo disponible para un nuevo dispositivo.

        Returns:
            bool: True si `obtener_ocupacion_actual() < self._capacidad_maxima`, False si ya está lleno.
        """
        # TODO (Emmanuel): Comparar la ocupación actual contra `self._capacidad_maxima`
        raise NotImplementedError("TODO (Emmanuel): Implementar SegmentoRed.verificar_capacidad()")

    def agregar_dispositivo(self, dispositivo: Dispositivo) -> bool:
        """
        Agrega un dispositivo al segmento de red validando las reglas de negocio.

        Args:
            dispositivo (Dispositivo): Objeto Dispositivo (EquipoPersonal o Servidor) a asignar.

        Returns:
            bool: True si se asignó correctamente.

        Raises:
            ValueError:
                1. Si el dispositivo ya está asignado a este mismo segmento
                   (Tabla 5: "Rechazarlo indicando que el dispositivo ya ocupa una dirección ahí").
                2. Si el segmento ya llegó a su límite de direcciones
                   (Tabla 5: "Rechazarlo informando que se superó el cupo máximo permitido").
        """
        # TODO (Emmanuel): Implementar la lógica de asignación dentro del contenedor:
        # Paso 1: Verificar si `dispositivo.id_dispositivo` ya está en `[d.id_dispositivo for d in self._dispositivos]`.
        #         Si ya está, lanzar `ValueError("Rechazado: El dispositivo ya ocupa una dirección en este segmento de red.")`
        # Paso 2: Verificar si `not self.verificar_capacidad()`.
        #         Si no hay cupo, lanzar `ValueError("Rechazado: Se superó el cupo máximo permitido en el segmento de red.")`
        # Paso 3: Hacer `self._dispositivos.append(dispositivo)` y retornar `True`.
        raise NotImplementedError("TODO (Emmanuel): Implementar SegmentoRed.agregar_dispositivo(dispositivo)")


class Bitacora:
    """
    Persiste y gestiona el historial de eventos para delegar la tarea del registro
    de operaciones dentro del sistema.

    [Responsabilidad de: Jesús Emmanuel Huante Jiménez]
    """

    def __init__(self) -> None:
        """Inicializa la bitácora con una lista vacía de eventos."""
        self._eventos: list[str] = []

    @property
    def eventos(self) -> list[str]:
        """Devuelve la lista de eventos registrados en la bitácora."""
        return list(self._eventos)

    def registrar_evento(self, descripcion_evento: str) -> None:
        """
        Agrega una nueva entrada al historial de eventos de la bitácora.

        Args:
            descripcion_evento (str): Mensaje descriptivo del evento ocurrido.
        """
        # TODO (Emmanuel): Puedes enriquecer este método con fecha/hora (`datetime.now()`)
        # o persistirlo en archivo si lo deseas. Por ahora almacena en memoria para no bloquear `registrar()`.
        if descripcion_evento and isinstance(descripcion_evento, str):
            self._eventos.append(descripcion_evento.strip())

    def obtener_historial(self) -> list[str]:
        """
        Devuelve todo el historial de eventos registrados.

        Returns:
            list[str]: Lista de eventos.
        """
        return list(self._eventos)


# =====================================================================
# CLASE ORQUESTADORA: SistemaRed (Contrato Principal)
# =====================================================================


class SistemaRed:
    """
    Orquesta las operaciones principales del contrato aplicando las reglas de negocio:
    - registrar(objeto) y listar() -> Implementados por Diego Barba.
    - asignar(identificador, clave), guardar(ruta) y cargar(ruta) -> Cimientos para Emmanuel Huante.
    """

    def __init__(self) -> None:
        """
        Inicializa el sistema de red con su catálogo de dispositivos,
        catálogo de segmentos de red y bitácora de eventos.
        """
        self._dispositivos: dict[str, Dispositivo] = {}
        self._segmentos: dict[str, SegmentoRed] = {}
        self._bitacora: Bitacora = Bitacora()

    @property
    def dispositivos(self) -> dict[str, Dispositivo]:
        """Devuelve una copia del diccionario de dispositivos dados de alta."""
        return dict(self._dispositivos)

    @property
    def segmentos(self) -> dict[str, SegmentoRed]:
        """Devuelve una copia del diccionario de segmentos de red registrados."""
        return dict(self._segmentos)

    @property
    def bitacora(self) -> Bitacora:
        """Devuelve la instancia de la bitácora del sistema."""
        return self._bitacora

    # -----------------------------------------------------------------
    # MÉTODOS DEL CONTRATO: DIEGO BARBA (Modelado y Operaciones Base)
    # -----------------------------------------------------------------

    def registrar(self, objeto: Dispositivo) -> bool:
        """
        Registra (da de alta) un dispositivo en el sistema aplicando todas las
        validaciones de negocio correspondientes al registro.

        Validaciones aplicadas (Sección 5 del Hito 1):
        1. Verifica que `objeto` sea una instancia válida de `Dispositivo` (o sus clases hijas).
        2. Verifica que el responsable o dueño no esté en blanco.
        3. Verifica que el identificador tenga el formato y longitud esperados (8 caracteres: DEV-/SRV-/EQP- + 4 dígitos).
        4. Previene identificadores duplicados rechazando si el `id_dispositivo` ya fue guardado previamente.

        Args:
            objeto (Dispositivo): Instancia de Dispositivo, EquipoPersonal o Servidor.

        Returns:
            bool: True si el dispositivo fue registrado exitosamente.

        Raises:
            TypeError: Si el objeto recibido no es una instancia de Dispositivo.
            ValueError: Si falla cualquiera de las validaciones de negocio del registro.
        """
        if not isinstance(objeto, Dispositivo):
            raise TypeError(
                "Rechazado: Solo se pueden registrar objetos que hereden de la clase 'Dispositivo' "
                "(como EquipoPersonal o Servidor)."
            )

        # Re-verificación defensiva de responsable obligatorio
        if not objeto.responsable or (
            isinstance(objeto.responsable, str) and not objeto.responsable.strip()
        ):
            raise ValueError(
                "Rechazado: El campo responsable o dueño es obligatorio y no puede dejarse en blanco."
            )

        # Re-verificación defensiva del formato del identificador
        if not objeto.validar_identificador():
            raise ValueError(
                f"Rechazado: El identificador '{objeto.id_dispositivo}' tiene un formato incorrecto. "
                "Se espera una longitud exacta de 8 caracteres con la estructura 'PREFIJO-0000' "
                "(prefijos válidos: DEV-, SRV-, EQP- seguidos de 4 dígitos)."
            )

        # Validación de prevención de identificadores duplicados en el sistema (Tabla 5 del Hito 1)
        if objeto.id_dispositivo in self._dispositivos:
            raise ValueError(
                f"Rechazado: El identificador '{objeto.id_dispositivo}' ya existe previamente guardado en el sistema. "
                "No se permiten dispositivos con identificadores duplicados."
            )

        # Alta exitosa en el catálogo del sistema y registro en bitácora
        self._dispositivos[objeto.id_dispositivo] = objeto
        self._bitacora.registrar_evento(
            f"ALTA DISPOSITIVO: {objeto.id_dispositivo} ({objeto.nombre_host}) registrado a cargo de {objeto.nombre_responsable}."
        )
        return True

    def listar(self) -> list[str]:
        """
        Lista todos los dispositivos registrados en el sistema invocando
        de manera polimórfica el método `describir()` de cada objeto.

        Returns:
            list[str]: Lista con las descripciones polimórficas de todos los dispositivos registrados.
        """
        return [dispositivo.describir() for dispositivo in self._dispositivos.values()]

    # -----------------------------------------------------------------
    # MÉTODOS AUXILIARES Y DEL CONTRATO: EMMANUEL HUANTE
    # (Gestión de Contenedores y Persistencia)
    # -----------------------------------------------------------------

    def agregar_segmento(self, segmento: SegmentoRed) -> None:
        """
        Registra un contenedor `SegmentoRed` dentro del catálogo de segmentos del sistema.

        Args:
            segmento (SegmentoRed): Instancia de SegmentoRed a dar de alta.
        """
        if not isinstance(segmento, SegmentoRed):
            raise TypeError("Rechazado: El contenedor debe ser una instancia de SegmentoRed.")
        if segmento.id_segmento in self._segmentos:
            raise ValueError(f"Rechazado: El segmento '{segmento.id_segmento}' ya existe en el sistema.")
        self._segmentos[segmento.id_segmento] = segmento

    def asignar(self, identificador: str, clave: str) -> bool:
        """
        Asigna un dispositivo previamente registrado (identificado por `identificador`)
        a un segmento de red existente (identificado por `clave`).

        [Responsabilidad de: Jesús Emmanuel Huante Jiménez]

        Validaciones que debes programar aquí (Sección 5 del Hito 1):
        1. Asignar un dispositivo a un segmento de red inexistente:
           -> Si `clave` no está en `self._segmentos`, rechazarlo con `KeyError` o `ValueError`
              notificando que la clave del contenedor no fue encontrada.
        2. Asignar un equipo que no ha sido dado de alta mediante el método `registrar`:
           -> Si `identificador` no está en `self._dispositivos`, rechazarlo con `ValueError`
              pidiendo registrar el dispositivo previamente.
        3. Asignar un dispositivo a un segmento que ya llegó a su límite de direcciones:
           -> Delegar en `segmento.agregar_dispositivo(dispositivo)` o verificar `segmento.verificar_capacidad()`
              y rechazarlo informando que se superó el cupo máximo permitido.
        4. Asignar un mismo equipo dos veces al mismo segmento de red:
           -> Rechazarlo indicando que el dispositivo ya ocupa una dirección ahí.

        Args:
            identificador (str): ID del dispositivo (ej. 'DEV-0001').
            clave (str): Clave o ID del segmento de red (ej. 'SEG-01').

        Returns:
            bool: True si la asignación fue exitosa.
        """
        # TODO (Emmanuel): Implementar las 4 validaciones de asignación listadas en el docstring
        # y registrar el evento en `self._bitacora.registrar_evento(...)`.
        raise NotImplementedError(
            "TODO (Emmanuel): Implementar SistemaRed.asignar(identificador, clave)"
        )

    def guardar(self, ruta: str) -> None:
        """
        Método de instancia que delega en la función del contrato `guardar(sistema, ruta)`.

        Args:
            ruta (str): Ruta del archivo donde se persistirá el estado del sistema (ej. 'datos_red.json').
        """
        guardar(self, ruta)

    def cargar(self, ruta: str) -> bool:
        """
        Método de instancia que delega en la función del contrato `cargar(sistema, ruta)`.

        Args:
            ruta (str): Ruta del archivo desde donde se cargará el estado del sistema.

        Returns:
            bool: True si se cargaron datos, False si se inició en limpio por no existir el archivo.
        """
        return cargar(self, ruta)


# =====================================================================
# FUNCIONES DEL CONTRATO A NIVEL MÓDULO (Persistencia - Emmanuel Huante)
# =====================================================================


def guardar(sistema: SistemaRed, ruta: str) -> None:
    """
    Guarda el estado actual del sistema (dispositivos, segmentos, asignaciones y bitácora)
    en un archivo en la `ruta` indicada (por ejemplo en formato JSON).

    [Responsabilidad de: Jesús Emmanuel Huante Jiménez]

    Args:
        sistema (SistemaRed): Instancia del sistema de red a persistir.
        ruta (str): Ruta del archivo de salida (ej. 'red_estado.json').
    """
    # TODO (Emmanuel): Implementar la persistencia en archivo (ej. usando `import json`).
    # Pista: Cada `Dispositivo` ya cuenta con el método `.obtener_resumen()` programado por Diego
    # que devuelve un `dict` listo para serializar con `json.dump(..., indent=4, ensure_ascii=False)`.
    raise NotImplementedError("TODO (Emmanuel): Implementar guardar(sistema, ruta)")


def cargar(sistema: SistemaRed, ruta: str) -> bool:
    """
    Carga el estado del sistema desde un archivo en la `ruta` indicada.
    Cumple con la regla de "Arranque Limpio": si el archivo no existe, maneja
    el caso limpiamente sin que el programa colapse.

    [Responsabilidad de: Jesús Emmanuel Huante Jiménez]

    Args:
        sistema (SistemaRed): Instancia del sistema donde se reconstruirán los objetos.
        ruta (str): Ruta del archivo de datos a leer.

    Returns:
        bool: True si el archivo existía y se cargó correctamente;
              False si el archivo no existe (arranque limpio sin colapsar).
    """
    # TODO (Emmanuel): Implementar la lectura desde archivo asegurando el Arranque Limpio:
    # Pista:
    #   try:
    #       with open(ruta, "r", encoding="utf-8") as archivo:
    #           datos = json.load(archivo)
    #           # Reconstruir objetos EquipoPersonal, Servidor y SegmentoRed dentro de `sistema`
    #           return True
    #   except FileNotFoundError:
    #       # Arranque limpio: informar que no hay archivo previo e iniciar con el sistema vacío
    #       return False
    raise NotImplementedError("TODO (Emmanuel): Implementar cargar(sistema, ruta) con Arranque Limpio")

