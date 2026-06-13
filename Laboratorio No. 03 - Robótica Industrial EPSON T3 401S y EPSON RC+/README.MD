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
| Controlador | DX100 | IRC5 | RC700 |
|Consumo de potencia | 1.5 kVA | 0.44 kW | 0.66 kVA|
|Nivel de protección | No especificado | IP67 | IP20|
|Tipo de actuadores | Servomotores AC | Servomotores AC |Servomotores AC |
| Lenguaje de programación | Python | RAPID | SPEL+ |
|Software compatible | RoboDK | RobotStudio | EPSON RC+ 7.0|
|Aplicaciones | Soldadura | Ensamblaje | Pick-and-place
---

## Posición de HOME

La configuración HOME corresponde a la posición de referencia utilizada por el manipulador para establecer un punto seguro de operación. A diferencia de otros robots industriales donde la posición de referencia suele expresarse directamente en grados o unidades lineales, en el EPSON T3-401S la configuración HOME se almacena mediante los pulsos del codificador (encoder pulses) asociados a cada articulación. Estos pulsos representan la posición absoluta de los ejes y permiten al controlador determinar con precisión la ubicación de cada articulación durante el proceso de homing.

Para "Junior", que es el robot utilizado en el laboratorio, la configuración mostrada correspondía a J1 = 204800 pulsos, mientras que J2, J3 y J4 se encontraban en 0 pulsos. Adicionalmente, el procedimiento de retorno a HOME se ejecuta siguiendo un orden específico de movimiento de las articulaciones, priorizando el eje vertical (J3) para garantizar que el manipulador alcance la posición de referencia de manera segura y así evitar posibles colisiones.

**IMAGEN 1

Desde el punto de vista geométrico, la posición HOME del EPSON T3-401S ubica los dos eslabones principales del brazo SCARA alineados entre sí, formando una configuración recta respecto al eje de la base. Asimismo, el eje vertical (J3) se posiciona en su punto superior de recorrido, manteniendo la herramienta alejada de la superficie de trabajo. Esta configuración proporciona una posición fácilmente identificable, minimiza el riesgo de interferencias con objetos del entorno y constituye el punto de partida para la ejecución de trayectorias y tareas programadas.

***IMAGEN 2

## Movimiento

Para realizar movimientos manuales del manipulador EPSON T3-401S mediante el software EPSON RC+, primero es necesario acceder al menú \textbf{Herramientas} ubicado en la barra superior del programa. Posteriormente, se selecciona la opción Administrador del robot y, dentro de esta ventana, se ingresa al apartado Mover y enseñar, el cual proporciona las herramientas necesarias para controlar manualmente la posición y orientación del robot.

Una vez dentro de la interfaz de movimiento manual, el usuario puede seleccionar el modo de operación mediante la lista desplegable Modo. Cuando se requiere desplazar el robot utilizando coordenadas cartesianas, debe seleccionarse el modo Mundo, el cual permite realizar movimientos respecto al sistema de coordenadas global. Por otro lado, si se desea controlar directamente cada articulación del manipulador, debe seleccionarse el modo Articulación, permitiendo actuar individualmente sobre los ejes del robot.

**IMAGEN 3

En el modo Mundo, los desplazamientos se realizan mediante los botones de dirección mostrados en pantalla. Los movimientos de traslación se efectúan sobre los ejes cartesianos X, Y y Z utilizando los controles +X, -X, +Y -Y, +Z y -Z. De esta manera, el efector final puede desplazarse dentro del espacio de trabajo sin necesidad de controlar cada articulación por separado.

En el modo Articulación, la orientación de los eslabones se puede modificar mediante los controles de rotación asociados a los ejes J1, J2 y J4 (J3 es lineal). Los botones +J1 y -J1, +J2 y -J2, así como +J4 y -J4, permiten realizar rotaciones positivas y negativas alrededor de cada eje de orientación, respectivamente. A su vez, con +J3 y -J3 se controla la posición lineal del eje vertical.

**IMAGEN 4

Finalmente, el software muestra en tiempo real la posición actual del robot, indicando las coordenadas X, Y y Z en milímetros, así como los ángulos de orientación correspondientes. Esta información permite verificar los movimientos ejecutados y facilita la enseñanza de puntos para la posterior programación de trayectorias.


