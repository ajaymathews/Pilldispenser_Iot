# Pill Dispenser IoT

A fingerprint sensor-secured Smart Pill Dispenser that displays alerts via an LCD and notifies caretakers instantly using the Blynk platform if a patient misses their medication course. 

## Circuit & Hardware Description
The device combines a **Raspberry Pi** handling the main logic loop with real-world peripherals:
1. **Fingerprint Sensor**: Communicating over Serial (`/dev/ttyUSB0` via `pyserial`). It authenticates users securely before granting access.
2. **Stepper Motor System**:
    - **A4988/DRV8825 Motor Driver**: Controls the connected stepper motor utilizing GPIO out pins.
    - **Step Pin (7)** & **Direction Pin (5)**: Managed securely via `RPi.GPIO` by the software to rotate the physical pill slots forwards/backwards according to the medication schedule.
3. **LCD Display**: Provides user-friendly visual feedback on the scheduled next course and authentication status.
4. **Blynk Cloud**: Connects to the Blynk service to push critical alerts remotely to a caretaker's smartphone application.

## Prerequisites & Installation

This project requires **Python 3.10+** and the following structural dependencies.

1. **Install Python Packages**:
   Clone the repository and install the standard prerequisites listed in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Blynk Integration**:
   - Open `main.py`.
   - Locate the `BLYNK_AUTH = '<YOUR_API_KEY>'` variable assignment at the top of the file.
   - Replace `<YOUR_API_KEY>` with your official Authentication Token from the Blynk smartphone app to protect your privacy and ensure real-time operation.

3. **Running the Daemon**:
   To initiate the pill dispenser background daemon safely, simply run:
   ```bash
   sudo python main.py
   ```
   *Note: `sudo` may be required for `RPi.GPIO` and strict TTY Serial interactions on certain legacy Raspberry Pi OS versions.*
