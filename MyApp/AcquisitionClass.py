import matplotlib.pyplot as plt
import nidaqmx
import time
import timeit
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
        duration = 0.001
        self.sample_rate = 10000
        self.samples_to_read = int(duration * self.sample_rate)
        
    def assign_thermistor_positions(self):
        self.data = np.full((256, 2), np.nan)
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
            self.data[position] = real_thermistor_positions[i]   
        return self.data
        
    def Power_thermistor(self):
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
                    self.voltage_data[i] = np.nan # retourne (x, y, voltage) pour chaucune des 61 thermistors
                    continue
                if binary_str[-8] == '1':
                    #print(np.shape(self.data))
                    #print(np.shape(self.voltage_data))
                    self.data = np.hstack((self.data, self.voltage_data))
                    return self.data
                
                do_task.write(value, auto_start=True)
                voltage_therm_i = ai_task.read(number_of_samples_per_channel=self.samples_to_read)
                self.voltage_data[i] = np.mean(voltage_therm_i)   # retourne (x, y, voltage) pour chaucune des 61 thermistors
                
                
            
                
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
            data = np.hstack((self.data, self.voltage_data))
            return self.voltage_data    
    
    def fitting(self):
        diameter = 25
        radius = diameter / 2
        data = self.data[~np.isnan(self.data).any(axis=1)]
        x, y, z = data[:, 0], data[:, 1], data[:, -1]
        initial_guess = [float(max(z)-min(z)), 0, 0, 2.5, 2.5, float(min(z))]
        bounds = ([0, -12.5, -12.5, 0, 0, -np.inf], [np.inf, 12.5, 12.5, np.inf, np.inf, np.inf])
        xy = np.vstack((x, y))   # isole x et y 
        params, _ = curve_fit(gaussian_2d, xy, z, p0=initial_guess, bounds=bounds)
        A, x_peak, y_peak, sigma_x, sigma_y, offset = params
        xi = np.linspace(-13, 13, 50)
        yi = np.linspace(-13, 13, 50)
        X_grid, Y_grid = np.meshgrid(xi, yi)
        Z_fit = gaussian_2d((X_grid.ravel(), Y_grid.ravel()), *params).reshape(X_grid.shape)
        
        #print(initial_guess)
        #print(params)
        #print(x[0], y[0])
        #print(params[0] * np.exp(-((x[0] - params[1])**2 / (2 * params[3]**2) + (y[0] - params[2])**2 / (2 * params[4]**2))) + params[5])
        A, x_peak, y_peak, sigma_x, sigma_y, offset = params
        #print(f"Fitted Peak: x = {x_peak}, y = {y_peak}")
        
        xi = np.linspace(-13, 13, 200)
        yi = np.linspace(-13, 13, 200)
        X_grid, Y_grid = np.meshgrid(xi, yi)
        Z_fit = gaussian_2d((X_grid.ravel(), Y_grid.ravel()), *params).reshape(X_grid.shape)
        R = np.sqrt(X_grid**2 + Y_grid**2)
        Z_fit_masked = np.where(R <= radius, Z_fit, np.nan)
        
        return params, Z_fit_masked, x_peak, y_peak
    
        plt.figure(figsize=(7, 6))
        sc = plt.scatter(x, y, c=z, cmap='coolwarm', s=100, edgecolor='k')
        plt.plot(x_peak, y_peak, 'kx', markersize=10, markeredgewidth=3)
        plt.contourf(X_grid, Y_grid, Z_fit_masked, levels=20, cmap='coolwarm', alpha=0.2)
        plt.colorbar(sc, label='Voltage')
        plt.grid(True)
        
        theta = np.linspace(0, 2 * np.pi, 100)
        circle_x = radius * np.cos(theta)
        circle_y = radius * np.sin(theta)
        plt.plot(circle_x, circle_y, 'k--')
        plt.grid(True)
        plt.show()
                   
'''
allo = Acquisition()
allo.assign_thermistor_positions()
allo.Power_thermistor()
allo.fitting()'''