import matplotlib.pyplot as plt
import nidaqmx
import time
import numpy as np
from itertools import cycle
from matplotlib.animation import FuncAnimation


max_value = 64  
delay = 5 
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
    
voltageliste = []
while True:
    start_time = time.perf_counter()
    set_daq_output(value)
    voltage = read_voltage()
    voltageliste.append(voltage)
    value += 1
    if value >= max_value:
        print(f"Elapsed time: {time.perf_counter() - start_time:.5f} seconds")
        value = 0
        print("voltage", voltageliste)
        time.sleep(delay)