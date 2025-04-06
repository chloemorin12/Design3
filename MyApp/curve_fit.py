import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import pandas as pd
import scipy.optimize

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
    [3.125, 10.825317547305483], [6.25, 10.825317547305483]
]
print(len(real_thermistor_positions))
def gaussian_2d(coords, A, x0, y0, sigma_x, sigma_y, offset):
    x, y = coords
    return A * np.exp(-((x - x0)**2 / (2 * sigma_x**2) + (y - y0)**2 / (2 * sigma_y**2))) + offset


file_path = r'c:\Users\AlexisGiroux\Downloads\thermistance_echellon.xlsx'
data = pd.read_excel(file_path, sheet_name='data')
data = data.to_numpy().T
temps, ailette, center, left, right, top, bottom, top_left, top_right, bottom_left, bottom_right = data  
ailette = ailette - 273.15
center = center - 273.15
left = left - 273.15
right = right - 273.15
top = top - 273.15
bottom = bottom - 273.15
top_left = top_left - 273.15
top_right = top_right - 273.15
bottom_left = bottom_left - 273.15
bottom_right = bottom_right - 273.15 

plt.ion()

thermistor_positions = np.array([[0, 0], [9.325, 0], [-9.325, 0], [0, 10.825], [0, -10.825],
                                 [6.25, 5.413], [6.25, -5.413], [-6.25, -5.413], [-6.25, 5.413]])


fig, ax = plt.subplots(figsize=(10, 6))

for i in range(0, len(temps), 10):
    temperature_values = np.array([center[i], right[i], left[i], top[i], bottom[i], top_right[i], bottom_right[i], bottom_left[i], top_left[i]])

    x_data = thermistor_positions[:, 0]
    y_data = thermistor_positions[:, 1]
    z_data = temperature_values
    
    initial_guess = [np.max(z_data), np.mean(x_data), np.mean(y_data), 5, 5, np.min(z_data)]
    params, _ = scipy.optimize.curve_fit(gaussian_2d, (x_data, y_data), z_data, p0=initial_guess)
    A, x_peak, y_peak, sigma_x, sigma_y, offset = params

    x = np.linspace(-10, 10, 100)
    y = np.linspace(-12, 12, 100)
    x, y = np.meshgrid(x, y)
    z = gaussian_2d((x, y), A, x_peak, y_peak, sigma_x, sigma_y, offset)
    
    ax.clear()
    
    im = ax.imshow(z, origin='lower', extent=(-10, 10, -12, 12), cmap='coolwarm')
    ax.set_title("Heat Source Localization using Gaussian Fit")
    ax.set_xlabel("X Position")
    ax.set_ylabel("Y Position")
    
    if i == 0:
        cbar = fig.colorbar(im, ax=ax, label='Temperature (°C)')
    else:
        cbar.set_ticks(np.linspace(np.min(z), np.max(z), num=5))
        cbar.update_ticks()
    plt.draw()
    plt.pause(0.1)

plt.ioff()
plt.show()