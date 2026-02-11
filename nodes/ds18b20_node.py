#!/usr/bin/env python3
# Copyright 2025 The ds18b20_temp Authors
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
"""ROS2 node that reads DS18B20 over 1-Wire and publishes temperature."""

import time

from ds18b20_temp.ds18b20_driver import DS18B20Driver, FakeDS18B20Driver
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Temperature
from std_srvs.srv import Trigger


class DS18B20TempNode(Node):
    """ROS2 node for DS18B20 digital temperature sensor."""

    def __init__(self):
        """Initialize the DS18B20 temperature sensor node."""
        super().__init__('ds18b20_temp_node')

        # ── Declare parameters ────────────────────────────────────
        self.declare_parameter('fake_mode', True)
        self.declare_parameter('device_id', '')
        self.declare_parameter('resolution', 12)
        self.declare_parameter('publish_rate', 1.0)
        self.declare_parameter('frame_id', 'ds18b20_link')
        self.declare_parameter('temperature_variance', 0.0)

        # ── Read parameters ───────────────────────────────────────
        self.fake_mode = self.get_parameter('fake_mode').value
        self.device_id = self.get_parameter('device_id').value
        self.resolution = self.get_parameter('resolution').value
        rate = self.get_parameter('publish_rate').value
        self.frame_id = self.get_parameter('frame_id').value
        self.temp_var = self.get_parameter('temperature_variance').value

        # ── Bias (set by calibration) ──────────────────────────────
        self.temp_bias = 0.0

        # ── Initialise driver ─────────────────────────────────────
        self._init_driver()

        # ── Publisher + timer ─────────────────────────────────────
        self.pub_temp = self.create_publisher(
            Temperature, 'ds18b20/temperature', 10)
        self.timer = self.create_timer(1.0 / rate, self._timer_cb)
        self.get_logger().info(
            f'Publishing on "ds18b20/temperature" @ {rate} Hz')

        # ── Services ──────────────────────────────────────────────
        self.create_service(Trigger, 'ds18b20/calibrate', self._calibrate_cb)
        self.create_service(Trigger, 'ds18b20/reset', self._reset_cb)
        self.get_logger().info(
            'Services: "ds18b20/calibrate", "ds18b20/reset"')

        # ── Parameter change callback ─────────────────────────────
        self.add_on_set_parameters_callback(self._on_param_change)

    def _init_driver(self):
        """Initialize the DS18B20 driver in fake or real mode."""
        if self.fake_mode:
            self.driver = FakeDS18B20Driver()
            self.get_logger().info(
                'FAKE MODE enabled — generating random temperature data')
        else:
            try:
                self.driver = DS18B20Driver(
                    self.device_id, self.resolution)
                self.get_logger().info(
                    f'DS18B20 initialised  device={self.driver.device_path}  '
                    f'resolution={self.resolution}-bit')
            except Exception as e:
                self.get_logger().fatal(f'Failed to open DS18B20: {e}')
                raise

    def _timer_cb(self):
        """Read sensor data and publish temperature."""
        try:
            temperature = self.driver.read_temperature()
        except OSError as e:
            self.get_logger().warn(
                f'DS18B20 read error: {e}', throttle_duration_sec=5.0)
            return

        temperature -= self.temp_bias

        stamp = self.get_clock().now().to_msg()

        temp_msg = Temperature()
        temp_msg.header.stamp = stamp
        temp_msg.header.frame_id = self.frame_id
        temp_msg.temperature = temperature
        temp_msg.variance = self.temp_var
        self.pub_temp.publish(temp_msg)

    def _calibrate_cb(self, request, response):
        """Handle calibrate service: collect samples to compute bias."""
        if self.fake_mode:
            response.success = True
            response.message = 'Calibration complete (fake)'
            self.get_logger().info(
                'Calibration requested in fake mode — skipped')
            return response

        self.get_logger().info(
            'Calibrating — collecting data for 5 seconds...')
        temp_samples = []
        end_time = time.monotonic() + 5.0
        while time.monotonic() < end_time:
            try:
                t = self.driver.read_temperature()
                temp_samples.append(t)
            except OSError:
                pass
            time.sleep(1.0)

        if not temp_samples:
            response.success = False
            response.message = 'Calibration failed — no samples collected'
            return response

        n = len(temp_samples)
        self.temp_bias = 0.0

        response.success = True
        response.message = (
            f'Calibration complete — {n} samples, '
            f'avg_temp={sum(temp_samples) / n:.2f} C')
        self.get_logger().info(response.message)
        return response

    def _reset_cb(self, request, response):
        """Handle reset service: clear bias and reinitialize sensor."""
        self.temp_bias = 0.0
        self.driver.close()
        self._init_driver()

        response.success = True
        response.message = 'Sensor reset complete'
        self.get_logger().info(response.message)
        return response

    def _on_param_change(self, params):
        """Handle runtime parameter changes such as publish_rate."""
        for param in params:
            if param.name == 'publish_rate':
                new_rate = param.value
                if new_rate <= 0.0:
                    return SetParametersResult(
                        successful=False,
                        reason='publish_rate must be > 0')
                self.timer.cancel()
                self.timer = self.create_timer(
                    1.0 / new_rate, self._timer_cb)
                self.get_logger().info(
                    f'publish_rate changed to {new_rate} Hz')
        return SetParametersResult(successful=True)


def main(args=None):
    """Entry point for the DS18B20 temperature sensor node."""
    rclpy.init(args=args)
    node = DS18B20TempNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.driver.close()
        node.destroy_node()
        try:
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()
