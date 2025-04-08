import matplotlib.pyplot as plt
import nidaqmx
import time
import numpy as np
from nidaqmx.constants import AcquisitionType

voltage_data = np.full((256, 1), np.nan)
thermistor = np.full((256, 2), np.nan)
max_value = 255 
delay = 0.001
value = 0

duration = 0.05 #seconds
sample_rate = 1000
samples_to_read = int(sample_rate * duration)

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

def assign_thermistor_positions():
    for i in range(len(real_thermistor_positions)):
        position = liste_thermistor_values[i]
        thermistor[position] = real_thermistor_positions[i]
    return thermistor

def set_daq_output(value):
    with nidaqmx.Task() as do_task:
        do_task.do_channels.add_do_chan("Dev1/port0/line0:7")
        do_task.write(value, auto_start=True)

def read_voltage():
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan("Dev1/ai7")
        task.timing.cfg_samp_clk_timing(
            rate=sample_rate,
            sample_mode=AcquisitionType.FINITE,
            samps_per_chan=samples_to_read)
        data = task.read(number_of_samples_per_channel=samples_to_read)
        return(np.mean(data))

thermistor = assign_thermistor_positions()

start_time = time.perf_counter()
for i in range(0, 256):
    binary_str = format(value, '08b')
    if binary_str[-4] == '1':
        value = value+8
        binary_str = format(value, '08b')
    if binary_str[-8] == '1':
        #print(voltage_data)
        value = 0
        data = np.hstack((thermistor,voltage_data))
        data = data[~np.isnan(data).any(axis=1)]
        stop_time = time.perf_counter()
        print('temps: ', stop_time - start_time)
        '''x = data[:, 0]
        y = data[:, 1]
        z = data[:, 2]
        plt.figure(figsize=(6, 5))
        sc = plt.scatter(x, y, c=z, cmap='coolwarm', s=100, edgecolor='k')  # You can change 'viridis' to other colormaps
        plt.colorbar(sc, label='Z value (color)')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('2D Scatter with Colormap from Z')
        plt.grid(True)
        plt.show()'''
        break
    
    set_daq_output(value)
    voltage = read_voltage()
    voltage_data[value] = voltage

    time.sleep(delay)
    #print(value)
    #print(f"Voltage: {voltage:.5f} V")
    value += 1
stop_time = time.perf_counter()        
#print('temps: ', stop_time - start_time) 