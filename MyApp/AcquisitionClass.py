import matplotlib.pyplot as plt
import nidaqmx
import time
import numpy as np
from nidaqmx.constants import AcquisitionType
from scipy.optimize import curve_fit

def gaussian_2d(coords, A, x0, y0, sigma_x, sigma_y, offset):
    x, y = coords
    return A * np.exp(-((x - x0)**2 / (2 * sigma_x**2) + (y - y0)**2 / (2 * sigma_y**2))) + offset

class Acquisition:
    def __init__(self):
        self.voltage_data = np.full((256, 1), np.nan)
        self.data = np.full((256, 1), np.nan)
        self.thermistor = np.full((256, 2), np.nan)
        duration = 0.01
        self.sample_rate = 1000
        self.samples_to_read = int(duration * self.sample_rate)
        
    def assign_thermistor_positions(self):
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
            self.thermistor[position] = real_thermistor_positions[i]
        return self.thermistor
        
    def Power_thermistor(self):
        max_value = 256
        value = 0
        with nidaqmx.Task() as do_task, nidaqmx.Task() as ai_task:
            do_task.do_channels.add_do_chan("Dev1/port0/line0:7")
            ai_task.ai_channels.add_ai_voltage_chan("Dev1/ai7")
            ai_task.timing.cfg_samp_clk_timing(
                rate=self.sample_rate,
                sample_mode=AcquisitionType.FINITE,
                samps_per_chan=self.samples_to_read)

            for i in range(129):
                value = i
                binary_str = format(value, '08b')
                if binary_str[-4] == '1':
                    value += 8
                    binary_str = format(value, '08b')
                if binary_str[-8] == '1':
                    self.data = np.hstack((self.thermistor, self.voltage_data))
                    self.data = self.data[~np.isnan(self.data).any(axis=1)]
                    x, y, z = self.data[:, 0], self.data[:, 1], self.data[:, 2]
                    return self.voltage_data
                
                do_task.write(value, auto_start=True)
                self.data = ai_task.read(number_of_samples_per_channel=self.samples_to_read)
                self.voltage_data[i] = np.mean(self.data)
                
    def Wavelength_thermistor(self):
        with nidaqmx.Task() as do_task, nidaqmx.Task() as ai_task:
            do_task.do_channels.add_do_chan("Dev1/port0/line0:7")
            ai_task.ai_channels.add_ai_voltage_chan("Dev1/ai7")
            ai_task.timing.cfg_samp_clk_timing(
                rate=self.sample_rate,
                sample_mode=AcquisitionType.FINITE,
                samps_per_chan=self.samples_to_read)
            
            do_task.write(136, auto_start=True)
            data = ai_task.read(number_of_samples_per_channel=self.samples_to_read)
            self.voltage_data[136] = np.mean(data)
            do_task.write(153, auto_start=True)
            data = ai_task.read(number_of_samples_per_channel=self.samples_to_read)
            self.voltage_data[153] = np.mean(data) 
            do_task.write(170, auto_start=True)
            data = ai_task.read(number_of_samples_per_channel=self.samples_to_read)
            self.voltage_data[170] = np.mean(data) 
            do_task.write(187, auto_start=True)
            data = ai_task.read(number_of_samples_per_channel=self.samples_to_read)
            self.voltage_data[187] = np.mean(data)  
            data = np.hstack((self.thermistor, self.voltage_data))
            return self.voltage_data    
    
    def fitting(self):
        diameter = 25
        radius = diameter / 2
        self.data = self.data[~np.isnan(self.data).any(axis=1)]
        x, y, z = self.data[:, 0], self.data[:, 1], self.data[:, 2]
        initial_guess = [np.max(z), 1, 1, 2.5, 2.5, np.min(z)]
        xy = np.vstack((x, y))
        params, _ = curve_fit(gaussian_2d, xy, z, p0=initial_guess)
        A, x_peak, y_peak, sigma_x, sigma_y, offset = params
        print(f"Fitted Peak: x = {x_peak}, y = {y_peak}")
        
        xi = np.linspace(-13, 13, 200)
        yi = np.linspace(-13, 13, 200)
        X_grid, Y_grid = np.meshgrid(xi, yi)
        Z_fit = gaussian_2d((X_grid.ravel(), Y_grid.ravel()), *params).reshape(X_grid.shape)
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
                   

# Example usage:
allo = Acquisition()
allo.assign_thermistor_positions()
allo.Power_thermistor()
allo.fitting()