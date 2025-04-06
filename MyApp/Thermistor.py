import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import pandas as pd 
import math

def steinhart_hart(R, A, B, C):
    return A + B * np.log(R) + C * (np.log(R))**3
color = 'red'

file_path = r"c:\Users\AlexisGiroux\Downloads\Données thermistances.xlsx"
for sheet_name in pd.ExcelFile(file_path).sheet_names:
    if sheet_name == 'Thermistance 9':
        color = 'green'
    data = pd.read_excel(file_path, sheet_name=sheet_name)
    data = np.array(data).T
    T_data_C = data[0]
    R_data = data[1]*1000
    T_data_K = T_data_C + 273.15
    for i in range(len(T_data_C)):
        if int(T_data_C[i]) == 45:
            T50 = 45 + 273.15
            R50 = R_data[i]
        if int(T_data_C[i]) == 50:
            T70 = 50 + 273.15
            R70 = R_data[i]
    B_Value = math.log(R70/R50) / (1/T70 - 1/T50)
    print(f"B Value: {round(B_Value,2)}")
    Y_data = 1 / T_data_K
    popt, _ = curve_fit(steinhart_hart, R_data, Y_data)
    print(f"Fitted coefficients: A={round(popt[0],6)}, B={round(popt[1],6)}, C={round(popt[2],8)}")
    R_fit = np.linspace(min(R_data), max(R_data), 100)
    T_fit = 1 / steinhart_hart(R_fit, *popt)
    T_fit_C = T_fit - 273.15
    plt.scatter(T_data_C, R_data, color='blue', label="Measured Data", s=5)
    plt.plot(T_fit_C, R_fit, color=color, label="Fitted Steinhart-Hart Curve")
    print('T @ 10kΩ: ',round(1/steinhart_hart(10000, A=popt[0], B=popt[1], C=popt[2])-273.15,2))   
    plt.yscale("log")
    plt.ylabel("Resistance (Ω)")
    plt.xlabel("Temperature (°C)")
    plt.title("Steinhart-Hart Curve Fitting")
    #plt.legend()
    plt.grid()
    print()
plt.show()
    
        
