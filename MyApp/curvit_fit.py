import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit



# Define the second-order step response function with gain
def second_order_step_response(t, zeta, omega_n, K):
    omega_d = omega_n * np.sqrt(1 - zeta**2)  # Damped natural frequency
    return K * (1 - np.exp(-zeta * omega_n * t) * (
        np.cos(omega_d * t) + (zeta * omega_n / omega_d) * np.sin(omega_d * t)
    ))

# Load your data (time and response)
file_path = r"C:\Users\chloe\5mm_bas_validation_copie.xlsx"
df = pd.read_excel(file_path)

# Assuming your data has columns 'Time' and 'Response'
time = df.iloc[:, 10]
#response = df.iloc[:, 4]


thermistance_moyenne = df.iloc[:, :9]
ref = df.iloc[:, 9]
thermistance_moyenne = thermistance_moyenne.apply(lambda col: col -ref, axis=0)  #subtract(ref, axis=0) #
response = thermistance_moyenne.mean(axis=1)
print(response)





# Initial guess for the parameters [zeta, omega_n, K]
initial_guess = [0.83, 0.051, 19.3]# Adjust initial guesses as needed

# Fit the curve
params, covariance = curve_fit(second_order_step_response, time, response, p0=initial_guess)

# Extract the fitted parameters
zeta_fitted, omega_n_fitted, K_fitted = params
print(f"Fitted Damping Ratio (zeta): {zeta_fitted}")
print(f"Fitted Natural Frequency (omega_n): {omega_n_fitted}")
print(f"Fitted Gain (K): {K_fitted}")

# Generate the fitted curve
fitted_response = second_order_step_response(time, zeta_fitted, omega_n_fitted, K_fitted)

# Plot the original data and the fitted curve
plt.figure(figsize=(10, 6))
plt.plot(time, response, 'b-', label='Original Data')
plt.plot(time, fitted_response, 'r--', label='Fitted Curve')
plt.xlabel('Time (s)')
plt.ylabel('Response')
plt.title('Second-Order Step Response Curve Fit with Gain')
plt.legend()
plt.grid()
plt.show()