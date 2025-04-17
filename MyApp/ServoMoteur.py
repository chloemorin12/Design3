import nidaqmx
import numpy as np
import time

def angle_to_pulse_width_ms(angle_rad):
    # Mappe -π à π → 1 ms à 2 ms
    return 1.5 + (angle_rad / np.pi) * 0.5

def send_software_pwm(channel="Dev1/port1/line0", angle_rad=0.0, duration=2.0):
    pulse_width_ms = angle_to_pulse_width_ms(angle_rad)
    period_ms = 20  # SG90: 50 Hz = 20 ms période
    high_time = pulse_width_ms / 1000  # en secondes
    low_time = (period_ms - pulse_width_ms) / 1000  # en secondes

    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(channel)
        start_time = time.time()
        print(f"Envoi PWM logiciel : angle={angle_rad:.2f} rad, pulse={pulse_width_ms:.2f} ms")

        while time.time() - start_time < duration:
            task.write(True)   # impulsion haute
            time.sleep(high_time)
            task.write(False)  # impulsion basse
            time.sleep(low_time)

# Exemple : tourner à +π/2 radians (~90°)
send_software_pwm(angle_rad=np.pi/2)
