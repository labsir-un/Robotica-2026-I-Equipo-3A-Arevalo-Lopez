#!/usr/bin/env python3

"""
Actividad 13
Enseñanza y repetición de poses

Funciones:
1. Mover el robot a una configuración
2. Guardar la configuración actual
3. Asignar nombre a la pose
4. Almacenar múltiples poses en YAML
5. Reproducir poses en orden
6. Modificar tiempo entre poses
7. Detener reproducción
"""

import math
import time
import yaml
import rclpy

from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import UInt32


class Teacher(Node):

    def __init__(self):

        super().__init__('teacher_mode')

        # Publicador de velocidad
        self.vel_pub = self.create_publisher(
            UInt32,
            '/pincher/profile_velocity',
            10
        )

        # Publicador de comandos articulares
        self.cmd_pub = self.create_publisher(
            JointState,
            '/pincher/command',
            10
        )

        # Lectura de posición real
        self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_callback,
            10
        )

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

        # Límites articulares del robot (q1 a q5)
        self.limites = {
            "waist": (-147, 147),     
            "shoulder": (-74, 72),    
            "elbow": (-118, 132),     
            "wrist": (-99, 97),       
            "gripper": (-87, 87)      
        }

        # Posición medida por el robot
        self.q_actual = [0.0] * 5

        # Tiempo entre poses
        self.transition_time = 2.0

        # Bandera para detener reproducción
        self.stop_requested = False

        # Archivo YAML
        self.yaml_file = "poses.yaml"


    ##################################################################
    # Callback de joint states
    ##################################################################

    def joint_callback(self, msg):

        self.q_actual = list(msg.position)

    ##################################################################
    # Configuración de velocidad
    ##################################################################

    def velocidad(self, vel):

        msg = UInt32()
        msg.data = vel

        self.vel_pub.publish(msg)

    ##################################################################
    # Enviar pose
    ##################################################################

    def mover_pose(self, pose_deg):

        pose_rad = [
            math.radians(x)
            for x in pose_deg
        ]

        msg = JointState()

        msg.name = self.joints
        msg.position = pose_rad

        self.cmd_pub.publish(msg)

    ##################################################################
    # Esperar llegada
    ##################################################################

    def esperar_llegada(self, pose_deg):

        pose_rad = [
            math.radians(x)
            for x in pose_deg
        ]

        tolerancia = math.radians(2)

        while rclpy.ok():

            rclpy.spin_once(self, timeout_sec=0.1)

            error_max = max(
                abs(qd - qm)
                for qd, qm in zip(
                    pose_rad,
                    self.q_actual
                )
            )

            if error_max < tolerancia:
                break

    ##################################################################
    # Guardar pose
    ##################################################################

    def guardar_pose(self, nombre):

        try:

            with open(
                self.yaml_file,
                'r'
            ) as file:

                datos = yaml.safe_load(file)

                if datos is None:
                    datos = {}

        except FileNotFoundError:

            datos = {}

        if "poses" not in datos:
            datos["poses"] = {}

        pose_grados = [
            round(math.degrees(x), 2)
            for x in self.q_actual
        ]

        datos["poses"][nombre] = pose_grados

        with open(
            self.yaml_file,
            'w'
        ) as file:

            yaml.dump(
                datos,
                file,
                sort_keys=False
            )

        print(f"\nPose '{nombre}' guardada.")

    ##################################################################
    # Cargar poses
    ##################################################################

    def cargar_poses(self):

        try:

            with open(
                self.yaml_file,
                'r'
            ) as file:

                datos = yaml.safe_load(file)

                if datos is None:
                    return {}

                return datos.get(
                    "poses",
                    {}
                )

        except FileNotFoundError:

            return {}

    ##################################################################
    # Reproducción
    ##################################################################

    def reproducir(self):

        poses = self.cargar_poses()

        if len(poses) == 0:

            print(
                "\nNo existen poses guardadas."
            )

            return

        self.stop_requested = False

        print(
            "\nReproduciendo secuencia..."
        )

        for nombre, pose in poses.items():

            if self.stop_requested:
                break

            print(
                f"Ejecutando: {nombre}"
            )

            self.mover_pose(pose)

            self.esperar_llegada(pose)

            inicio = time.time()

            while (
                time.time() - inicio
                < self.transition_time
            ):

                if self.stop_requested:
                    break

                time.sleep(0.1)

        print(
            "\nFin de reproducción."
        )

    ##################################################################
    # Detener reproducción
    ##################################################################

    def detener(self):

        self.stop_requested = True


######################################################################
# Programa principal
######################################################################

def main():

    rclpy.init()

    robot = Teacher()

    time.sleep(1)

    while True:

        print("\n========================")
        print(" MODO ENSEÑANZA ")
        print("========================")

        print("1. Mover robot")
        print("2. Guardar pose actual")
        print("3. Listar poses")
        print("4. Reproducir poses")
        print("5. Cambiar tiempo transición")
        print("6. Detener reproducción")
        print("0. Salir")

        opcion = input(
            "\nSeleccione opción: "
        )

        ##############################################################

        if opcion == "1":

            pose = []
            movimiento_valido = True

            for joint in robot.joints:

                valor = float(
                    input(
                        f"{joint} [deg]: "
                    )
                )

                # Validación de límites articulares
                lim_inf, lim_sup = robot.limites[joint]
                
                if not (lim_inf <= valor <= lim_sup):
                    print(f"\n[ERROR] Movimiento cancelado. El ángulo para '{joint}' ({valor}°) está fuera del rango permitido [{lim_inf}°, {lim_sup}°].")
                    movimiento_valido = False
                    break # Salimos del for, no seguimos preguntando

                pose.append(valor)

            # Solo movemos el robot si todas las articulaciones pasaron la validación
            if movimiento_valido:
                robot.mover_pose(pose)

        ##############################################################

        elif opcion == "2":

            rclpy.spin_once(
                robot,
                timeout_sec=0.1
            )

            nombre = input(
                "Nombre de la pose: "
            )

            robot.guardar_pose(nombre)

        ##############################################################

        elif opcion == "3":

            poses = robot.cargar_poses()

            print()

            for nombre in poses:

                print(nombre)

        ##############################################################

        elif opcion == "4":

            robot.velocidad(40)


            robot.reproducir()

        ##############################################################

        elif opcion == "5":

            robot.transition_time = float(
                input(
                    "Nuevo tiempo [s]: "
                )
            )

        ##############################################################

        elif opcion == "6":

            robot.detener()

        ##############################################################

        elif opcion == "0":

            break

    robot.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()