#!/usr/bin/env python3

import math
import time
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
# Longitudes del robot (mm)
############################################################

l1 = 43.0 + 84.0
l2 = 104.0
l3 = 104.0
l4 = 75.0

############################################################
# Límites articulares (grados)
############################################################

limites = {
    "q1": (-147, 147),
    "q2": (-74, 72),
    "q3": (-118, 132),
    "q4": (-99, 97)
}

############################################################
# Verifica si una configuración respeta los límites
############################################################

def configuracion_valida(q1, q2, q3, q4):

    articulaciones = {
        "q1": math.degrees(q1),
        "q2": math.degrees(q2),
        "q3": math.degrees(q3),
        "q4": math.degrees(q4)
    }

    errores = []

    for nombre, valor in articulaciones.items():

        lim_inf, lim_sup = limites[nombre]

        if valor < lim_inf or valor > lim_sup:

            errores.append(
                (nombre, valor, lim_inf, lim_sup)
            )

    return len(errores) == 0, errores

############################################################
# Cinemática inversa
############################################################
# Se agregó el parámetro "verbose" para silenciar los prints 
# y la selección manual durante la trayectoria del círculo.
def cinematica_inversa(Px, Py, Pz, theta_deg, verbose=True):

    ########################################################
    # Conversión a radianes
    ########################################################

    theta = math.radians(theta_deg)

    ########################################################
    # q1
    ########################################################

    q1 = math.atan2(Py, Px)

    ########################################################
    # Variables auxiliares
    ########################################################

    L = math.sqrt(Px**2 + Py**2)

    d = L - l4 * math.sin(theta)

    Pzp = -l4 * math.cos(theta) + Pz - l1

    ########################################################
    # cos(q3)
    ########################################################

    cos_q3 = (
        Pzp**2 +
        d**2 -
        l2**2 -
        l3**2
    ) / (2 * l2 * l3)

    ########################################################
    # Verificar alcanzabilidad
    ########################################################

    if abs(cos_q3) > 1:
        if verbose:
            print("\nEl punto solicitado está fuera del espacio de trabajo.")
        return None

    ########################################################
    # Dos soluciones para q3
    ########################################################

    sin_q3_up = math.sqrt(1 - cos_q3**2)
    sin_q3_down = -sin_q3_up

    q3_up = math.atan2(sin_q3_up, cos_q3)
    q3_down = math.atan2(sin_q3_down, cos_q3)

    ########################################################
    # Constantes auxiliares
    ########################################################

    k1_up = l2 + l3 * math.cos(q3_up)
    k2_up = l3 * math.sin(q3_up)

    k1_down = l2 + l3 * math.cos(q3_down)
    k2_down = l3 * math.sin(q3_down)

    ########################################################
    # q2
    ########################################################

    q2_up = math.atan2(d, Pzp) - math.atan2(k2_up, k1_up)
    q2_down = math.atan2(d, Pzp) - math.atan2(k2_down, k1_down)

    ########################################################
    # q4
    ########################################################

    q4_up = theta - q2_up - q3_up
    q4_down = theta - q2_down - q3_down

    ########################################################
    # Lista de configuraciones
    ########################################################

    configuraciones = [
        ("Codo arriba", [q1, q2_up, q3_up, q4_up]),
        ("Codo abajo", [q1, q2_down, q3_down, q4_down])
    ]

    ########################################################
    # Verificar límites
    ########################################################

    configuraciones_validas = []

    if verbose:
        print("\n====================================")

    for nombre, q in configuraciones:

        if verbose:
            print(f"\n{nombre}")
            print(f"q1 = {math.degrees(q[0]):8.2f}°")
            print(f"q2 = {math.degrees(q[1]):8.2f}°")
            print(f"q3 = {math.degrees(q[2]):8.2f}°")
            print(f"q4 = {math.degrees(q[3]):8.2f}°")

        valida, errores = configuracion_valida(
            q[0], q[1], q[2], q[3]
        )

        if valida:
            if verbose:
                print("Estado: CONFIGURACIÓN VÁLIDA")
            configuraciones_validas.append((nombre, q))
        else:
            if verbose:
                print("Estado: FUERA DE LÍMITES")
                for e in errores:
                    print(f"  {e[0]} = {e[1]:.2f}° (límite [{e[2]}°, {e[3]}°])")

    ########################################################
    # No existe ninguna solución válida
    ########################################################

    if len(configuraciones_validas) == 0:
        if verbose:
            print("\nNo existe ninguna configuración que respete los límites.")
        return None

    ########################################################
    # Elegir configuración (Automático o Manual)
    ########################################################

    # Si estamos en modo automático (verbose=False), simplemente
    # seleccionamos la primera configuración válida disponible.
    if not verbose:
        return configuraciones_validas[0][1]

    print("\n====================================")
    print("Configuraciones disponibles:")

    for i, (nombre, _) in enumerate(configuraciones_validas):
        print(f"{i+1}. {nombre}")

    while True:
        opcion = input("\nSeleccione una configuración (ENTER para cancelar): ")
        if opcion == "":
            return None
        try:
            opcion = int(opcion)
            if 1 <= opcion <= len(configuraciones_validas):
                break
        except ValueError:
            pass
        print("Opción inválida.")

    seleccion = configuraciones_validas[opcion-1]

    print("\nConfiguración seleccionada:")
    print(seleccion[0])
    print(f"q1 = {math.degrees(seleccion[1][0]):.2f}°")
    print(f"q2 = {math.degrees(seleccion[1][1]):.2f}°")
    print(f"q3 = {math.degrees(seleccion[1][2]):.2f}°")
    print(f"q4 = {math.degrees(seleccion[1][3]):.2f}°")

    return seleccion[1]

############################################################
# Programa principal
############################################################

def main():



    rclpy.init()
    robot = ControlRobot()
    time.sleep(1)

    robot.velocidad(20)

    posicion_home = [0.0, 0.0, 0.0, 0.0, 0.0]

    # 2. MOVIMIENTO INICIAL A HOME
    print("\n========== MOVIENDO A POSICIÓN HOME (INICIO) ==========\n")
    robot.mover(posicion_home)
    # Le damos 2.5 segundos para que llegue de manera segura desde donde esté
    time.sleep(2.5)


    print("\n========== TRAZANDO CÍRCULO EN EL PLANO XY ==========\n")

    # Parámetros del círculo (puedes ajustarlos)
    radio = 45.0           # mm
    centro_x = 104.0       # mm (Alejado hacia el frente para estar en un buen espacio de trabajo)
    centro_y = 0.0         # mm
    z_constante = 156    # Altura constante (mm)
    theta_constante = 180  # Orientación constante del TCP (grados)
    num_puntos = 100        # Cantidad de puntos (mientras más, más suave el círculo)

    # Bucle para generar y enviar la trayectoria
    for i in range(num_puntos + 1):
        
        # Calcular ángulo en radianes para el punto actual
        angulo_circulo = (i * 2 * math.pi) / num_puntos
        
        # Calcular coordenadas X e Y en el círculo
        Px = centro_x + radio * math.cos(angulo_circulo)
        Py = centro_y + radio * math.sin(angulo_circulo)

        # Calculamos la cinemática en modo silencioso (verbose=False)
        q = cinematica_inversa(
            Px,
            Py,
            z_constante,
            theta_constante,
            verbose=False
        )

    print("\n========== TRAZANDO CÍRCULO EN EL PLANO XY ==========\n")

    # Declaramos la bandera ANTES del bucle
    primer = 1 

    # Bucle para generar y enviar la trayectoria
    for i in range(num_puntos + 1):
        
        angulo_circulo = (i * 2 * math.pi) / num_puntos
        Px = centro_x + radio * math.cos(angulo_circulo)
        Py = centro_y + radio * math.sin(angulo_circulo)

        q = cinematica_inversa(Px, Py, z_constante, theta_constante, verbose=False)

        if q is not None:
            # Convertimos a grados
            q_deg = [math.degrees(angulo) for angulo in q]

            # Enviamos el comando de movimiento
            robot.mover([
                q_deg[0],
                q_deg[1],
                q_deg[2],
                q_deg[3],
                0.0  # Gripper
            ])
            
            print(f"Punto enviado -> X: {Px:.1f}, Y: {Py:.1f}")
            
            # Lógica de la pausa
            if primer == 1:
                time.sleep(10)  # Pausa larga solo para el primer punto
                primer = 0       # ¡CRUCIAL! Apagamos la bandera para los siguientes puntos
            else:
                time.sleep(0.15) # Pausa corta para el resto del círculo
            
        else:
            print(f"ALERTA: El punto (X: {Px:.1f}, Y: {Py:.1f}) no es alcanzable.")

    print("\n¡Trayectoria circular completada!")
    
    # Tiempo para asegurar que se publique el último mensaje antes de cerrar
    time.sleep(0.5)


    print("\n========== REGRESANDO A POSICIÓN HOME (FINAL) ==========\n")
    robot.mover(posicion_home)
    # Le damos tiempo suficiente para regresar por completo antes de apagar el nodo
    time.sleep(2.5)

    print("\n¡Robot en HOME de manera segura!")
    rclpy.shutdown()
    rclpy.shutdown()

############################################################

if __name__ == "__main__":

    main()