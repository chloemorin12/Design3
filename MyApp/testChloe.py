import math
import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd



file_path = r"C:\Users\chloe\echellon.xlsx"
df = pd.read_excel(file_path)

thermistance = df.iloc[:, :9]
ref = df.iloc[:, 9]
#t = df.iloc[:, 10]
t = pd.to_numeric(df.iloc[:, 10], errors='coerce')
thermistance = thermistance.apply(lambda col: col -ref, axis=0)


# paramètre de la fonction de transfert (2e ordre)
a_0 = 530084
b_0 = -1060164
c_0 = 0.4
d_0 = 64935

k = 1.965
tau = 15.35

def puissance_calcul(temps, te):


    puissance = []

    # Modifier selon le profil de température
    #moyenne différence temp pour avoir énergie
    for i in range(2, len(temps)):
        E = temps.iloc[i, :9].mean()
        dt = te.iloc[i] - te.iloc[i-1]
        dE = (temps.iloc[i, :9].mean() - temps.iloc[i-1, :9].mean())/dt

        # 2e ordre
        # T_k = temps.iloc[k].mean()
        # T_k_1 = temps.iloc[k-1].mean()
        # T_k_2 = temps.iloc[k-2].mean()
        # Fctn_de_transfert 2e ordre
        #P_t = a_0*T_k + b_0*T_k_1 + c_0*T_k_2 + d_0

        P_t = E/k + (tau/k)*dE
        puissance.append(P_t)

    puissance = [np.nan, np.nan] + puissance
    return puissance
    
df['Puissance'] = puissance_calcul(thermistance, t)

output_file = 'thermistance_echellon_with_puissance.xlsx'
df.to_excel(output_file, index=False)



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


coefficients = (1.40e-3, 2.37e-4, 9.90e-8)
resistance = 10000  # ohms
temperature_kelvin = steinhart_hart_resistance_to_temperature(resistance, coefficients)
print(f"Temperature: {temperature_kelvin} K")
#print('hummmmmm', VoltageToResistance(0.779,22000,2.5,43000))


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
