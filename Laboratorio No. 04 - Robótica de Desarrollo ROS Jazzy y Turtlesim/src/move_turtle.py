# ==============================================================================
# SCRIPT DE CONTROL PRINCIPAL - LAB 04 ROBÓTICA
# Este nodo permite controlar a 'turtle1' en el simulador Turtlesim mediante
# teclado, trazar figuras automáticas y letras personalizadas.
# ==============================================================================

from platform import node

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

# Diccionario que mapea las secuencias de escape del teclado (flechas) 
# a velocidades específicas. Formato: (velocidad_lineal_x, velocidad_angular_z)

key_bindings = {
    '\x1b[A': (2.0, 0.0),   # Flecha Arriba: Avanzar
    '\x1b[B': (-2.0, 0.0),  # Flecha Abajo: Retroceder
    '\x1b[C': (0.0, -2.0),  # Flecha Derecha: Girar horario
    '\x1b[D': (0.0, 2.0),   # Flecha Izquierda: Girar antihorario
}

class TurtleController(Node):
    def __init__(self):
        # 1. Inicialización del nodo en ROS 2
        super().__init__('turtle_controller')
        
        # 2. Publicador de movimiento: Envía comandos de velocidad (Twist) a turtle1
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
        # 3. Clientes de servicios: Permiten modificar propiedades en el simulador
        self.pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        self.teleport_client = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        
        # 4. Suscriptor de posición: Lee constantemente dónde está turtle1
        self.pose_subscriber = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.current_pose = None
        
        # 5. Banderas (flags) lógicas para el control de flujo
        self.pen_is_off = False 
        self.is_drawing = False 
        self.auto_mode = False 
        
        # 6. Guardar la configuración original de la terminal para restaurarla al salir
        self.settings = termios.tcgetattr(sys.stdin)
        
        # 7. Interfaz de consola para el usuario
        self.get_logger().info('¡Controlador iniciado!')
        self.get_logger().info('Flechas: Mover | S: Cuadrado | T: Triángulo | A: Autónomo')
        self.get_logger().info('Letras: E, Z(para la A), J, L | Q: Detener | R: Reiniciar | P: Lápiz')
        
        # 8. Temporizador que ejecuta la lectura del teclado cada 0.05 segundos (20Hz)
        self.timer = self.create_timer(0.05, self.read_keyboard_loop)

    def pose_callback(self, msg):
        # Actualiza la variable con la posición y orientación real de la tortuga
        self.current_pose = msg

    def get_key(self):
        # Lee el teclado de forma no bloqueante (sin pausar el código)
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
        if rlist:
            key = sys.stdin.read(1)
            if key == '\x1b':
                key += sys.stdin.read(2) 
        else:
            key = ''
        # Restaura la consola inmediatamente después de leer la tecla
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def execute_movement(self, linear, angular, duration):
        # Ejecuta un movimiento de velocidad constante durante un tiempo específico
        start_time = time.time()
        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular
        
        abort = False
        # Mientras no se acabe el tiempo 'duration', sigue publicando el comando
        while time.time() - start_time < duration:
            self.publisher_.publish(msg) 
            # Bloque de lectura de teclado de emergencia durante el movimiento
            tty.setraw(sys.stdin.fileno())
            rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
            char = ''
            if rlist:
                char = sys.stdin.read(1)
                if char == '\x1b':
                    char += sys.stdin.read(2)
            
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
            # Procesamiento de teclas de interrupción
            if char:
                if char.startswith('\x1b'): pass 
                elif char.lower() == 'q' or char == '\x03': abort = True 
                elif char.lower() == 'p': self.toggle_pen() 
                elif char.lower() == 'r': self.reset_position() 
            
            if abort: break
        # Si el movimiento fue abortado por el usuario, frena la tortuga
        if abort: self.stop_turtle()
        return abort 

    def stop_turtle(self):
        # Envía un comando de velocidad 0 para frenar por completo
        self.auto_mode = False
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.publisher_.publish(msg)

    def autonomous_bounce(self):
        # Modo autónomo: Si la tortuga se acerca a los límites (1.5 o 9.5), gira
        if self.current_pose is None: return
        msg = Twist()
        if (self.current_pose.x < 1.5 or self.current_pose.x > 9.5 or 
            self.current_pose.y < 1.5 or self.current_pose.y > 9.5):
            msg.linear.x = 0.5
            msg.angular.z = 2.0 # Gira para escapar del borde
        else:
            msg.linear.x = 2.0
            msg.angular.z = 0.0 # Avanza en línea recta
        self.publisher_.publish(msg)

    def draw_square(self):
        # Dibuja un cuadrado iterando 4 veces un trazo recto y un giro de 90 grados
        self.is_drawing = True
        self.get_logger().info('Dibujando Cuadrado...')
        for _ in range(4):
            if self.execute_movement(2.0, 0.0, 1.0): self.is_drawing = False; return 
            if self.execute_movement(0.0, math.pi / 2.0, 1.0): self.is_drawing = False; return
        self.stop_turtle(); self.is_drawing = False

    def draw_triangle(self):
        # Dibuja un triángulo iterando 3 veces un trazo recto y un giro de 120 grados
        self.is_drawing = True
        self.get_logger().info('Dibujando Triángulo...')
        for _ in range(3):
            if self.execute_movement(2.0, 0.0, 1.0): self.is_drawing = False; return
            if self.execute_movement(0.0, (2.0 * math.pi) / 3.0, 1.0): self.is_drawing = False; return
        self.stop_turtle(); self.is_drawing = False

# ================= FUNCIONES DE LAS LETRAS =================
    # Secuencias encadenadas utilizando execute_movement. Si la función devuelve True (abort), se interrumpe.
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
        # Invoca el servicio TeleportAbsolute para colocar a la tortuga en el centro (5.5, 5.5)
        if self.teleport_client.wait_for_service(timeout_sec=1.0):
            req = TeleportAbsolute.Request()
            req.x = 5.544445; req.y = 5.544445; req.theta = 0.0
            self.teleport_client.call_async(req)

    def toggle_pen(self):
        # Invoca el servicio SetPen para encender o apagar el rastro visual de la tortuga
        if self.pen_client.wait_for_service(timeout_sec=1.0):
            req = SetPen.Request()
            req.r = 255; req.g = 255; req.b = 255; req.width = 3
            self.pen_is_off = not self.pen_is_off
            req.off = int(self.pen_is_off)
            self.pen_client.call_async(req)

    def read_keyboard_loop(self):
        # Si está en medio de un dibujo, ignora las teclas generales
        if self.is_drawing: return 

        key = self.get_key()
        
        # Bloque de comandos manuales (Flechas)
        if key in key_bindings:
            self.auto_mode = False 
            vel = key_bindings[key]
            msg = Twist()
            msg.linear.x = vel[0]
            msg.angular.z = vel[1]
            self.publisher_.publish(msg)
        
        # Comandos de trayectorias
        elif key.lower() == 'a':
            self.auto_mode = True
            self.get_logger().info('Modo autónomo activado.')
        elif key.lower() == 's': self.auto_mode = False; self.draw_square()
        elif key.lower() == 't': self.auto_mode = False; self.draw_triangle()
        
        # TECLAS DE LAS INICIALES
        elif key.lower() == 'e': self.auto_mode = False; self.draw_E()
        elif key.lower() == 'z': self.auto_mode = False; self.draw_A()# Z se utiliza para representar la letra A.
        elif key.lower() == 'j': self.auto_mode = False; self.draw_J()
        elif key.lower() == 'l': self.auto_mode = False; self.draw_L()
        
        # Comandos de control   
        elif key.lower() == 'q': self.stop_turtle()
        elif key.lower() == 'r': self.reset_position()
        elif key.lower() == 'p': self.toggle_pen()
        elif key == '\x03': sys.exit(0)

        # Si el modo autónomo está activo, ejecuta la lógica de rebote
        if self.auto_mode:
            self.autonomous_bounce()

def main(args=None):
    # Función principal de inicialización y ejecución del nodo
    rclpy.init(args=args)
    node = TurtleController()
    try: rclpy.spin(node) # Mantiene el nodo activo escuchando eventos    except KeyboardInterrupt: pass
    finally:
        # Limpieza: restaura la terminal y destruye el nodo
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, node.settings)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()