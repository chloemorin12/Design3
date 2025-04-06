import matplotlib.pyplot as plt
import nidaqmx
import time
import numpy as np
from itertools import cycle
from matplotlib.animation import FuncAnimation

voltage_data = np.full((256, 1), np.nan)
voltage_iteration = np.full((256, 1), np.nan)
max_value = 255 
delay = 0.01
value = 0

print("SSSTTTAAARRRTTT")

def set_daq_output(value):
    """Writes a digital output to Dev1/port0/line0:7."""
    with nidaqmx.Task() as do_task:
        do_task.do_channels.add_do_chan("Dev1/port0/line0:7")
        do_task.write(value, auto_start=True)
        #print(f"Output set to {value}")

def read_voltage():
    """Reads voltage from Dev1/ai7."""
    with nidaqmx.Task() as ai_task:
        ai_task.ai_channels.add_ai_voltage_chan("Dev1/ai7")
        return ai_task.read()
    
listerandom = []
valeur112 = []
valeur113 = []
valeur3 = []
valeur39 = []
valeur115 = []
listevoltage = []
while True:
    binary_str = format(value, '08b')
    if binary_str[-4] == '1':
        value = value+8
        binary_str = format(value, '08b')
    if binary_str[-8] == '1':
        value = 0
        print(len(listerandom))
        

    set_daq_output(value)  
    start_time = time.perf_counter()
    
        
    '''voltage = read_voltage()
    voltage_iteration[value] = voltage
    voltage = read_voltage()
    voltage_iteration[value] = voltage
    voltage = read_voltage()
    voltage_iteration[value] = voltage'''
    
    if value == 113:
        valeur113.append(voltage)
    if value == 112:
        valeur112.append(voltage)
    if value == 3:
        valeur3.append(voltage)
    if value == 39:
        valeur39.append(voltage)        
    if value == 115:
        valeur115.append(voltage)
        
    time.sleep(delay)
    listerandom.append(value)
    print(value)
    print(f"Voltage: {voltage:.5f} V")
    #print()
    value += 1
    if value > max_value:
        value = 0
        