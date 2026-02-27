# 🌡️ ds18b20_temp - Easy Temperature Readings from Sensor

[![Download Latest Release](https://img.shields.io/badge/Download-Get%20Release-blue)](https://github.com/Marco19519/ds18b20_temp/releases)

---

## 📖 What is ds18b20_temp?

ds18b20_temp is a simple tool designed to work with the Dallas DS18B20 temperature sensor. It helps you read temperature data from the sensor using a Raspberry Pi or other compatible devices. This tool uses ROS2 Jazzy, a system for robot software, to communicate with the sensor smoothly.

If you want to measure water or air temperature easily and reliably, ds18b20_temp can help. It works with waterproof sensors and uses the 1-wire communication method.

---

## 🖥️ System Requirements

Before you start, check that your setup matches the following needs:

- A computer running Linux (Ubuntu or Raspberry Pi OS recommended).
- A Raspberry Pi or similar device with GPIO pins to connect the sensor.
- Installed ROS2 Jazzy version (for managing sensor data).
- Python 3.8 or above installed.
- Basic cable and connector for 1-wire sensor connection.
- Internet connection to download the software package.

If you are using Raspberry Pi, make sure your device is updated to the latest version and has the necessary permissions to access GPIO pins.

---

## 🔧 Hardware Needed

To get accurate temperature readings, you will need:

- Dallas DS18B20 digital temperature sensor (waterproof or non-waterproof type).
- A Raspberry Pi with an accessible GPIO interface.
- A 4.7k ohm resistor (acts as a pull-up for the sensor data line).
- Connecting wires or a breadboard for easy setup.

---

## 🚀 Getting Started

This guide walks you through getting the temperature sensor working with your Raspberry Pi quickly.

### Step 1 – Connect the Sensor

1. Plug the DS18B20 sensor to your Raspberry Pi:

   - Connect the **Red wire** (VCC) to a 3.3V power pin.
   - Connect the **Black wire** (GND) to a ground pin.
   - Connect the **Yellow wire** (Data) to GPIO pin 4.
   
2. Place the 4.7k ohm resistor between the red (power) and yellow (data) wires. This helps the sensor communicate properly.

3. Double-check the connections to ensure no wires are loose or touching incorrectly.

### Step 2 – Enable 1-Wire Interface on Raspberry Pi

Before running the software, enable the 1-Wire interface on your device:

1. Open a terminal window.

2. Enter the following command to edit the boot configuration:

    ```
    sudo nano /boot/config.txt
    ```

3. Add this line at the end of the file:

    ```
    dtoverlay=w1-gpio
    ```

4. Save the file and reboot your Raspberry Pi by running:

    ```
    sudo reboot
    ```

After reboot, confirm that the 1-Wire module loaded:

```
lsmod | grep w1_gpio
```

You should see a line related to w1_gpio if it’s active.

---

## 📥 Download & Install

You can get the software by visiting the release page here:

**[Download ds18b20_temp releases](https://github.com/Marco19519/ds18b20_temp/releases)**

### How to Download and Run

1. Click the button above or visit the link directly to see available versions.

2. Download the latest release package suitable for your system (usually a .tar.gz or .zip file).

3. Extract the downloaded file to a folder on your Raspberry Pi or computer.

4. Open a terminal and navigate to the extracted folder.

5. Install required Python libraries used by ds18b20_temp:

    ```
    pip3 install -r requirements.txt
    ```

6. Run the software by typing:

    ```
    python3 ds18b20_temp_node.py
    ```

This will start the temperature driver and begin reading data from your sensor.

---

## ⚙️ How It Works

ds18b20_temp reads temperature data by communicating with the sensor over the 1-Wire bus. The driver converts raw data from the sensor into readable temperature values shown in Celsius.

It uses ROS2 Jazzy, a robot operating system framework, to publish temperature readings. This makes it easy for other ROS2-compatible devices or applications to access temperature data.

The software supports multiple sensors connected to the same 1-Wire line. It identifies each sensor uniquely so that you can monitor different locations or fluids.

---

## 🔍 Features

- Compatible with Dallas DS18B20 digital temperature sensors.
- Supports waterproof sensor versions for outdoor or wet environments.
- Uses standard 1-Wire protocol on Raspberry Pi GPIO pin 4.
- Integrates naturally with ROS2 Jazzy systems.
- Python-based, easy to install and run.
- Provides stable and accurate temperature readings.
- Supports multiple sensors on a single 1-Wire bus.

---

## 🧰 Troubleshooting

If the sensor does not work or readings seem off, try these steps:

- Check the wiring and resistor connection carefully.
- Confirm the 1-Wire interface is enabled by reviewing `/boot/config.txt`.
- Verify your user has permission to access GPIO pins.
- Make sure the sensor is not damaged and is compatible.
- Restart your Raspberry Pi after any changes.
- Look at the terminal output for error messages when running the program.
- If temperature values stay constant or show errors, unplug and reconnect the sensor.

---

## 🙋 Where to Get Help

You can look for help in these places:

- GitHub Issues page of this repository for bugs or enhancements.
- ROS2 Jazzy user forums for questions about ROS setup.
- Raspberry Pi community forums for hardware-related trouble.
- Online tutorials for DS18B20 sensor wiring and use.

---

## 📚 Learn More

If you want to dive deeper, here are some useful resources:

- Dallas DS18B20 sensor datasheet (search online).
- ROS2 Jazzy official documentation.
- Raspberry Pi GPIO pinout guides.
- Python tutorials on reading 1-Wire sensors.

---

## ⚖️ License

ds18b20_temp is open-source software. It uses standard open-license terms. Review the LICENSE file in the repository for details.

---

[![Download Latest Release](https://img.shields.io/badge/Download-Get%20Release-blue)](https://github.com/Marco19519/ds18b20_temp/releases)