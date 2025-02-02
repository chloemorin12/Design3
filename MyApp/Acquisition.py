import nidaqmx
import time
import matplotlib.pyplot as plt
from statistics import stdev

# Initialize the plot
plt.ion()
fig, ax = plt.subplots()
line, = ax.plot([], [], 'b-', linewidth=1) 
ax.set_xlabel("Time")
ax.set_ylabel("Voltage (V)")
ax.set_title("Real-Time Voltage Reading")

liste = []

with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan("Dev1/ai0")

    while True:
        voltage = task.read()
        liste.append(voltage)

        line.set_xdata(range(len(liste)))
        line.set_ydata(liste)
        ax.set_xlim(0, len(liste) - 1)
        ax.relim()
        ax.autoscale_view()

        plt.draw()
        plt.pause(0.1)
        time.sleep(0.1)