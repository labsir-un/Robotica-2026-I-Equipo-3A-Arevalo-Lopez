# ==============================================================================
# SCRIPT SEGUIDOR - LAB 04 ROBÓTICA
# Nodo encargado de crear una segunda tortuga que persigue automáticamente 
# a la tortuga principal (turtle1) en tiempo real.
# ==============================================================================

from urllib import request

import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from turtlesim.srv import Spawn
import math

class Follower(Node):
    def __init__(self):
        super().__init__('turtle_follower')
        
        # 1. Cliente de servicio Spawn: Llama al servicio para crear a turtle2        
        self.spawn_client = self.create_client(Spawn, 'spawn')
        self.spawn_turtle()

        # 2. Suscriptores de posición: Obtienen las coordenadas en tiempo real de ambas tortugas
        self.pose1 = None # Pose de la tortuga líder
        self.pose2 = None # Pose de la tortuga seguidora
        self.sub_pose1 = self.create_subscription(Pose, '/turtle1/pose', self.pose1_callback, 10)
        self.sub_pose2 = self.create_subscription(Pose, '/turtle2/pose', self.pose2_callback, 10)

        #3. Publicador de movimiento: Envía las velocidades calculadas únicamente a turtle2
        self.pub_cmd_vel = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)

        # 4. Temporizador de control: Ejecuta el algoritmo de seguimiento 20 veces por segundo
        self.timer = self.create_timer(0.05, self.control_loop)

    def spawn_turtle(self):
        # Bucle de seguridad: Espera a que el servicio spawn esté en línea en la arquitectura ROS
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Esperando al servicio spawn para crear turtle2...')
            
        request = Spawn.Request()
        request.x = 2.0  # Posición inicial X para turtle2
        request.y = 2.0  # Posición inicial Y para turtle2
        request.theta = 0.0 # Orientación inicial
        request.name = 'turtle2'
        
        # Llama al servicio de forma asíncrona (sin bloquear el código)
        self.spawn_client.call_async(request)
        self.get_logger().info('¡Turtle2 ha entrado al simulador!')

    def pose1_callback(self, msg):
        # Callback invocado automáticamente al recibir datos de /turtle1/pose
        self.pose1 = msg

    def pose2_callback(self, msg):
        # Función ejecutada periódicamente por el temporizador.
        # Calcula el movimiento necesario para que turtle2 siga a turtle1.
        self.pose2 = msg

    def control_loop(self):
        # Callback invocado automáticamente al recibir datos de /turtle2/pose
        if self.pose1 is None or self.pose2 is None:
            return

        # Calcular la diferencia de distancia geométrica (hipotenusa)
        dx = self.pose1.x - self.pose2.x
        dy = self.pose1.y - self.pose2.y
        distance = math.sqrt(dx**2 + dy**2)

        msg = Twist()

        # Si la distancia es mayor a 0.5, la perseguimos (para evitar que se superpongan)
        if distance > 0.5:
            # Calcular el ángulo hacia el que debe mirar turtle2
            angle_to_target = math.atan2(dy, dx)
            
            # Diferencia entre donde mira y donde debería mirar
            angle_diff = angle_to_target - self.pose2.theta
            
            # Normalizar el ángulo para que siempre gire por el camino más corto
            angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))

            # Velocidad lineal proporcional a la distancia
            msg.linear.x = 1.5 * distance
            # Limitamos la velocidad para que no "vuele" de forma incontrolable
            if msg.linear.x > 3.0: 
                msg.linear.x = 3.0
            
            # Velocidad angular proporcional a la diferencia de ángulo
            msg.angular.z = 4.0 * angle_diff
        else:
            # Ya la alcanzó, se detiene
            msg.linear.x = 0.0
            msg.angular.z = 0.0

        # Publicar la velocidad para que turtle2 se mueva
        self.pub_cmd_vel.publish(msg)

def main(args=None):
    # Función principal de inicialización y ejecución del nodo seguidor
    rclpy.init(args=args)
    node = Follower()
    try:
        rclpy.spin(node) # Mantiene el nodo vivo procesando callbacks
    except KeyboardInterrupt:
        pass
    finally:
        # Apagado limpio
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()