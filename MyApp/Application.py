
from tkinter import filedialog, messagebox
import random
from testChloe import data_gradient_temperature, position, puissance_calcul
import matplotlib.pyplot as plt
import matplotlib, sys
matplotlib.use('TkAgg')
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from datetime import datetime
from tkinter.messagebox import askyesnocancel
import tkinter as tk
from tkinter import ttk
from app import App
from bindable import Bindable
from base import Base
from AcquisitionClass import Acquisition 
import threading
import time
from Algorithm_wavelength import trouver_longueurs_donde, longueur_donde_commune, plot_graph, adjust_value, wavelength_calculator, corr_spectrale
import numpy as np
import nidaqmx
from nidaqmx.errors import DaqError
import csv
from PIL import Image, ImageTk
from nidaqmx.errors import DaqReadError


class PowerMeterApp(App):
    def __init__(self):
        App.__init__(self)
        self.root.option_add("*Font", "Segoe 10")
        self.root.configure(bg="#f0f4f8")
        self.device = PowerMeterDevice()
        self.is_refreshing = False
        self.initialise = False

        self.ct = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.historique_puissance = []
        self.historique_temps_mesure = []
        self.historique_position_x = []
        self.historique_position_y = []
        self.wl = self.device.wavelength
        self.temps1 = 0
        self.temps2 = 0
        self.current_tab_index = 0

        
        
        self.root.title("Puissance-mètre")

        #self.root.attributes("-fullscreen", True)

        #self.root.bind("<Escape>", self.exit_fullscreen)


        # Disposition des éléments dans les onglets
        self.root.grid_rowconfigure(0, weight=1)  
        self.root.grid_columnconfigure(0, weight=1)  
        #self.root.attributes("-fullscreen", True)  # Mettre l'application en plein écran
        self.root.state('zoomed')  # Mettre l'application en plein écran (Windows)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)  



        # Création des onglets
        self.tab_puissance = tk.Frame(self.notebook)
        self.notebook.add(self.tab_puissance, text="Puissance")
        self.tab_puissance.grid_rowconfigure(0, weight=1) 
        self.tab_puissance.grid_columnconfigure(0, weight=1)  

        self.tab_longeur_onde = tk.Frame(self.notebook)
        self.notebook.add(self.tab_longeur_onde, text="Longueur d'onde")
        self.tab_longeur_onde.grid_rowconfigure(0, weight=1)   
        self.tab_longeur_onde.grid_columnconfigure(0, weight=1)  





        # Disposition sur l'onglet longueur d'onde
        self.top_frame = tk.Frame(self.tab_longeur_onde)
        self.top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        main_frame = tk.Frame(self.tab_longeur_onde)
        main_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="n")



        # Variables pour les trois cases d'incertitudes
        case1_value = tk.DoubleVar(value=1.0)  # Valeur initiale
        case2_value = tk.DoubleVar(value=1.0)
        case3_value = tk.DoubleVar(value=1.0)
        


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
        case_frame = tk.Frame(main_frame)
        case_frame.grid(row=2, column=2, padx=20)

        # Créer les trois cases à droite
        create_case(case_frame, case1_value, "Incertitude F2 (%):", 0, 0)
        create_case(case_frame, case2_value, "Incertitude F3 (%):", 1, 0)
        create_case(case_frame, case3_value, "Incertitude F4 (%):", 2, 0)

        

        

        #Aquisition initiale pour la mesure de la longueur d'onde
        self.ST = Acquisition()
        self.calibration = [20,20, 20, 20] # liste de calibration pour les températures des filtres

        # Permet d'acquisitionner pour obtenir les valeur de températures de termistance des filtres
        def change_calib():
            self.calibration = self.ST.Wavelength_thermistor(self.device.dev)   # Va chercher les valeurs de calibration
            messagebox.showinfo("Info", "Calibration effectuée avec succès")
            #print(self.calibration)


        
        # Fonction qui retourne la différence enre les puissances mesurées et les puissances de calibraiton
        def wl_power(calib, T_now):
            delta = abs(np.array(T_now) - np.array(calib))
            Powers = delta /np.max(delta) * 100
            return Powers

        

        # Fonction pour calculer la longueur d'onde lorsque l'utilisateur clique sur le bouton 'Cliquez sur 'Lancer les calculs'
        def on_button_click():

            # Créer une fenêtre modale pour afficher le message "Calcul en cours..."
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Calcul en cours")

            progress_window.resizable(False, False)
            progress_window.transient(self.root)  # Associer la fenêtre modale à la fenêtre principale
            progress_window.grab_set()  # Rendre la fenêtre modale
            window_width = 300
            window_height = 100
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            position_x = (screen_width // 2) - (window_width // 2)
            position_y = (screen_height // 2) - (window_height // 2)
            progress_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")


            # Ajouter un label pour afficher le message
            progress_label = tk.Label(progress_window, text="Calcul de la longueur d'onde en cours...", font=("Arial", 12))
            progress_label.pack(pady=20)

            # Forcer l'affichage de la fenêtre avant de commencer le calcul
            self.root.update()



            T_now = self.ST.Wavelength_thermistor(self.device.dev)
            Powers = wl_power(self.calibration, T_now)
            #print(Powers)
            iterations = 0
            ytols = np.array([2.0, 2.0, 2.0])
                
            while wavelength_calculator(Powers, ytols, canvas_frame, result_value_label) == 0 and iterations < 99:
                ytols+=1
                iterations += 1
                #messagebox.showinfo("Info", "Calcul de la longueur d'onde en cours...")
                self.root.update()
                if wavelength_calculator(Powers, ytols, canvas_frame, result_value_label) != 0 or iterations == 98:
                    break
            progress_window.destroy()  # Fermer la fenêtre modale après le calcul
            case1_value.set(ytols[0])
            case2_value.set(ytols[1])
            case3_value.set(ytols[2])
            if wavelength_calculator(Powers, ytols, canvas_frame, result_value_label) == 0:
                messagebox.showinfo("Info", "Aucune longueur d'onde ne correspond aux puissances entrées")
                return 0, 0
            final_result, incertainty, wl_individuelles = wavelength_calculator(Powers, ytols, canvas_frame, result_value_label) 
            graphe = plot_graph(wl_individuelles[0], wl_individuelles[1], wl_individuelles[2], final_result, incertainty, canvas_frame)
            messagebox.showinfo("Info", "La mesure de longueur d'onde est finie")

            
            # Permet de récupérer la longueur d'onde mesurée et de l'afficher dans le champ d'entrée et de l'associer à la valeur de la longueur d'onde de l'appareil
            self.wavelength_entry.config(state='normal')  
            self.wavelength_entry.delete(0, tk.END)
            self.wavelength_entry.insert(0, str(final_result))  
            self.wl = final_result
            self.device.wavelength = final_result 
            self.wavelength_entry.config(state='disabled') 


            return final_result, incertainty, graphe, ytols  # retourner les informations voulues, dont la longueur d'onde et les incertitudes
    

        



















        # Pour le moteur
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        

        # Bouton pour lancer les calculs
        # Ajouter instructions au besoin
        self.label = tk.Label(self.top_frame, text="2. Cliquez sur 'Lancer les calculs'", font=("Arial", 12))
        self.label.grid(row=1, column=0, columnspan=1, padx=10, pady=10)
        self.button = tk.Button(self.top_frame, text="Lancer les calculs", command=on_button_click, font=("Arial", 12), bg="lightblue")
        self.button.grid(row=1, column=1, padx=10, pady=10)

        # Bouton 'Calibration' activer par l'utilisateur pour calibrer lorsque le laser est éteint
        self.label_1 = tk.Label(self.top_frame, text="1. Calibrer avant le démarrage du laser", font=("Arial", 12))
        self.label_1.grid(row=0, column=0, columnspan=1, padx=10, pady=10)
        self.calib_button = tk.Button(self.top_frame, text="Calibration", command=change_calib, font=("Arial", 12), bg="lightblue")
        self.calib_button.grid(row=0, column=1, padx=10, pady=10)

        # Canvas pour afficher le graphique
        canvas_frame = tk.Frame(self.tab_longeur_onde)
        canvas_frame.grid(row=1, column=0, columnspan=6, padx=10, pady=10, sticky="n")
        
        #result_frame = tk.Frame(self.tab_longeur_onde)
        #result_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        label_result = tk.Label(main_frame, 
                            text="Longueur d'onde mesurée : ", 
                            font=("Arial", 16, "bold"), 
                            fg="#2e4053", 
                            bg="#f0f4f8", 
                            padx=10, pady=10)
        label_result.grid(row=2, column=0, padx=10, pady=5)

        result_value_label = tk.Label(main_frame, 
                                text=" --- nm", 
                                font=("Arial", 20, "italic"), 
                                fg="#1e3d59", 
                                bg="#f0f4f8")
        result_value_label.grid(row=2, column=1, padx=10, pady=5)

        # Fonction pour initialiser le graphique
        plot_graph(None, None, None, 250, 0, canvas_frame)




        self.Évènements = ['', '', '',''] # Liste des communications à enregistrer dans un fichier

        self.actions_frame = tk.LabelFrame(self.tab_puissance, text="Actions", bg="#f0f4f8", fg="#2c3e50",
                                            font=("Segoe UI", 10, "bold"), bd=1, relief="solid")
        self.actions_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        button_cfg = dict(font=("Segoe UI", 10, "bold"), relief="groove", padx=10, pady=5, highlightthickness=1, bd=2, activebackground="#7f8c8d")

        self.start_button = tk.Button(self.actions_frame, text="Démarrer", command=self.click_start,
                                      bg="#95a5a6", fg="white", **button_cfg)
        self.start_button.grid(row=0, column=1, pady=15, padx=5, sticky="w")

        self.misea0 = tk.Button(self.actions_frame, text="Mise à zéro", command=self.click_clear,
                                bg="#95a5a6", fg="white", **button_cfg)
        self.misea0.grid(row=0, column=2, pady=15, padx=5)

        self.paramètre = tk.Button(self.actions_frame, text="Paramètres", command=self.click_chose_parametres,
                                   bg="#95a5a6", fg="white", **button_cfg)
        self.paramètre.grid(row=0, column=3, pady=15, padx=5)



        self.save_button = tk.Button(self.actions_frame, text="Enregistrer les données", command=self.click_save,
                                     bg="#95a5a6", fg="white", **button_cfg)
        self.save_button.grid(row=0, column=5, padx=10, pady=10)

        self.status_light = tk.Canvas(self.actions_frame, width=24, height=24, bg='white', highlightthickness=0)
        self.light_id = self.status_light.create_oval(4, 4, 20, 20, fill="red", outline="gray")
        self.status_light.grid(row=0, column=0, padx=10, pady=15)
        

        #self.connexion = tk.Button(self.actions_frame, text="Connexion", bg="#95a5a6", fg="white", **button_cfg)
        #self.connexion.grid(row=0, column=4, pady=15, padx=5)


        # Liste options
        self.pratique_connect = self.device.get_firmware_from_device()
        print(self.pratique_connect)


        # Create the Combobox
        self.combobox_1 = ttk.Combobox(self.actions_frame, values=self.pratique_connect, state="readonly", font=("Segoe UI", 10))
        self.combobox_1.grid(row=0, column=10, pady=15, padx=5, sticky="w")

        # Set a default value (optional)
        self.combobox_1.set("Sélectionnez une option")

        # Bind an event to handle selection changes
        self.combobox_1.bind("<<ComboboxSelected>>", self.on_combobox_select)


        try:
                pass
        except DaqReadError as e:
                messagebox.showerror("Erreur DAQ", f"Erreur de lecture DAQ : {str(e)}\nVeuillez vérifier la connexion USB ou le câble.")
            

        # --- Graphique de puissance ---
        self.graphs_frame = tk.Frame(self.tab_puissance, bg="#f0f4f8")
        self.graphs_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        self.power_frame = tk.LabelFrame(self.graphs_frame, text="Puissance en temps réel",
                                         bg="#f0f4f8", fg="#2c3e50", font=("Segoe UI", 10, "bold"), bd=1, relief="solid")
        self.power_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.plot_puissance = plt.figure(figsize=(7, 5))
        self.ax_puissance = self.plot_puissance.add_subplot(111)
        self.ax_puissance.set_ylim(0, 11)
        self.ax_puissance.set_ylabel('Puissance [W]')
        self.ax_puissance.set_xlabel('Tic temporel')
        self.line_puissance, = self.ax_puissance.plot([], [], color='tab:blue', linewidth=2)

        self.ax_puissance.set_facecolor("#ffffff")
        self.ax_puissance.grid(True, linestyle="--", alpha=0.3)
        self.ax_puissance.set_title("Historique de Puissance", fontsize=11, color="#2c3e50")
        self.ax_puissance.tick_params(colors="#2c3e50")
        self.ax_puissance.spines['top'].set_visible(False)
        self.ax_puissance.spines['right'].set_visible(False)

        self.canvas = FigureCanvasTkAgg(self.plot_puissance, master=self.power_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, pady=15, padx=5, sticky="nsew")

        self.toolbar_frame_puissance = tk.Frame(self.power_frame, bg="#f0f4f8")
        self.toolbar_frame_puissance.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.toolbar_puissance = NavigationToolbar2Tk(self.canvas, self.toolbar_frame_puissance)
        self.toolbar_puissance.update()
        self.toolbar_puissance.grid(row=0, column=0, sticky="ew")


        # Graphique de position
        self.pos_frame = tk.LabelFrame(self.graphs_frame, text="Position en temps réel",
                                       bg="#f0f4f8", fg="#2c3e50", font=("Segoe UI", 10, "bold"), bd=1, relief="solid")
        self.pos_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.fig = plt.figure(figsize=(7, 5))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#ffffff")
        self.ax.grid(True, linestyle="--", alpha=0.3)
        self.ax.set_title("Position du laser", fontsize=11)
        self.ax.set_xlim(-15, 15)
        self.ax.set_ylim(-15, 15)
        self.ax.set_aspect('equal', adjustable='box')
        self.ax.set_xlabel("Position X [mm]")
        self.ax.set_ylabel("Position Y [mm]")
        self.pos_canvas = FigureCanvasTkAgg(self.fig, master=self.pos_frame)
        self.pos_canvas_widget = self.pos_canvas.get_tk_widget()
        self.pos_canvas_widget.grid(row=0, column=0, pady=15, padx=5, sticky="nsew")
        
        sigma = 2.5
        self.outer_circle = patches.Circle((0, 0), radius=12.5, fill=False, edgecolor='black', linewidth=2)
        self.ax.add_patch(self.outer_circle)

        # Add red circle (will move and change size)
        self.red_circle = patches.Circle((0, 0), radius=sigma, fill=True, facecolor='red', edgecolor='black', linewidth=1)
        self.ax.add_patch(self.red_circle)

        # Add black x (initial dummy position)
        self.cross_marker, = self.ax.plot([0], [0], 'kx', markersize=10, markeredgewidth=3)



        # Ajouter une image dans l'onglet "Puissance"
        #self.image_frame = tk.Frame(self.graphs_frame, bg="#f0f4f8")
        #self.image_frame.grid(row=4, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        # Charger l'image PNG
        try:
            image = Image.open("Logo_transparent.png")  # Remplacez par le chemin de votre image
            image = image.resize((430, 600), Image.Resampling.LANCZOS)  # Redimensionner l'image si nécessaire
            self.image_tk = ImageTk.PhotoImage(image)

            # Ajouter l'image dans un Label
            self.image_label = tk.Label(self.graphs_frame, image=self.image_tk, bg="#f0f4f8")
            self.image_label.grid(row=0, column=3, padx=10, pady=10)
        except Exception as e:
            print(f"Erreur lors du chargement de l'image : {e}")

        

       
        self.measurement_label = tk.Label(self.power_frame, text="--- W",
                                          font=("Segoe UI", 16, "bold"), fg="#1e3d59", bg="#f0f4f8")
        self.measurement_label.grid(row=2, column=0, pady=15, padx=5)

        self.position_label = tk.Label(self.pos_frame, text="x=0, y=0",
                                       font=("Segoe UI", 16, "bold"), fg="#1e3d59", bg="#f0f4f8")
        self.position_label.grid(row=2, column=0, pady=15, padx=5, sticky="nsew")


        self.communication_frame = tk.Frame(self.tab_puissance, bg="#f0f4f8")
        self.communication_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        self.com_label_frame = tk.LabelFrame(self.communication_frame, text="Communication",
                                             bg="#f0f4f8", fg="#2c3e50", font=("Segoe UI", 10, "bold"), bd=1, relief="solid")
        self.com_label_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")


        #self.label_com = tk.Label(self.com_label_frame, text="Démarrage Interface", font=("Segoe UI", 9), bg="#f0f4f8", fg="#2c3e50", justify="left")
        #self.label_com.grid(row=0, column=0, padx=10, pady=10, sticky="nw")


        self.Évènements.append(self.get_time() + ' : ' + 'Démarrage Interface')
        self.label_com = tk.Label(self.com_label_frame, text=self.get_time() + ' : ' + 'Démarrage Interface', font=("Segoe UI", 9), bg="#f0f4f8", fg="#2c3e50", justify="left")
        self.label_com.grid( row=0, column=0, columnspan=1, padx=25, pady=10, sticky="nsew")
        

        
        self.wavelength_entry_label = tk.Label(self.actions_frame, text="Longueur d'onde:", font=("Segoe UI", 10), bg="#f0f4f8", fg="#2c3e50")
        self.wavelength_entry_label.grid(row=0, column=6, pady=15, padx=5, sticky="w")

        self.wavelength_entry = tk.Entry(self.actions_frame, state='normal') #,"Entrer la longueur d'onde manuellement ou longueur d'onde mesurée:")
        self.wavelength_entry.grid(row=0, column=7, pady=15, padx=5, sticky="w")
                
        self.wavelength_entry.delete(0, tk.END)  # Clear the entry field before inserting new text
        self.wavelength_entry.insert(0, self.wl)  # donne la longueur d'onde mesurée par le puissance-mètre
        self.wavelength_entry.config(state="disabled")  # Disable the entry field

        self.wavelength_button = tk.Button(self.actions_frame, text="Entrer une longueur d'onde manuellement", command=self.enregistre_longueur_donde_manuel, bg="#95a5a6", fg="white", **button_cfg)
        self.wavelength_button.grid(row=0, column=8, pady=15, padx=5, sticky="w")

        self.wavelength_button_1 = tk.Button(self.actions_frame, text="Valider", command=self.valider, bg="#95a5a6", fg="white", **button_cfg)
        self.wavelength_button_1.grid(row=0, column=9, pady=15, padx=5, sticky="w")
        #self.device.bind_properties("wavelength", self.wavelength_entry, "value_variable")
        
        size = 15
        #self.bigb_font = tk tkFont.Font(family='Helvetica', size=size, weight='bold')
        #self.big_font = tkFont.Font(family='Helvetica', size=size)
        #self.measurement_label = tk.Label(self.power_frame, text="--- mW") #, font=self.big_font)
        #self.measurement_label.grid(row=2, column=0, pady=15, padx=5)




        self.communication_frame = tk.Frame(self.tab_puissance)
        self.communication_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        # GRaphique de puissance
        #self.com_label_frame = tk.LabelFrame(self.communication_frame, text="Communication")
        #self.com_label_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Communication
        
        #Changer la couleur du box3, ou trouver élément pour communiquer avec l'usager
        #self.initialise = False
    # À valider
    #def exit_fullscreen(self, event=None):
    #    self.root.attributes("-fullscreen", False)    
    
    def on_combobox_select(self, event):
            selected_value = self.combobox_1.get()
            print(f"Selected value: {selected_value}")
            # Perform actions based on the selected value
            self.Évènements.append(self.get_time() + f" : Option sélectionnée : {selected_value}")
            self.label_com.config(text=self.Évènements[len(self.Évènements)-1]
                                + '\n' + self.Évènements[len(self.Évènements)-2]
                                + '\n' + self.Évènements[len(self.Évènements)-3]
                                + '\n' + self.Évènements[len(self.Évènements)-4]
                                + '\n' + self.Évènements[len(self.Évènements)-5])
    def show_combobox_popup(self):
    # Create a popup window
        popup = tk.Toplevel(self.root)
        popup.title("Sélectionnez une option")
        popup.geometry("300x150")
        popup.transient(self.root)  # Associate the popup with the main window
        popup.grab_set()  # Make the popup modal

        # Add a label
        label = tk.Label(popup, text="Veuillez sélectionner une option :", font=("Segoe UI", 10))
        label.pack(pady=10)

        # Add the Combobox
        combobox = ttk.Combobox(popup, values=self.pratique_connect, state="readonly", font=("Segoe UI", 10))
        combobox.pack(pady=10)
        combobox.set("Sélectionnez une option")

        
        def confirm_selection(event):
            selected_value = combobox.get()
            if selected_value != "Sélectionnez une option":
                self.combobox_1.set(selected_value)  # Update the main Combobox
                popup.destroy()  # Close the popup

        combobox.bind("<<ComboboxSelected>>", confirm_selection)




    def on_combo_validation(self):
        try:
            selected_value = self.combobox_1.get()
        except DaqError as e:
            messagebox.showerror("Erreur DAQ", f"Erreur de lecture DAQ : {str(e)}\nVeuillez vérifier la connexion USB ou le câble.")
            return False
        if selected_value == "Sélectionnez une option":
            messagebox.showerror("Erreur", "Veuillez sélectionner une option de port de connection valide.")
            a = self.show_combobox_popup()
            #highlight_combobox(self.combobox)
            #self.combobox.configure(style="Highlight.TCombobox")
            #style = ttk.Style()
            #style.configure("Highlight.TCombobox", fieldbackground="yellow", bordercolor="red", borderwidth=2)
            self.is_refreshing = False
            self.status_light.itemconfig(self.light_id, fill="red")
            self.start_button.config(text="Démarrer")


            return False

        return True
    


    
    
            
    def send_software_pwm(self, channel, page):
        if page == 'Wavelenght':
            with nidaqmx.Task() as task:
                task.do_channels.add_do_chan(channel)
                task.write(True)
                time.sleep(0.1)
                task.write(False)
        elif page == 'Power':
            with nidaqmx.Task() as task:
                task.do_channels.add_do_chan(channel)
                task.write(True)
                time.sleep(0.1)
                task.write(False)
            
                
    # à vérifier
    def on_tab_change(self, event):
        
        notebook = event.widget

        new_tab_index = notebook.index(notebook.select())
        tab_text =  notebook.tab(new_tab_index, "text")

        if new_tab_index != self.current_tab_index:
            tab_text = notebook.tab(new_tab_index, "text")
            confirm = messagebox.askyesno("Confirmation", f"Voulez-vous vraiment passer à l'onglet '{tab_text}' ?")

            if not confirm:
                # Prevent tab switching by re-selecting the current tab
                notebook.select(self.current_tab_index)
                tab_text = notebook.tab(self.current_tab_index, "text")
            else:
                # Update the current tab index if the user confirms
                self.current_tab_index = new_tab_index
                

        if tab_text == "Longueur d'onde":
            print("Longueur d'onde sélectionnée → Servo vers 180°")
            self.send_software_pwm(channel=f"{self.device.get_firmware_from_device()}/port1/line0", page = 'Wavelenght')  # ≈ 180°
        elif tab_text == "Puissance":
            print("Puissance sélectionnée → Servo vers 0°")
            self.send_software_pwm(channel=f"{self.device.get_firmware_from_device()}/port1/line1", page = 'Power')  # Retour à 0°
        



        '''

        if self.initialise:
            return

        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")

        
        confirm = messagebox.askyesno("Confirmation", f"Voulez-vous vraiment passer à l'onglet '{tab_text}' ?")
        print(confirm)
        if not confirm:
            print("Changement d'onglet annulé.")
         # Prevent tab switching by re-selecting the current tab
            #current = self.notebook.index("current")
            current_tab = event.widget.index("current")
            print(current_tab)
            #event.widget.tab(self.previous_tab, text=self.previous_tab_text)  # Restore the previous tab text
            selected_tab = event.widget.select(current_tab)

            print(event.widget.tab(selected_tab, 'text'))
            return
    
        if tab_text == "Longueur d'onde":
            #print("Longueur d'onde sélectionnée → Servo vers 180°")
            self.send_software_pwm(channel=f"{self.device.get_firmware_from_device()}/port1/line0", page = 'Wavelenght')  # ≈ 180°
        elif tab_text == "Puissance":
            #print("Puissance sélectionnée → Servo vers 0°")
            self.send_software_pwm(channel=f"{self.device.get_firmware_from_device()}/port1/line1", page = 'Power')  # Retour à 0°
        
        '''

    def get_time(self):
        return(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def click_start(self):
        try:
            self.device.get_power_from_device() # À revoir
        except DaqError as e:
            messagebox.showerror("Erreur DAQ", 'Veuillez vérifier la connexion USB ou le câble.')
            
          
        if not self.is_refreshing:
            self.is_refreshing = True
            self.status_light.itemconfig(self.light_id, fill="green")
            self.update_loop()
            self.start_button.config(text="Arrêter")
            # Historique communication
            self.Évènements.append(self.get_time() + ' : '+'La prise de donnée est en cours')
            #self.label_com.value_variable.set(self.get_time() + ' : '+'La prise de donnée est en cours')
            self.label_com.config(text=self.Évènements[len(self.Évènements)-1]
                                          + '\n' + self.Évènements[len(self.Évènements)-2]
                                          + '\n' + self.Évènements[len(self.Évènements)-3]
                                          + '\n' + self.Évènements[len(self.Évènements)-4]
                                          + '\n' + self.Évènements[len(self.Évènements)-5]) 
            #self.update_thread = threading.Thread(target=self.device.update_from_device, daemon=True)
            #self.update_thread.start()
            self.save_button.config(state='disabled')
            self.misea0.config(state='disabled')
            self.paramètre.config(state='disabled') 
            self.wavelength_entry.config(state='disabled')
            self.wavelength_button.config(state='disabled')
            self.connexion.config(state='disabled')
            self.wavelength_entry_label.config(state='disabled')
            self.wavelength_button_1.config(state='disabled')
            self.toolbar_puissance.grid_remove()
            self.notebook.forget(self.tab_longeur_onde) # PEUT ÊTRE ENLEVER *****
        else:
            
            
            #try: 
            #    pass
            #except DaqReadError as e:
            #    messagebox.showerror("Erreur DAQ", f"Erreur de lecture DAQ : {str(e)}\nVeuillez vérifier la connexion USB ou le câble.")
            self.is_refreshing = False
            self.status_light.itemconfig(self.light_id, fill="red")
            self.start_button.config(text="Démarrer")

            
            # Historique communication
            self.Évènements.append(self.get_time()+ ' : '+'La prise de donnée est mise en pause')
            #self.label_com.value_variable.set(self.get_time()+ ' : '+'La prise de donnée est mise en pause')
            self.label_com.config(text=self.Évènements[len(self.Évènements)-1]
                                          + '\n' + self.Évènements[len(self.Évènements)-2]
                                          + '\n' + self.Évènements[len(self.Évènements)-3]
                                          + '\n' + self.Évènements[len(self.Évènements)-4]
                                          + '\n' + self.Évènements[len(self.Évènements)-5]) 
            self.save_button.config(state='normal')
            self.misea0.config(state='normal')
            self.paramètre.config(state='normal') 
            self.wavelength_entry.config(state='disabled')
            self.wavelength_button.config(state='normal')
            self.connexion.config(state='normal')
            self.wavelength_entry_label.config(state='normal')
            self.wavelength_button_1.config(state='normal')
            self.toolbar_puissance.grid()
            self.notebook.add(self.tab_longeur_onde, text="Longueur d'onde") # PEUT ÊTRE ENLEVER	*****



    def click_chose_parametres(self): 
        self.parameters = []
        self.dico_parameters = {}
        filepath = filedialog.askopenfilename(filetypes=[('Data file','.dat'),('CSV file','.csv')])
        file = open(filepath, 'r')

        self.parameters.append(file.read())
        self.parameters = self.parameters[0].split('\n')
        for i in range(len(self.parameters)):
            self.parameters[i] = self.parameters[i].split(';')

            if len(self.parameters[i]) == 2:
                self.dico_parameters.update({self.parameters[i][0]:self.parameters[i][1]})

        #print(self.dico_parameters['parametre1'])
        self.Évènements.append(self.get_time() + ' : '+'Le fichier de paramètres '+ filepath + ' a été chargé')
        #self.label_com.value_variable.set(self.get_time() + ' : '+'Le fichier de paramètres '+ filepath + ' a été chargé')
        self.label_com.config(text=self.Évènements[len(self.Évènements)-1]
                                          + '\n' + self.Évènements[len(self.Évènements)-2]
                                          + '\n' + self.Évènements[len(self.Évènements)-3]
                                          + '\n' + self.Évènements[len(self.Évènements)-4]
                                          + '\n' + self.Évènements[len(self.Évènements)-5]) 
       
        file.close()
        
    #def power_values(self):
    #    self.device = PowerMeterDevice()
    #    self.device.update_from_device()
    #    return self.device.power
    
    def update_plot(self):
        N = 100  # show only the last 100 points
        x_data = list(range(max(0, len(self.historique_temps_mesure) - N), len(self.historique_temps_mesure)))
        y_data = self.historique_puissance[-N:]
        if x_data:
            self.ax_puissance.set_xlim(min(x_data), max(x_data))
        self.line_puissance.set_data(x_data, y_data)
        #self.ax_puissance.set_ylim(0, max(y_data) * 1.1 if y_data else 15)
        self.canvas.draw()

      
        
        
        values = self.device.z  # [params, Z_interp, x_peak, y_peak]
        params = values[0]
        sigma = (params[3] + params[4]) / 2
        

        if sigma >= 1.5 and sigma <= 4:
            self.red_circle.center = (values[2], values[3])
            self.red_circle.set_radius(sigma)
            self.red_circle.set_visible(True)
        else:
            self.red_circle.set_visible(False)
        self.red_circle.center = (values[2], values[3])
        self.red_circle.set_radius(sigma)
        self.cross_marker.set_data([values[2]], [values[3]])
        if self.device.power < 0.5:
            self.red_circle.set_visible(False)
            self.cross_marker.set_visible(False)
            self.position_label.config(text="Pas de laser détecté")
        self.pos_canvas.draw()




    def update_loop(self):
        try:
            self.on_combo_validation()
            self.initialise = False
            print()
            self.temps2 = time.time()
            print('Temps Total:', self.temps2-self.temps1)
            
            self.device.update_from_device() # modif ici
            power = self.device.power
            z = self.device.z
            x_peak, y_peak = z[2], z[3]
            #thermistor_values = self.device.get_temperature_from_device() # modifier pour données en temps réel
            #_, _2, x_peak, y_peak = self.device.get_temperature_from_device() # maybe juste self.device.temperature
            
            self.historique_temps_mesure.append(self.get_time())
            self.historique_position_x.append(x_peak)      # modifier pour données en temps réel
            self.historique_position_y.append(y_peak)        # modifier pour données en temps réel
            self.historique_puissance.append(power)
            #self.after(0, self.update_plot)  # Update the plot
            self.position_label.config(text=f"(x={x_peak:.2f}, "f"y={y_peak:.2f})")
            self.update_plot()

            self.measurement_label.config(text=f"{power:.2f} W")
            
            
        
            
            if self.is_refreshing:
                self.after(300, self.update_loop)   # To-Do ajouter bouton pour modifier rate
            self.temps1 = self.temps2

        except DaqReadError as e:
            messagebox.showerror("Erreur DAQ", f"Erreur de lecture DAQ : Veuillez vérifier la connexion USB ou le câble.")
            print("DAQ read error occurred:", e)
            self.is_refreshing = False
            #try: 
            #    pass
            #except DaqReadError as e:
            #    messagebox.showerror("Erreur DAQ", f"Erreur de lecture DAQ : {str(e)}\nVeuillez vérifier la connexion USB ou le câble.")
                
            self.status_light.itemconfig(self.light_id, fill="red")
            self.start_button.config(text="Démarrer")
            
            # Historique communication
            self.Évènements.append(self.get_time()+ ' : '+'La prise de donnée est mise en pause')
            #self.label_com.value_variable.set(self.get_time()+ ' : '+'La prise de donnée est mise en pause')
            self.label_com.config(text=self.Évènements[len(self.Évènements)-1]
                                          + '\n' + self.Évènements[len(self.Évènements)-2]
                                          + '\n' + self.Évènements[len(self.Évènements)-3]
                                          + '\n' + self.Évènements[len(self.Évènements)-4]
                                          + '\n' + self.Évènements[len(self.Évènements)-5]) 
            self.save_button.config(state='normal')
            self.misea0.config(state='normal')
            self.paramètre.config(state='normal') 
            self.wavelength_entry.config(state='normal')
            self.wavelength_button.config(state='normal')
            self.connexion.config(state='normal')
            self.wavelength_entry_label.config(state='normal')
            self.wavelength_button_1.config(state='normal')
            return None
        
        
    def click_save(self):

        filepath = filedialog.asksaveasfilename(
            parent=self.root,
            title="Choisissez un nom de fichier:",
            filetypes=[('CSV file','.csv'), ('Data file','.dat')],
        )
        
        if filepath != "":
            with open(filepath, 'w') as file:
                file.write('Temps' + '' +  'Puissance' + '' + 'Position_X' + '' + 'Position_Y' + '' +  'longueur_onde' + ''+ '\n')
                for i in range(len(self.historique_puissance)):
                    file.write((str(self.historique_temps_mesure[i]) + ' ' + str(self.historique_puissance[i])) + ' ' + str(self.historique_position_x[i]) +  ' ' +str(self.historique_position_y[i]) +' '+ str(self.device.wavelength) +' '+ '\n')
            
            pass 

        # Historique des actions à enregistrer dans un fichier
        filepath_action = filepath + '_actions'

        if filepath_action != "":
            with open(filepath_action, 'w') as file:
                for i in range(len(self.Évènements)):
                    file.write(self.Évènements[i] + '\n')


        messagebox.showinfo("Enregistrement", "Les données ont été enregistrées avec succès !")
        #self.click_clear() EST-ce qu'on veut clear ca ?


    def on_close(self):
        '''
        Pour quitter l'application et offrir la sauvegrade
        '''
        response = askyesnocancel(
            title="Enregistrement des données",
            message="Voulez-vous enregistrer les données avant de quitter?",
        )
        if response is True:
            self.click_save()
        elif response is False:  
            self.quit()  # 

    #TO ADD
    def enregistre_longueur_donde_manuel(self):
        self.wavelength_entry.config(state="normal")
        
        #TO ADD
    def valider(self):
        self.wavelength_entry.config(state="disabled")
        self.wl = self.wavelength_entry.get()
        self.device.wavelength = self.wl # ?
        return self.wl

        
        
    def click_clear(self):

        
        click = askyesnocancel(title="Confirmation", message="Voulez-vous enregistrer les données aquisitionnées avant de mettre à zéro les données? ")
        if click is True:  # User clicked "Yes"
            self.click_save()
            self.Évènements.append(self.get_time()+ ' : '+'Sauvarde des données aquisitionnées')
            self.label_com.config(text=self.Évènements[len(self.Évènements)-1]
                                          + '\n' + self.Évènements[len(self.Évènements)-2]
                                          + '\n' + self.Évènements[len(self.Évènements)-3]
                                          + '\n' + self.Évènements[len(self.Évènements)-4]
                                          + '\n' + self.Évènements[len(self.Évènements)-5]) 
            
        elif click is False:  # User clicked "No"
            pass

        self.historique_temps_mesure = []
        self.historique_puissance = []
        # Modifier axis selon tkinter
        #self.plot_puissance.first_axis.clear()
        self.update_plot()

        # Historique communication
        self.Évènements.append(self.get_time() + ' : '+'Mise à zéro effectuée')
        self.label_com.config(text=self.Évènements[len(self.Évènements)-1]
                                            + '\n' + self.Évènements[len(self.Évènements)-2]
                                            + '\n' + self.Évènements[len(self.Évènements)-3]
                                            + '\n' + self.Évènements[len(self.Évènements)-4]
                                            + '\n' + self.Évènements[len(self.Évènements)-5]) 
     
     

class PowerMeterDevice(Bindable):
    debug = True

    def __init__(self):
        super().__init__()

        self.supertest = Acquisition()
        self.supertest.assign_thermistor_positions()
        #print(self.supertest.data)

        self.power = 404
        self.wavelength = 976 
        #self.firmware = None
        self.old = 19.6
        self.temperature = []
        self.alexis = 0
        self.z = None 
        self.dev = self.supertest.daq_device
        self.calibration = [20,20,20,20]
        


    # Fonction pour obtenir la dernière valeur de voltage de la thermistance
    def get_thermistane_from_device(self):   
        pass

        # self.power = appel fonction à partir d'aquisition qui retourne une valeur de voltage (la dernière)


    def get_power_from_device(self):
        #try:
            self.supertest.Power_thermistor(self.dev)
            self.z = self.supertest.fitting()
            voltage = self.supertest.liste_voltage
            data = self.supertest.data[~np.isnan(self.supertest.data).any(axis=1)]
            data = data.T 
            data = data[-1]
            
            self.save_voltage_to_csv(voltage, data, self.supertest.liste_ref, self.supertest.liste_tension_ref)  # Save voltage values to CSV
            self.power, self.old = puissance_calcul(self.supertest.data , self.supertest.liste_ref, self.old)
            #print(self.wavelength)
            self.power = corr_spectrale(self.power, self.wavelength)    # Avec corection spectrale Problème communication longeuru d'onde avec l'autre class
            
            return self.power
        #except DaqReadError as e:
            messagebox.showerror("Erreur DAQ", f"Erreur de lecture DAQ : {str(e)}\nVeuillez vérifier la connexion USB ou le câble.")
            print("DAQ read error occurred:", e)
            return None
    

    # À tester
    def get_temperature_from_device(self):
        # Utilise les valeurs de tension pour l'instant et non de température !
        #try:
            self.supertest.Power_thermistor(self.device.dev)
            self.z = self.supertest.fitting()
            return self.z
        #except DaqError as e:
            messagebox.showerror("Erreur DAQ", "Erreur de communication avec le DAQ. Vérifier la connexion.")
            print("DAQ error occurred:", e)
            return None

        
    
    
    # à valider Pour les tests préliminaires seulement
    def save_voltage_to_csv(self, voltage, temperature, ref, tension_ref):
        output_file = "voltage_temperature_data.csv"  # Specify the CSV file name

            # Ensure all inputs are lists
        voltage = list(voltage)
        temperature = list(temperature)
        ref = list(ref)
        tension_ref = list(tension_ref)
        #print(ref)

        #print(len(voltage), len(temperature), len(ref))

        # Open the file in append mode
        with open(output_file, mode="a", newline="") as file:
            writer = csv.writer(file)

            # Write the header if the file is empty
            if file.tell() == 0:  # Check if the file is empty
                header = (
                    [f"Voltage_{i+1}" for i in range(len(voltage))] +
                    [f"Temperature_{i+1}" for i in range(len(temperature))] +
                    [f"Ref_{i+1}" for i in range(len(ref))] +
                    [f"Ref_{i+1}" for i in range(len(tension_ref))]
                )
                writer.writerow(header)

            # Append the voltage, temperature, and reference values as a new row
            row = voltage + temperature + ref + tension_ref # Combine voltage, temperature, and reference into a single row
            writer.writerow(row)

        #print(f"Voltage, temperature, and reference values saved to {output_file}")
        

    def get_firmware_from_device(self):
        self.dev = self.supertest.daq_device
        print(self.dev)

        return self.dev

    
    #def get_wavelength_from_device(self):
            
    

    def update_from_device(self):
        self.get_power_from_device()
        self.get_firmware_from_device()
        
        #self.get_temperature_from_device()
        #self.get_wavelength_from_device()



