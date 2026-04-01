import time
import datetime
import serial
import binascii
import logging
from lcd import *
import RPi.GPIO as GPIO # Explicitly imported for error catching

# Modernized: using logging to track bugs easier in production
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import BlynkLib

# <YOUR_API_KEY> has been placed here to mask real authentication details
BLYNK_AUTH = '<YOUR_API_KEY>'

try:
    blynk = BlynkLib.Blynk(BLYNK_AUTH)
except Exception as e:
    logging.error(f"Failed to connect to Blynk Server: {e}")
    blynk = None

# Stepper Motor Configurations
StepPin = 7 # red
Dir = 5     # blue
ms2 = 11
rot = 50

# Global States
i = 1       # Current schedule index
count = 0
icheck = 0
pillflag = 0

FastSpeed = 0.001 
LowSpeed = 0.001

def setup_hardware():
    """Initializes Stepper Motor GPIOs."""
    try:
        GPIO.setup(Dir, GPIO.OUT)
        GPIO.setup(StepPin, GPIO.OUT)
        GPIO.setup(ms2, GPIO.OUT)
        GPIO.output(ms2, 1)
        logging.info("Hardware setup completed.")
    except Exception as e:
        logging.error(f"Failed to setup GPIO pins: {e}")

def get_serial_connection():
    """Returns a serial connection with error handling."""
    try:
        return serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=9600,
            timeout=1
        )
    except Exception as e:
        logging.error(f"Serial connection error: {e}")
        return None

def curr_tym():
    """Returns the current minute."""
    now = datetime.datetime.now()
    return now.minute

def generate_pill_times():
    """Generates schedule times derived from current time."""
    now = datetime.datetime.now()
    strt_tym = now.minute
    # Use modulo 60 to prevent invalid minutes > 59
    return [(strt_tym + offset) % 60 for offset in range(1, 18, 2)]

tym = generate_pill_times()

def notify():
    """Sends a Blynk alert if available."""
    if blynk:
        try:
            blynk.notify('ALERT')
            logging.info("Alert notification sent.")
        except Exception as e:
            logging.error(f"Blynk notification failed: {e}")
    else:
        logging.warning("Blynk not initialized, alert not sent.")

def safe_lcd_string(message, line, col):
    """Wraps LCD communication in try-except to prevent connection crashes."""
    try:
        lcd_string(message, line, col)
    except Exception as e:
        logging.error(f"LCD string error: {e}")

def next_corse():
    global i, count, icheck
    logging.info("Next Course")
    safe_lcd_string("Next_Course:", 1, 1)
    
    # Range check to remain safe
    if i < len(tym):
        safe_lcd_string(f"{tym[i]}", 1, 13)
        if curr_tym() == tym[i]:
            pass
    
    icheck = 0
    count = 0

def step_motor(direction, total_rotations):
    """Safely handles the stepper motor rotation to prevent software stops on hardware exception."""
    try:
        # 0 forward, 1 backwards
        GPIO.output(Dir, direction)
        for _ in range(total_rotations):
            GPIO.output(StepPin, 0)
            time.sleep(LowSpeed)
            GPIO.output(StepPin, 1)
            time.sleep(LowSpeed)
    except RuntimeError as e:
        logging.error(f"RuntimeError during motor rotation (Permissions/Pin setup): {e}")
    except Exception as e:
        logging.error(f"Unexpected Stepper Motor failure: {e}")
    finally:
        # Failsafe to ensure step pin does not stay High
        try:
            GPIO.output(StepPin, 0)
        except Exception:
            pass

def main():
    global i, count, icheck, pillflag

    setup_hardware()
    ser = get_serial_connection()

    while True:
        try:
            if blynk:
                blynk.run()
        except OSError as e:
            logging.error(f"Networking error while running Blynk: {e}")
        except Exception as e:
            logging.error(f"Unknown Blynk error: {e}")

        # Ensure index within bounds
        if i >= len(tym):
            i = 0

        if curr_tym() == tym[i]:
            safe_lcd_string("                ", 1, 1)
            count = 0 
            
            if not ser:
                logging.error("Serial disconnected. Retrying...")
                time.sleep(2)
                ser = get_serial_connection()
                continue
                
            try:
                x = ser.readline()
                hex_string = x.hex()
            except Exception as e:
                logging.error(f"Failed to read from fingerprint serial: {e}")
                hex_string = ''

            # Fingerprint checking loop
            while hex_string == '' and count < 55:
                try:
                    x = ser.readline()
                    hex_string = x.hex()
                except Exception:
                    pass
                
                safe_lcd_string("place ur Finger", 1, 1)
                time.sleep(0.1)
                count += 1
                
                if count > 43:
                    logging.warning("Alert triggered - Fingerprint timeout")
                    notify()
                    next_corse()
                    
                    if icheck == 0:
                        i += 1
                        icheck = 1
                        break
                        
                if blynk:
                    try:
                        blynk.run()
                    except Exception as e:
                        logging.error(f"Blynk wait loop exception: {e}")
          
            if hex_string in ('00', '01', '03'):
                logging.info("Finger identified")
                safe_lcd_string("          ", 1, 1)
                safe_lcd_string("Successful", 1, 1)
                logging.info(f"{i+1} moving forward")
                
                step_motor(direction=0, total_rotations=(rot * i))
                time.sleep(3)
                
                pillflag = 1
                time.sleep(1)
                
                step_motor(direction=1, total_rotations=(rot * i))
                time.sleep(3)
                i += 1
                
            elif hex_string == 'ff':
                safe_lcd_string("             ", 1, 1)
                safe_lcd_string("Invalid", 1, 1)
                logging.warning("Invalid fingerprint")
                time.sleep(1)
                
        else:
            if pillflag == 1:
                logging.info("pill box reset")
                time.sleep(0.5)
                logging.info(f"{i+1} reverse")
                pillflag = 0
                
            next_corse()
            time.sleep(1) # sleep to prevent busy wait

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Terminated by user.")
    except Exception as e:
        logging.critical(f"Program crashed: {e}")
    finally:
        try:
            GPIO.cleanup()
        except Exception:
            pass
