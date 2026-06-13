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

## Introducción

La robótica industrial se ha consolidado como una de las tecnologías más importantes dentro de los procesos de automatización moderna, permitiendo incrementar la productividad, la precisión y la seguridad en diferentes sectores industriales. Los manipuladores robóticos son capaces de ejecutar tareas repetitivas y complejas mediante movimientos controlados y programados, lo que los convierte en herramientas fundamentales para aplicaciones de ensamblaje, manipulación de materiales, inspección y manufactura. Debido a la gran variedad de configuraciones y prestaciones existentes, resulta necesario comprender las características técnicas y operativas de cada tipo de robot para seleccionar la alternativa más adecuada según los requerimientos de una aplicación específica.

En el presente laboratorio se estudió el manipulador industrial EPSON T3-401S, abordando sus configuraciones iniciales, modos de operación manual y herramientas de programación mediante el software EPSON RC+ 7.0. Asimismo, se realizó una comparación de sus características con otros manipuladores industriales, se analizaron las trayectorias disponibles para su movimiento y se desarrolló una aplicación de manipulación. Debido a inconvenientes técnicos, no fue posible llevar a cabo la implementación física de la trayectoria programada. Por esto, el desarrollo del laboratorio se enfocó en la simulación y validación virtual de las rutinas propuestas.

---

## Especificaciones técnicas

A través de un cuadro comparativo de las especificaciones técnicas de cada robot empleado hasta la fecha en el curso de Robótica, se propone identificar similitudes y diferencias en sus parámetros.   

| Especificación | Motoman MH6 | ABB IRB 140 | EPSON T3-401S |
|----------------|------------:|------------:|--------------:|
|Fabricante |  Yaskawa  |  ABB  |  Epson |
| Tipo de robot | Articulado | Articulado | SCARA |
| Grados de libertad | 6 | 6 | 4 |
| Carga útil máxima| 6 kg | 6 kg | 3 kg |
| Alcance máximo | 1422 mm | 810 mm | 400 mm |
| Repetibilidad | ±0.08 mm | ±0.03 mm | ±0.02 mm |
| Peso del robot | 130 kg | 98 kg | 16 kg |
|Vel. máxima | 200°/s | 200°/s | 3700mm/s  2.600°/s|
|Montaje en lab. | Raíl (eje lineal) | Suelo | Cabina|
| Controlador | DX100 | IRC5 | RC700A |
|Consumo de potencia | 1.5 kVA | 0.44 kW | 0.3 kVA|
|Nivel de protección | No especificado | IP67 | IP20|
|Tipo de actuadores | Servomotores AC | Servomotores AC |Servomotores AC |
| Lenguaje de programación | Python | RAPID | SPEL+ |
|Software compatible | RoboDK | RobotStudio | EPSON RC+ 7.0|
|Aplicaciones | Soldadura | Ensamblaje | Pick-and-place
---

