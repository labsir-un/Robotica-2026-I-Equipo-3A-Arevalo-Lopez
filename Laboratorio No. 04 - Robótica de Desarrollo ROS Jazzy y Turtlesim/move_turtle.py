import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import SetPen, TeleportAbsolute
import sys
import select
import termios
import tty
import time
import math

key_bindings = {
    '\x1b[A': (2.0, 0.0),   
    '\x1b[B': (-2.0, 0.0),  
    '\x1b[C': (0.0, -2.0),  
    '\x1b[D': (0.0, 2.0),   
}

class TurtleController(Node):
    def __init__(self):
        super().__init__('turtle_controller')
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        self.teleport_client = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        
        self.pose_subscriber = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.current_pose = None
        
        self.pen_is_off = False 
        self.is_drawing = False 
        self.auto_mode = False 
        
        self.settings = termios.tcgetattr(sys.stdin)
        self.get_logger().info('¡Controlador iniciado!')
        self.get_logger().info('Flechas: Mover | S: Cuadrado | T: Triángulo | A: Autónomo')
        self.get_logger().info('Letras: E, Z(para la A), J, L | Q: Detener | R: Reiniciar | P: Lápiz')
        
        self.timer = self.create_timer(0.05, self.read_keyboard_loop)

    def pose_callback(self, msg):
        self.current_pose = msg

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
        if rlist:
            key = sys.stdin.read(1)
            if key == '\x1b':
                key += sys.stdin.read(2) 
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def execute_movement(self, linear, angular, duration):
        start_time = time.time()
        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular
        
        abort = False
        while time.time() - start_time < duration:
            self.publisher_.publish(msg) 
            tty.setraw(sys.stdin.fileno())
            rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
            char = ''
            if rlist:
                char = sys.stdin.read(1)
                if char == '\x1b':
                    char += sys.stdin.read(2)
            
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
            
            if char:
                if char.startswith('\x1b'): pass 
                elif char.lower() == 'q' or char == '\x03': abort = True 
                elif char.lower() == 'p': self.toggle_pen() 
                elif char.lower() == 'r': self.reset_position() 
            
            if abort: break

        if abort: self.stop_turtle()
        return abort 

    def stop_turtle(self):
        self.auto_mode = False
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.publisher_.publish(msg)

    def autonomous_bounce(self):
        if self.current_pose is None: return
        msg = Twist()
        if (self.current_pose.x < 1.5 or self.current_pose.x > 9.5 or 
            self.current_pose.y < 1.5 or self.current_pose.y > 9.5):
            msg.linear.x = 0.5
            msg.angular.z = 2.0 
        else:
            msg.linear.x = 2.0
            msg.angular.z = 0.0
        self.publisher_.publish(msg)

    def draw_square(self):
        self.is_drawing = True
        self.get_logger().info('Dibujando Cuadrado...')
        for _ in range(4):
            if self.execute_movement(2.0, 0.0, 1.0): self.is_drawing = False; return 
            if self.execute_movement(0.0, math.pi / 2.0, 1.0): self.is_drawing = False; return
        self.stop_turtle(); self.is_drawing = False

    def draw_triangle(self):
        self.is_drawing = True
        self.get_logger().info('Dibujando Triángulo...')
        for _ in range(3):
            if self.execute_movement(2.0, 0.0, 1.0): self.is_drawing = False; return
            if self.execute_movement(0.0, (2.0 * math.pi) / 3.0, 1.0): self.is_drawing = False; return
        self.stop_turtle(); self.is_drawing = False

    # ================= FUNCIONES DE LAS LETRAS =================
    def draw_E(self):
        self.is_drawing = True
        self.get_logger().info('Dibujando letra E...')
        if self.execute_movement(1.5, 0.0, 1.0): self.is_drawing = False; return # Trazo arriba
        if self.execute_movement(-1.5, 0.0, 1.0): self.is_drawing = False; return # Regresa
        if self.execute_movement(0.0, -math.pi/2, 1.0): self.is_drawing = False; return # Gira 90 der
        if self.execute_movement(1.5, 0.0, 1.0): self.is_drawing = False; return # Baja mitad
        if self.execute_movement(0.0, math.pi/2, 1.0): self.is_drawing = False; return # Gira 90 izq
        if self.execute_movement(1.0, 0.0, 1.0): self.is_drawing = False; return # Trazo medio
        if self.execute_movement(-1.0, 0.0, 1.0): self.is_drawing = False; return # Regresa
        if self.execute_movement(0.0, -math.pi/2, 1.0): self.is_drawing = False; return # Gira 90 der
        if self.execute_movement(1.5, 0.0, 1.0): self.is_drawing = False; return # Baja final
        if self.execute_movement(0.0, math.pi/2, 1.0): self.is_drawing = False; return # Gira 90 izq
        if self.execute_movement(1.5, 0.0, 1.0): self.is_drawing = False; return # Trazo abajo
        self.stop_turtle(); self.is_drawing = False

    def draw_A(self):
        self.is_drawing = True
        self.get_logger().info('Dibujando letra A...')
        if self.execute_movement(0.0, 1.2, 1.0): self.is_drawing = False; return # Gira diagonal izq
        if self.execute_movement(2.5, 0.0, 1.0): self.is_drawing = False; return # Sube
        if self.execute_movement(0.0, -2.4, 1.0): self.is_drawing = False; return # Gira diagonal der
        if self.execute_movement(2.5, 0.0, 1.0): self.is_drawing = False; return # Baja
        if self.execute_movement(-1.25, 0.0, 1.0): self.is_drawing = False; return # Sube por la misma pata
        if self.execute_movement(0.0, 1.2, 1.0): self.is_drawing = False; return # Se endereza
        if self.execute_movement(-1.0, 0.0, 1.0): self.is_drawing = False; return # Hace el puente horizontal
        self.stop_turtle(); self.is_drawing = False

    def draw_J(self):
        self.is_drawing = True
        self.get_logger().info('Dibujando letra J...')
        if self.execute_movement(2.0, 0.0, 1.0): self.is_drawing = False; return # Trazo arriba
        if self.execute_movement(-1.0, 0.0, 1.0): self.is_drawing = False; return # Al centro
        if self.execute_movement(0.0, -math.pi/2, 1.0): self.is_drawing = False; return # Gira 90 der
        if self.execute_movement(2.0, 0.0, 1.0): self.is_drawing = False; return # Baja
        if self.execute_movement(0.0, -math.pi/2, 1.0): self.is_drawing = False; return # Gira 90 der para la curva
        if self.execute_movement(1.0, 0.0, 1.0): self.is_drawing = False; return # Curva abajo
        self.stop_turtle(); self.is_drawing = False

    def draw_L(self):
        self.is_drawing = True
        self.get_logger().info('Dibujando letra L...')
        if self.execute_movement(0.0, -math.pi/2, 1.0): self.is_drawing = False; return # Gira hacia abajo
        if self.execute_movement(2.5, 0.0, 1.0): self.is_drawing = False; return # Baja
        if self.execute_movement(0.0, math.pi/2, 1.0): self.is_drawing = False; return # Gira a la derecha
        if self.execute_movement(1.5, 0.0, 1.0): self.is_drawing = False; return # Trazo base
        self.stop_turtle(); self.is_drawing = False
    # ==========================================================
        
    def reset_position(self):
        if self.teleport_client.wait_for_service(timeout_sec=1.0):
            req = TeleportAbsolute.Request()
            req.x = 5.544445; req.y = 5.544445; req.theta = 0.0
            self.teleport_client.call_async(req)

    def toggle_pen(self):
        if self.pen_client.wait_for_service(timeout_sec=1.0):
            req = SetPen.Request()
            req.r = 255; req.g = 255; req.b = 255; req.width = 3
            self.pen_is_off = not self.pen_is_off
            req.off = int(self.pen_is_off)
            self.pen_client.call_async(req)

    def read_keyboard_loop(self):
        if self.is_drawing: return 

        key = self.get_key()
        
        if key in key_bindings:
            self.auto_mode = False 
            vel = key_bindings[key]
            msg = Twist()
            msg.linear.x = vel[0]
            msg.angular.z = vel[1]
            self.publisher_.publish(msg)
            
        elif key.lower() == 'a':
            self.auto_mode = True
            self.get_logger().info('Modo autónomo activado.')
        elif key.lower() == 's': self.auto_mode = False; self.draw_square()
        elif key.lower() == 't': self.auto_mode = False; self.draw_triangle()
        
        # TECLAS DE LAS INICIALES
        elif key.lower() == 'e': self.auto_mode = False; self.draw_E()
        elif key.lower() == 'z': self.auto_mode = False; self.draw_A()
        elif key.lower() == 'j': self.auto_mode = False; self.draw_J()
        elif key.lower() == 'l': self.auto_mode = False; self.draw_L()
        
        elif key.lower() == 'q': self.stop_turtle()
        elif key.lower() == 'r': self.reset_position()
        elif key.lower() == 'p': self.toggle_pen()
        elif key == '\x03': sys.exit(0)

        if self.auto_mode:
            self.autonomous_bounce()

def main(args=None):
    rclpy.init(args=args)
    node = TurtleController()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, node.settings)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()