# Robótica Industrial - Análisis y Operación del Manipulador EPSON T3-401S

**Universidad Nacional de Colombia**  
Facultad de Ingeniería – Sede Bogotá

**Estudiantes:**
  - Edward Jeisen Jair Arévalo Peña
  - Juan Diego López Mayorga

**Profesores:**
  - Pedro Fabian Cardenas Herrera
  - Manuel Felipe Carranza Montenegro
---

## Descripción

Este repositorio contiene el desarrollo del Laboratorio 03 de la asignatura **Robótica (2016770)**, cuyo objetivo fue analizar el funcionamiento del manipulador industrial **EPSON T3-401S**, estudiar sus modos de operación y desarrollar una aplicación de manipulación mediante simulación.

Durante el laboratorio se abordaron los siguientes aspectos:

- Análisis de las especificaciones técnicas del manipulador.
- Estudio de las posiciones *Home*.
- Operación mediante el *Teach Pendant*.
- Programación utilizando EPSON RC+ 7.0.
- Comparación con otros manipuladores industriales.
- Comparación entre RoboDK y RobotStudio.
- Diseño de una rutina de movimiento y su diagrama de flujo.

Debido a inconvenientes técnicos durante la práctica, la trayectoria programada no pudo ejecutarse sobre el robot físico, por lo que su validación se realizó mediante simulación.

---

## Contenido del repositorio


---

## Especificaciones técnicas

| Especificación | Motoman MH6 | ABB IRB 140 | EPSON T3-401S |
|----------------|------------:|------------:|--------------:|
| Tipo de robot | Articulado | Articulado | SCARA |
| Grados de libertad | 6 | 6 | 4 |
| Carga útil | 6 kg | 6 kg | 3 kg |
| Alcance máximo | 1422 mm | 810 mm | 400 mm |
| Repetibilidad | ±0.08 mm | ±0.03 mm | ±0.02 mm |
| Peso | 130 kg | 98 kg | 16 kg |
| Controlador | DX100 | IRC5 | RC700A |
| Lenguaje de programación | Python | RAPID | SPEL+ |

---

