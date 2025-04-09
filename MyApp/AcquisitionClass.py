import matplotlib.pyplot as plt
import nidaqmx
import time
import numpy as np
from nidaqmx.constants import AcquisitionType

class Acquisition:
    def __init__(self):
        self.voltage_data = np.full((256, 1), np.nan)
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
        start_time = time.perf_counter()
        with nidaqmx.Task() as do_task, nidaqmx.Task() as ai_task:
            do_task.do_channels.add_do_chan("Dev1/port0/line0:7")
            ai_task.ai_channels.add_ai_voltage_chan("Dev1/ai7")
            ai_task.timing.cfg_samp_clk_timing(
                rate=self.sample_rate,
                sample_mode=AcquisitionType.FINITE,
                samps_per_chan=self.samples_to_read)

            for i in range(max_value):
                value = i
                binary_str = format(value, '08b')

                if binary_str[-4] == '1':
                    value += 8
                    binary_str = format(value, '08b')
                if binary_str[-8] == '1':
                    data = np.hstack((self.thermistor, self.voltage_data))
                    data = data[~np.isnan(data).any(axis=1)]
                    x, y, z = data[:, 0], data[:, 1], data[:, 2]
                    plt.figure(figsize=(6, 5))
                    sc = plt.scatter(x, y, c=z, cmap='coolwarm', s=100, edgecolor='k')
                    plt.colorbar(sc, label='Voltage')
                    plt.xlabel('X')
                    plt.ylabel('Y')
                    plt.title('2D Scatter of Thermistor Readings')
                    plt.grid(True)
                    plt.show()

                    stop_time = time.perf_counter()
                    print(f"Temps total: {stop_time - start_time:.2f} s")
                    return self.voltage_data
                
                do_task.write(value, auto_start=True)
                data = ai_task.read(number_of_samples_per_channel=self.samples_to_read)
                self.voltage_data[i] = np.mean(data)
                
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
            
                   

allo = Acquisition()
allo.assign_thermistor_positions()
allo.Power_thermistor()