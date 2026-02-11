# DS18B20 Temperature Sensor — ROS2 Jazzy Driver (1-Wire)

ROS2 Jazzy driver for the **Dallas DS18B20** digital temperature sensor over the Linux 1-Wire (w1) sysfs interface.

## Features

- Publishes `sensor_msgs/Temperature` on `ds18b20/temperature`
- `fake_mode` for testing without hardware (random Gaussian data)
- Auto-detects first DS18B20 device on the 1-Wire bus
- Configurable resolution (9-12 bit)
- CRC validation via kernel w1-therm driver
- Rejects 85°C power-on-reset artifact
- Runtime `publish_rate` change via `ros2 param set`
- Calibration and reset services

## Why this package?

There are several temperature sensors with ROS2 drivers. The DS18B20 is unique for its waterproof probe variants and 1-Wire multi-sensor bus:

| Feature | SHT31 (sht31_env) | DHT22 (dht22_env) | DS18B20 (this package) |
|---|---|---|---|
| **Interface** | I2C | Proprietary GPIO | 1-Wire (kernel sysfs) |
| **Measures** | Temp + Humidity | Temp + Humidity | Temperature only |
| **Temperature range** | -40 ~ 125 °C | -40 ~ 80 °C | -55 ~ 125 °C |
| **Temperature accuracy** | ±0.2 °C | ±0.5 °C | ±0.5 °C |
| **Resolution** | 0.015 °C (fixed) | 0.1 °C (fixed) | 0.0625 ~ 0.5 °C (configurable) |
| **Max sampling rate** | ~66 Hz | ~0.5 Hz | ~1.3 Hz (12-bit) |
| **Multi-sensor bus** | 2 per I2C bus | 1 per GPIO | Many on 1 GPIO pin |
| **Waterproof probe** | No | No | Yes (widely available) |
| **Price** | ~$6-14 | ~$2-4 | ~$1-3 |
| **Driver dependency** | smbus2 | adafruit-circuitpython-dht | None (kernel sysfs) |

**Choose this package** for waterproof temperature monitoring, multi-sensor setups on a single wire, or when no external Python library is desired.

## Prerequisites

- ROS 2 Jazzy
- Python 3
- Real hardware only:
  - 1-Wire kernel modules enabled: `dtoverlay=w1-gpio` in `/boot/config.txt`
  - 4.7k Ohm pull-up resistor between data line and 3.3V

## Installation

```bash
cd ~/ros2_ws
colcon build --packages-select ds18b20_temp --symlink-install
source install/setup.bash
```

## Usage

### Launch (fake mode — default)

```bash
ros2 launch ds18b20_temp ds18b20_launch.py
```

### Run node directly

```bash
ros2 run ds18b20_temp ds18b20_node.py
```

### Real hardware (Raspberry Pi)

```bash
ros2 launch ds18b20_temp ds18b20_launch.py \
  params_file:=path/to/your_params.yaml
```

Set `fake_mode: false` in your YAML file. Optionally set `device_id` to a specific sensor (e.g., `28-00000221bf22`); leave empty for auto-detection.

### Verify output

```bash
ros2 topic echo /ds18b20/temperature
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fake_mode` | bool | `true` | Generate random data without hardware |
| `device_id` | string | `""` | 1-Wire device ID (auto-detect if empty) |
| `resolution` | int | `12` | ADC resolution in bits (9, 10, 11, or 12) |
| `publish_rate` | float | `1.0` | Publishing rate in Hz (max ~1.3 Hz at 12-bit) |
| `frame_id` | string | `ds18b20_link` | TF frame ID |
| `temperature_variance` | float | `0.0` | Temperature variance (0 = unknown) |

## Services

| Service | Type | Description |
|---------|------|-------------|
| `ds18b20/calibrate` | `std_srvs/srv/Trigger` | Collect samples for 5 s, report averages |
| `ds18b20/reset` | `std_srvs/srv/Trigger` | Clear bias, reinitialize sensor |

## Package Structure

```
ds18b20_temp/
├── CMakeLists.txt
├── package.xml
├── config/
│   └── ds18b20_params.yaml
├── launch/
│   └── ds18b20_launch.py
├── ds18b20_temp/
│   ├── __init__.py
│   └── ds18b20_driver.py
├── nodes/
│   └── ds18b20_node.py
├── test/
│   └── test_ds18b20_node.py
├── .gitignore
├── LICENSE
├── CONTRIBUTING.md
└── README.md
```

## Test Results

Tested on Ubuntu 24.04 (WSL2) with `fake_mode: true`.

| Test Category | Test | Result |
|---|---|---|
| **Topics** | `ds18b20/temperature` publishes `sensor_msgs/Temperature` | PASS |
| **Services** | `ds18b20/calibrate` returns `success=True` | PASS |
| **Services** | `ds18b20/reset` returns `success=True` | PASS |
| **Parameters** | `publish_rate` runtime change | PASS |
| **Shutdown** | Clean exit | PASS |
| **Linting** | pep257, flake8, copyright, xmllint | PASS |

## License

MIT
