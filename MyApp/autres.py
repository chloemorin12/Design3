"""
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

def puissance_calcul(temps, te):


    puissance = []

    #a_0, a_1, a_2 = inverse_transfer_function(0.85, 0.13, 1)
    #b_0, b_1, b_2 = inverse_transfer_function(0.86, 0.12, 1)
    c_0, c_1, c_2 = inverse_transfer_function(19.26677379649072,  0.05307996738598514, 0.8342156871242603)
    #d_0, d_1, d_2 = inverse_transfer_function(0.73, -0.08, -0.52)

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
        P_t = c_0*T_k + c_1*T_k_1 + c_2*T_k_2

            
        puissance.append(P_t)

    puissance = [np.nan, np.nan] + puissance
    return puissance
    
df['Puissance'] = puissance_calcul(thermistance1, t)

output_file = 'thermistance_echellon_with_puissance_dimanche_2.xlsx'
df.to_excel(output_file, index=False)
print(f"Data with power column saved to {output_file}")




# Version / thermistance
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

"""