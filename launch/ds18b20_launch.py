# Copyright 2025 The ds18b20_temp Authors
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
"""Launch file for ds18b20_temp package."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for DS18B20 temperature sensor node."""
    pkg_dir = get_package_share_directory('ds18b20_temp')
    default_params = os.path.join(pkg_dir, 'config', 'ds18b20_params.yaml')

    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params,
            description='Full path to the parameter YAML file',
        ),

        Node(
            package='ds18b20_temp',
            executable='ds18b20_node.py',
            name='ds18b20_temp_node',
            output='screen',
            parameters=[LaunchConfiguration('params_file')],
            remappings=[
                ('ds18b20/temperature', 'ds18b20/temperature'),
            ],
        ),
    ])
