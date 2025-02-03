import math

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

coefficients = (1.40e-3, 2.37e-4, 9.90e-8)
resistance = 10000  # ohms
temperature_kelvin = steinhart_hart_resistance_to_temperature(resistance, coefficients)
print(f"Temperature: {temperature_kelvin} K")

print('hummmmmm', VoltageToResistance(0.779,22000,2.5,43000))