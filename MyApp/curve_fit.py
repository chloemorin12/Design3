import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import pandas as pd
import scipy.optimize


def gaussian_2d(coords, A, x0, y0, sigma_x, sigma_y, offset):
    x, y = coords
    return A * np.exp(-((x - x0)**2 / (2 * sigma_x**2) + (y - y0)**2 / (2 * sigma_y**2))) + offset

 

z_data= []
x_data = []
y_data = []


initial_guess = [np.max(z_data), np.mean(x_data), np.mean(y_data), 5, 5, np.min(z_data)]
params, _ = scipy.optimize.curve_fit(gaussian_2d, (x_data, y_data), z_data, p0=initial_guess)
A, x_peak, y_peak, sigma_x, sigma_y, offset = params

x = np.linspace(-10, 10, 100)
y = np.linspace(-12, 12, 100)
x, y = np.meshgrid(x, y)
z = gaussian_2d((x, y), A, x_peak, y_peak, sigma_x, sigma_y, offset)

