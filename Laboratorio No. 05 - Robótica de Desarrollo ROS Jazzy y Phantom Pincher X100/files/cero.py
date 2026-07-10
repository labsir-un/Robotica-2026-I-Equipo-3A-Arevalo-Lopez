#!/usr/bin/env python3

import math
import time
import numpy as np
import rclpy
import matplotlib.pyplot as plt

from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import UInt32

class ControlRobot(Node):

    def __init__(self):
        super().__init__('control_robot')

        # Publicador de velocidad
        self.vel_pub = self.create_publisher(
            UInt32,
            '/pincher/profile_velocity',
            10
        )

        # Publicador de comandos (posiciones deseadas)
        self.pub = self.create_publisher(
            JointState,
            '/pincher/command',
            10
        )

        # Suscriptor para leer las posiciones reales (medidas)
        self.sub = self.create_subscription(
            JointState,
            '/joint_states', 
            self.callback_medicion,
            10
        )

        # Nombres de las articulaciones
        self.joints = [
            'waist',
            'shoulder',
            'elbow',
            'wrist',
            'gripper'
        ]

        # Offset experimental actual del robot (rad)
        self.offset = {
            'waist': -0.005118,
            'shoulder': 0.017755,
            'elbow': 0.004693,
            'wrist': 0.015707,
            'gripper': 0.019449
        }

        # Diccionario para almacenar las posiciones medidas en tiempo real
        self.posicion_actual = {name: 0.0 for name in self.joints}

    ####################################################################
    # Callback para actualizar posiciones medidas
    ####################################################################
    def callback_medicion(self, msg):
        for i, name in enumerate(msg.name):
            if name in self.posicion_actual:
                self.posicion_actual[name] = msg.position[i]

    ####################################################################
    # Configurar velocidad
    ####################################################################
    def velocidad(self, vel):
        msg = UInt32()
        msg.data = vel
        self.vel_pub.publish(msg)

    ####################################################################
    # Enviar configuración al robot
    ####################################################################
    def mover(self, pose_deg):
        pose = [
            math.radians(pose_deg[0]) + self.offset['waist'],
            math.radians(pose_deg[1]) + self.offset['shoulder'],
            math.radians(pose_deg[2]) + self.offset['elbow'],
            math.radians(pose_deg[3]) + self.offset['wrist'],
            math.radians(pose_deg[4]) + self.offset['gripper']
        ]

        msg = JointState()
        msg.name = self.joints
        msg.position = pose
        self.pub.publish(msg)

############################################################
# Función de pausa no bloqueante para ROS 2
############################################################
def pausa_y_actualiza(nodo, segundos):
    """
    Realiza una pausa pero sigue actualizando los callbacks del nodo.
    """
    inicio = time.time()
    while time.time() - inicio < segundos:
        rclpy.spin_once(nodo, timeout_sec=0.1)

############################################################
# Límites articulares (grados)
############################################################
# NOTA: Ajusta los límites del 'gripper' según tu hardware real
limites = {
    "waist": (-147, 147),     # q1
    "shoulder": (-74, 72),    # q2
    "elbow": (-118, 132),     # q3
    "wrist": (-99, 97),       # q4
    "gripper": (-87, 87)      # q5
}

############################################################
# Programa principal: Rutina de Calibración
############################################################

def main():
    rclpy.init()
    robot = ControlRobot()
    
    pausa_y_actualiza(robot, 1.0)
    
    print("\n========== INICIANDO RUTINA DE CALIBRACIÓN ==========\n")
    print("Moviendo a posición HOME inicial...")
    robot.mover([0.0, 0.0, 0.0, 0.0, 0.0])
    pausa_y_actualiza(robot, 3.0)

    resultados_calibracion = {}
    nuevos_offsets_rad = {}

    # Ahora incluimos la 5ta articulación (gripper)
    articulaciones_calibrar = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']

    for idx, nombre_articulacion in enumerate(articulaciones_calibrar):
        print(f"\n--- Calibrando {nombre_articulacion.upper()} ---")
        
        lim_inf, lim_sup = limites[nombre_articulacion]
        
        # Generar 5 puntos distribuidos en un rango seguro (90% del límite)
        rango_seguro_inf = lim_inf * 0.9
        rango_seguro_sup = lim_sup * 0.9
        posiciones_deseadas = np.linspace(rango_seguro_inf, rango_seguro_sup, 5)
        
        deseados_grados = []
        medidos_grados = []
        errores_grados = []

        for angulo in posiciones_deseadas:
            # Crear pose donde todo es 0 excepto la articulación actual
            pose = [0.0, 0.0, 0.0, 0.0, 0.0]
            pose[idx] = angulo
            
            robot.mover(pose)
            
            # PAUSA de 3 segundos para vencer la inercia
            pausa_y_actualiza(robot, 3.0)
            
            q_deseado_deg = angulo
            
            q_medido_rad = robot.posicion_actual.get(nombre_articulacion, 0.0)
            q_medido_deg = math.degrees(q_medido_rad)
            
            eq_deg = q_deseado_deg - q_medido_deg
            
            print(f"Punto: Deseado = {q_deseado_deg:7.2f}° | Medido = {q_medido_deg:7.2f}° | Error = {eq_deg:7.2f}°")
            
            deseados_grados.append(q_deseado_deg)
            medidos_grados.append(q_medido_deg)
            errores_grados.append(eq_deg)

        print(f"Regresando a HOME tras calibrar {nombre_articulacion}...")
        robot.mover([0.0, 0.0, 0.0, 0.0, 0.0])
        pausa_y_actualiza(robot, 3.0)

        resultados_calibracion[nombre_articulacion] = {
            'deseado': deseados_grados,
            'medido': medidos_grados,
            'errores': errores_grados
        }

    # =======================================================
    # PROCESAMIENTO DE DATOS Y DETERMINACIÓN DE CORRECCIÓN
    # =======================================================
    print("\n========== RESULTADOS DE CALIBRACIÓN Y CORRECCIÓN ==========\n")

    for nombre, datos in resultados_calibracion.items():
        errores = np.array(datos['errores'])
        
        error_max = np.max(np.abs(errores))
        error_promedio = np.mean(errores)
        
        idx_cero = np.argmin(np.abs(np.array(datos['deseado'])))
        desplazamiento_cero = errores[idx_cero]
        
        offset_viejo_rad = robot.offset[nombre]
        offset_sugerido_rad = offset_viejo_rad - math.radians(error_promedio)
        
        nuevos_offsets_rad[nombre] = round(offset_sugerido_rad, 6)

        print(f"[{nombre.upper()}]")
        print(f"  Error Máximo:        {error_max:.3f}°")
        print(f"  Error Promedio:      {error_promedio:.3f}°")
        print(f"  Desplazamiento Cero: {desplazamiento_cero:.3f}°")

    print("\n========== IMPLEMENTACIÓN DE CERO SUGERIDA ==========")
    print("Reemplaza tu bloque 'self.offset' en el código base por el siguiente:\n")
    print("self.offset = {")
    print(f"    'waist': {nuevos_offsets_rad.get('waist', 0.0)},")
    print(f"    'shoulder': {nuevos_offsets_rad.get('shoulder', 0.0)},")
    print(f"    'elbow': {nuevos_offsets_rad.get('elbow', 0.0)},")
    print(f"    'wrist': {nuevos_offsets_rad.get('wrist', 0.0)},")
    print(f"    'gripper': {nuevos_offsets_rad.get('gripper', 0.0)}")
    print("}")

    # =======================================================
    # GRÁFICOS SOLICITADOS (Ahora para 5 articulaciones)
    # =======================================================
    # Creamos una grilla de 2 filas x 3 columnas
    fig, axs = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Calibración de cero y error articular - Deseado vs Medido', fontsize=16)

    axs_flat = axs.flatten()
    for idx, nombre in enumerate(articulaciones_calibrar):
        ax = axs_flat[idx]
        deseados = resultados_calibracion[nombre]['deseado']
        medidos = resultados_calibracion[nombre]['medido']
        
        ax.plot(deseados, deseados, 'k--', label='Ideal Perfecta')
        ax.plot(deseados, medidos, 'o-', color='blue', label='Reportada por Servomotor')
        
        ax.set_title(f'Articulación: {nombre.capitalize()}')
        ax.set_xlabel('Posición Deseada $q_{deseado}$ [Grados]')
        ax.set_ylabel('Posición Medida $q_{medido}$ [Grados]')
        ax.legend()
        ax.grid(True)

    # Ocultar el sexto subplot vacío (ya que solo tenemos 5 articulaciones)
    axs_flat[5].set_visible(False)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    print("\nMostrando gráficas... Cierra la ventana de la gráfica para apagar el programa.")
    plt.show()

    robot.get_logger().info("Rutina finalizada.")
    rclpy.shutdown()

############################################################
if __name__ == "__main__":
    main()