import matplotlib.pyplot as plt
import nidaqmx
import time
import numpy as np

# Initialize the plot
plt.ion()
fig, ax = plt.subplots()
line, = ax.plot([], [], 'b-', linewidth=1)
ax.set_xlabel("Time")
ax.set_ylabel("Voltage (V)")
ax.set_title("Real-Time Voltage Reading")

liste = []
mean_values = []
while True:
    delay = 0.001  # Time interval in seconds
    max_value = 61
    value = 0
    with nidaqmx.Task() as do_task:
        do_task.do_channels.add_do_chan("Dev1/port0/line0:7")
        for value in range(max_value):
            print(value)
            do_task.write(value, auto_start=True)

    with nidaqmx.Task() as ai_task:
        ai_task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
        
        #while True:
        voltage = ai_task.read()
        liste.append(voltage)
        
        # Calculate the mean of the last 50 data points
        if len(liste) >= 10:
            mean_value = np.mean(liste[-10:])
        else:
            mean_value = np.mean(liste)
        
        mean_values.append(mean_value)
        
        line.set_xdata(range(len(mean_values)))
        line.set_ydata(mean_values)
        ax.set_xlim(0, len(mean_values) - 1)
        ax.relim()
        ax.autoscale_view()
        print(mean_value)
        plt.draw()
        plt.pause(0.1)
        time.sleep(0.1)