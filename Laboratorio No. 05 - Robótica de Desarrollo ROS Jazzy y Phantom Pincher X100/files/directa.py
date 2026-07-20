#!/usr/bin/env python3

import time
import math
import numpy as np
import rclpy

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

        # Publicador de posiciones
        self.pub = self.create_publisher(
            JointState,
            '/pincher/command',
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

        # Offset experimental del robot (rad)
        self.offset = {
            'waist': -0.005118,
            'shoulder': 0.017755,
            'elbow': 0.004693,
            'wrist': 0.015707,
            'gripper': 0.019449
        }

        # Límites de las articulaciones en grados (min, max)
        # IMPORTANTE: Ajusta estos valores según los límites físicos reales de tu robot.
        self.limits = {
            'waist':    (-147, 147),
            'shoulder': (-74, 72),
            'elbow':    (-118, 132),
            'wrist':    (-99, 97),
            'gripper':  (-87, 87)
        }

    ####################################################################
    # Matriz homogénea Denavit-Hartenberg
    ####################################################################
    def DH(self, theta, d, a, alpha):
        ct = math.cos(theta)
        st = math.sin(theta)
        ca = math.cos(alpha)
        sa = math.sin(alpha)

        return np.array([
            [ct, -st * ca,  st * sa, a * ct],
            [st,  ct * ca, -ct * sa, a * st],
            [0,       sa,       ca,      d],
            [0,        0,        0,      1]
        ])

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
        # 1. Validar que la configuración esté dentro de los límites
        for i, joint in enumerate(self.joints):
            lim_min, lim_max = self.limits[joint]
            angulo = pose_deg[i]
            
            if not (lim_min <= angulo <= lim_max):
                self.get_logger().error(
                    f'MOVIMIENTO ABORTADO: La articulación "{joint}" ({angulo}°) '
                    f'excede los límites permitidos [{lim_min}°, {lim_max}°].'
                )
                return False # Detiene la ejecución de la función y no publica

        # 2. Si pasa la validación, procesa y envía las posiciones
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
        self.get_logger().info(f'Configuración válida y enviada: {pose_deg}')
        return True


def main():

    rclpy.init()
    robot = ControlRobot()
    time.sleep(1)

    ####################################################################
    # Longitudes de los eslabones (mm)
    ####################################################################
    l1 = 43+84
    l2 = 104
    l3 = 104
    l4 = 75

    ####################################################################
    # Configuración del robot (grados)
    ####################################################################
    q = [
        0,      # q1
        0,      # q2
        90,     # q3
        90,     # q4
        0       # q5 (no participa)
    ]

    ####################################################################
    # Enviar configuración al robot
    ####################################################################
    robot.velocidad(50)
    
    # Intentar mover el robot (retorna True si cumple límites, False si los viola)
    movimiento_exitoso = robot.mover(q)
    
    rclpy.spin_once(robot, timeout_sec=0.1)

    # Solo calcular y mostrar la cinemática directa si la pose era válida
    if movimiento_exitoso:
        ####################################################################
        # Convertir los cuatro ángulos a radianes
        ####################################################################
        q1 = math.radians(q[0])
        q2 = math.radians(q[1])
        q3 = math.radians(q[2])
        q4 = math.radians(q[3])

        ####################################################################
        # Construcción de matrices DH
        ####################################################################
        A1 = robot.DH(q1, l1, 0, math.radians(-90))
        A2 = robot.DH(q2 - math.pi / 2, 0, l2, 0)
        A3 = robot.DH(q3, 0, l3, 0)
        A4 = robot.DH(q4 + math.pi / 2, 0, 0, math.radians(90))
        A5 = robot.DH(0, l4, 0, 0)

        ####################################################################
        # Cinemática directa
        ####################################################################
        T05 = A1 @ A2 @ A3 @ A4 @ A5

        ####################################################################
        # Posición del TCP
        ####################################################################
        x = T05[0, 3]
        y = T05[1, 3]
        z = T05[2, 3]

        ####################################################################
        # Matriz de rotación
        ####################################################################
        R = T05[0:3, 0:3]

        ####################################################################
        # Conversión a Roll-Pitch-Yaw (ZYX)
        ####################################################################
        pitch = math.atan2(-R[2, 0], math.sqrt(R[0, 0]**2 + R[1, 0]**2))
        roll = math.atan2(R[2, 1], R[2, 2])
        yaw = math.atan2(R[1, 0], R[0, 0])

        roll = math.degrees(roll)
        pitch = math.degrees(pitch)
        yaw = math.degrees(yaw)

        ####################################################################
        # Mostrar resultados
        ####################################################################
        print("\n========== MATRIZ T05 ==========\n")
        print(T05)
        print("\n========== POSICIÓN ==========\n")
        print(f"x = {x:.2f} mm")
        print(f"y = {y:.2f} mm")
        print(f"z = {z:.2f} mm")
        print("\n========== ORIENTACIÓN ==========\n")
        print(f"Roll  = {roll:.2f}°")
        print(f"Pitch = {pitch:.2f}°")
        print(f"Yaw   = {yaw:.2f}°")

    time.sleep(2)
    robot.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()  
