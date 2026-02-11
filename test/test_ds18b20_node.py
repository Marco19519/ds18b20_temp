# Copyright 2025 The ds18b20_temp Authors
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
"""Launch test for DS18B20 temperature sensor node."""

import unittest

import launch
import launch_ros.actions
import launch_testing
import launch_testing.actions
import launch_testing.markers
from launch_testing_ros import WaitForTopics
import pytest
from rcl_interfaces.srv import SetParameters
import rclpy
from rclpy.parameter import Parameter
from sensor_msgs.msg import Temperature
from std_srvs.srv import Trigger


@pytest.mark.launch_test
@launch_testing.markers.keep_alive
def generate_test_description():
    """Launch DS18B20 node in fake_mode for testing."""
    ds18b20_node = launch_ros.actions.Node(
        package='ds18b20_temp',
        executable='ds18b20_node.py',
        name='ds18b20_temp_node',
        parameters=[{
            'fake_mode': True,
            'publish_rate': 50.0,
        }],
    )

    return launch.LaunchDescription([
        ds18b20_node,
        launch_testing.actions.ReadyToTest(),
    ]), {'ds18b20_node': ds18b20_node}


class TestDS18B20Topics(unittest.TestCase):
    """Verify that the temperature topic publishes valid sensor data."""

    def test_topic_published(self):
        """Temperature topic should receive at least one message."""
        topic_list = [('ds18b20/temperature', Temperature)]
        with WaitForTopics(topic_list, timeout=10.0) as wait:
            received = wait.topics_received()
            self.assertEqual(received, {'ds18b20/temperature'})

    def test_temperature_range(self):
        """Temperature should be near 25 C (fake_mode default)."""
        topic_list = [('ds18b20/temperature', Temperature)]
        with WaitForTopics(
            topic_list, timeout=10.0, messages_received_buffer_length=5
        ) as wait:
            msgs = wait.received_messages('ds18b20/temperature')
            self.assertGreater(len(msgs), 0)
            for msg in msgs:
                self.assertGreater(msg.temperature, 15.0)
                self.assertLess(msg.temperature, 35.0)
                self.assertEqual(msg.header.frame_id, 'ds18b20_link')


class TestDS18B20Services(unittest.TestCase):
    """Verify calibrate and reset services."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = rclpy.create_node('test_ds18b20_services')

    def tearDown(self):
        self.node.destroy_node()

    def test_calibrate_service(self):
        """Calibrate should return success=True with 'fake' in message."""
        client = self.node.create_client(Trigger, 'ds18b20/calibrate')
        self.assertTrue(
            client.wait_for_service(timeout_sec=10.0),
            'calibrate service not available',
        )

        future = client.call_async(Trigger.Request())
        rclpy.spin_until_future_complete(self.node, future, timeout_sec=10.0)
        self.assertTrue(future.done(), 'calibrate call timed out')

        result = future.result()
        self.assertTrue(result.success)
        self.assertIn('fake', result.message.lower())
        self.node.destroy_client(client)

    def test_reset_service(self):
        """Reset should return success=True with 'reset complete' message."""
        client = self.node.create_client(Trigger, 'ds18b20/reset')
        self.assertTrue(
            client.wait_for_service(timeout_sec=10.0),
            'reset service not available',
        )

        future = client.call_async(Trigger.Request())
        rclpy.spin_until_future_complete(self.node, future, timeout_sec=10.0)
        self.assertTrue(future.done(), 'reset call timed out')

        result = future.result()
        self.assertTrue(result.success)
        self.assertIn('reset complete', result.message.lower())
        self.node.destroy_client(client)


class TestDS18B20Parameters(unittest.TestCase):
    """Verify runtime parameter changes."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = rclpy.create_node('test_ds18b20_params')

    def tearDown(self):
        self.node.destroy_node()

    def test_change_publish_rate(self):
        """Publish_rate should be changeable at runtime."""
        client = self.node.create_client(
            SetParameters, 'ds18b20_temp_node/set_parameters')
        self.assertTrue(
            client.wait_for_service(timeout_sec=10.0),
            'set_parameters service not available',
        )

        request = SetParameters.Request()
        request.parameters = [
            Parameter('publish_rate', value=5.0).to_parameter_msg(),
        ]
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self.node, future, timeout_sec=10.0)
        self.assertTrue(future.done(), 'set_parameters call timed out')

        result = future.result()
        self.assertTrue(result.results[0].successful)
        self.node.destroy_client(client)


@launch_testing.post_shutdown_test()
class TestShutdown(unittest.TestCase):
    """Verify clean shutdown."""

    def test_exit_code(self, proc_info):
        """Node should exit cleanly."""
        launch_testing.asserts.assertExitCodes(
            proc_info, allowable_exit_codes=[0, -2, -15])
