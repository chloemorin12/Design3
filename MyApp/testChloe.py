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


# Fonction de transfert invers 2e ordre 

def inverse_transfer_function( Gain, w_n, z):
    T1 = (2*z)/w_n
    T2 = 1/w_n**2
    G = Gain

    Coef1 = (1 + T1/0.15 + T2/(0.15**2))/ G
    Coef2 = (T1/0.15 - 2*T2/(0.15**2))/G
    Coef3 = (T2/(0.15**2 * G))

    return [Coef1, Coef2, Coef3]
    



file_path = r"C:\Users\chloe\5mm_bas_validation_copie.xlsx"
df = pd.read_excel(file_path)



thermistance1 = df.iloc[:, :9]
ref = df.iloc[:, 9]
t = pd.to_numeric(df.iloc[:, 10], errors='coerce')
thermistance1 = thermistance1.apply(lambda col: col -ref, axis=0)  #subtract(ref, axis=0) #






# paramètre de la fonction de transfert (2e ordre)

def puissance_calcul( data, ref):

    inital_data_t_1 = [0]*61
    inital_data_t_2 = [0]*61


    # changer pour si la liste de data a au moins 2 ou trois colonne, prendre les colonne (-2), (-3)


    ref = [ref[1], ref[2]]
    ref = np.mean(ref)
      
    
    data = data[~np.isnan(data).any(axis=1)] # tension values 
    data = data.T 

    if data.shape[0] == 4:
        inital_data_t_1 = data[-2]
        inital_data_t_1 = inital_data_t_1 - ref
    if data.shape[0] == 5:
        inital_data_t_1 = data[-2]
        inital_data_t_1 = inital_data_t_1 - ref
        inital_data_t_2 = data[-3]
        inital_data_t_2 = inital_data_t_2 - ref

    print('t1', inital_data_t_1)
    print('t2', inital_data_t_2)

         

    data = np.array(data[-1]) - ref

    
    puissance = []

    #a_0, a_1, a_2 = inverse_transfer_function(0.85, 0.13, 1)
    #b_0, b_1, b_2 = inverse_transfer_function(0.86, 0.12, 1)
    c_0, c_1, c_2 = inverse_transfer_function(19.26677379649072,  0.05307996738598514, 0.8342156871242603)
    #d_0, d_1, d_2 = inverse_transfer_function(0.73, -0.08, -0.52)

    # Modifier selon le profil de température
    #moyenne différence temp pour avoir énergie
    #for i in range(2, len(data)):
        

        #E = temps.iloc[i, :9].mean()
        #dt = te.iloc[i] - te.iloc[i-1]
        #dE = (temps.iloc[i, :9].mean() - temps.iloc[i-1, :9].mean())/dt
        #P_t = E/k + (tau/k)*dE

            # 2e ordre
    T_k = np.mean(data)
    T_k_1 = np.mean(inital_data_t_1)
    T_k_2 = np.mean(inital_data_t_2)
        # Fctn_de_transfert 2e ordre
    P_t = c_0*T_k + c_1*T_k_1 + c_2*T_k_2
    print(P_t)
            

    return P_t


#Pour sortir les données
'''
from AcquisitionClass import Acquisition
allo = Acquisition()
allo.assign_thermistor_positions()
d = allo.Power_thermistor()
#print(d[0])
test = puissance_calcul( d[0], d[1])







#df['Puissance'] 
output_file = 'thermistance_echellon_with_puissance_dimanche_2.xlsx'
df.to_excel(output_file, index=False)
print(f"Data with power column saved to {output_file}")
'''






'''# Version / thermistance
thermistance = df.iloc[:, :1]
ref = df.iloc[:, 2]
t = pd.to_numeric(df.iloc[:, 3], errors='coerce')
thermistance = thermistance.apply(lambda col: col -ref, axis=0)


# paramètre de la fonction de transfert (2e ordre)

def puissance_calcul(temps, te):


    puissance = []

    a_0, a_1, a_2 = inverse_transfer_function(0.85, 0.13, 1)
    b_0, b_1, b_2 = inverse_transfer_function(0.86, 0.12, 1)
    c_0, c_1, c_2 = inverse_transfer_function(2.14, -0.08, -0.52)
    d_0, d_1, d_2 = inverse_transfer_function(0.73, -0.08, -0.52)
    
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

output_file = 'thermistance_echellon_with_puissance_dim.xlsx'
df.to_excel(output_file, index=False)
print(f"Data with power column saved to {output_file}")
'''






# Version actuelle pour les données de température au hasard
# Fonction de transfert _ simulation Oli 5mm en bas 


def get_position_v2(array_thermistor):
    ''' 
    thermistor_positions = np.array([
        [0, 2], [1, 3], [2, 4], [3, 3], [4, 2],[1, 1], [2, 2], [3, 1],[2, 0]])
    temperature_values = np.array(array_thermistor)
    print(array_thermistor)


    x_data = thermistor_positions[:, 0]
    y_data = thermistor_positions[:, 1]
    z_data = array_thermistor

    # Intial guess sometimes doen't work
    initial_guess = [np.max(z_data), np.mean(x_data), np.mean(y_data), 1, 1, np.min(z_data)]
    '''

    params = array_thermistor #, _ = scipy.optimize.curve_fit(gaussian_2d, (x_data, y_data), z_data, p0=initial_guess)
    print(params)
    A, x_peak, y_peak, sigma_x, sigma_y, offset = params
    print(f"Estimated heat peak at: ({x_peak:.2f}, {y_peak:.2f})")

    x = np.linspace(0, 6, 100)
    y = np.linspace(0, 6, 100)
    x,y = np.meshgrid(x, y)
    z = gaussian_2d((x, y), A, x_peak, y_peak, sigma_x, sigma_y, offset)
    return [z, x_peak, y_peak]

def data_gradient_temperature(liste_temp):
        result = get_position_v2(liste_temp)
        return  result[0]
        
def position(liste_temp):
        return [get_position_v2(liste_temp)[1], get_position_v2(liste_temp)[2]]




