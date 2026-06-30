# Robótica Industrial - Laboratorio No. 05 - Phantom X Pincher X100 – ROS 2 Jazzy – RViz

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

Para modelar la geometría del manipulador, se procedió a determinar las dimensiones físicas de sus componentes principales. En la Figura X se presenta el diagrama esquemático del robot, el cual ilustra las longitudes de los eslabones, las distancias entre los ejes de articulaciones consecutivas y la asignación de los sistemas de coordenadas para cada junta. 

Cabe resaltar que este diagrama y los sistemas de referencia aquí definidos fueron establecidos mediante el método visto en clase para cinemática directa. Dicho diagrama se tendrá en cuenta para la actividad de cinemática directa.

*** INSERTAR ESQUEMA

A partir de la medición del manipulador mediante calibrador, se consolidaron las siguientes medidas (en mm):

| Parámetro | Valor |
| :--- | :---: |
| **L1** | 84 |
| **L2** | 43 |
| **L3** | 104 |
| **L4** | 104 |
| **L5** | 75 |
| **L7** | 36 |
| **D6** | 40 |

> **Nota sobre D6:** la medida **D6** representa qué tan abierto o cerrado está el *gripper*. Por consiguiente, **no es una constante geométrica** de la estructura del brazo, sino una variable de operación que cambia dependiendo de la posición del motor de la pinza.

## Actividad 4. Movimiento individual de articulaciones

Para esta actividad se desarrolló un nodo en Python bajo el framework de **ROS 2 Jazzy** con el objetivo de controlar de forma independiente y selectiva cada una de las articulaciones del robot Phantom X Pincher X100 (base, hombro, codo, muñeca y pinza). 

El programa permite al usuario interactuar a través de la terminal para seleccionar la articulación que desea mover y definir la posición angular objetivo. Como medida de seguridad, el código valida que el ángulo ingresado se encuentre dentro de los límites seguros determinados previamente en la Actividad 6 antes de enviar el comando a los servomotores Dynamixel AX-12A.

Para comprobar el correcto funcionamiento del control y la respuesta física del manipulador, se realizaron pruebas independientes en cada articulación ejecutando al menos tres (3) posiciones angulares distintas y retornando exitosamente a la posición de referencia (0° / posición de home) tras cada movimiento.

A continuación, se adjunta el código fuente completo implementado en Python para el desarrollo de esta actividad:

```python
#
```

### Evidencia en Video

La verificación física de esta actividad, donde se detalla el movimiento secuencial de las articulaciones pasando por las tres posiciones de prueba y su respectivo retorno a la posición segura, se encuentra en el siguiente link:




## Actividad 6. Determinación de límites seguros

Para garantizar la integridad física del manipulador, se determinaron experimentalmente los límites de operación para cada una de las articulaciones. Desde la posició de home, se realizó un barrido para cada articulación, de modo que el manipulador nunca sufriera choques o colisiones tanto con él mismo como con su entorno. A partir de las pruebas manuales y visuales, se establecieron los siguientes límites (todos expresados en grados). Además, se definió un margen de seguridad constante de 3° antes del límite físico real, pues es un margen aceptable que permite trabajar ampliamente con el manipulador.

| Articulación | Límite inferior | Límite superior | Margen de seguridad |
| :--- | :---: | :---: | :---: |
| **Base** | -150° | 150° | 3° |
| **Hombro** | -75° | 125° | 3° |
| **Codo** | -121° | 135° | 3° |
| **Muñeca** | -102° | 100° | 3° |
| **Pinza** | -90° | 90° | 3° |
