import math
import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd

    
    
def steinhart_hart_resistance_to_temperature(resistance, coefficients):
    A, B, C = coefficients
    lnR = math.log(resistance)
    temperature_kelvin = 1 / (A + B * lnR + C * lnR**3)
    return temperature_kelvin
'''
sampling_interval = 1  # s
total_time = 600          # s
time_steps = int(total_time / sampling_interval)
ambient = 25.0           # °C
# Thermal parameters
k = 0.5  # thermal constant (1/s), tune this!

# Simulated laser power profile
def laser_power(t):
    if t < 60:
        return 2.5
    elif t < 120:
        return 5
    elif t < 180:
        return 7.5
    elif t < 240:
        return 10
    elif t < 300:
        return 7.5
    elif t < 360:
        return 0
    elif t < 420:
        return 10
    elif t < 480:
        return 2.5
    elif t < 540:
        return 7.5
    else:
        return 5

# Simulated temperature response
def simulate_temperature(prev_temp, power):
    T_inf = ambient + power * 2  # final temp = linear function of power
    dTdt = k * (T_inf - prev_temp)
    return prev_temp + dTdt * sampling_interval

# Logs
T_proto = []
dTdt_vals = []
predicted_Temp = []
T_finale_prevu = []
time_log = []

temp = ambient

# Main loop
for i in range(time_steps):
    t = i * sampling_interval
    power = laser_power(t)
    true_Tinf = ambient + power * 2

    new_temp = simulate_temperature(temp, power)
    dTdt = (new_temp - temp) / sampling_interval
    print('LA', new_temp, temp)
    predicted_Tinf = new_temp + dTdt / k
    
    # Store logs
    T_proto.append(new_temp)
    dTdt_vals.append(dTdt)
    predicted_Temp.append(predicted_Tinf)
    T_finale_prevu.append(true_Tinf)
    time_log.append(t)

    temp = new_temp

    #if i % 10 == 0:
    print(f"t={t:.1f}s | T={new_temp:.2f}°C | dT/dt={dTdt:.2f}°C/s | "
            f"T∞ predicted={predicted_Tinf:.2f} | True T∞={true_Tinf:.2f}")

# Plot results
plt.figure(figsize=(12, 5))
plt.subplot(2, 1, 1)
plt.plot(time_log, T_proto, label="Température du prototype")
plt.plot(time_log, T_finale_prevu, label="Température finale", linestyle='--', color = 'black')
plt.plot(time_log, predicted_Temp, label="Prédiction de la température finale", linestyle=':')
plt.ylabel("Température")
plt.legend()
plt.grid(True)
plt.subplot(2, 1, 2)
plt.plot(time_log, dTdt_vals, label="dT/dt")
plt.xlabel("Temps")
plt.ylabel("Température Derivé")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()'''

def prediction_temperature(temperature_avant, temperature_presente):
    if temperature_avant == 0:
        return 20
    sampling_interval = 1
    time_steps = 3
    ambient = 22.0 
    k = 0.32/3
    dTdt = (temperature_presente - temperature_avant) / sampling_interval
    print(dTdt)
    predicted_Temperature = temperature_presente + dTdt / k
    print('Prédiction:', round(predicted_Temperature,2))
    return predicted_Temperature