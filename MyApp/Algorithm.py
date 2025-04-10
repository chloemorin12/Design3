import math
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd

arr = array = np.ones((256, 1), dtype=float)
arr[115] = 1.4
arr[116] = 1.1
arr[50] = 1.1
arr[99] = 1.1
arr[100] = 1.1
arr[51] = 1.1
arr[52] = 1.1

def gaussian_2d(coords, A, x0, y0, sigma_x, sigma_y, offset):
    x, y = coords
    return A * np.exp(-(((x - x0)**2 / (2 * sigma_x**2)) + ((y - y0)**2 / (2 * sigma_y**2)))) + offset

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

thermistor = np.full((256, 2), np.nan)

def assign_thermistor_positions():
        real_thermistor_positions = [
            [-6.25, -10.825317547305483], [-3.125, -10.825317547305483], [0.0, -10.825317547305483],
            [3.125, -10.825317547305483], [6.25, -10.825317547305483], [-7.8125, -8.118988160479113],
            [-4.6875, -8.118988160479113], [-1.5625, -8.118988160479113], [1.5625, -8.118988160479113],
            [4.6875, -8.118988160479113], [7.8125, -8.118988160479113], [-9.375, -5.412658773652741],
            [-6.25, -5.412658773652741], [-3.125, -5.412658773652741], [0.0, -5.412658773652741],
            [3.125, -5.412658773652741], [6.25, -5.412658773652741], [9.375, -5.412658773652741],
            [-10.9375, -2.7063293868263707], [-7.8125, -2.7063293868263707], [-4.6875, -2.7063293868263707],
            [-1.5625, -2.7063293868263707], [1.5625, -2.7063293868263707], [4.6875, -2.7063293868263707],
            [7.8125, -2.7063293868263707], [10.9375, -2.7063293868263707], [-12.5, 0.0], [-9.375, 0.0],
            [-6.25, 0.0], [-3.125, 0.0], [0.0, 0.0], [3.125, 0.0], [6.25, 0.0], [9.375, 0.0], [12.5, 0.0],
            [-10.9375, 2.7063293868263707], [-7.8125, 2.7063293868263707], [-4.6875, 2.7063293868263707],
            [-1.5625, 2.7063293868263707], [1.5625, 2.7063293868263707], [4.6875, 2.7063293868263707],
            [7.8125, 2.7063293868263707], [10.9375, 2.7063293868263707], [-9.375, 5.412658773652741],
            [-6.25, 5.412658773652741], [-3.125, 5.412658773652741], [0.0, 5.412658773652741],
            [3.125, 5.412658773652741], [6.25, 5.412658773652741], [9.375, 5.412658773652741],
            [-7.8125, 8.118988160479113], [-4.6875, 8.118988160479113], [-1.5625, 8.118988160479113],
            [1.5625, 8.118988160479113], [4.6875, 8.118988160479113], [7.8125, 8.118988160479113],
            [-6.25, 10.825317547305483], [-3.125, 10.825317547305483], [0.0, 10.825317547305483],
            [3.125, 10.825317547305483], [6.25, 10.825317547305483]]
        liste_thermistor_values = [
                           66,82,113,48,32,97,67,98,49,16,0,81,68,83,114,33,17,
                           1,65,69,84,99,50,34,18,2,112,70,85,100,115,51,35,19,
                           3,71,86,101,116,52,36,20,4,87,102,117,53,37,21,5,103,
                           118,54,38,22,6,119,55,39,23,7]
        for i in range(len(real_thermistor_positions)):
            position = liste_thermistor_values[i]
            thermistor[position] = real_thermistor_positions[i]
        return thermistor

data = assign_thermistor_positions()
data = np.hstack((data, arr))

def fitting(data):
    diameter = 25
    radius = diameter / 2
    data = data[~np.isnan(data).any(axis=1)]
    x, y, z = data[:, 0], data[:, 1], data[:, 2]

    initial_guess = [np.max(z), 1, 1, 5, 5, np.min(z)]
    print(initial_guess)
    params, _ = curve_fit(gaussian_2d, (x, y), z, p0=initial_guess)
    A, x_peak, y_peak, sigma_x, sigma_y, offset = params
    xi = np.linspace(-13, 13, 200)
    yi = np.linspace(-13, 13, 200)
    X_grid, Y_grid = np.meshgrid(xi, yi)
    Z_fit = gaussian_2d((X_grid, Y_grid), *params)
    R = np.sqrt(X_grid**2 + Y_grid**2)
    Z_fit_masked = np.where(R <= radius, Z_fit, np.nan)
    plt.figure(figsize=(7, 6))
    sc = plt.scatter(x, y, c=z, cmap='coolwarm', s=100, edgecolor='k', label='Data')
    plt.plot(x_peak, y_peak, 'kx', markersize=10, markeredgewidth=3, label='Peak')
    plt.contourf(X_grid, Y_grid, Z_fit_masked, levels=20, cmap='coolwarm', alpha=0.2)
    plt.colorbar(sc, label='Voltage')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('2D Gaussian Fit to Thermistor Readings')
    plt.grid(True)
    plt.legend()
    theta = np.linspace(0, 2 * np.pi, 100)
    circle_x = radius * np.cos(theta)
    circle_y = radius * np.sin(theta)
    plt.plot(circle_x, circle_y, 'k--', label=f"Circle (D={diameter})")
    plt.axis("equal")
    plt.grid(True)
    plt.show()
            
print(fitting(data))        