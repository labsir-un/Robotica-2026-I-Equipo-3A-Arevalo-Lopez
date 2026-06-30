import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from turtlesim.srv import Spawn
import math

class Follower(Node):
    def __init__(self):
        super().__init__('turtle_follower')
        
        # 1. Llamar al servicio Spawn para crear a turtle2
        self.spawn_client = self.create_client(Spawn, 'spawn')
        self.spawn_turtle()

        # 2. Suscriptores: Leer las posiciones de ambas tortugas
        self.pose1 = None
        self.pose2 = None
        self.sub_pose1 = self.create_subscription(Pose, '/turtle1/pose', self.pose1_callback, 10)
        self.sub_pose2 = self.create_subscription(Pose, '/turtle2/pose', self.pose2_callback, 10)

        # 3. Publicador: Enviar velocidades a turtle2
        self.pub_cmd_vel = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)

        # 4. Temporizador para calcular y ajustar el seguimiento 20 veces por segundo
        self.timer = self.create_timer(0.05, self.control_loop)

    def spawn_turtle(self):
        # Esperar a que el servicio esté disponible
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Esperando al servicio spawn para crear turtle2...')
            
        request = Spawn.Request()
        request.x = 2.0  # Posición inicial X
        request.y = 2.0  # Posición inicial Y
        request.theta = 0.0
        request.name = 'turtle2'
        
        # Llamar al servicio
        self.spawn_client.call_async(request)
        self.get_logger().info('¡Turtle2 ha entrado al simulador!')

    def pose1_callback(self, msg):
        self.pose1 = msg

    def pose2_callback(self, msg):
        self.pose2 = msg

    def control_loop(self):
        # Si aún no tenemos la posición de ambas tortugas, no hacemos nada
        if self.pose1 is None or self.pose2 is None:
            return

        # Calcular la diferencia de distancia en X y en Y
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
    rclpy.init(args=args)
    node = Follower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()