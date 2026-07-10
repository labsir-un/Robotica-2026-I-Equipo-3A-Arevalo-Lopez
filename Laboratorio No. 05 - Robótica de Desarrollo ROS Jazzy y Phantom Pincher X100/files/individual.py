#!/usr/bin/env python3

import time
import math
import rclpy

from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import UInt32


class ControlArticulacion(Node):

    def __init__(self):

        super().__init__('control_articulacion')

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

        self.joints = [
            'waist',
            'shoulder',
            'elbow',
            'wrist',
            'gripper'
        ]

        self.limites_grados = {
            'waist':    (-147, 147),
            'shoulder': (-74, 72),
            'elbow':    (-118, 132),
            'wrist':    (-99, 97),
            'gripper':  (-87, 87)
        }

        self.pose_actual = [0.0, 0.0, 0.0, 0.0, 0.0]


        #diferencia entre 0's (experimental)
        self.offset = {
            'waist': -0.005118,
            'shoulder': 0.017755,
            'elbow': 0.004693,
            'wrist': 0.015707,
            'gripper': 0.019449
        }

    def velocidad(self, vel):

        msg = UInt32()
        msg.data = vel

        self.vel_pub.publish(msg)

        self.get_logger().info(
            f'Velocidad configurada en {vel}'
        )

    def mover(self):

        msg = JointState()

        msg.name = self.joints
        msg.position = self.pose_actual

        self.pub.publish(msg)

        self.get_logger().info(
            f'Posición enviada: {self.pose_actual}'
        )


def main():

    rclpy.init()

    robot = ControlArticulacion()

    time.sleep(1)

    robot.velocidad(100)

    while True:

        print("\n===== CONTROL DE ARTICULACIONES =====")
        print("1. Waist")
        print("2. Shoulder")
        print("3. Elbow")
        print("4. Wrist")
        print("5. Gripper")
        print("0. Salir")

        opcion = input("Seleccione una articulación: ")

        if opcion == "0":
            break

        if opcion not in ["1", "2", "3", "4", "5"]:
            print("Opción inválida")
            continue

        indice = int(opcion) - 1
        nombre = robot.joints[indice]

        lim_inf, lim_sup = robot.limites_grados[nombre]

        print(
            f"\n{nombre}: rango permitido "
            f"[{lim_inf}°, {lim_sup}°]"
        )

        try:

            angulo_deg = float(
                input("Ingrese el ángulo en grados: ")
            )

        except ValueError:

            print("Debe ingresar un número")
            continue

        if angulo_deg < lim_inf or angulo_deg > lim_sup:

            print(
                f"ERROR: fuera de límites "
                f"[{lim_inf}°, {lim_sup}°]"
            )

            continue


        robot.pose_actual[indice] = robot.offset[nombre] + math.radians(
            angulo_deg
        )

        robot.mover()

        rclpy.spin_once(
            robot,
            timeout_sec=0.1
        )

    robot.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()