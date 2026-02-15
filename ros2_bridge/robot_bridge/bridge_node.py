"""
ROS2 Bridge Node: /odom 토픽 구독 → FastAPI 서버로 HTTP POST 전송

TODO (내일 같이 작업할 부분):
  - [ ] 실제 Gazebo 시뮬레이션에서 테스트
  - [ ] 에러 핸들링 강화 (서버 다운 시 재시도 로직)
  - [ ] orientation(theta) 데이터 추가
  - [ ] 배터리/속도 등 추가 센서 데이터 전송
"""

import time

import requests
import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node

from robot_bridge.config import MIN_PUBLISH_INTERVAL, POSITION_ENDPOINT, ROBOT_ID


class BridgeNode(Node):
    def __init__(self):
        super().__init__("robot_bridge_node")
        self.get_logger().info(f"Bridge Node 시작 - 서버: {POSITION_ENDPOINT}")

        # /odom 토픽 구독
        self.odom_sub = self.create_subscription(
            Odometry, "/odom", self.odom_callback, 10
        )

        self.last_send_time = 0.0

    def odom_callback(self, msg: Odometry):
        """오도메트리 데이터 수신 → 서버로 전송"""
        now = time.time()

        # 전송 주기 제한
        if now - self.last_send_time < MIN_PUBLISH_INTERVAL:
            return

        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        payload = {
            "robot_id": ROBOT_ID,
            "x": x,
            "y": y,
            "status": "active",
        }

        try:
            resp = requests.post(POSITION_ENDPOINT, json=payload, timeout=2)
            resp.raise_for_status()
            self.last_send_time = now
            self.get_logger().debug(f"전송 완료: x={x:.2f}, y={y:.2f}")
        except requests.RequestException as e:
            self.get_logger().warn(f"전송 실패: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = BridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
