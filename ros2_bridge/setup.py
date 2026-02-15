from setuptools import find_packages, setup

package_name = "robot_bridge"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/bridge_launch.py"]),
    ],
    install_requires=["setuptools", "requests"],
    zip_safe=True,
    entry_points={
        "console_scripts": [
            "bridge_node = robot_bridge.bridge_node:main",
        ],
    },
)
