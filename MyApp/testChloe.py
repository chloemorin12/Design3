import math
import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
from matplotlib.animation import FuncAnimation




def gaussian_2d(coords, A, x0, y0, sigma_x, sigma_y, offset):
    x, y = coords
    return A * np.exp(-((x - x0)**2 / (2 * sigma_x**2) + (y - y0)**2 / (2 * sigma_y**2))) + offset



# Version actuelle pour les données de température au hasard
# Fonction de transfert _ simulation Oli 5mm en bas 


def get_position_v2(array_thermistor):
        
    thermistor_positions = np.array([
        [0, 2], [1, 3], [2, 4], [3, 3], [4, 2],[1, 1], [2, 2], [3, 1],[2, 0]])
    temperature_values = np.array(array_thermistor)
    print(array_thermistor)


    x_data = thermistor_positions[:, 0]
    y_data = thermistor_positions[:, 1]
    z_data = array_thermistor

    # Intial guess sometimes doen't work
    initial_guess = [np.max(z_data), np.mean(x_data), np.mean(y_data), 1, 1, np.min(z_data)]
    params, _ = scipy.optimize.curve_fit(gaussian_2d, (x_data, y_data), z_data, p0=initial_guess)
    A, x_peak, y_peak, sigma_x, sigma_y, offset = params
    print(f"Estimated heat peak at: ({x_peak:.2f}, {y_peak:.2f})")

    x = np.linspace(0, 6, 100)
    y = np.linspace(0, 6, 100)
    x,y = np.meshgrid(x, y)
    z = gaussian_2d((x, y), A, x_peak, y_peak, sigma_x, sigma_y, offset)

    return [z, x_peak, y_peak]

def data_gradient_temperature(liste_temp):
        print(liste_temp)
        result = get_position_v2(liste_temp)
        return result[0]
        

def position(liste_temp):
        return [get_position_v2(liste_temp)[1], get_position_v2(liste_temp)[2]]


