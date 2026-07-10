#!/usr/bin/env python3

import time
import rclpy
import math
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import UInt32



class Bailarin(Node):

    def __init__(self):
        super().__init__('bailarin')

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

        self.offset = {
            'waist': -0.005118,
            'shoulder': 0.017755,
            'elbow': 0.004693,
            'wrist': 0.015707,
            'gripper': 0.019449
        }

        self.limites_grados = {
            'waist':    (-147, 147),
            'shoulder': (-74, 72),
            'elbow':    (-118, 132),
            'wrist':    (-99, 97),
            'gripper':  (-87, 87)
        }

        self.limites = {}

        for joint, (inf_deg, sup_deg) in self.limites_grados.items():
            self.limites[joint] = (
                math.radians(inf_deg),
                math.radians(sup_deg)
            )

    def velocidad(self, vel):

        msg = UInt32()
        msg.data = vel

        self.vel_pub.publish(msg)

        self.get_logger().info(f'Velocidad = {vel}')

    

    def mover(self, pose):

        for i, valor in enumerate(pose):

            nombre = self.joints[i]

            lim_inf, lim_sup = self.limites[nombre]

            if valor < lim_inf or valor > lim_sup:

                self.get_logger().error(
                    f'{nombre}: {math.degrees(valor):.1f}° '
                    f'fuera de límites '
                    f'[{math.degrees(lim_inf):.1f}°, '
                    f'{math.degrees(lim_sup):.1f}°]'
                )

                return

        msg = JointState()
        msg.name = self.joints
        msg.position = pose

        self.pub.publish(msg)

        self.get_logger().info(f'Moviendo a {pose}')


def main():

    rclpy.init()

    robot = Bailarin()

    time.sleep(1)


    home_d = [0, 0, 0, 0, 0]


    rutina1_d = [

        [30, -45, 90, 0, 0],
        [0, -45, 120, 0, 0],
        [-30, -45, 90, 0, 0],
        [0, -45, 120, 0, 0],

        [30, -45, 90, 0, 0],
        [0, -45, 120, 0, 0],
        [-30, -45, 90, 0, 0],
        [0, -45, 120, 0, 0],

        [30, -45, 90, 0, 0],
        [0, -45, 120, 0, 0],
        [-30, -45, 90, 0, 0],
        [0, -45, 120, 0, 0],

        [30, -45, 90, 0, 0],
        [0, -45, 120, 0, 0],
        [-30, -45, 90, 0, 0],
        [0, -45, 120, 0, 0]
    ]

    rutina2_d = [
        

        [30, 0, 0, 90, 80],
        [0, 0, 0, 0, 0],
        [-30, 0, 0, 90, 80],
        [0, 0, 0, 0, 0],

        [30, 0, 0, 90, 80],
        [0, 0, 0, 0, 0],
        [-30, 0, 0, 90, 80],
        [0, 0, 0, 0, 0],

        [30, 0, 0, 90, 80],
        [0, 0, 0, 0, 0],
        [-30, 0, 0, 90, 80],
        [0, 0, 0, 0, 0],

        [30, 0, 0, 90, 80],
        [0, 0, 0, 0, 0],
        [-30, 0, 0, 90, 80],
        [0, 0, 0, 0, 0]

    ]

    rutina3_d = [
        

        [90, 0, 0, 0, 0],
        
        [90, 60, 0, -60, 0],

        [-90, 60, 0, -60, 0],

        [-90, 0, 0, 0, 0],

        [90, 0, 0, 0, 0],
        
        [90, 60, 0, -60, 0],

        [-90, 60, 0, -60, 0],

        [-90, 0, 0, 0, 0]

    ]

    rutina4_d = [
        

        [0, 70, -90, -90, 0],
        
        [0, 70, -90, -90, 80],

        [0, -70, 90, 90, 80],

        [0, -70, 90, 90, 0],

        [0, 70, -90, -90, 0],
        
        [0, 70, -90, -90, 80],

        [0, -70, 90, 90, 80],

        [0, -70, 90, 90, 0],
        
    ]


    rutina1 = [
        [math.radians(x) for x in pose]
        for pose in rutina1_d
    ]

    rutina2 = [
        [math.radians(x) for x in pose]
        for pose in rutina2_d
    ]

    rutina3 = [
        [math.radians(x) for x in pose]
        for pose in rutina3_d
    ]

    rutina4 = [
        [math.radians(x) for x in pose]
        for pose in rutina4_d
    ]

    robot.velocidad(50)
    robot.mover(home_d)
    time.sleep(8)

    robot.velocidad(150)

    for pose in rutina2:

        robot.mover(pose)

        rclpy.spin_once(robot, timeout_sec=0.1)

        time.sleep(0.282)

        

    for pose in rutina2:

        robot.mover(pose)

        rclpy.spin_once(robot, timeout_sec=0.1)

        time.sleep(0.282)

        

    robot.velocidad(350)
    
    
    for pose in rutina3:

        robot.mover(pose)

        rclpy.spin_once(robot, timeout_sec=0.1)

        time.sleep(0.68)


    for pose in rutina3:

        robot.mover(pose)

        rclpy.spin_once(robot, timeout_sec=0.1)

        time.sleep(0.68)


    robot.velocidad(300)

    for pose in rutina4:

        robot.mover(pose)

        rclpy.spin_once(robot, timeout_sec=0.1)

        time.sleep(0.68)

    for pose in rutina4:

        robot.mover(pose)

        rclpy.spin_once(robot, timeout_sec=0.1)

        time.sleep(0.68)
        

    robot.velocidad(300)

    for pose in rutina1:

        robot.mover(pose)

        rclpy.spin_once(robot, timeout_sec=0.1)

        time.sleep(0.28)

        robot.velocidad(200)

    for pose in rutina1:

        robot.mover(pose)

        rclpy.spin_once(robot, timeout_sec=0.1)

        time.sleep(0.28)

        robot.velocidad(200)

        

    robot.velocidad(100)
    robot.mover(home_d)
    rclpy.spin_once(robot, timeout_sec=0.1)
    time.sleep(1)




    rclpy.shutdown()


if __name__ == '__main__':
    main()
