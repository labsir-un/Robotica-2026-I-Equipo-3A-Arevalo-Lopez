# Robótica de Desarrollo, Intro a ROS 2 Jazzy Jalisco - Turtlesim

**Universidad Nacional de Colombia**  
Facultad de Ingeniería – Sede Bogotá

**Estudiantes:**
  - Edward Jeisen Jair Arévalo Peña
  - Juan Diego López Mayorga

**Profesores:**
  - Pedro Fabian Cardenas Herrera
  - Manuel Felipe Carranza Montenegro

28 de Junio del 2026

---

# Descripción general del laboratorio

El presente laboratorio tuvo como objetivo desarrollar una aplicación de control para el simulador **Turtlesim** utilizando **ROS 2 Jazzy Jalisco** y el lenguaje de programación **Python** mediante la biblioteca **rclpy**. Durante el desarrollo se implementaron dos nodos principales: `move_turtle.py`, encargado del control y la interacción con la tortuga principal, y `turtle_follower.py`, responsable de crear una segunda tortuga y realizar un seguimiento automático de la primera.

El nodo **move_turtle.py** implementa un controlador interactivo basado en teclado que permite desplazar la tortuga mediante las flechas de dirección, publicando comandos de velocidad sobre el tópico `/turtle1/cmd_vel`. Además del control manual, incorpora diversas funcionalidades solicitadas en el laboratorio, entre ellas el dibujo automático de figuras geométricas como un cuadrado y un triángulo, el trazado de las letras **E**, **A**, **J** y **L**, un modo de movimiento autónomo dentro de los límites del simulador, el reinicio de la posición de la tortuga mediante servicios de teletransporte y la activación o desactivación del lápiz para controlar el dibujo sobre la pantalla. Todas estas acciones se realizan haciendo uso de la comunicación mediante tópicos y servicios propios de ROS 2.

Como complemento, se desarrolló el nodo **turtle_follower.py**, cuya función consiste en crear dinámicamente una segunda tortuga mediante el servicio `Spawn` y controlar su movimiento para que siga continuamente a la tortuga principal. Para ello, el nodo se suscribe a los tópicos de posición de ambas tortugas (`/turtle1/pose` y `/turtle2/pose`), calcula en tiempo real la distancia y el ángulo entre ellas y genera comandos de velocidad proporcionales que permiten un seguimiento suave y estable, manteniendo una separación mínima para evitar que ambas tortugas se superpongan.

Finalmente, el laboratorio permitió aplicar los conceptos fundamentales de ROS 2 relacionados con la creación de nodos, publicación y suscripción a tópicos, utilización de servicios, temporizadores y programación de aplicaciones distribuidas. Asimismo, se evidenció la interacción entre múltiples nodos ejecutándose simultáneamente y comunicándose mediante la arquitectura de ROS 2 para implementar un sistema completo de control y seguimiento en un entorno de simulación.
