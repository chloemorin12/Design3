import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
import matplotlib, sys
matplotlib.use('TkAgg')
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,  NavigationToolbar2Tk

from tkinter import filedialog, messagebox

# Charger le fichier Excel
file_path = r'Absortion_filtres_reel.xlsx'  # chemin du fichier contenant la transmission des filtres
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


# Fonction pour ajuster la valeur d'un pas de 0.5
def adjust_value(var, increment):
    new_value = var.get() + increment
    if 0 <= new_value <= 100:
        var.set(new_value)


# Fonction pour trouver les longueurs d'onde correspondant aux pourcentages donnés


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



def plot_graph(longueurs_donde_trouvees1, longueurs_donde_trouvees2, longueurs_donde_trouvees3, wl_finale, err, canvas_frame):
        # Tracer les courbes d'absorption
        fig, ax = plt.subplots(figsize=(10, 5))

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
        
        n = 100  
        alphas = np.linspace(1, 0, n)  
        xs = np.linspace(-err, err, n)  

        # Tracé du fond avec dégradé
        for dx, alpha in zip(xs, alphas):
            ax.axvline(wl_finale + dx, ymin=0, ymax=1, color='gray', alpha=alpha)
        
        ax.axvline(wl_finale, label="Longueur d'onde mesurée", color='k')
        # Ajouter des labels et une légende
        ax.set_xlabel('Longueur d\'onde (nm)')
        ax.set_ylabel('Absorption %')
        ax.set_title('Absorption des 4 filtres choisis')
        ax.legend()

        # Mettre à jour le canvas avec le nouveau graphique
        for widget in canvas_frame.winfo_children():
            widget.destroy()
        
        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw()

        toolbar_frame = tk.Frame(canvas_frame)
        toolbar_frame.grid(row=1, column=0, columnspan=3, sticky="ew")
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        toolbar.grid(row=0, column=0, columnspan=3, sticky="ew")

        canvas.get_tk_widget().grid(row=0, column=0, pady=15, padx=5, sticky="nsew")

# Fonction pour effectuer les calculs et afficher les résultats
def wavelength_calculator(Powers ,ytols, canvas_frame, label):
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
        if longueurs_donde_communes is None:
            return 0
        print("rendu")
        #pourcentages, longueurs_donde_communes, wl_individuelles = corr_pourcentages(puissances, pourcentages, longueurs_donde_communes, ytols)
        wl_finale, erreur = np.round(np.mean(longueurs_donde_communes)), np.round(np.std(longueurs_donde_communes))
        print(f" Longueur d'onde finale {wl_finale} ± {erreur} nm")

        # Mettre à jour le graphique
        plot_graph(longueurs_donde_trouvees1, longueurs_donde_trouvees2, longueurs_donde_trouvees3, wl_finale, erreur, canvas_frame)
        label.config(text=f" {wl_finale} ± {erreur} nm")
        return wl_finale, erreur, wl_individuelles
    
    #except Exception as e:
        #print(f"Une exception s'est produite : {e}")
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer des pourcentages valides séparés par des virgules.")

def corr_pourcentages(puissances, pourcentages, longueurs_donde_communes, ytols):
    interpolant = interp1d(df['Wavelength_Filter1'], df['Absorption_Filter1'], kind='linear', fill_value="extrapolate")
    pourcentages[0] = float(interpolant(np.round(np.mean(longueurs_donde_communes))))
    puissance_ref = 100*puissances[0]/pourcentages[0]
    pourcentages = [((p / puissance_ref) * (100)) for p in puissances]
    print(f" Absorption des filtres: {pourcentages} %")
    # Calcul des longueurs d'onde correspondant aux pourcentages corrigés itération 2.
    longueurs_donde_trouvees1, longueurs_donde_trouvees2, longueurs_donde_trouvees3 = trouver_longueurs_donde(pourcentages, ytols)
    longueurs_donde_communes = longueur_donde_commune(pourcentages, ytols)
    wl_individuelles = [longueurs_donde_trouvees1, longueurs_donde_trouvees2, longueurs_donde_trouvees3]
    if longueurs_donde_communes is None:
            return pourcentages, None, wl_individuelles
    print(f" Longueur d'onde itération :{np.round(np.mean(longueurs_donde_communes))} nm")
    
    return pourcentages, longueurs_donde_communes, wl_individuelles

file_path_s_texturée = r'absorption_laserax.xlsx'  # chemin du fichier contenant l'absorption de la surface texturée'
df2 = pd.read_excel(file_path_s_texturée)  # Charger les données à partir du fichier Excel
surface_names = pd.read_excel(file_path_s_texturée, header=0).iloc[0, 1::2].tolist()

# Renommer les colonnes 
df2.columns = ['Wavelength_s_texturée', 'Absorption_s_texturée']
df2['Absorption_s_texturée'] = pd.to_numeric(df2['Absorption_s_texturée'], errors='coerce')
df2['Wavelength_s_texturée'] = pd.to_numeric(df2['Wavelength_s_texturée'], errors='coerce')

def corr_spectrale(power, wl):
    absorption_interp = np.interp(wl, df2['Wavelength_s_texturée'], df2['Absorption_s_texturée'])
    power_corr = power*100/absorption_interp
    return power_corr