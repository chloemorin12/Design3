import matplotlib.pyplot as plt
import nidaqmx
import time
import timeit
import numpy as np
from nidaqmx.constants import AcquisitionType
from scipy.optimize import curve_fit
from Algorithm import steinhart_hart_resistance_to_temperature
import nidaqmx
from nidaqmx.system import System


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
        self.previous_params = None  # Store the last successful parameters
        self.daq_device = self.get_active_device()


        self.liste_tension = []

        self.wavelenght_tension = np.full((256, 1), np.nan)
    
    def get_active_device(self):
        system = System.local()
        device_names = [device.name for device in system.devices]
        #print(device_names)

        if not device_names:
            raise RuntimeError("No NI-DAQmx devices detected.")
        
        
        #Choisi le premier device
        active_device = device_names[0]
        print(f"Using device: {active_device}")
        return active_device
        
    def assign_thermistor_positions(self):
        self.data = np.full((256, 2), np.nan)
        real_thermistor_positions = [
            [10.825317547305483, -6.25], [10.825317547305483, -3.125], [10.825317547305483, 0.0],
            [10.825317547305483, 3.125], [10.825317547305483, 6.25], [8.118988160479113, -7.8125],
            [8.118988160479113, -4.6875], [8.118988160479113, -1.5625], [8.118988160479113, 1.5625],
            [8.118988160479113, 4.6875], [8.118988160479113, 7.8125], [5.412658773652741, -9.375],
            [5.412658773652741, -6.25], [5.412658773652741, -3.125], [5.412658773652741, 0.0],
            [5.412658773652741, 3.125], [5.412658773652741, 6.25], [5.412658773652741, 9.375],
            [2.7063293868263707, -10.9375], [2.7063293868263707, -7.8125], [2.7063293868263707, -4.6875],
            [2.7063293868263707, -1.5625], [2.7063293868263707, 1.5625], [2.7063293868263707, 4.6875],
            [2.7063293868263707, 7.8125], [2.7063293868263707, 10.9375], [0.0, -12.5], [0.0, -9.375],
            [0.0, -6.25], [0.0, -3.125], [0.0, 0.0], [0.0, 3.125], [0.0, 6.25], [0.0, 9.375], [0.0, 12.5],
            [-2.7063293868263707, -10.9375], [-2.7063293868263707, -7.8125], [-2.7063293868263707, -4.6875],
            [-2.7063293868263707, -1.5625], [-2.7063293868263707, 1.5625], [-2.7063293868263707, 4.6875],
            [-2.7063293868263707, 7.8125], [-2.7063293868263707, 10.9375], [-5.412658773652741, -9.375],
            [-5.412658773652741, -6.25], [-5.412658773652741, -3.125], [-5.412658773652741, 0.0],
            [-5.412658773652741, 3.125], [-5.412658773652741, 6.25], [-5.412658773652741, 9.375],
            [-8.118988160479113, -7.8125], [-8.118988160479113, -4.6875], [-8.118988160479113, -1.5625],
            [-8.118988160479113, 1.5625], [-8.118988160479113, 4.6875], [-8.118988160479113, 7.8125],
            [-10.825317547305483, -6.25], [-10.825317547305483, -3.125], [-10.825317547305483, 0.0],
            [-10.825317547305483, 3.125], [-10.825317547305483, 6.25]]
        #rotated_positions = [[-x, -y] for x, y in real_thermistor_positions]
        #thermisor_positions = rotated_positions
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
        start_time = time.perf_counter()
        self.liste_voltage = []
        self.liste_ref = []
        self.liste_tension_ref = []
        with nidaqmx.Task() as do_task, nidaqmx.Task() as ai_task:
            do_task.do_channels.add_do_chan(f"{self.daq_device}/port0/line0:7") 
            ai_task.ai_channels.add_ai_voltage_chan(f"{self.daq_device}/ai7")
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
                    self.data = np.hstack((self.data, self.voltage_data))

                    max_value = np.nanmax(list(np.nanmax(float(row[-1]) for row in self.data)))
                    #print(max_value)
                    stop_time = time.perf_counter()
                    elapsed_time = stop_time - start_time
                    print(f"Elapsed time: {elapsed_time:.2f} seconds")                    
                    return self.data, self.liste_ref, self.liste_voltage, self.liste_tension_ref
                if value <= 7:
                    self.voltage_data[i] = np.nan 
                    continue
                if value == 64 or value == 80 or value == 96:   
                    do_task.write(value, auto_start=True)
                    voltage_therm_i = ai_task.read(number_of_samples_per_channel=self.samples_to_read)
                    voltage = np.mean(voltage_therm_i)
                    
                    voltages = np.array([9.51, 9.25, 8.55, 7.9, 7.6, 7.2, 6.65 , 5.5, 5.1, 1.9])
                    temperatures = np.array([90, 85, 80, 75, 70, 65, 60 ,55, 50, 22])
                    coeffs = np.polyfit(voltages, temperatures, deg=1)
                    poly_func = np.poly1d(coeffs)
                    temp = poly_func(voltage)
                    self.liste_tension_ref.append(voltage)
                    #self.liste_tension_ref.append(voltage)
                    #A, B, C = self.params
                    #temperature = steinhart_hart(voltage, A, B, C)
                    #temperature = steinhart_hart_resistance_to_temperature(resistance, [0.00088692, 0.00025122, 0.00000019716])
                    self.liste_ref.append(temp)
                    #print('liste_ref dans acquisition',self.liste_ref)
                else:
                    do_task.write(value, auto_start=True)
                    voltage_therm_i = ai_task.read(number_of_samples_per_channel=self.samples_to_read)
                    voltage = np.mean(voltage_therm_i)
                    
                    voltages = np.array([9.51, 9.25, 8.55, 7.9, 7.6, 7.2, 6.65 , 5.5, 5.1, 1.9])
                    temperatures = np.array([90, 85, 80, 75, 70, 65, 60 ,55, 50, 22])
                    coeffs = np.polyfit(voltages, temperatures, deg=1)
                    poly_func = np.poly1d(coeffs)
                    temp = poly_func(voltage)
                    self.liste_voltage.append(voltage)
                    #A, B, C = self.params
                    #temperature = steinhart_hart(voltage, A, B, C)
                    #temperature = steinhart_hart_resistance_to_temperature(resistance, [0.00088692, 0.00025122, 0.00000019716])
                    self.voltage_data[i] = temp
                    time.sleep(0.001)

                    #print(self.liste_ref)


    def Curve_temp_voltage(self):
        voltages = np.array([9.51, 9.25, 8.55, 7.9, 7.6, 7.2, 6.65 , 5.5, 5.1, 1.9])
        temperatures = np.array([100, 95, 90, 85, 80, 75, 70 ,60, 55, 22])    
        temperatures_kelvin = temperatures + 273.15
        initial_guess = [1e-3, 1e-4, 1e-7]
        self.params, covariance = curve_fit(steinhart_hart_resistance_to_temperature, voltages, temperatures_kelvin, p0=initial_guess)
        return self.params
                
            
                
    def Wavelength_thermistor(self):
        with nidaqmx.Task() as do_task, nidaqmx.Task() as ai_task:
            do_task.do_channels.add_do_chan(f"{self.daq_device}/port0/line0:7")
            ai_task.ai_channels.add_ai_voltage_chan(f"{self.daq_device}/ai7")
            ai_task.timing.cfg_samp_clk_timing(
                rate=self.sample_rate,
                sample_mode=AcquisitionType.FINITE,
                samps_per_chan=self.samples_to_read)

            do_task.write(65, auto_start=True)
            data = ai_task.read(number_of_samples_per_channel=self.samples_to_read)
            self.wavelenght_tension[65] = np.mean(data)
            do_task.write(7, auto_start=True)
            data = ai_task.read(number_of_samples_per_channel=self.samples_to_read)
            self.wavelenght_tension[7] = np.mean(data) 
            do_task.write(0, auto_start=True)
            data = ai_task.read(number_of_samples_per_channel=self.samples_to_read)
            self.wavelenght_tension[0] = np.mean(data) 
            do_task.write(113, auto_start=True)
            data = ai_task.read(number_of_samples_per_channel=self.samples_to_read)
            self.wavelenght_tension[113] = np.mean(data)  
            powers = self.wavelenght_tension[~np.isnan(self.wavelenght_tension).any(axis=1)]
            powers.tolist()
            return powers  
    
    def fitting(self):
        diameter = 25
        radius = diameter / 2
        data = self.data[~np.isnan(self.data).any(axis=1)]
        x, y, z = data[:, 0], data[:, 1], data[:, -1]
        initial_guess = [float(max(z)-min(z)), 0, 0, 2.5, 2.5, float(min(z))]
        bounds = ([0, -12.5, -12.5, 0, 0, -np.inf], [np.inf, 12.5, 12.5, np.inf, np.inf, np.inf])
        xy = np.vstack((x, y))   # isole x et y 
        '''
        try:
            params, _ = curve_fit(gaussian_2d, xy, z, p0=initial_guess, bounds=bounds)
            A, x_peak, y_peak, sigma_x, sigma_y, offset = params
            xi = np.linspace(-13, 13, 50)
            yi = np.linspace(-13, 13, 50)
            X_grid, Y_grid = np.meshgrid(xi, yi)
            Z_fit = gaussian_2d((X_grid.ravel(), Y_grid.ravel()), *params).reshape(X_grid.shape)
        except RuntimeError as e:
            print("Error in curve fitting:", e)
            return None, None, None, None
        '''

        try:
            # Attempt to fit the curve
            params, _ = curve_fit(gaussian_2d, xy, z, p0=initial_guess, bounds=bounds)
            self.previous_params = params  # Save the successful parameters
        except RuntimeError as e:
            print("Error in curve fitting:", e)
            if self.previous_params is not None:
                print("Using previous parameters.")
                params = self.previous_params  # Use the last successful parameters
            else:
                print("No previous parameters available.")
                return None, None, None, None

        # Extract parameters
        A, x_peak, y_peak, sigma_x, sigma_y, offset = params
        xi = np.linspace(-13, 13, 200)
        yi = np.linspace(-13, 13, 200)
        X_grid, Y_grid = np.meshgrid(xi, yi)
        Z_fit = gaussian_2d((X_grid.ravel(), Y_grid.ravel()), *params).reshape(X_grid.shape)
        R = np.sqrt(X_grid**2 + Y_grid**2)
        Z_fit_masked = np.where(R <= radius, Z_fit, np.nan)

        return params, Z_fit_masked, x_peak, y_peak
                   
'''
allo = Acquisition()
allo.assign_thermistor_positions()
allo.Power_thermistor()
allo.fitting()
'''