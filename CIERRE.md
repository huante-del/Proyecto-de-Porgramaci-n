# Documento de Cierre — Proyecto de Programación

**Universidad de Guadalajara**  
**Proyecto:** Sistema de Gestión y Control de Dispositivos en Red (Opción C)  
**Integrantes:**
- **Diego Barba Mier Y Concha** (`225996364`)
- **Jesús Emmanuel Huante Jiménez** (`222479008`)

---

## 1. Resumen del Proyecto

El proyecto implementó un sistema orientado a objetos en Python para administrar el inventario de infraestructura de red, permitiendo dar de alta equipos personales (`EquipoPersonal`), servidores (`Servidor`) y segmentos de red (`SegmentoRed`), asignar equipos respetando límites de capacidad y rangos IPv4 (`RangoIP`), llevar historial en una `Bitacora` y persistir/recuperar el estado completo en archivos JSON con soporte de arranque limpio.

## 2. Reparto de Trabajo y Cumplimiento

- **Diego Barba Mier Y Concha:**
  - Diseño e implementación de la jerarquía de clases en `modelos.py` (`Responsable`, `Dispositivo`, `EquipoPersonal`, `Servidor`) con encapsulamiento (`_` y `@property`), herencia y polimorfismo en `describir()` y `obtener_resumen()`.
  - Implementación de `SistemaRed.registrar(objeto)` (con soporte para `Dispositivo` y `SegmentoRed`) y `SistemaRed.listar()` (impresión en consola y retorno de lista).
  - Validaciones de registro (responsable obligatorio, formato estricto de identificador de 8 caracteres y prevención de duplicados).
  - Suite de pruebas automáticas (`test_sistema.py`), actualización de documentación (`README.md`) y documento de cierre (`CIERRE.md`).

- **Jesús Emmanuel Huante Jiménez:**
  - Implementación de `RangoIP`, `SegmentoRed` y `Bitacora` en `sistema.py`.
  - Lógica de control de cupo, validación de rangos IPv4 con `ipaddress` y prevención de doble asignación en el mismo segmento.
  - Implementación de `SistemaRed.asignar(identificador, clave)` y persistencia en JSON mediante `guardar(sistema, ruta)` y `cargar(sistema, ruta)` con arranque limpio ante `FileNotFoundError`.

## 3. Incidencias Detectadas en la Evaluación y Correcciones Aplicadas

Durante la revisión y pruebas de aceptación del Hito 3 se detectaron puntos críticos que fueron corregidos en la versión final:

1. **`SistemaRed.registrar()` rechazaba `SegmentoRed` con `TypeError`:**
   - *Causa:* Originalmente se creó un método separado `agregar_segmento()`, por lo que `registrar()` solo aceptaba `Dispositivo`.
   - *Corrección:* Se actualizó `SistemaRed.registrar()` para aceptar tanto `Dispositivo` como `SegmentoRed` (manteniendo `agregar_segmento()` por compatibilidad) y validando duplicados en ambos catálogos.
2. **`SistemaRed.listar()` no imprimía en consola en la versión remota:**
   - *Causa:* El cambio local realizado en `sistema.py` no había sido sincronizado al repositorio remoto, provocando una discrepancia con el `README.md`.
   - *Corrección:* `listar()` imprime las descripciones polimórficas en consola (o un aviso si no hay dispositivos) y retorna la lista `list[str]`, coincidiendo exactamente con la documentación.
3. **Ausencia de suite de pruebas automáticas:**
   - *Corrección:* Se creó `test_sistema.py` usando la biblioteca estándar `unittest`, cubriendo modelos, polimorfismo, registro de dispositivos y segmentos, salida de `listar()`, todas las reglas de rechazo de registro y asignación, persistencia JSON y arranque limpio.
4. **Historial de commits y sincronización del repositorio:**
   - *Corrección:* Se subieron las correcciones mediante commits atómicos y descriptivos al repositorio principal y se eliminó un `return True` redundante en `cargar()`.

## 4. Verificación y Pruebas

Todas las funcionalidades se validan ejecutando:
```bash
python3 -m unittest discover -v
python3 main.py
```
La suite verifica de manera automatizada tanto los caminos exitosos como los rechazos controlados (`ValueError` / `TypeError`) sin errores nativos inesperados ni dependencias externas.

## 5. Conclusiones y Aprendizajes

- **Contrato e interfaz clara:** Alinear las firmas exactas del contrato (`registrar` recibiendo tanto entidades como contenedores, y `listar` imprimiendo de forma visible) es fundamental para que las pruebas de aceptación pasen sin fricción.
- **Pruebas automatizadas desde el inicio:** Contar con una suite `unittest` evita regresiones y permite comprobar en segundos que cada regla de negocio sigue funcionando tras cada cambio.
- **Disciplina en Git:** Hacer commits frecuentes y verificar `git status` / `git push` antes del cierre evita que correcciones ya realizadas localmente queden fuera de la entrega evaluada.
