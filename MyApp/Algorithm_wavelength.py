import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Charger le fichier Excel
file_path = r'C:\Users\chloe\Absortion_filtres_reel.xlsx'  # chemin du fichier contenant la transmission des filtres
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


# Créer l'interface graphique avec Tkinter
def create_gui():
    # Créer la fenêtre principale
    window = tk.Tk()
    window.title("Calcul des longueurs d'onde")

    # Ajouter un label
    label = tk.Label(window, text="Sélectionnez les puissances et cliquez sur 'Lancer les calculs'", font=("Arial", 12))
    label.pack(pady=10)

    # Frame pour les entrées de puissances et les cases
    top_frame = tk.Frame(window)
    top_frame.pack(pady=10)

    # Entrée pour les puissances
    label_pourcentages = tk.Label(top_frame, text="Entrez les puissances séparés par des virgules (ex: 500, 55, 499, 250) mW", font=("Arial", 10))
    label_pourcentages.grid(row=0, column=0, padx=10)

    # Champ de texte pour les puissances
    entry_pourcentages = tk.Entry(top_frame, font=("Arial", 10), width=25)
    entry_pourcentages.grid(row=0, column=1, padx=10)

    # Variables pour les trois cases
    case1_value = tk.DoubleVar(value=1.0)  # Valeur initiale
    case2_value = tk.DoubleVar(value=1.0)
    case3_value = tk.DoubleVar(value=1.0)

    # Fonction pour ajuster la valeur d'un pas de 0.5
    def adjust_value(var, increment):
        new_value = var.get() + increment
        if 0 <= new_value <= 100:
            var.set(new_value)

    # Fonction pour créer une case avec flèches
    def create_case(frame, var, label_text, row, col):
        label = tk.Label(frame, text=label_text, font=("Arial", 10))
        label.grid(row=row, column=col, padx=5)

        entry = tk.Entry(frame, textvariable=var, font=("Arial", 10), width=5)
        entry.grid(row=row, column=col+1, padx=5)

        # Flèches pour augmenter et diminuer
        up_button = tk.Button(frame, text="↑", command=lambda: adjust_value(var, 0.5))
        up_button.grid(row=row, column=col+2, padx=5)
        
        down_button = tk.Button(frame, text="↓", command=lambda: adjust_value(var, -0.5))
        down_button.grid(row=row, column=col+3, padx=5)

    # Frame pour les cases avec flèches, à placer à droite de la frame des entrées
    case_frame = tk.Frame(top_frame)
    case_frame.grid(row=0, column=2, padx=10)

    # Créer les trois cases à droite
    create_case(case_frame, case1_value, "Incertitude F2 (%):", 0, 0)
    create_case(case_frame, case2_value, "Incertitude F3 (%):", 1, 0)
    create_case(case_frame, case3_value, "Incertitude F4 (%):", 2, 0)

    def on_button_click():
        iterations = 0
        if iterations == 0:
            case1_value.set(1.0)
            case2_value.set(1.0)
            case3_value.set(1.0)
        
        case1_percentage = case1_value.get()
        case2_percentage = case2_value.get()
        case3_percentage = case3_value.get()

        ytols = np.array([case1_percentage, case2_percentage, case3_percentage])
        
        while wavelength_calculator(ytols) == 0 and iterations < 98:
            ytols+=1
            case1_value.set(ytols[0])
            case2_value.set(ytols[1])
            case3_value.set(ytols[2])
            iterations += 1

        
    # Fonction pour effectuer les calculs et afficher les résultats
    def wavelength_calculator(ytols):
        try:
            # Lire les pourcentages à partir de l'entrée utilisateur
            puissances = list(map(float, entry_pourcentages.get().split(',')))
            pourcentages = [(p / puissances[0]) * 100 for p in puissances]
            print(pourcentages)

            
            # Calcul des longueurs d'onde correspondant aux pourcentages approximatifs
            longueurs_donde_trouvees1, longueurs_donde_trouvees2, longueurs_donde_trouvees3 = trouver_longueurs_donde(pourcentages, ytols)
            longueurs_donde_communes = longueur_donde_commune(pourcentages, ytols)
            if longueurs_donde_communes is None:
                return 0
            print(f" Longueur d'onde itération 1 :{np.round(np.mean(longueurs_donde_communes))} nm")
            print("##################################################################################################")
            interpolant = interp1d(df['Wavelength_Filter1'], df['Absorption_Filter1'], kind='linear', fill_value="extrapolate")
            pourcentages[0] = float(interpolant(np.round(np.mean(longueurs_donde_communes))))
            puissance_ref = 100*puissances[0]/pourcentages[0]
            pourcentages = [((p / puissance_ref) * (100)) for p in puissances]
            print(pourcentages)
            # Calcul des longueurs d'onde correspondant aux pourcentages corrigés.
            longueurs_donde_trouvees1, longueurs_donde_trouvees2, longueurs_donde_trouvees3 = trouver_longueurs_donde(pourcentages, ytols)
            longueurs_donde_communes = longueur_donde_commune(pourcentages, ytols)
            print(f" Longueur d'onde finale {np.round(np.mean(longueurs_donde_communes))} nm")
            
            messagebox.showinfo("Info", "La mesure de longueur d'onde est finie")

            # Mettre à jour le graphique
            plot_graph(longueurs_donde_trouvees1, longueurs_donde_trouvees2, longueurs_donde_trouvees3, canvas_frame)
            result_value_label.config(text=f" {np.round(np.mean(longueurs_donde_communes))} ± {np.round(np.std(longueurs_donde_communes))} nm")
            return np.round(np.mean(longueurs_donde_communes)), np.round(np.std(longueurs_donde_communes))
        
        #except Exception as e:
            #print(f"Une exception s'est produite : {e}")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des pourcentages valides séparés par des virgules.")

    # Bouton pour lancer les calculs
    button = tk.Button(window, text="Lancer les calculs", command=on_button_click, font=("Arial", 12), bg="lightblue")
    button.pack(pady=20)

    # Canvas pour afficher le graphique
    canvas_frame = tk.Frame(window)
    canvas_frame.pack(padx=20, pady=10)
    
    result_frame = tk.Frame(window)
    result_frame.pack(padx=20, pady=10)
    label_result = tk.Label(result_frame, 
                        text="Longueur d'onde mesurée : ", 
                        font=("Arial", 16, "bold"), 
                        fg="#2e4053", 
                        bg="#f0f4f8", 
                        padx=10, pady=10)
    label_result.pack(pady=10)

    result_value_label = tk.Label(result_frame, 
                              text=" --- nm", 
                              font=("Arial", 20, "italic"), 
                              fg="#1e3d59", 
                              bg="#f0f4f8")
    result_value_label.pack(pady=5)

    # Fonction pour initialiser le graphique
    plot_graph(None, None, None, canvas_frame)

    # Lancer l'interface graphique
    window.mainloop()


def plot_graph(longueurs_donde_trouvees1, longueurs_donde_trouvees2, longueurs_donde_trouvees3, canvas_frame):
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

    # Mettre à jour le canvas avec le nouveau graphique
    for widget in canvas_frame.winfo_children():
        widget.destroy()
    
    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()

    toolbar_frame = tk.Frame(canvas_frame)
    toolbar_frame.pack(side="bottom", fill=tk.X)
    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
    toolbar.update()
    toolbar.pack(side="bottom", fill=tk.X)

    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

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

def longueur_donde_commune(pourcentages, ytols, xtol=5):
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

# Lancer l'interface graphique
create_gui()
