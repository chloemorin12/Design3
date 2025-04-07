import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import pandas as pd 
import math

def steinhart_hart(R, A, B, C):
    return A + B * np.log(R) + C * (np.log(R))**3

R_data = np.array([10000, 5000, 2000, 1000, 500])
T_data_C = np.array([25, 35, 50, 70, 100])
T_data_K = T_data_C + 273.15
Y_data = 1 / T_data_K   

file_path = r"c:\Users\AlexisGiroux\OneDrive - Laserax inc\Bureau\Groupe 1 - 4680.xlsx"
for sheet_name in pd.ExcelFile(file_path).sheet_names:
    data = pd.read_excel(file_path)
    data = np.array(data).T
    temperature = data[0]
    resistance = data[1]
    popt, _ = curve_fit(steinhart_hart, R_data, Y_data)
    print(f"Fitted coefficients: A={popt[0]}, B={popt[1]}, C={popt[2]}")
    R_fit = np.linspace(min(R_data), max(R_data), 100)
    T_fit = 1 / steinhart_hart(R_fit, *popt)
    T_fit_C = T_fit - 273.15
    plt.scatter(T_data_C, R_data, color='blue', label="Measured Data")
    plt.plot(T_fit_C, R_fit, color='red', label="Fitted Steinhart-Hart Curve")
    plt.yscale("log")
    plt.ylabel("Resistance (Ω)")
    plt.xlabel("Temperature (°C)")
    plt.title("Steinhart-Hart Curve Fitting")
    plt.legend()
    plt.grid()
    plt.show()
    
        
