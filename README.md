# Sistema de Gestión y Control de Dispositivos en Red

**Universidad de Guadalajara — Proyecto de Programación**  
**Opción Elegida:** C — Dispositivos en red

### Integrantes del Equipo
- **Diego Barba Mier Y Concha** (`225996364`) — *Modelado de Dispositivos y Operaciones Base*
- **Jesús Emmanuel Guante Jiménez** (`222479008`) — *Gestión de Contenedores y Persistencia*

---

## 1. Propósito del Sistema

El sistema registra **equipos personales** (`EquipoPersonal`) o **servidores** (`Servidor`) y los asigna a **segmentos de red** (`SegmentoRed`) específicos que los contienen dentro de un límite de direcciones IP. Sirve para llevar control de la infraestructura asegurando:
1. Un **identificador único con formato válido** para cada dispositivo.
2. Un **responsable o dueño obligatorio** asignado a cada máquina.
3. Que **ningún segmento de red exceda su capacidad máxima** ni tenga el mismo dispositivo duplicado.

---

## 2. Arquitectura y Responsabilidades de Clases

| Archivo | Clase / Función | Responsable | Tarea Principal |
| :--- | :--- | :--- | :--- |
| `modelos.py` | `Dispositivo` | Diego Barba | Clase base que define los datos comunes (`_id_dispositivo`, `_nombre_host`, `_direccion_mac`, `_direccion_ip`, `_responsable`), validaciones de registro y el método polimórfico `describir()`. |
| `modelos.py` | `EquipoPersonal` | Diego Barba | Clase hija que representa una computadora de uso individual asociada a su `_tipo_equipo` y `_sistema_operativo`, además de `solicitar_acceso_vpn()`. |
| `modelos.py` | `Servidor` | Diego Barba | Clase hija que modela una máquina centralizada dedicada a proveer un servicio (`_rol_servidor`, `_puerto_servicio`, `_es_critico`) y `ejecutar_diagnostico()`. |
| `modelos.py` | `Responsable` | Diego Barba | Modela los datos del empleado o dueño a cargo de un dispositivo (`_id_empleado`, `_nombre`, `_correo`, `_departamento`). |
| `sistema.py` | `SegmentoRed` y `RangoIP` | Emmanuel Huante | Contenedor que controla el cupo máximo de direcciones disponibles para un grupo de conexiones y su rango de direcciones IPv4. |
| `sistema.py` | `Bitacora` | Emmanuel Huante | Persiste y administra el historial de eventos para delegar la tarea del registro. |
| `sistema.py` | `SistemaRed` | Ambos | Orquesta las operaciones principales del contrato aplicando las reglas de negocio (`registrar`, `listar`, `asignar`, `guardar`, `cargar`). |

---

## 3. Reglas de Validación del Programa

### 3.1 Validaciones de Registro (Implementadas en `modelos.py` y `SistemaRed.registrar`)
- **Responsable obligatorio:** Si se intenta crear o registrar un dispositivo dejando el responsable o dueño en blanco (`""` o `None`), se rechaza con un `ValueError` indicando que el campo es obligatorio.
- **Formato del identificador:** El `id_dispositivo` debe tener una **longitud exacta de 8 caracteres** con la estructura `PREFIJO-0000`, donde el prefijo sea `DEV-`, `SRV-` o `EQP-` seguido de 4 dígitos numéricos (ej. `DEV-0001`, `SRV-0001`, `EQP-0015`). Cualquier otro formato es rechazado detallando la estructura y longitud esperada.
- **Prevención de duplicados:** Si se intenta registrar un equipo con un `id_dispositivo` previamente guardado en el sistema, `sistema.registrar(objeto)` lo rechaza avisando que ese identificador ya existe.

### 3.2 Validaciones de Asignación y Persistencia (Sección de Emmanuel en `sistema.py`)
- **Segmento inexistente:** Al llamar a `asignar(identificador, clave)`, rechazar si la `clave` del contenedor `SegmentoRed` no existe.
- **Dispositivo no registrado:** Rechazar si el `identificador` del equipo no ha sido dado de alta previamente mediante `registrar(objeto)`.
- **Cupo máximo superado:** Rechazar si el `SegmentoRed` ya llegó a su límite de direcciones (`_capacidad_maxima`).
- **Doble asignación en el mismo segmento:** Rechazar si se intenta asignar el mismo dispositivo dos veces al mismo `SegmentoRed`.
- **Arranque limpio:** `cargar(sistema, ruta)` debe manejar el caso donde el archivo de datos no existe aún (`FileNotFoundError`) sin que el programa colapse.

---

## 4. Cómo Ejecutar el Proyecto

Requisitos: **Python 3.10+** (solo utiliza la biblioteca estándar de Python).

Para ejecutar la demostración y la batería de pruebas de validación desde la raíz del proyecto:

```bash
python3 main.py
```

### Uso Rápido desde Código Python

```python
from modelos import EquipoPersonal, Servidor, Responsable
from sistema import SistemaRed, SegmentoRed, RangoIP, guardar, cargar

# 1. Inicializar el sistema
sistema = SistemaRed()

# 2. Crear responsable y dispositivos (Hito 2 - Parte de Diego Barba)
admin = Responsable("EMP-01", "Diego Barba", "diego@udg.mx", "TI")
laptop = EquipoPersonal("EQP-0001", "host-laptop", "00:1A:2B:3C:4D:5E", "192.168.1.10", admin, "Laptop", "Ubuntu 24.04")
servidor = Servidor("SRV-0001", "host-db", "00:1A:2B:3C:4D:99", "10.0.0.10", admin, "Base de Datos", 5432, es_critico=True)

# 3. Registrar y listar polimórficamente
sistema.registrar(laptop)
sistema.registrar(servidor)

for descripcion in sistema.listar():
    print(descripcion)
```

---

## 5. Guía para Emma

En el archivo `sistema.py` ya están creados los cimientos de las clases y métodos con comentarios `# TODO (Emmanuel)` paso a paso:

1. **`RangoIP`**: Completar `ip_esta_en_rango(ip)` y `obtener_total_direcciones()`.
2. **`SegmentoRed`**: Completar `obtener_ocupacion_actual()`, `verificar_capacidad()` y `agregar_dispositivo(dispositivo)`.
3. **`SistemaRed.asignar(identificador, clave)`**: Implementar las 4 validaciones de asignación descritas en el docstring.
4. **`guardar(sistema, ruta)` y `cargar(sistema, ruta)`**: Implementar la serialización/deserialización (puedes apoyarte en `dispositivo.obtener_resumen()` que ya devuelve un `dict` listo para `json.dump`) cuidando el **Arranque Limpio** con `try / except FileNotFoundError`.
