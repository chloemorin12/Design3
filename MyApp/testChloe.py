import math
import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
from matplotlib.animation import FuncAnimation

def VoltageToResistance(voltage, R2, gain, R4):
    Vin = 12
    diffdepot = voltage/(gain*Vin)
    R_eq = R2/(R2+R4)
    Resistance = R2*(R_eq-diffdepot)/(1+diffdepot-R_eq)
    return Resistance
    
    
def steinhart_hart_resistance_to_temperature(resistance, coefficients):
    A, B, C = coefficients
    lnR = math.log(resistance)
    temperature_kelvin = 1 / (A + B * lnR + C * lnR**3)
    return temperature_kelvin

def gaussian_2d(coords, A, x0, y0, sigma_x, sigma_y, offset):
    x, y = coords
    return A * np.exp(-((x - x0)**2 / (2 * sigma_x**2) + (y - y0)**2 / (2 * sigma_y**2))) + offset



file_path = r"C:\Users\chloe\echellon.xlsx"
df = pd.read_excel(file_path)

thermistance = df.iloc[:, :9]
ref = df.iloc[:, 9]
#t = df.iloc[:, 10]
t = pd.to_numeric(df.iloc[:, 10], errors='coerce')
thermistance = thermistance.apply(lambda col: col -ref, axis=0)


# paramètre de la fonction de transfert (2e ordre)
a_0 = 3286
b_0 = -6450
c_0 = 3245

k = 1.965
tau = 15.35

def puissance_calcul(temps, te):


    puissance = []

    # Modifier selon le profil de température
    #moyenne différence temp pour avoir énergie
    for i in range(2, len(temps)):
        #E = temps.iloc[i, :9].mean()
        #dt = te.iloc[i] - te.iloc[i-1]
        #dE = (temps.iloc[i, :9].mean() - temps.iloc[i-1, :9].mean())/dt
        #P_t = E/k + (tau/k)*dE

        # 2e ordre
        T_k = temps.iloc[i].mean()
        T_k_1 = temps.iloc[i-1].mean()
        T_k_2 = temps.iloc[i-2].mean()
        # Fctn_de_transfert 2e ordre
        P_t = a_0*T_k + b_0*T_k_1 + c_0*T_k_2

        
        puissance.append(P_t)

    puissance = [np.nan, np.nan] + puissance
    return puissance
    
df['Puissance'] = puissance_calcul(thermistance, t)

output_file = 'thermistance_echellon_with_puissance.xlsx'
df.to_excel(output_file, index=False)





# Version actuelle pour les données de température au hasard
# Fonction de transfert _ simulation Oli 5mm en bas 


def get_position_v2(array_thermistor):
        
    thermistor_positions = np.array([
        [0, 2], [1, 3], [2, 4], [3, 3], [4, 2],[1, 1], [2, 2], [3, 1],[2, 0]])
    temperature_values = np.array(array_thermistor)
    print(array_thermistor)


    x_data = thermistor_positions[:, 0]
    y_data = thermistor_positions[:, 1]
    z_data = array_thermistor

    # Intial guess sometimes doen't work
    initial_guess = [np.max(z_data), np.mean(x_data), np.mean(y_data), 1, 1, np.min(z_data)]
    params, _ = scipy.optimize.curve_fit(gaussian_2d, (x_data, y_data), z_data, p0=initial_guess)
    A, x_peak, y_peak, sigma_x, sigma_y, offset = params
    print(f"Estimated heat peak at: ({x_peak:.2f}, {y_peak:.2f})")

    x = np.linspace(0, 6, 100)
    y = np.linspace(0, 6, 100)
    x,y = np.meshgrid(x, y)
    z = gaussian_2d((x, y), A, x_peak, y_peak, sigma_x, sigma_y, offset)

    return [z, x_peak, y_peak]

def data_gradient_temperature(liste_temp):
        print(liste_temp)
        result = get_position_v2(liste_temp)
        return result[0]
        

def position(liste_temp):
        return [get_position_v2(liste_temp)[1], get_position_v2(liste_temp)[2]]







# code pour visualiser la position du peak dans le temps



def gaussian_2d(coords, A, x0, y0, sigma_x, sigma_y, offset):
    x, y = coords
    return A * np.exp(
        -((x - x0) ** 2 / (2 * sigma_x**2) + (y - y0) ** 2 / (2 * sigma_y**2))
    ) + offset


thermistor_positions = np.array([
    [0, 0], [0, 1], [0, -1], [1, 0], [-1, 0], [-1, -1], [-1, 1], [1, 1], [1, -1]
])

# Load temperature data from an Excel file
file_path = r"C:\Users\chloe\9_temp.xlsx"
df = pd.read_excel(file_path)
thermistance = df.iloc[::100, :9]  # Extract temperature data for thermistors

# Initialize the plot
fig, ax = plt.subplots()
line, = ax.plot([], [], 'bo-', label='Peak Position')  # Line for peak positions
ax.set_xlim(-2, 2)  # Set X-axis limits
ax.set_ylim(-2, 2)  # Set Y-axis limits
ax.set_xlabel("X Position")
ax.set_ylabel("Y Position")
ax.set_title("Peak Position Over Time")
ax.legend()

# Initialize data storage for peak positions
x_peaks = []
y_peaks = []

# Function to update the plot for each iteration
def update_peak_position(frame):
    global x_peaks, y_peaks

    # Get the temperature data for the current iteration
    if frame < len(thermistance):
        temp_array = thermistance.iloc[frame, :].values
    else:
        return  # Stop updating if the frame exceeds the data length

    # Fit the Gaussian model
    x_data = thermistor_positions[:, 0]
    y_data = thermistor_positions[:, 1]
    z_data = temp_array

    # Normalize z_data to avoid numerical instability
    z_data = (z_data - np.min(z_data)) / (np.max(z_data) - np.min(z_data))

    # Define the initial guess for the Gaussian parameters
    initial_guess = [
        np.max(z_data),  # Amplitude
        x_data[np.argmax(z_data)],  # x-coordinate of the peak
        y_data[np.argmax(z_data)],  # y-coordinate of the peak
        1,  # Standard deviation in x
        1,  # Standard deviation in y
        np.min(z_data)  # Offset
    ]
    
    

    # Add parameter bounds
    bounds = (
        [0, -np.inf, -np.inf, 0, 0, -np.inf],  # Lower bounds
        [np.inf, np.inf, np.inf, np.inf, np.inf, np.inf]  # Upper bounds
    )

    # Fit the Gaussian model
    try:
        params, _ = scipy.optimize.curve_fit(
            gaussian_2d, (x_data, y_data), z_data, p0=initial_guess, bounds=bounds, maxfev=10000
        )
        _, x_peak, y_peak, _, _, _ = params
    except RuntimeError as e:
        print(f"Frame {frame + 1}: Fit failed - {e}")
        return

    # Append the new peak position
    x_peaks.append(x_peak)
    y_peaks.append(y_peak)

    if len(x_peaks) > 50:
        x_peaks = [x_peaks[0]] + x_peaks[-49:]
    if len(y_peaks) > 50:
        y_peaks = [y_peaks[0]] + y_peaks[-49:]


    # Update the line data
    line.set_data(x_peaks, y_peaks)

    # Update the title with the frame number
    ax.set_title(f"Peak Position Over Time (Frame {frame + 1})")

# Use FuncAnimation to update the plot dynamically
ani = FuncAnimation(fig, update_peak_position, frames=len(thermistance), interval=0.0001)

plt.show()