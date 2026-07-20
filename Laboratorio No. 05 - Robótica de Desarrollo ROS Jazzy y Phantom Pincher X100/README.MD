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

El presente repositorio documenta el desarrollo del Laboratorio No. 05 de la asignatura de Robótica, cuyo propósito principal es controlar las articulaciones del manipulador Phantom X Pincher X100 utilizando el entorno de ROS 2 Jazzy. A través de este proyecto, se implementan soluciones, abarcando desde la medición del manipulador, hasta la aplicación de cinemática directa e inversa. Asimismo, se exploran diferentes tipos de control de movimiento (individual, simultáneo, secuencial e interpolado), culminando con la programación de trayectorias, la repetición de poses y la ejecución de rutinas complejas o tareas artísticas.

Para contextualizar el entorno físico donde se ejecutan estas implementaciones y asegurar un desarrollo seguro de las trayectorias programadas, se presenta a continuación el plano de planta del laboratorio. En este esquema se delimita la ubicación del manipulador, las áreas de trabajo de los operadores y las zonas de seguridad requeridas para la operación del Phantom X Pincher:

![image](files/Planta.jpeg)

## Actividad 1. Preparación del robot

Para dar inicio a las pruebas experimentales, se llevó a cabo el protocolo de inicialización del sistema físico, garantizando la seguridad del equipo. El procedimiento simplificado consistió en los siguientes pasos:
1. Posicionamiento inicial: Se ubicó el robot manipulador en una posición segura antes de cualquier manipulación eléctrica.
2. Conexión de interfaz de datos: Se verificó la conexión de la red de servomotores  y se conectó el adaptador de comunicación TTL (U2D2) al puerto USB del computador para establecer la comunicación serial con los motores Dynamixel.
3. Energización del sistema: Una vez aseguradas las conexiones de datos, se energizó el sistema encendiendo la fuente de alimentación.

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/ACT1.png)

4. Validación en entorno virtual: Como paso final de comprobación, se verificó que el estado y la posición del modelo tridimensional visualizado en la herramienta RViz correspondiera correctamente con la postura física actual del manipulador.

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/homeRVIZ.png)

Hacemos la anotación de que, inicialmente, la posición de home que se visualizaba en RViz era una especie de L: el robot estaba retraido 90° en la articulación del codo. Esto no concordaba con lo que estaba ocurriendo con el robot real, pues este último se veía totalmente vertical al estar en la posición de home. Para arreglar esto, fue necesario modificar el script `ros2_jazzy/phantom_ws/src/pincher_description/urdf/robot.xacro`, más específicamente la sección de definición de la configuración de la articulación del codo o 'elbow':

```python
  <joint name="elbow" type="revolute">
    #<origin xyz="${Lm} ${-L2} 0.0" rpy="0.0 0.0 ${-atan2(L2,Lm) - 1.5708}"/> 
    <origin xyz="${Lm} ${-L2} 0.0" rpy="0.0 0.0 ${-atan2(L2,Lm) - 1.5708}"/> # se agrega corrección
    <parent link="link2"/>
    <child link="link3"/>
    <axis xyz="0.0 0.0 1.0"/>
    <limit lower="${-150*pi/180}" upper="${150*pi/180}" effort="4.0" velocity="2.0"/>
  </joint>
```

De manera similar, fue necesario editar el sentido de giro establecido en la simulación, pues este no correspondia con el movimiento que el robot real estaba presentando. El archivo modificado en esta ocasión fue `ros2_jazzy/phantom_ws/src/pincher_control/pincher_control/control_servo.py`, en el cual cambiamos unicamente la siguiente linea:

```python
        #self.declare_parameter('joint_signs', [1.0, -1.0, -1.0, -1.0, 1.0])
        self.declare_parameter('joint_signs', [1.0, 1.0, 1.0, 1.0, 1.0]) #sentido de giro corregido
```

Adicionalmente, se observa una diferencia entre el modelo dispuesto en RViz y el manipulador físico: el eslabón presente entre el hombro y el codo es totalmente recto en la realidad, mientras que el modelo importado mediante el archivo stl cuenta con forma de L. Es importante tener en cuenta esta discrepancia, pues puede ser crítica en aplicaciones en donde se requiera de alta presición. Por facilidad en el ensamble y para evitar modificar modelados y/o scripts excesivamente, se decidió proceder con este modelo en RViz y realizar los ejercicios posteriores teniendo en cuenta esta ligera distición.

## Actividad 2. Identificación de motores y articulaciones
Para comprender la cinemática del robot y garantizar un control adecuado, se realizó una inspección física detallada. El objetivo fue identificar cada uno de los servomotores (todos de la referencia Dynamixel AX-12A), su ubicación exacta en la cadena cinemática, su identificador (ID) dentro de la red y el sentido de giro positivo para cada eje.
En la siguiente imagen, se ilustran las articulaciones principales junto con sus respectivos ejes de rotación positiva (indicados con flechas naranjas que representan el eje Z), definidos mediante la regla de la mano derecha.

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/articulaciones.png)

En la siguiente imagen, se detallan los IDs correspondientes a cada servomotor.

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/motores.png)

A partir de esta inspección visual y técnica, se consolidó la siguiente información: 

| Articulación | ID | Referencia | Sentido positivo | Función |
| :--- | :---: | :--- | :--- | :--- |
| **Base** | 001 | 0° (Frente al área de trabajo) | Antihorario (visto desde arriba, eje Z hacia arriba) | Rotación panorámica de toda la estructura del brazo. |
| **Hombro** | 002 | 0° (Alineado verticalmente) | Antihorario (visto desde el lateral derecho, eje Z saliente) | Elevación e inclinación del eslabón principal. |
| **Codo** | 003 | 0° (Alineado con el eslabón anterior) | Antihorario (visto desde el lateral derecho, eje Z saliente) | Extensión y flexión del antebrazo. |
| **Muñeca** | 004 | 0° (Alineado con el eslabón anterior) | Antihorario (visto desde el lateral derecho, eje Z saliente) | Orientación de cabeceo del efector final. |
| **Pinza** | 005 | 0° (Apertura máxima) | Cierre de las mordazas | Agarre, sujeción y liberación de objetos. |


## Actividad 3. Medición del robot

Para modelar la geometría del manipulador, se procedió a determinar las dimensiones físicas de sus componentes principales. En la siguiente figura se presenta el diagrama esquemático del robot, el cual ilustra las longitudes de los eslabones, las distancias entre los ejes de articulaciones consecutivas y la asignación de los sistemas de coordenadas para cada junta. 

Cabe resaltar que este diagrama y los sistemas de referencia aquí definidos fueron establecidos mediante el método visto en clase para cinemática directa. Dicho diagrama se tendrá en cuenta para la actividad de cinemática directa.

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/diagrama.png)

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

Para esta actividad se desarrolló un nodo en Python bajo el framework de **ROS 2 Jazzy** con el objetivo de controlar de forma independiente y selectiva cada una de las articulaciones del robot (base, hombro, codo, muñeca y pinza). 

El programa permite al usuario interactuar a través de la terminal para seleccionar la articulación que desea mover y definir la posición angular objetivo. Como medida de seguridad, el código valida que el ángulo ingresado se encuentre dentro de los límites seguros determinados en la Actividad 6 antes de enviar el comando a los servomotores Dynamixel AX-12A.

[Código del ejercicio](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/individual.py)

```mermaid
flowchart TD
    A[Inicio] --> B[Inicializar ROS 2: rclpy.init]
    B --> C[Instanciar nodo ControlArticulacion]
    C --> D[Esperar 1s y publicar velocidad = 100]

    D --> E[Mostrar menú de selección]
    E --> F[/Leer opción del usuario/]

    F --> G{¿Opción == '0'?}
    G -- Sí --> N[Destruir nodo y rclpy.shutdown]
    N --> O[Fin]

    G -- No --> H{¿Opción en '1'..'5'?}
    H -- No --> I[Mostrar 'Opción inválida'] --> E

    H -- Sí --> J[Obtener límites de la articulación]
    J --> K[/Leer ángulo en grados/]

    K --> L{¿Entrada es numérica?}
    L -- No --> M[Mostrar 'Debe ingresar un número'] --> E

    L -- Sí --> P{¿Ángulo dentro de límites?}
    P -- No --> Q[Mostrar 'ERROR: fuera de límites'] --> E

    P -- Sí --> R[Calcular rad + offset en pose_actual]
    R --> S[Publicar JointState en /pincher/command]
    S --> T[Ejecutar rclpy.spin_once]
    T --> E
```

Para comprobar el correcto funcionamiento del control y la respuesta física del manipulador, se realizaron pruebas independientes en cada articulación ejecutando al menos tres (3) posiciones angulares distintas y retornando exitosamente a la posición de referencia (0° / posición de home) tras cada movimiento.

Los ángulos proporcionados para cada articulación se muestran en el video adjunto.

[![Ver el video](https://img.youtube.com/vi/GWDrMEiTvxc/maxresdefault.jpg)](https://www.youtube.com/watch?v=GWDrMEiTvxc)

## Actividad 5. Calibración de cero y error articular

Para garantizar la precisión de los movimientos del robot en las tareas posteriores, se realizó un proceso de calibración y análisis de error para cada uno de los servomotores. El procedimiento consistió en enviar cinco posiciones angulares distintas (distribuidas dentro de su rango seguro de operación) y registrar tanto la posición solicitada (deseada) como la posición real reportada por el *encoder* interno de cada motor. Con estos datos se calculó el error absoluto para cada medición. A partir de esto, se determinó el error máximo, el error promedio y el desplazamiento de cero (offset) de cada articulación, implementando vía software la corrección necesaria para mitigar dicho desfase.

[Código del ejercicio](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/cero.py)

```mermaid
flowchart TD
    A[Inicio] --> B[Inicializar ROS 2: rclpy.init]
    B --> C[Instanciar nodo ControlRobot y suscriptores/publicadores]
    C --> D[Mover robot a posición HOME inicial]
    D --> E[Pausa 3s: rclpy.spin_once]

    E --> F[Iterar por cada articulación: waist, shoulder, elbow, wrist, gripper]
    F --> G[Generar 5 puntos de prueba entre el 90% de límites]

    G --> H[Iterar por cada ángulo generado]
    H --> I[Publicar movimiento a la articulación en evaluación]
    I --> J[Pausa 3s: rclpy.spin_once para estabilizar]
    J --> K[Leer posición medida desde /joint_states]
    K --> L[Calcular error: eq = q_deseado - q_medido]
    L --> M[Guardar datos de deseado, medido y error]

    M --> N{¿Quedan ángulos de prueba?}
    N -- Sí --> H
    N -- No --> O[Mover robot a posición HOME]
    O --> P[Pausa 3s: rclpy.spin_once]

    P --> Q{¿Quedan articulaciones por calibrar?}
    Q -- Sí --> F

    Q -- No --> R[Calcular error promedio, máximo y despl. de cero]
    R --> S[Calcular nuevos offsets sugeridos en radianes]
    S --> T[/Imprimir nuevo bloque self.offset en consola/]
    T --> U[Generar subplots con Matplotlib]
    U --> V[Mostrar gráficas: plt.show]
    V --> W[rclpy.shutdown]
    W --> X[Fin]
```

A continuación, se presentan las gráficas comparativas de posición para todas las articulaciones y los datos extraidos por consola:

![Calibración Base](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/errores.png)

![Calibración Base](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/Act5_1.png)
![Calibración Base](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/Act5_2.png)
![Calibración Base](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/Act5_3.png)
![Calibración Base](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/Act5_4.png)

Al observar las gráficas resultantes y analizar numéricamente los datos, se evidencia un error bajo e inherente en todos los servomotores. Este comportamiento es completamente esperado y se debe a múltiples factores propios de los actuadores (como la resolución finita de los encoders internos, las pequeñas oscilaciones que pueden presentarse durante la medición, y la holgura mecánica o "juego" presente en las cajas reductoras). Además, se observó que el mayor error está presente en la articulación del hombro "shoulder", la cual es, especificamente, la más expuesta a componentes de masa e inerciales.

Finalmente, fue posible aplicar una compensación directa en el nodo de control. Esta corrección de software resulta ser un paso fundamental, ya que garantiza que el "cero" lógico del programa coincida con el "cero" físico real del manipulador, mejorando drásticamente la exactitud posicional requerida para el posterior cálculo de la cinemática directa e inversa.

## Actividad 6. Determinación de límites seguros

Para garantizar la integridad física del manipulador, se determinaron experimentalmente los límites de operación para cada una de las articulaciones. Desde la posició de home, se realizó un barrido para cada articulación, de modo que el manipulador nunca sufriera choques o colisiones tanto con él mismo como con su entorno. A partir de las pruebas manuales y visuales, se establecieron los siguientes límites (todos expresados en grados). Además, se definió un margen de seguridad constante de 3° antes del límite físico real, pues es un margen aceptable que permite trabajar ampliamente con el manipulador.

| Articulación | Límite inferior | Límite superior | Margen de seguridad |
| :--- | :---: | :---: | :---: |
| **Base** | -150° | 150° | 3° |
| **Hombro** | -75° | 125° | 3° |
| **Codo** | -121° | 135° | 3° |
| **Muñeca** | -102° | 100° | 3° |
| **Pinza** | -90° | 90° | 3° |

## Actividad 7. Movimiento simultáneo

Para esta etapa del laboratorio, se programó un nodo en ROS 2 Jazzy capaz de enviar comandos de posición a todos los servomotores al mismo tiempo, logrando un desplazamiento coordinado del brazo. Durante las pruebas experimentales, se enviaron las cinco configuraciones articulares solicitadas con una espera constante.

[Código del ejercicio](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/simultaneo.py)

```mermaid
flowchart TD
    A[Inicio] --> B[Inicializar ROS 2: rclpy.init]
    B --> C[Instanciar nodo Bailarin y convertidor de límites a rad]
    C --> D[Esperar 1s]
    D --> E[Definir rutina1_d y convertir poses a radianes]

    E --> F[Configurar velocidad = 50]
    F --> G[Mover a posición HOME]
    G --> H[Esperar 8s]

    H --> I[Configurar velocidad = 40]
    I --> J[Iterar sobre cada pose de la rutina]

    J --> K{¿Pose dentro de límites articulares?}
    K -- No --> L[Registrar error y omitir movimiento] --> O
    K -- Sí --> M[Publicar JointState en /pincher/command]
    M --> N[Ejecutar rclpy.spin_once]
    N --> O[Esperar 8s]

    O --> P{¿Quedan poses en la rutina?}
    P -- Sí --> J

    P -- No --> Q[Mover a posición HOME]
    Q --> R[Ejecutar rclpy.spin_once]
    R --> S[Esperar 1s]
    S --> T[rclpy.shutdown]
    T --> U[Fin]
```

Video del ejercicio:

[![Ver el video](https://img.youtube.com/vi/H-eo34o0XAY/maxresdefault.jpg)](https://www.youtube.com/watch?v=H-eo34o0XAY)

## Actividad 8. Movimiento secuencial

A diferencia de la actividad anterior, se desarrolló un script para alcanzar las configuraciones objetivo moviendo las articulaciones de manera estrictamente ordenada y enviando las nuevas configuraciones cuando se haya alcanzado el objetivo inmediatamente anterior. La configuración que se ejecutó en esta actividad fue [25, 25, 20, −20, 0].

[Código del ejercicio](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/secuencial.py)

```mermaid
flowchart TD
    A[Inicio] --> B[Inicializar ROS 2: rclpy.init]
    B --> C[Instanciar nodo Bailarin y suscribirse a /joint_states]
    C --> D[Esperar 1s]
    D --> E[Definir rutina1_d y convertir poses a radianes]

    E --> F[Configurar velocidad = 40]
    F --> G[Mover a posición HOME]
    G --> H[Esperar 8s]

    H --> I[Iterar sobre cada pose de la rutina]

    I --> J{¿Pose dentro de límites?}
    J -- No --> K[Registrar error y omitir pose] --> P
    J -- Sí --> L[Publicar JointState en /pincher/command]

    L --> M[Verificar llego_a_pose]
    M --> N{"¿Alcanzó objetivo?\n|qd - qm| <= 2°"}
    N -- No --> O[rclpy.spin_once Actualizar q_medida vía callback] --> M

    N -- Sí --> P{¿Quedan poses en la rutina?}
    P -- Sí --> I

    P -- No --> Q[Mover a posición HOME]
    Q --> R[Ejecutar rclpy.spin_once]
    R --> S[Esperar 1s]
    S --> T[rclpy.shutdown]
    T --> U[Fin]
```

Video del ejercicio

[![Ver el video](https://img.youtube.com/vi/5a1SOcvFOQw/maxresdefault.jpg)](https://www.youtube.com/watch?v=5a1SOcvFOQw)

Comparativamente, podemos mencionar que:

- Tiempo de ejecución: El movimiento simultáneo es significativamente más eficiente y rápido, ya que todos los actuadores operan en paralelo. Por su parte, el movimiento secuencial es más lento porque acumula los tiempos de desplazamiento de cada motor de forma individual. Sin embargo, este último cuenta con un movimiento más controlado, pues primero se debe asegurar que el manipulador llegó con una articulación para mover la inmediatamente siguiente.
- Trayectoria del TCP: En el modo simultáneo, el efector final describe una trayectoria más directa en el espacio hacia su objetivo, lo que en trayectorias cortas puede asemejarse al trazado de una linea recta en el espacio. En el modo secuencial, el TCP realiza una trayectoria escalonada y fragmentada, describiendo arcos basante pronunciados que dependen de la articulación que se esté moviendo en ese instante.
- Suavidad: El desplazamiento simultáneo resulta mucho más natural, armónico y fluido para la estructura mecánica. El control secuencial, al arrancar y detenerse en cada eslabón, genera un movimiento rígido que puede inducir mayores vibraciones e inercia en la base del manipulador, aunque en el desplazamiento simultaneo también se evidencian efectos de inercia pero en menor magnitud.

## Actividad 9. Interpolación de trayectorias

En esta actividad se implementó un algoritmo de interpolación de trayectorias. Este método permite calcular puntos intermedios entre una configuración articular inicial y una configuración objetivo a lo largo de un tiempo determinado, generando perfiles de movimiento suaves para cada servomotor. Durante la ejecución de las pruebas físicas, se registraron los datos cinemáticos de las articulaciones para analizar su comportamiento en el tiempo.

[Código del ejercicio](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/interpolacion.py)

```mermaid
flowchart TD
    A[Inicio] --> B[Inicializar ROS 2: rclpy.init]
    B --> C[Instanciar nodo Interpolador y suscribirse a /joint_states]
    C --> D[Configurar velocidad = 150]

    D --> E[Mover a posición HOME]
    E --> F[Esperar 5s]

    F --> G["Calcular trayectoria lineal (s = t / T)"]
    G --> H["Ejecutar y registrar trayectoria lineal\n(dt = 0.05s)"]

    H --> I[Iterar por cada pose de la trayectoria]
    I --> J[Publicar pose en /pincher/command]
    J --> K[rclpy.spin_once: leer q_medida]
    K --> L[Guardar datos de q_deseada y q_medida en grados]
    L --> M{¿Quedan poses?}
    M -- Sí --> I

    M -- No --> N[Regresar a HOME y esperar 5s]

    N --> O["Calcular trayectoria cúbica (s = 3s² - 2s³)"]
    O --> P["Ejecutar y registrar trayectoria cúbica\n(dt = 0.05s)"]

    P --> Q[Regresar a HOME y esperar 5s]

    Q --> R[Calcular errores: e = q_deseada - q_medida]
    R --> S[Generar gráficas de trayectorias y errores con Matplotlib]
    S --> T[Mostrar gráficas: plt.show]
    T --> U[rclpy.shutdown]
    U --> V[Fin]
```

A continuación, se presentan las gráficas resultantes que ilustran la evolución de las posiciones articulares durante el movimiento interpolado:

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/L1.png)

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/L2.png)

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/L3.png)

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/L4.png)

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/E1.png)

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/E2.png)

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/E3.png)

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/E4.png)

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/C1.png)

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/C2.png)

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/C3.png)

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/C4.png)

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/EC1.png)

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/EC2.png)

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/EC3.png)

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/EC4.png)

Al analizar las gráficas y el comportamiento físico del manipulador bajo los dos métodos de interpolación, se concluye que ambos algoritmos ofrecen un buen performance general, logrando que el movimiento del robot sea suave y controlado. Sin embargo, al observar el detalle del seguimiento de trayectoria de los servomotores, se evidencian las siguientes diferencias:

- Interpolación Lineal: Se notó que la diferencia entre la trayectoria deseada calculada por el algoritmo y la posición actual reportada por el motor se mantiene casi constante a lo largo de todo el movimiento. Esto ocurre porque la interpolación lineal asume una velocidad constante que arranca y se detiene abruptamente, obligando al motor a mantener un "retraso" constante mientras intenta perseguir el punto objetivo que avanza linealmente.
- Interpolación Cúbica: Por otro lado, en la interpolación cúbica se nota una mejora significativa. La diferencia entre la trayectoria actual y la deseada se mantiene considerablemente más baja al comienzo y al final del ciclo si la comparamos con el método de interpolación lineal analizado anteriormente. Gracias a que este método genera un perfil de velocidades suave, el servomotor tiene la dinámica adecuada para alcanzar su posición final con mayor prontitud, por lo que se preferiría emplear este método si se desea obtener un error menor.

## Actividad 10. Seguimiento de trayectoria sinusoidal

Para evaluar la capacidad de respuesta dinámica del manipulador, se implementó una rutina donde la articulación del codo describe una trayectoria sinusoidal continua en el tiempo. El objetivo de esta prueba fue analizar cómo el cambio en la frecuencia y la amplitud de la señal (que se traduce en la rapidez del movimiento) afecta la capacidad del servomotor para seguir la ruta deseada con precisión.

[Código del ejercicio](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/sinusoidal.py)

```mermaid
flowchart TD
    A[Inicio] --> B[Inicializar ROS 2: rclpy.init]
    B --> C[Instanciar nodo Senoidal y suscribirse a /joint_states]
    C --> D[Configurar velocidad = 200]
    D --> E[Seleccionar articulación Elbow e índice 2, Duración = 10s]

    E --> F[Iterar por cada prueba\n A=40°/70°, f=0.1Hz/0.3Hz]

    F --> G{¿Amplitud excede límites?}
    G -- Sí --> H[Mostrar error y cancelar prueba] --> P
    G -- No --> I[Iniciar temporizador t = 0]

    I --> J["Ecuación senoidal:\nq = A * sin(2*π*f*t)"]
    J --> K[Publicar pose en /pincher/command]
    K --> L[rclpy.spin_once: leer q_medida]
    L --> M[Guardar t, q_deseada y q_medida]

    M --> N{¿t > duración?}
    N -- No --> J
    N -- Sí --> O[Calcular Error Máximo y RMSE]
    O --> Q[Imprimir métricas en consola]
    Q --> R[Generar y mostrar gráfica: plt.show]
    R --> P{¿Quedan pruebas por ejecutar?}

    P -- Sí --> F
    P -- No --> S[Destruir nodo y rclpy.shutdown]
    S --> T[Fin]
```

A continuación, se presentan las gráficas y los indicadores que contrastan la posición calculada (deseada) contra la posición medida (real) por el actuador del codo a diferentes frecuencias:

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/Sinu1.png)

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/Sinu2.png)

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/Sinu3.png)

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/Sinu4.png)


| Amplitud (°) | Frecuencia (Hz) | Error máximo (°) | Error cuadrático medio |
| :--- | :---: | :---: | :---: |
| 70 | 0.1 | 27.867 | 16.839 |
| 70 | 0.3 | 88.780 | 53.981 |
| 40 | 0.1 | 17.164 | 9.662 |
| 40 | 0.3 | 53.911 | 30.261 |


Al analizar el comportamiento físico del manipulador y los datos graficados, se evidenció una relación directa entre la frecuencia de la trayectoria y la magnitud del error de seguimiento. Se pudo notar que los errores son significativamente más grandes cuando la frecuencia del movimiento es más alta y cuando se aumenta la amplitud. Esto se debe a que una mayor frecuencia exige una mayor velocidad y aceleración instantánea en la articulación del codo para poder completar el ciclo en menos tiempo. De manera equivalente, si se aumenta la amplitud, el manipulador debe recorrer mayor distancia en el mismo tiempo. Al someter al servomotor a esta alta demanda, las limitaciones mecánicas y de control del sistema se hacen evidentes, impidiendo que el motor alcance la posición a tiempo. Como consecuencia, se genera un desfase o "lag" evidente, resultando en una mayor diferencia entre la posición calculada teóricamente y la posición real que el sensor logra medir en ese instante de tiempo.

## Actividad 11. Cinemática directa

Para esta actividad, se obtuvieron los parámetros de Denavit-Hartenberg (DH) del manipulador, elaborando el diagrama con la guía de 9 pasos vista en clase:

1) Enumerar articulaciones
2) Enumerar eslabones
3) Enumerar ejes (J_i)
4) Definir normales comunes (n_i)
5) Definir ejes (z_i)
6) Definir orígenes (O_i)
7) Definir ejes (x_i)
8) Definir ejes (y_i)
9) Extraer parámetros DH

![image](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/diagrama.png)

La tabla de parámetros Denavit-Hartenberg se presenta a continuación: 

| i | θ_i | d_i | a_i | α_i |
| :--- | :---: | :---: | :---: | :---: |
| 1 | q_1 | l_1 | 0 | -90° |
| 2 | q_2 - 90° | 0 | l_2 | 0 |
| 3 | q_3 | 0 | l_3 | 0 |
| 4 | q_4 + 90° | 0 | 0 | 90° |
| 5 | 0 | l_4 | 0 | 0 |

> **Nota:** la fila i = 5 fue agregada con el objetivo de tener una matríz de transformación homogénea que nos permita llegar efectivamente al efector final, pues sin esta, el punto final se encontraría en la articulación de la muñeca.

El programa que posteriormente se desarrolló está diseñado para recibir los cuatro valores articulares del brazo (q_1, q_2, q_3, q_4) y, a partir de ellos, construir las matrices de transformación homogéneas y calcular las coordenadas cartesianas y la orientación de la herramienta (x, y, z, roll, pitch, yaw).

[Código del ejercicio](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/directa.py)

```mermaid
flowchart TD
    A[Inicio] --> B[Inicializar ROS 2: rclpy.init]
    B --> C[Instanciar nodo ControlRobot]
    C --> D[Definir eslabones l1..l4 y pose deseada q]
    D --> E[Configurar velocidad = 50]

    E --> F{¿Pose q dentro de límites?}
    F -- No --> G[Mostrar 'MOVIMIENTO ABORTADO' y cancelar] --> N
    F -- Sí --> H[Sumar offsets, convertir a rad y publicar JointState]
    
    H --> I[Ejecutar rclpy.spin_once]
    I --> J[Convertir q1..q4 a radianes]
    J --> K[Construir matrices DH: A1, A2, A3, A4, A5]
    K --> L["Calcular matriz homogénea T05\n(T05 = A1 * A2 * A3 * A4 * A5)"]
    L --> M[Extraer Posición x, y, z de T05]
    M --> O[Calcular Orientación RPY: Roll, Pitch, Yaw]
    O --> P[/Imprimir T05, Posición y Orientación en consola/]

    P --> N[Esperar 2s, destruir nodo y rclpy.shutdown]
    N --> Q[Fin]
```

Para comprobar el funcionamiento del algoritmo, se adjuntan pantallazos en donde se evalúa la cinemática directa utilizando cinco configuraciones articulares (las cuales se muestran al principio de la consola), comparando los resultados calculados de posición y orientación del efector final con los observados gráficamente en la simulación de RViz.
![Directa 1](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/DIRE1.png)
![Directa 2](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/DIRE2.png)
![Directa 3](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/DIRE3.png)
![Directa 4](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/DIRE4.png)
![Directa 5](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/DIRE5.png)

Durante esta comparación, se observó una ligera discrepancia entre el modelo matemático (el código desarrollado), el simulado en RViz y el comportamiento del robot real. Esta diferencia tiene su origen en que el modelado tridimensional (los archivos .stl) del eslabón que conecta la articulación del hombro con la del codo presenta dimensiones ligeramente diferentes a la estructura física en nuestro manipulador. A nivel práctico, este desfase se traduce en un error de posición en el efector final de apenas unos pocos milímetros. Para aplicaciones generales de desplazamiento o ejecución de coreografías, esta pequeña diferencia no afecta de manera significativa el rendimiento ni la apreciación del movimiento. Sin embargo, es importante mencionar que si se deseara utilizar este brazo para aplicaciones industriales de alta precisión (como tareas finas de pick and place descritas en el proyecto), sí sería necesario revisar el modelado del eslabón con mayor detenimiento y calibrar el modelo cinemático para mitigar esta discrepancia física. Pero, de manera general, se observó que el modelo descrito por el script desarrollado en Python y el comportamiento del robot físico se corresponden de manera excelente: aunque no fue posible tomar medidas rigurosas del robot en las configuraciones proporcionadas, visualmente se identifica que el efector final del robot sí se encuentra en la posición y orientación que el script registra.

## Actividad 12. Cinemática inversa

La cinemática inversa permite determinar la configuración articular (los ángulos de cada motor) necesaria para que el efector final del manipulador alcance una posición espacial específica, definida por sus coordenadas cartesianas (x, y, z). Para dar solución a este problema, en primera instancia se realizó el planteamiento geométrica. Esto permitió plantear las ecuaciones necesarias para hallar las múltiples soluciones posibles, incluyendo las configuraciones de codo arriba y codo abajo.

A continuación, se adjunta la evidencia del desarrollo:

![Procedimiento matemático 1](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/CinematicaInversa1.jpg)

![Procedimiento matemático 2](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/CinematicaInversa2.jpg)

![Procedimiento matemático 3](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/CinematicaInversa3.jpg)

Posteriormente, las ecuaciones obtenidas se implementaron en el código del ejercicio. El algoritmo resultante no solo calcula los ángulos requeridos, sino que incluye una lógica de validación que cumple con los siguientes requisitos:

1. Calcula todas las soluciones articulares posibles para la configuración del efector final (x, y, z, θ) ingresada inicialmente.
2. Identifica y clasifica si las configuraciones resultantes corresponden a posturas de *codo arriba* o *codo abajo*.
3. Filtra y descarta automáticamente aquellas soluciones matemáticas que incumplan los límites físicos de seguridad de los servomotores (establecidos en la Actividad 6).
4. Genera una alerta informativa en caso de que el punto espacial solicitado se encuentre fuera del espacio de trabajo del robot.
5. Selecciona y ejecuta de manera autónoma la solución válida elegida.

[Código del ejercicio](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/inversa.py)

```mermaid
flowchart TD
    A[Inicio] --> B[Inicializar ROS 2: rclpy.init]
    B --> C[Instanciar nodo ControlRobot]
    C --> D[/Solicitar Px, Py, Pz y Theta TCP al usuario/]

    D --> E["Calcular q1 = atan2(Py, Px)\ny cos(q3)"]

    E --> F{"¿|cos(q3)| <= 1?\n(Punto alcanzable)"}
    F -- No --> G[Mostrar error: Fuera del espacio de trabajo] --> N
    F -- Sí --> H["Calcular soluciones q2, q3 y q4\n(Codo Arriba y Codo Abajo)"]

    H --> I[Validar límites articulares para ambas soluciones]
    I --> J{¿Hay soluciones válidas?}

    J -- No --> K[Mostrar error: Configuración fuera de límites] --> N
    J -- Sí --> L[/Mostrar soluciones válidas y solicitar selección/]

    L --> M{¿Selección válida?}
    M -- Cancelar / Vacío --> N
    M -- Sí --> O[Convertir q a grados]
    O --> P[Publicar comando con robot.mover]
    P --> Q[Esperar 0.5s] --> N

    N[rclpy.shutdown] --> R[Fin]
```

![Procedimiento matemático 3](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/inv6.png)
![Procedimiento matemático 3](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/inversa2.png)
![Procedimiento matemático 3](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/inversa3.png)
![Procedimiento matemático 3](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/inversa4.png)
![Procedimiento matemático 3](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/inversa5.png)



## Actividad 13. Enseñanza y repetición de poses

Para esta sección, se desarrolló un nodo que habilita un modo de "enseñanza" en el robot. Este programa permite mover el manipulador manualmente o por comandos hacia posiciones específicas, guardar la configuración articular actual, y asignarle un nombre identificador. En total se registraron y almacenaron ocho poses diferentes. Para garantizar la persistencia de los datos, estas posturas fueron guardadas en un archivo de configuración .yaml. Finalmente, la rutina de repetición lee este archivo y reproduce las poses en el orden registrado.

[Código del ejercicio](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/ensenanza.py)

```mermaid
flowchart TD
    A[Inicio] --> B[Inicializar ROS 2: rclpy.init]
    B --> C[Instanciar nodo Teacher / MODO ENSEÑANZA]
    C --> D[Mostrar Menú Principal]

    D --> E{Seleccionar Opción}

    E -- "1: Mover robot" --> F1[Solicitar ángulos q1 a q5]
    F1 --> F2{¿Ángulos dentro\nde límites?}
    F2 -- No --> F3[Mostrar error y cancelar] --> D
    F2 -- Sí --> F4[Publicar pose con mover_pose] --> D

    E -- "2: Guardar pose" --> G1[rclpy.spin_once: leer position]
    G1 --> G2[Solicitar nombre de la pose]
    G2 --> G3[Guardar q_actual en grados dentro de poses.yaml] --> D

    E -- "3: Listar poses" --> H1[Cargar poses desde poses.yaml]
    H1 --> H2[Mostrar lista de poses en consola] --> D

    E -- "4: Reproducir poses" --> I1[Configurar velocidad = 40]
    I1 --> I2[Cargar secuencia desde poses.yaml]
    I2 --> I3[Iterar por cada pose de la secuencia]
    I3 --> I4[Enviar pose y esperar llegada error < 2°]
    I4 --> I5[Esperar tiempo de transición]
    I5 --> I6{¿Fin de lista o stop_requested?}
    I6 -- Siguiente pose --> I3
    I6 -- Terminado / Cancelado --> D

    E -- "5: Cambiar tiempo" --> J1[Solicitar nuevo tiempo de transición]
    J1 --> J2[Actualizar self.transition_time] --> D

    E -- "6: Detener" --> K1[Activar stop_requested = True] --> D

    E -- "0: Salir" --> L[Destruir nodo y rclpy.shutdown]
    L --> M[Fin]
```

Video del ejercicio:

[![Ver el video](https://img.youtube.com/vi/4CZ2Z-obUDc/maxresdefault.jpg)](https://www.youtube.com/watch?v=4CZ2Z-obUDc)

## Actividad 14. Trazado de una figura

Con el fin de validar la cinemática inversa del manipulador, se procedió a realizar el trazado de un circulo en el aire. Para lograr esto, la trayectoria geométrica no se programó enviando ángulos directamente a los motores, sino que se definió mediante una lista de coordenadas de puntos cartesianos (x, y, z) en el espacio de trabajo. Se definió que el manipulador trazaría una circunferencia, estableciendo la ubicación del centro, el radio y el plano z constante en donde se realizaría dicho trazo. Posteriormente, el algoritmo resuelve la cinemática inversa para cada uno de estos puntos, calculando y enviando los ángulos articulares exactos que el robot requiere para mover el efector final y dibujar la figura de manera continua.

[Código del ejercicio](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/circuloinversa.py)

```mermaid
flowchart TD
    A[Inicio] --> B[Inicializar ROS 2: rclpy.init]
    B --> C[Instanciar nodo ControlRobot y configurar velocidad = 20]
    C --> D[Mover robot a posición HOME inicial y esperar 2.5s]

    D --> E["Definir parámetros del círculo:\nR = 45mm, Cx = 104mm, Cy = 0mm\nZ = 156mm, θ = 180°, N = 100 puntos"]
    
    E --> F["Inicializar bandera: primer = 1\nIterar i desde 0 hasta N"]

    F --> G["Calcular ángulo del punto i:\nPx = Cx + R*cos(θ)\nPy = Cy + R*sin(θ)"]
    G --> H["Calcular Cinemática Inversa silenciosa\n(verbose = False)"]

    H --> I{"¿Solución válida y dentro de límites?"}
    I -- No --> J[Mostrar alerta: Punto no alcanzable] --> O
    I -- Sí --> K[Convertir q a grados y enviar con robot.mover]

    K --> L{"¿primer == 1?"}
    L -- Sí --> M1["Esperar 10s (alcanzar inicio)\ny cambiar primer = 0"] --> O
    L -- No --> M2[Esperar 0.15s] --> O

    O --> P{¿Quedan puntos por procesar?}
    P -- Sí (Siguiente i) --> G
    P -- No --> Q[Mover robot a posición HOME final y esperar 2.5s]

    Q --> R[rclpy.shutdown]
    R --> S[Fin]
```

Video del ejercicio:

[![Ver el video](https://img.youtube.com/vi/647Dq322C7E/maxresdefault.jpg)](https://www.youtube.com/watch?v=647Dq322C7E)

El comportamiento presentado en la prueba física es el esperado en cuanto a la determinación de las configuraciones articulares: el trazado del circulo es fácil de apreciar e identificar. Sin embargo, el movimiento no se nota tan fluido, lo que puede deberse principalemente a componentes inerciales al mover el manipulador o a la cantidad de puntos que coponían la circunferencia.

## Actividad 15. Coreografía robótica

Como cierre del laboratorio, se integraron los conceptos de control de movimiento, tiempos de transición e interpolación para programar una coreografía robótica automatizada al ritmo de la canción Chipi Chipi Chapa Chapa. El desarrollo de esta actividad cumple rigurosamente con los parámetros de sincronización, participación total, duración, autonomía y seguridad.

[Código del ejercicio](https://github.com/labsir-un/Robotica-2026-I-Equipo-3A-Arevalo-Lopez/blob/main/Laboratorio%20No.%2005%20-%20Rob%C3%B3tica%20de%20Desarrollo%20ROS%20Jazzy%20y%20Phantom%20Pincher%20X100/files/baile.py)

```mermaid
flowchart TD
    A[Inicio] --> B[Inicializar ROS 2: rclpy.init]
    B --> C["Instanciar nodo Bailarin\n(Convertir límites articulares a radianes)"]
    C --> D["Convertir rutinas (1, 2, 3 y 4)\nde grados a radianes"]

    D --> E["Mover a HOME inicial:\nVelocidad = 50 | Esperar 8s"]

    E --> F1["RUTINA 2 (2 iteraciones):\nVelocidad = 150"]
    F1 --> F2["Iterar poses -> mover(pose)\nspin_once(0.1s) -> sleep(0.282s)"]

    F2 --> G1["RUTINA 3 (2 iteraciones):\nVelocidad = 350"]
    G1 --> G2["Iterar poses -> mover(pose)\nspin_once(0.1s) -> sleep(0.68s)"]

    G2 --> H1["RUTINA 4 (2 iteraciones):\nVelocidad = 300"]
    H1 --> H2["Iterar poses -> mover(pose)\nspin_once(0.1s) -> sleep(0.68s)"]

    H2 --> I1["RUTINA 1 (2 iteraciones):\nVelocidad = 300 / 200"]
    I1 --> I2["Iterar poses -> mover(pose)\nspin_once(0.1s) -> sleep(0.28s)"]

    I2 --> J["Regreso a HOME:\nVelocidad = 100 | Mover a HOME | Esperar 1s"]

    J --> K[rclpy.shutdown]
    K --> L[Fin]

```

Video del ejercicio:

[![Ver el video](https://img.youtube.com/vi/fc764ZbglbgkA1iQ/maxresdefault.jpg)](https://www.youtube.com/watch?v=fc764ZbglbgkA1iQ)

Se evidenció un comportamiento fluido en su mayoría. La mayor parte de las inconsistencias en el movimiento se deben a efectos inerciales, por ejemplo, cuando el hombro tiene una configuración articular cercana a 90° o -90° y el brazo está totalmente estirado.

## Conclusiones

- La alineación precisa entre el modelo virtual en RViz y el robot real —ajustando poses y sentidos de giro— resulta indispensable para prevenir colisiones y garantizar un control seguro. Relacionado a esto y, como aspecto a mejorar, se desea implementar el modelado correcto de los eslabones en los archivos stl, pues esto limita de manera directa la precisión en la manipulación del robot.

- Calibración y Compensación de Errores: Ajustar los offsets por software es clave para corregir el juego mecánico y la carga inercial (más crítica en el hombro), asegurando la mayor presición posible con las herramientas que se disponía en este laboratorio.

- El movimiento coordinado entre articulaciones es más rápido en movimienteo combinados (varios motores moviendose en simultaneo). Este movimiento simultaneo resulta más fluido y natural para el desplazamiento del efector final, a diferencia del modo secuencial que eleva el tiempo de ciclo e induce vibraciones.

- Los perfiles cúbicos superan a los lineales al evitar cambios bruscos de aceleración, reduciendo significativamente el error de seguimiento, por lo menos al inicio y final de cada trayectoria.

- El seguimiento de señales senoidales evidenció que a mayor frecuencia o amplitud, mayor es el desfase, demostrando las limitaciones físicas de velocidad y par de los servomotores AX-12A.

## Referencias

- LABSIR UN. (2026). 06_Rob_2026_I_ROS2_Jazzy_PhantomX100_RVIZ [Repositorio de GitHub]. GitHub. https://github.com/labsir-un/06_Rob_2026_I_ROS2_Jazzy_PhantomX100_RVIZ

