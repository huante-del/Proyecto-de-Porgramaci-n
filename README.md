# Sistema de Gestión y Control de Dispositivos en Red

**Universidad de Guadalajara — Proyecto de Programación**  
**Opción Elegida:** C — Dispositivos en red

### Integrantes del Equipo
- **Diego Barba Mier Y Concha** (`225996364`) — *Modelado de Dispositivos, Operaciones Base y Pruebas*
- **Jesús Emmanuel Huante Jiménez** (`222479008`) — *Gestión de Contenedores y Persistencia*

---

## 1. Propósito del Sistema

El sistema registra **equipos personales** (`EquipoPersonal`), **servidores** (`Servidor`) y **segmentos de red** (`SegmentoRed`), y asigna dispositivos a segmentos específicos que los contienen dentro de un límite de direcciones IP. Sirve para llevar control de la infraestructura asegurando:
1. Un **identificador único con formato válido** para cada dispositivo.
2. Un **responsable o dueño obligatorio** asignado a cada máquina.
3. Que **ningún segmento de red exceda su capacidad máxima** ni tenga el mismo dispositivo duplicado.
4. **Persistencia en JSON** con arranque limpio cuando aún no existe archivo de datos.

---

## 2. Arquitectura y Estructura de Archivos

| Archivo | Clase / Contenido | Responsable | Tarea Principal |
| :--- | :--- | :--- | :--- |
| `modelos.py` | `Dispositivo` | Diego Barba | Clase base con atributos encapsulados (`_id_dispositivo`, `_nombre_host`, `_direccion_mac`, `_direccion_ip`, `_responsable`), validaciones de registro y método polimórfico `describir()`. |
| `modelos.py` | `EquipoPersonal` | Diego Barba | Clase hija para computadoras de uso individual (`_tipo_equipo`, `_sistema_operativo`) y `solicitar_acceso_vpn()`. |
| `modelos.py` | `Servidor` | Diego Barba | Clase hija para máquinas dedicadas a servicios (`_rol_servidor`, `_puerto_servicio`, `_es_critico`) y `ejecutar_diagnostico()`. |
| `modelos.py` | `Responsable` | Diego Barba | Modela los datos del empleado o dueño a cargo (`_id_empleado`, `_nombre`, `_correo`, `_departamento`). |
| `sistema.py` | `SegmentoRed` y `RangoIP` | Emmanuel Huante | Contenedor que controla el cupo máximo de direcciones disponibles para un grupo de conexiones y valida el rango IPv4. |
| `sistema.py` | `Bitacora` | Emmanuel Huante | Registra y mantiene el historial de eventos con marca de tiempo. |
| `sistema.py` | `SistemaRed`, `guardar()`, `cargar()` | Ambos | Orquesta las operaciones del contrato: `registrar(objeto)` (acepta `Dispositivo` y `SegmentoRed`), `listar()` (imprime en consola y retorna la lista de descripciones), `asignar(identificador, clave)`, `guardar(sistema, ruta)` y `cargar(sistema, ruta)`. |
| `test_sistema.py` | Suite `unittest` | Equipo | Pruebas automáticas de modelos, validaciones, registro, listado, contenedores, asignación y persistencia. |
| `main.py` | Script demostrativo | Equipo | Recorrido completo de uso y pruebas de validación en consola. |
| `CIERRE.md` | Documento de cierre | Equipo | Reflexión final, cobertura, incidencias resueltas y conclusiones del proyecto. |

---

## 3. Reglas de Validación del Programa

### 3.1 Validaciones de Registro (`modelos.py` y `SistemaRed.registrar`)
- **Soporte de dispositivos y contenedores:** `sistema.registrar(objeto)` acepta instancias de `Dispositivo` (`EquipoPersonal`, `Servidor`) y de `SegmentoRed`; cualquier otro tipo lanza `TypeError`.
- **Responsable obligatorio:** Si se intenta crear o registrar un dispositivo dejando el responsable o dueño en blanco (`""` o `None`), se rechaza con `ValueError`.
- **Formato del identificador:** `id_dispositivo` debe tener una **longitud exacta de 8 caracteres** con estructura `PREFIJO-0000` (`DEV-`, `SRV-` o `EQP-` + 4 dígitos, ej. `DEV-0001`, `SRV-0001`, `EQP-0015`).
- **Prevención de duplicados:** Rechaza con `ValueError` si el `id_dispositivo` o `id_segmento` ya existe en el sistema.

### 3.2 Validaciones de Asignación y Persistencia (`sistema.py`)
- **Segmento inexistente:** `asignar(identificador, clave)` rechaza con `ValueError` si `clave` no existe.
- **Dispositivo no registrado:** Rechaza con `ValueError` si `identificador` no fue dado de alta con `registrar()`.
- **Cupo máximo superado:** Rechaza con `ValueError` si el `SegmentoRed` llegó a su `_capacidad_maxima`.
- **Doble asignación en el mismo segmento:** Rechaza con `ValueError` si el dispositivo ya ocupa una dirección en ese segmento.
- **Rango IP:** Si el segmento tiene `RangoIP`, valida que la IP del dispositivo pertenezca al rango.
- **Arranque limpio:** `cargar(sistema, ruta)` captura `FileNotFoundError` y retorna `False` sin colapsar.

---

## 4. Cómo Ejecutar el Proyecto y las Pruebas

Requisitos: **Python 3.10+** (solo biblioteca estándar).

### Ejecutar el script demostrativo
```bash
python3 main.py
```

### Ejecutar la suite de pruebas automáticas
```bash
python3 -m unittest discover -v
```

### Uso Rápido desde Código Python
```python
from modelos import EquipoPersonal, Servidor, Responsable
from sistema import SistemaRed, SegmentoRed, RangoIP, guardar, cargar

sistema = SistemaRed()

admin = Responsable("EMP-01", "Diego Barba", "diego@udg.mx", "TI")
laptop = EquipoPersonal("EQP-0001", "host-laptop", "00:1A:2B:3C:4D:5E", "192.168.1.10", admin, "Laptop", "Ubuntu 24.04")
servidor = Servidor("SRV-0001", "host-db", "00:1A:2B:3C:4D:99", "192.168.1.20", admin, "Base de Datos", 5432, es_critico=True)
segmento = SegmentoRed("SEG-01", "LAN Principal", 10, RangoIP("192.168.1.1", "192.168.1.254", "255.255.255.0"))

# Registrar dispositivos y segmentos
sistema.registrar(laptop)
sistema.registrar(servidor)
sistema.registrar(segmento)

# Asignar dispositivos al segmento
sistema.asignar("EQP-0001", "SEG-01")
sistema.asignar("SRV-0001", "SEG-01")

# Listar: imprime cada descripción polimórfica en consola y devuelve list[str]
descripciones = sistema.listar()

# Persistir y recargar
guardar(sistema, "estado_red.json")
cargar(sistema, "estado_red.json")
```
