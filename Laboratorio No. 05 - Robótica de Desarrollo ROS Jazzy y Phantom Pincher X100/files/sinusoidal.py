import math
import time
import numpy as np
import matplotlib.pyplot as plt

import rclpy

from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import UInt32


class Senoidal(Node):

    def __init__(self):

        super().__init__('senoidal')

        ####################################################
        # Publicador de velocidad
        ####################################################

        self.vel_pub = self.create_publisher(
            UInt32,
            '/pincher/profile_velocity',
            10
        )

        ####################################################
        # Publicador de comandos
        ####################################################

        self.cmd_pub = self.create_publisher(
            JointState,
            '/pincher/command',
            10
        )

        ####################################################
        # Suscriptor de posición real
        ####################################################

        self.create_subscription(
            JointState,
            '/joint_states',
            self.callback_joint,
            10
        )

        ####################################################
        # Articulaciones
        ####################################################

        self.joints = [
            'waist',
            'shoulder',
            'elbow',
            'wrist',
            'gripper'
        ]

        self.offset = {
            'waist': -0.005118,
            'shoulder': 0.017755,
            'elbow': 0.004693,
            'wrist': 0.015707,
            'gripper': 0.019449
        }

        ####################################################
        # Límites articulares del robot (grados)
        ####################################################

        self.limites = {
            "waist": (-147, 147),     
            "shoulder": (-74, 72),    
            "elbow": (-118, 132),     
            "wrist": (-99, 97),       
            "gripper": (-87, 87)      
        }

        ####################################################
        # Posición medida
        ####################################################

        self.q_medida = [0.0] * 5

    ########################################################

    def callback_joint(self, msg):

        self.q_medida = list(msg.position)

    ########################################################

    def velocidad(self, vel):

        msg = UInt32()

        msg.data = vel

        self.vel_pub.publish(msg)

    ########################################################

    def mover(self, pose):

        msg = JointState()

        msg.name = self.joints
        msg.position = pose

        self.cmd_pub.publish(msg)


############################################################

def ejecutar_prueba(
        robot,
        amplitud_deg,
        frecuencia,
        duracion,
        indice_articulacion):

    ########################################################
    # Validación de límites articulares
    ########################################################

    nombre_articulacion = robot.joints[indice_articulacion]
    lim_inf, lim_sup = robot.limites[nombre_articulacion]

    # En una onda senoidal pura alrededor de 0, los picos son +Amplitud y -Amplitud
    if (amplitud_deg > lim_sup) or (-amplitud_deg < lim_inf):
        print(f"\n[ERROR ABORTADO] La prueba con A = {amplitud_deg}° excede los límites de la articulación '{nombre_articulacion}' [{lim_inf}°, {lim_sup}°].")
        return

    ########################################################
    # Conversión a radianes
    ########################################################

    A = math.radians(amplitud_deg)

    q0 = 0.0

    ########################################################
    # Vectores para guardar datos
    ########################################################

    tiempo_vec = []

    q_deseada = []

    q_medida = []

    ########################################################

    inicio = time.time()

    while True:

        t = time.time() - inicio

        if t > duracion:
            break

        ####################################################
        # Ecuación senoidal
        ####################################################

        q = q0 + A * math.sin(
            2 * math.pi * frecuencia * t
        )

        ####################################################
        # Construir pose completa
        ####################################################

        pose = [0.0] * 5

        pose[indice_articulacion] = q

        ####################################################
        # Enviar comando
        ####################################################

        robot.mover(pose)

        ####################################################
        # Actualizar ROS
        ####################################################

        rclpy.spin_once(
            robot,
            timeout_sec=0.001
        )

        ####################################################
        # Guardar datos
        ####################################################

        tiempo_vec.append(t)

        q_deseada.append(
            math.degrees(q)
        )

        q_medida.append(
            math.degrees(
                robot.q_medida[
                    indice_articulacion
                ]
            )
        )

        ####################################################
        # Frecuencia de muestreo
        ####################################################

        time.sleep(0.02)

    ########################################################
    # Cálculo de errores
    ########################################################

    error = np.array(
        q_deseada
    ) - np.array(
        q_medida
    )

    error_max = np.max(
        np.abs(error)
    )

    rmse = np.sqrt(
        np.mean(error**2)
    )

    ########################################################
    # Resultados
    ########################################################

    print("\n====================")
    print(
        f"A = {amplitud_deg}°"
    )
    print(
        f"f = {frecuencia} Hz"
    )
    print(
        f"Error máximo = "
        f"{error_max:.3f}°"
    )
    print(
        f"RMSE = "
        f"{rmse:.3f}°"
    )

    ########################################################
    # Gráfica
    ########################################################

    plt.figure()

    plt.plot(
        tiempo_vec,
        q_deseada,
        label='Deseada'
    )

    plt.plot(
        tiempo_vec,
        q_medida,
        label='Medida'
    )

    plt.xlabel(
        'Tiempo [s]'
    )

    plt.ylabel(
        'Posición [°]'
    )

    plt.title(
        f'A={amplitud_deg}° '
        f'f={frecuencia}Hz'
    )

    plt.grid(True)

    plt.legend()

    plt.show()


############################################################

def main():

    rclpy.init()

    robot = Senoidal()

    time.sleep(1)

    ########################################################
    # Velocidad
    ########################################################

    robot.velocidad(200)

    ########################################################
    # Seleccionar articulación
    ########################################################

    indice_articulacion = 2

    ########################################################
    # Duración de cada prueba
    ########################################################

    duracion = 10

    ########################################################
    # PRUEBA 1
    ########################################################

    ejecutar_prueba(
        robot,
        amplitud_deg=40,
        frecuencia=0.1,
        duracion=duracion,
        indice_articulacion=indice_articulacion
    )

    ########################################################
    # PRUEBA 2
    ########################################################

    ejecutar_prueba(
        robot,
        amplitud_deg=40,
        frecuencia=0.3,
        duracion=duracion,
        indice_articulacion=indice_articulacion
    )

    ########################################################
    # PRUEBA 3
    ########################################################

    ejecutar_prueba(
        robot,
        amplitud_deg=70,
        frecuencia=0.1,
        duracion=duracion,
        indice_articulacion=indice_articulacion
    )

    ########################################################
    # PRUEBA 4
    ########################################################

    ejecutar_prueba(
        robot,
        amplitud_deg=70,
        frecuencia=0.3,
        duracion=duracion,
        indice_articulacion=indice_articulacion
    )

    ########################################################

    robot.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()