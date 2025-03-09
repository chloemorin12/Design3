import math
import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def VoltageToResistance(voltage, R2, gain, R4):
    Vin = 12
    diffdepot = voltage/(gain*Vin)
    R_eq = R2/(R2+R4)
    Resistance = R2*(R_eq-diffdepot)/(1+diffdepot-R_eq)
    return Resistance
    
    
def steinhart_hart_resistance_to_temperature(resistance, coefficients):
    A, B, C = coefficients
    lnR = math.log(resistance)
    temperature_kelvin = 1 / (A + B * lnR + C * lnR**3)
    return temperature_kelvin

def gaussian_2d(coords, A, x0, y0, sigma_x, sigma_y, offset):
    x, y = coords
    return A * np.exp(-((x - x0)**2 / (2 * sigma_x**2) + (y - y0)**2 / (2 * sigma_y**2))) + offset


coefficients = (1.40e-3, 2.37e-4, 9.90e-8)
resistance = 10000  # ohms
temperature_kelvin = steinhart_hart_resistance_to_temperature(resistance, coefficients)
print(f"Temperature: {temperature_kelvin} K")
print('hummmmmm', VoltageToResistance(0.779,22000,2.5,43000))




thermistor_positions = np.array([
    [0, 2], [1, 3], [2, 4], [3, 3], [4, 2],[1, 1], [2, 2], [3, 1],[2, 0]])
temperature_values = np.array([21, 24, 30, 27, 70, 26, 35, 28, 23])


x_data = thermistor_positions[:, 0]
y_data = thermistor_positions[:, 1]
z_data = temperature_values

initial_guess = [np.max(z_data), np.mean(x_data), np.mean(y_data), 1, 1, np.min(z_data)]
params, _ = scipy.optimize.curve_fit(gaussian_2d, (x_data, y_data), z_data, p0=initial_guess)
A, x_peak, y_peak, sigma_x, sigma_y, offset = params
print(f"Estimated heat peak at: ({x_peak:.2f}, {y_peak:.2f})")

x = np.linspace(0, 6, 100)
y = np.linspace(0, 6, 100)
x,y = np.meshgrid(x, y)
z = gaussian_2d((x, y), A, x_peak, y_peak, sigma_x, sigma_y, offset)

'''
plt.imshow(z, origin='lower', extent=(0, 5, 0, 5), cmap='coolwarm')
plt.colorbar(label='Temperature (°C)')
plt.title("Heat Source Localization using Gaussian Fit")
plt.xlabel("X Position")
plt.ylabel("Y Position")
plt.show()
'''

def data_gradient_temperature():
    return z

def position():
    return [x_peak, y_peak]

'''
fig, ax = plt.subplots(figsize=(10, 6))
scatter = ax.scatter(x_data, y_data, c=z_data, cmap='coolwarm', marker='o', label='Thermistor Readings')
ax.scatter(x_peak, y_peak, c='black', marker='x', s=30, label="Estimated Heat Source")
ax.set_xlabel("X Position")
ax.set_ylabel("Y Position")
ax.set_title("Heat Source Localization using Gaussian Fit")
ax.legend()
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Temperature (°C)')
plt.show()
'''
