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

El presente repositorio documenta el desarrollo del Laboratorio No. 05 de la asignatura de Robótica, cuyo propósito principal es controlar las articulaciones del manipulador Phantom X Pincher X100 utilizando el entorno de ROS 2 Jazzy. A través de este proyecto, se implementan soluciones a partir de los paquetes base provistos , abarcando desde la medición y el modelado geométrico del manipulador , hasta la aplicación de cinemática directa e inversa. Asimismo, se exploran diferentes tipos de control de movimiento (individual, simultáneo, secuencial e interpolado) , culminando con la programación de trayectorias, la repetición de poses y la ejecución de rutinas complejas o tareas artísticas.

## Actividad 1. Preparación del robot

Para dar inicio a las pruebas experimentales, se llevó a cabo el protocolo de inicialización del sistema físico, garantizando la seguridad del equipo. El procedimiento simplificado consistió en los siguientes pasos:
1. Posicionamiento inicial: Se ubicó el robot manipulador en una posición segura antes de cualquier manipulación eléctrica.
2. Conexión de interfaz de datos: Se verificó la conexión de la red de servomotores  y se conectó el adaptador de comunicación TTL (U2D2) al puerto USB del computador para establecer la comunicación serial con los motores Dynamixel.
3. Energización del sistema: Una vez aseguradas las conexiones de datos, se energizó el sistema encendiendo la fuente de alimentación, siguiendo estrictamente las indicaciones del docente.
4. Validación en entorno virtual: Como paso final de comprobación, se verificó que el estado y la posición del modelo tridimensional visualizado en la herramienta RViz correspondiera correctamente con la postura física actual del manipulador.

*****ADJUNTAR DOS IMAGENEES

## Actividad 2. Identificación de motores y articulaciones
Para comprender la cinemática del robot y garantizar un control adecuado, se realizó una inspección física detallada. El objetivo fue identificar cada uno de los servomotores (todos de la referencia Dynamixel AX-12A), su ubicación exacta en la cadena cinemática, su identificador (ID) dentro de la red y el sentido de giro positivo para cada eje.
En la Figura X, se ilustran las articulaciones principales junto con sus respectivos ejes de rotación positiva (indicados con flechas naranjas que representan el eje Z), definidos mediante la regla de la mano derecha. En la Figura X, se detallan los IDs correspondientes a cada servomotor.

***********adjuntar dos imagenes

A partir de esta inspección visual y técnica, se consolidó la siguiente información: 

| Articulación | ID | Referencia | Sentido positivo | Función |
| :--- | :---: | :--- | :--- | :--- |
| **Base** | 1 | 0° (Frente al área de trabajo) | Antihorario (visto desde arriba, eje Z hacia arriba) | Rotación panorámica de toda la estructura del brazo. |
| **Hombro** | 2 | 0° (Alineado verticalmente) | Antihorario (visto desde el lateral derecho, eje Z saliente) | Elevación e inclinación del eslabón principal. |
| **Codo** | 3 | 0° (Alineado con el eslabón anterior) | Antihorario (visto desde el lateral derecho, eje Z saliente) | Extensión y flexión del antebrazo. |
| **Muñeca** | 4 | 0° (Alineado con el eslabón anterior) | Antihorario (visto desde el lateral derecho, eje Z saliente) | Orientación de cabeceo del efector final. |
| **Pinza** | 5 | 0° (Apertura máxima) | Cierre de las mordazas | Agarre, sujeción y liberación de objetos. |


## Actividad 3. Medición del robot

[cite_start]Para modelar la geometría del manipulador, se procedió a determinar las dimensiones físicas de sus componentes principales[cite: 242]. [cite_start]En la **Figura 3** se presenta el diagrama esquemático del robot, el cual ilustra las longitudes de los eslabones, las distancias entre los ejes de articulaciones consecutivas y la asignación de los sistemas de coordenadas para cada junta[cite: 247, 248, 251]. 

Cabe resaltar que **este diagrama y los sistemas de referencia aquí definidos se tendrán en cuenta como base fundamental para la actividad de cinemática directa**.

![Diagrama cinemático y medidas](ruta/a/tu/image_8cbbde.png)
[cite_start]*Figura 3: Diagrama geométrico del robot con sistemas coordenados y parámetros de longitud[cite: 251].*

A partir de la inspección del manipulador, se consolidaron las siguientes medidas (en mm):

| Parámetro | Valor |
| :--- | :---: |
| **L1** | 84 |
| **L2** | 43 |
| **L3** | 104 |
| **L4** | 104 |
| **L5** | 75 |
| **L7** | 36 |
| **D6** | 40 |

> **Nota sobre la medida D6:** A diferencia de las longitudes de los eslabones ($L_1$ a $L_7$), la medida **D6** representa qué tan abierto o cerrado está el *gripper*. Por consiguiente, **no es una constante geométrica** de la estructura del brazo, sino una variable de operación que cambia dependiendo de la posición del motor de la pinza.
