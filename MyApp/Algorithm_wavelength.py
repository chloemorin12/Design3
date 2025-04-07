import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d

# Charger le fichier Excel
file_path = r'C:/Users/ilitah1/Downloads/Wavelength meter/Absortion_filtres_reel.xlsx'  # chemin du fichier contenant la transmission des filtres
df = pd.read_excel(file_path)  # Charger les données à partir du fichier Excel

filter_names = pd.read_excel(file_path, header=0).iloc[0, 1::2].tolist()

# Renommer les colonnes 
df.columns = ['Wavelength_Filter1', 'Transmission_Filter1', 
              'Wavelength_Filter2', 'Transmission_Filter2', 
              'Wavelength_Filter3', 'Transmission_Filter3',
              'Wavelength_Filter4', 'Transmission_Filter4']

# Convertir les colonnes en valeurs numériques
df['Transmission_Filter1'] = pd.to_numeric(df['Transmission_Filter1'], errors='coerce')
df['Transmission_Filter2'] = pd.to_numeric(df['Transmission_Filter2'], errors='coerce')
df['Transmission_Filter3'] = pd.to_numeric(df['Transmission_Filter3'], errors='coerce')
df['Transmission_Filter4'] = pd.to_numeric(df['Transmission_Filter4'], errors='coerce')

# Convertir la longueur d'onde en valeurs numériques aussi
df['Wavelength_Filter1'] = pd.to_numeric(df['Wavelength_Filter1'], errors='coerce')
df['Wavelength_Filter2'] = pd.to_numeric(df['Wavelength_Filter2'], errors='coerce')
df['Wavelength_Filter3'] = pd.to_numeric(df['Wavelength_Filter3'], errors='coerce')
df['Wavelength_Filter4'] = pd.to_numeric(df['Wavelength_Filter4'], errors='coerce')

df['Absorption_Filter1'] = 100 - df['Transmission_Filter1']
df['Absorption_Filter2'] = 100 - df['Transmission_Filter2']
df['Absorption_Filter3'] = 100 - df['Transmission_Filter3']
df['Absorption_Filter4'] = 100 - df['Transmission_Filter4']




def on_button_click(Powers):
    iterations = 0
    ytols = np.array([2.0, 2.0, 2.0])
        
    while wavelength_calculator(Powers, ytols) == 0 and iterations < 99:
        ytols+=1
        iterations += 1
        if wavelength_calculator(Powers, ytols) != 0 or iterations == 98:
            break
    final_result, incertainty, wl_individuelles = wavelength_calculator(Powers, ytols)
    graphe = plot_graph(wl_individuelles[0], wl_individuelles[1], wl_individuelles[2])
    return final_result, incertainty, graphe, ytols


        
# Fonction pour effectuer les calculs et afficher les résultats
def wavelength_calculator(Powers, ytols):
    try:
        # Lire les pourcentages à partir de l'entrée utilisateur
        puissances = Powers
        pourcentages = [(p / puissances[0]) * 100 for p in puissances]
        print(pourcentages) 
        # Calcul des longueurs d'onde correspondant aux pourcentages approximatifs
        longueurs_donde_trouvees1, longueurs_donde_trouvees2, longueurs_donde_trouvees3 = trouver_longueurs_donde(pourcentages, ytols)
        longueurs_donde_communes = longueur_donde_commune(pourcentages, ytols)
        if longueurs_donde_communes is None:
            return 0
        print(f" Longueur d'onde itération 1 :{np.round(np.mean(longueurs_donde_communes))} nm")
        print("##################################################################################################")
        pourcentages, longueurs_donde_communes, wl_individuelles = corr_pourcentages(puissances, pourcentages, longueurs_donde_communes, ytols)
        pourcentages, longueurs_donde_communes, wl_individuelles = corr_pourcentages(puissances, pourcentages, longueurs_donde_communes, ytols)
        print(f" Longueur d'onde finale {np.round(np.mean(longueurs_donde_communes))} ± {np.round(np.std(longueurs_donde_communes))} nm")
        
        return np.round(np.mean(longueurs_donde_communes)), np.round(np.std(longueurs_donde_communes)), wl_individuelles
        
    except Exception as e:
        print(f"Une exception s'est produite : {e}")

def corr_pourcentages(puissances, pourcentages, longueurs_donde_communes, ytols):
    interpolant = interp1d(df['Wavelength_Filter1'], df['Absorption_Filter1'], kind='linear', fill_value="extrapolate")
    pourcentages[0] = float(interpolant(np.round(np.mean(longueurs_donde_communes))))
    puissance_ref = 100*puissances[0]/pourcentages[0]
    pourcentages = [((p / puissance_ref) * (100)) for p in puissances]
    print(f" Absorption des filtres: {pourcentages} %")
    # Calcul des longueurs d'onde correspondant aux pourcentages corrigés itération 2.
    longueurs_donde_trouvees1, longueurs_donde_trouvees2, longueurs_donde_trouvees3 = trouver_longueurs_donde(pourcentages, ytols)
    longueurs_donde_communes = longueur_donde_commune(pourcentages, ytols)
    print(f" Longueur d'onde itération :{np.round(np.mean(longueurs_donde_communes))} nm")
    wl_individuelles = [longueurs_donde_trouvees1, longueurs_donde_trouvees2, longueurs_donde_trouvees3]
    return pourcentages, longueurs_donde_communes, wl_individuelles


def plot_graph(longueurs_donde_trouvees1, longueurs_donde_trouvees2, longueurs_donde_trouvees3):
    # Tracer les courbes d'absorption
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(df['Wavelength_Filter1'], df['Absorption_Filter1'], label=filter_names[0], color='b')
    ax.plot(df['Wavelength_Filter2'], df['Absorption_Filter2'], label=filter_names[1], color='g')
    ax.plot(df['Wavelength_Filter3'], df['Absorption_Filter3'], label=filter_names[2], color='r')
    ax.plot(df['Wavelength_Filter4'], df['Absorption_Filter4'], label=filter_names[3], color='c')

    # Ajouter des croix aux points trouvés
    if longueurs_donde_trouvees1 is not None:
        ax.scatter(longueurs_donde_trouvees1, np.interp(longueurs_donde_trouvees1, df['Wavelength_Filter2'], df['Absorption_Filter2']),
                   color='g', zorder=5, label="Filtre 2 (Points trouvés)")
    if longueurs_donde_trouvees2 is not None:
        ax.scatter(longueurs_donde_trouvees2, np.interp(longueurs_donde_trouvees2, df['Wavelength_Filter3'], df['Absorption_Filter3']),
                   color='r', zorder=5, label="Filtre 3 (Points trouvés)")
    if longueurs_donde_trouvees3 is not None:
        ax.scatter(longueurs_donde_trouvees3, np.interp(longueurs_donde_trouvees3, df['Wavelength_Filter4'], df['Absorption_Filter4']),
                   color='c', zorder=5, label="Filtre 4 (Points trouvés)")

    # Ajouter des labels et une légende
    ax.set_xlabel('Longueur d\'onde (nm)')
    ax.set_ylabel('Absorption %')
    ax.set_title('Absorption des 4 filtres choisis')
    ax.legend()
    return fig

# Fonction pour trouver les longueurs d'onde correspondant aux pourcentages donnés
def trouver_longueurs_donde(pourcentages, ytols):
    wl = np.linspace(250, 2500, 4500)
    
    # Interpolation des données d'absorption/transmission pour chaque filtre
    interpolation2 = interp1d(df['Wavelength_Filter2'], df['Absorption_Filter2'], kind='linear', fill_value="extrapolate")
    interpolation3 = interp1d(df['Wavelength_Filter3'], df['Absorption_Filter3'], kind='linear', fill_value="extrapolate")
    interpolation4 = interp1d(df['Wavelength_Filter4'], df['Absorption_Filter4'], kind='linear', fill_value="extrapolate")
    
    # Trouver toutes les longueurs d'onde où l'absorption est proche du pourcentage donné
    absorption2_interp = interpolation2(wl)
    absorption3_interp = interpolation3(wl)
    absorption4_interp = interpolation4(wl)
    
    indices2 = np.where(np.isclose(absorption2_interp, pourcentages[1], atol=ytols[0]))[0]
    indices3 = np.where(np.isclose(absorption3_interp, pourcentages[2], atol=ytols[1]))[0]
    indices4 = np.where(np.isclose(absorption4_interp, pourcentages[3], atol=ytols[2]))[0]

    # Filtrer les indices pour chaque filtre
    def filter_indices(indices):
        filtered_indices = []
        previous_wl = None
        for i in indices:
            if previous_wl is None or abs(wl[i] - previous_wl) > 1:  # Seuil de tolérance pour les valeurs proches
                filtered_indices.append(i)
                previous_wl = wl[i]
        return filtered_indices

    filtered_indices2 = filter_indices(indices2)
    filtered_indices3 = filter_indices(indices3)
    filtered_indices4 = filter_indices(indices4)
    
    return wl[filtered_indices2], wl[filtered_indices3], wl[filtered_indices4]

def longueur_donde_commune(pourcentages, ytols, xtol=1):
    longueurs_donde_trouvees1, longueurs_donde_trouvees2, longueurs_donde_trouvees3 = trouver_longueurs_donde(pourcentages, ytols)
    
    # Trouver l'intersection des trois ensembles de longueurs d'onde avec tolérance
    commune = []
    
    # Vérification de chaque longueur d'onde du filtre 1
    for wl1 in longueurs_donde_trouvees1:
        if any(abs(wl1 - wl2) <= xtol for wl2 in longueurs_donde_trouvees2) and \
           any(abs(wl1 - wl3) <= xtol for wl3 in longueurs_donde_trouvees3):
            commune.append(wl1)
    
    if len(commune) > 0:
        return np.array(commune)
    else:
        return None

final_result, incertainty, graphe, tolerances_filtres = on_button_click([80,10,50,50])
print(f"tolérances utilisées sur les puissances entrées en %: {tolerances_filtres}")
plt.show()