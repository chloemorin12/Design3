import matplotlib.pyplot as plt
import nidaqmx
import time
import numpy as np
from itertools import cycle
from matplotlib.animation import FuncAnimation

start_time = time.perf_counter() 
# Define parameters
max_value = 4  # Number of iterations (for 4 different outputs)
delay = 0.1  # Time interval in seconds

# Initialize lists for data storage
liste1, liste2, liste3, liste4 = [], [], [], []
data_lists = [liste1, liste2, liste3, liste4]

# Initialize plot
fig, ax = plt.subplots()
lines = [ax.plot([], [], label=f"Channel {i+1}")[0] for i in range(max_value)]
ax.set_xlim(0, 100)  # Initial x-axis range
ax.set_ylim(0, 5)  # Adjust based on expected voltage range
ax.legend()
ax.set_xlabel("Time Step")
ax.set_ylabel("Voltage (V)")
ax.set_title("Real-Time Voltage Reading")

# Cycling through channels
channel_cycle = cycle(range(max_value))

print("SSSTTTAAARRRTTT")

def set_daq_output(value):
    """Writes a digital output to Dev1/port0/line0:7."""
    with nidaqmx.Task() as do_task:
        do_task.do_channels.add_do_chan("Dev1/port0/line0:7")
        do_task.write(value, auto_start=True)

def read_voltage():
    """Reads voltage from Dev1/ai7."""
    with nidaqmx.Task() as ai_task:
        ai_task.ai_channels.add_ai_voltage_chan("Dev1/ai7")
        return ai_task.read()

def update(frame):
    """Updates the plot and DAQ output."""
    i = next(channel_cycle)  # Get next channel index (0,1,2,3)
    
    # Set DAQ output
    set_daq_output(i)  # Write 'i' as digital output
    time.sleep(delay)  # Wait for circuit response
    
    # Read voltage from DAQ
    voltage = read_voltage()
    data_lists[i].append(voltage)  # Append to the correct list
    
    # Update each line's data
    for j, line in enumerate(lines):
        x_data = list(range(len(data_lists[j])))
        y_data = data_lists[j]
        line.set_xdata(x_data)
        line.set_ydata(y_data)

    # Adjust x-axis dynamically
    max_len = max(len(lst) for lst in data_lists)
    ax.set_xlim(max(0, max_len - 100), max_len)  # Keep last 100 points visible
    ax.relim()
    ax.autoscale_view(True, True, True)

    print(f"Channel {i}: Voltage = {voltage:.3f} V")  # Print DAQ output
    end_time = time.perf_counter()  # End the timer
    elapsed_time = end_time - start_time
    #print(elapsed_time)
    return lines

# Start real-time plotting
ani = FuncAnimation(fig, update, interval=100)  # Update every second

plt.show()