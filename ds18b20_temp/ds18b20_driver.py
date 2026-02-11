# Copyright 2025 The ds18b20_temp Authors
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
"""DS18B20 1-Wire Driver - Digital temperature sensor via Linux sysfs."""

import glob
import random

W1_DEVICES_PATH = '/sys/bus/w1/devices/'
DEVICE_PREFIX = '28-'


class FakeDS18B20Driver:
    """Fake driver generating random temperature without 1-Wire hardware."""

    def __init__(self, **kwargs):
        """Initialize fake driver (no hardware needed)."""

    def read_temperature(self):
        """Return temperature in degrees Celsius."""
        return 25.0 + random.gauss(0.0, 0.3)

    def close(self):
        """No-op close."""


class DS18B20Driver:
    """1-Wire driver for Dallas DS18B20 via Linux sysfs (w1-therm)."""

    def __init__(self, device_id: str = '', resolution: int = 12):
        """Initialize DS18B20 driver with given device ID and resolution."""
        if device_id:
            self.device_path = W1_DEVICES_PATH + device_id
        else:
            self.device_path = self._auto_detect()

        self.w1_slave_path = self.device_path + '/w1_slave'

        # Validate device exists
        try:
            with open(self.w1_slave_path, 'r'):
                pass
        except FileNotFoundError:
            raise OSError(
                f'DS18B20 not found at {self.w1_slave_path}')

        # Set resolution if supported
        self._set_resolution(resolution)

    @staticmethod
    def _auto_detect():
        """Find the first DS18B20 device on the 1-Wire bus."""
        devices = glob.glob(W1_DEVICES_PATH + DEVICE_PREFIX + '*')
        if not devices:
            raise OSError(
                'No DS18B20 device found on 1-Wire bus')
        return devices[0]

    def _set_resolution(self, bits: int):
        """Set measurement resolution (9, 10, 11, or 12 bits)."""
        if bits not in (9, 10, 11, 12):
            raise ValueError(f'Resolution must be 9-12, got {bits}')
        resolution_path = self.device_path + '/resolution'
        try:
            with open(resolution_path, 'w') as f:
                f.write(str(bits))
        except (PermissionError, FileNotFoundError):
            pass  # May not have write access; use kernel default

    def read_temperature(self):
        """Read temperature (C) from DS18B20 via w1_slave sysfs file."""
        with open(self.w1_slave_path, 'r') as f:
            lines = f.readlines()

        if len(lines) < 2:
            raise OSError('DS18B20 returned incomplete data')

        # Check CRC validity on line 1
        if not lines[0].strip().endswith('YES'):
            raise OSError('DS18B20 CRC check failed')

        # Extract temperature from line 2
        t_pos = lines[1].find('t=')
        if t_pos == -1:
            raise OSError('DS18B20 temperature field not found')

        temp_millic = int(lines[1][t_pos + 2:])

        # Reject power-on-reset value (85.0 C)
        if temp_millic == 85000:
            raise OSError('DS18B20 returned power-on-reset value (85 C)')

        return temp_millic / 1000.0

    def close(self):
        """Release resources (no-op for sysfs)."""
