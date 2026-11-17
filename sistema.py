"""
Módulo de Gestión de Contenedores, Bitácora y Sistema Principal (Opción C: Dispositivos en red).

Reparto de Trabajo en este archivo:
- Diego Barba Mier Y Concha (225996364):
    * Implementación completa de `registrar(objeto)` y `listar()` en `SistemaRed`.
    * Validaciones de registro (campos vacíos, formato de identificador y duplicados).
- Jesús Emmanuel Huante Jiménez (222479008):
    * Implementación completa para `RangoIP`, `SegmentoRed`, `Bitacora`,
      `asignar(identificador, clave)`, `guardar(sistema, ruta)` y `cargar(sistema, ruta)`.
"""

from typing import Optional
from ipaddress import ip_address
from datetime import datetime
import json
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
        try:
            ip_evaluar = ip_address(ip)
            inicio = ip_address(self._ip_inicio)
            fin = ip_address(self._ip_fin)
            return inicio <= ip_evaluar <= fin
        except ValueError:
            return False

    def obtener_total_direcciones(self) -> int:
        """
        Calcula el total de direcciones disponibles dentro del rango.

        Returns:
            int: Cantidad total de direcciones IP en el rango.
        """
        inicio = int(ip_address(self._ip_inicio))
        fin = int(ip_address(self._ip_fin))
        return fin - inicio + 1

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
        if not id_segmento or not id_segmento.strip():
            raise ValueError("Rechazado: El identificador del segmento no puede estar vacío.")
        if capacidad_maxima <= 0:
            raise ValueError("Rechazado: La capacidad máxima del segmento debe ser mayor a 0.")
        
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
        return len(self._dispositivos)

    def verificar_capacidad(self) -> bool:
        """
        Verifica si el segmento de red aún tiene cupo disponible para un nuevo dispositivo.

        Returns:
            bool: True si `obtener_ocupacion_actual() < self._capacidad_maxima`, False si ya está lleno.
        """
        return self.obtener_ocupacion_actual() < self._capacidad_maxima

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
        # Paso 1: Revisar que el dispositivo no esté repetido en este mismo segmento
        ids_actuales = [d.id_dispositivo for d in self._dispositivos]
        if dispositivo.id_dispositivo in ids_actuales:
            raise ValueError(
                "Rechazado: El dispositivo ya ocupa una dirección en este segmento de red."
            )

        # Paso 2: Revisar que aún quede lugar disponible en el segmento
        if not self.verificar_capacidad():
            raise ValueError(
                "Rechazado: Se superó el cupo máximo permitido en el segmento de red."
            )

        # Paso 3: Si el segmento tiene un RangoIP definido, validar la IP del equipo
        if self._rango_ip is not None and not self._rango_ip.ip_esta_en_rango(dispositivo.direccion_ip):
            raise ValueError(
                f"Rechazado: La IP '{dispositivo.direccion_ip}' está fuera del rango permitido "
                f"({self._rango_ip.ip_inicio} - {self._rango_ip.ip_fin})."
            )

        # Paso 4: Si pasó todos los filtros, guardarlo en la lista y confirmar
        self._dispositivos.append(dispositivo)

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
        if descripcion_evento and isinstance(descripcion_evento, str):
            marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._eventos.append(f"[{marca_tiempo}] {descripcion_evento.strip()}")
            
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
        # Validación 1: Verificar que el segmento de red exista en el sistema
        if clave not in self._segmentos:
            raise ValueError(
                f"Rechazado: La clave del contenedor '{clave}' no fue encontrada en el sistema."
            )

        # Validación 2: Verificar que el dispositivo ya haya sido dado de alta con registrar()
        if identificador not in self._dispositivos:
            raise ValueError(
                f"Rechazado: El dispositivo '{identificador}' no está registrado. "
                "Debes darlo de alta previamente mediante registrar()."
            )

        # Recuperamos ambos objetos desde sus diccionarios
        segmento = self._segmentos[clave]
        dispositivo = self._dispositivos[identificador]

        # Validaciones 3 y 4: Delegamos en el segmento (él revisa duplicados, cupo y rango IP)
        segmento.agregar_dispositivo(dispositivo)

        # Si agregar_dispositivo no lanzó ningún ValueError, registramos el éxito en la bitácora
        self._bitacora.registrar_evento(
            f"ASIGNACIÓN: Dispositivo {dispositivo.id_dispositivo} ({dispositivo.nombre_host}) "
            f"asignado al segmento {segmento.id_segmento} ({segmento.nombre_segmento})."
        )
        return True

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
    # 1. Convertir cada dispositivo a diccionario usando el método de Diego
    lista_dispositivos = [
        disp.obtener_resumen() for disp in sistema.dispositivos.values()
    ]

    # 2. Convertir cada segmento (incluyendo su RangoIP y los IDs de sus dispositivos asignados)
    lista_segmentos = []
    for seg in sistema.segmentos.values():
        rango_dict = None
        if seg.rango_ip is not None:
            rango_dict = {
                "ip_inicio": seg.rango_ip.ip_inicio,
                "ip_fin": seg.rango_ip.ip_fin,
                "mascara_subred": seg.rango_ip.mascara_subred,
            }

        lista_segmentos.append(
            {
                "id_segmento": seg.id_segmento,
                "nombre_segmento": seg.nombre_segmento,
                "capacidad_maxima": seg.capacidad_maxima,
                "rango_ip": rango_dict,
                "dispositivos_asignados": [d.id_dispositivo for d in seg.dispositivos],
            }
        )

    # 3. Armar el paquete completo del sistema
    datos_sistema = {
        "dispositivos": lista_dispositivos,
        "segmentos": lista_segmentos,
        "bitacora": sistema.bitacora.obtener_historial(),
    }

    # 4. Escribir en el archivo JSON
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos_sistema, archivo, indent=4, ensure_ascii=False)

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
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except FileNotFoundError:
        return False

    # Limpiamos el estado actual antes de reconstruir para evitar duplicados
    sistema._dispositivos.clear()
    sistema._segmentos.clear()
    sistema._bitacora._eventos.clear()

    # 1. Reconstruir todos los dispositivos y registrarlos en el sistema
    for item in datos.get("dispositivos", []):
        # Reconstruir responsable (puede venir como dict de Responsable o como str)
        resp_raw = item["responsable"]
        if isinstance(resp_raw, dict):
            responsable = Responsable(
                id_empleado=resp_raw["id_empleado"],
                nombre=resp_raw["nombre"],
                correo=resp_raw.get("correo", ""),
                departamento=resp_raw.get("departamento", ""),
            )
        else:
            responsable = resp_raw

        tipo = item.get("tipo_clase")
        if tipo == "EquipoPersonal":
            dispositivo = EquipoPersonal(
                id_dispositivo=item["id_dispositivo"],
                nombre_host=item["nombre_host"],
                direccion_mac=item["direccion_mac"],
                direccion_ip=item["direccion_ip"],
                responsable=responsable,
                tipo_equipo=item["tipo_equipo"],
                sistema_operativo=item["sistema_operativo"],
            )
        elif tipo == "Servidor":
            dispositivo = Servidor(
                id_dispositivo=item["id_dispositivo"],
                nombre_host=item["nombre_host"],
                direccion_mac=item["direccion_mac"],
                direccion_ip=item["direccion_ip"],
                responsable=responsable,
                rol_servidor=item["rol_servidor"],
                puerto_servicio=int(item["puerto_servicio"]),
                es_critico=bool(item.get("es_critico", False)),
            )
        else:
            dispositivo = Dispositivo(
                id_dispositivo=item["id_dispositivo"],
                nombre_host=item["nombre_host"],
                direccion_mac=item["direccion_mac"],
                direccion_ip=item["direccion_ip"],
                responsable=responsable,
            )

        sistema.registrar(dispositivo)

    # 2. Reconstruir los segmentos de red y re-asignar sus dispositivos
    for seg_data in datos.get("segmentos", []):
        rango_obj = None
        if seg_data.get("rango_ip") is not None:
            r = seg_data["rango_ip"]
            rango_obj = RangoIP(
                ip_inicio=r["ip_inicio"],
                ip_fin=r["ip_fin"],
                mascara_subred=r["mascara_subred"],
            )

        segmento = SegmentoRed(
            id_segmento=seg_data["id_segmento"],
            nombre_segmento=seg_data["nombre_segmento"],
            capacidad_maxima=int(seg_data["capacidad_maxima"]),
            rango_ip=rango_obj,
        )
        sistema.agregar_segmento(segmento)

        # Volver a vincular los dispositivos que pertenecían a este segmento
        for id_disp in seg_data.get("dispositivos_asignados", []):
            if id_disp in sistema.dispositivos:
                sistema.asignar(id_disp, segmento.id_segmento)

    # 3. Restaurar el historial exacto de la bitácora que estaba guardado
    if "bitacora" in datos:
        sistema._bitacora._eventos = list(datos["bitacora"])

    return True