from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(
                package="robot_bridge",
                executable="bridge_node",
                name="robot_bridge_node",
                output="screen",
            ),
        ]
    )
