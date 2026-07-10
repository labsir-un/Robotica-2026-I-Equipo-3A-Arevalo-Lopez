#!/usr/bin/env python3

import time
import math
import rclpy
import matplotlib.pyplot as plt

from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import UInt32


class Interpolador(Node):

    def __init__(self):

        super().__init__('interpolador')

        ####################################################
        # Publicadores
        ####################################################

        self.vel_pub = self.create_publisher(
            UInt32,
            '/pincher/profile_velocity',
            10
        )

        self.pub = self.create_publisher(
            JointState,
            '/pincher/command',
            10
        )

        ####################################################
        # Suscriptor
        ####################################################

        self.create_subscription(
            JointState,
            '/joint_states',
            self.callback_joint,
            10
        )

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

        self.pub.publish(msg)

    ########################################################

    def trayectoria_lineal(
        self,
        q0,
        qf,
        T,
        dt
    ):

        tiempos = []
        trayectoria = []

        t = 0.0

        while t <= T:

            s = t / T

            q = []

            for qi, qfi in zip(q0, qf):

                q.append(
                    qi +
                    s * (qfi - qi)
                )

            trayectoria.append(q)

            tiempos.append(t)

            t += dt

        return tiempos, trayectoria

    ########################################################

    def trayectoria_cubica(
        self,
        q0,
        qf,
        T,
        dt
    ):

        tiempos = []
        trayectoria = []

        t = 0.0

        while t <= T:

            s = t / T

            h = (
                3 * s**2
                -
                2 * s**3
            )

            q = []

            for qi, qfi in zip(q0, qf):

                q.append(
                    qi +
                    h * (qfi - qi)
                )

            trayectoria.append(q)

            tiempos.append(t)

            t += dt

        return tiempos, trayectoria


############################################################
# Ejecutar trayectoria y registrar datos
############################################################

def ejecutar_y_registrar(
    robot,
    trayectoria,
    dt
):

    tiempos = []

    q_deseada = [[] for _ in range(5)]

    q_medida = [[] for _ in range(5)]

    inicio = time.time()

    for pose in trayectoria:

        robot.mover(pose)

        rclpy.spin_once(
            robot,
            timeout_sec=0.01
        )

        tiempo_actual = (
            time.time()
            -
            inicio
        )

        tiempos.append(
            tiempo_actual
        )

        ####################################################
        # Guardar deseadas y medidas
        ####################################################

        for i in range(5):

            q_deseada[i].append(
                math.degrees(
                    pose[i]
                )
            )

            q_medida[i].append(
                math.degrees(
                    robot.q_medida[i]
                )
            )

        time.sleep(dt)

    return (
        tiempos,
        q_deseada,
        q_medida
    )


############################################################
# Esperar llegada aproximada
############################################################

def esperar(segundos):

    inicio = time.time()

    while time.time() - inicio < segundos:

        time.sleep(0.05)


############################################################
# MAIN
############################################################

def main():

    rclpy.init()

    robot = Interpolador()

    time.sleep(2)

    ########################################################
    # Velocidad
    ########################################################

    robot.velocidad(150)

    ########################################################
    # HOME
    ########################################################

    home = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
    ]

    ########################################################
    # Pose final
    ########################################################

    qf_deg = [
        90,
        60,
        -90,
        -60,
        0
    ]

    qf = [
        math.radians(x)
        for x in qf_deg
    ]

    ########################################################
    # Ir a HOME al iniciar
    ########################################################

    print("\nMoviendo a HOME...")

    robot.mover(home)

    esperar(5)

    ########################################################
    # Trayectoria lineal
    ########################################################

    T = 5.0

    dt = 0.05

    t_lin, tray_lin = (
        robot.trayectoria_lineal(
            home,
            qf,
            T,
            dt
        )
    )

    print(
        "\nEjecutando interpolación lineal..."
    )

    (
        tiempo_lin,
        qd_lin,
        qm_lin
    ) = ejecutar_y_registrar(
        robot,
        tray_lin,
        dt
    )

    ########################################################
    # Volver HOME
    ########################################################

    print(
        "\nRegresando a HOME..."
    )

    robot.mover(home)

    esperar(5)

    ########################################################
    # Trayectoria cúbica
    ########################################################

    t_cub, tray_cub = (
        robot.trayectoria_cubica(
            home,
            qf,
            T,
            dt
        )
    )

    print(
        "\nEjecutando interpolación cúbica..."
    )

    (
        tiempo_cub,
        qd_cub,
        qm_cub
    ) = ejecutar_y_registrar(
        robot,
        tray_cub,
        dt
    )

    ########################################################
    # HOME FINAL
    ########################################################

    print(
        "\nVolviendo a HOME..."
    )

    robot.mover(home)

    esperar(5)

    ########################################################
    # Nombres
    ########################################################

    nombres = [
        "Waist",
        "Shoulder",
        "Elbow",
        "Wrist",
        "Gripper"
    ]

    ########################################################
    # GRAFICAS LINEALES
    ########################################################

    for i in range(5):

        plt.figure()

        plt.plot(
            tiempo_lin,
            qd_lin[i],
            label='Deseada'
        )

        plt.plot(
            tiempo_lin,
            qm_lin[i],
            label='Medida'
        )

        plt.title(
            f'Lineal - {nombres[i]}'
        )

        plt.xlabel(
            'Tiempo [s]'
        )

        plt.ylabel(
            'Posición [°]'
        )

        plt.grid(True)

        plt.legend()

    ########################################################
    # GRAFICAS CUBICAS
    ########################################################

    for i in range(5):

        plt.figure()

        plt.plot(
            tiempo_cub,
            qd_cub[i],
            label='Deseada'
        )

        plt.plot(
            tiempo_cub,
            qm_cub[i],
            label='Medida'
        )

        plt.title(
            f'Cúbica - {nombres[i]}'
        )

        plt.xlabel(
            'Tiempo [s]'
        )

        plt.ylabel(
            'Posición [°]'
        )

        plt.grid(True)

        plt.legend()

    ########################################################
    # ERRORES LINEALES
    ########################################################

    for i in range(5):

        error = []

        for d, m in zip(
            qd_lin[i],
            qm_lin[i]
        ):

            error.append(
                d - m
            )

        plt.figure()

        plt.plot(
            tiempo_lin,
            error
        )

        plt.title(
            f'Error Lineal - {nombres[i]}'
        )

        plt.xlabel(
            'Tiempo [s]'
        )

        plt.ylabel(
            'Error [°]'
        )

        plt.grid(True)

    ########################################################
    # ERRORES CUBICOS
    ########################################################

    for i in range(5):

        error = []

        for d, m in zip(
            qd_cub[i],
            qm_cub[i]
        ):

            error.append(
                d - m
            )

        plt.figure()

        plt.plot(
            tiempo_cub,
            error
        )

        plt.title(
            f'Error Cúbico - {nombres[i]}'
        )

        plt.xlabel(
            'Tiempo [s]'
        )

        plt.ylabel(
            'Error [°]'
        )

        plt.grid(True)

    ########################################################

    plt.show()

    rclpy.shutdown()


if __name__ == '__main__':
    main()