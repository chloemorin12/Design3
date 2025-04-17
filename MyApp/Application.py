
from tkinter import filedialog, messagebox
import random
from testChloe import data_gradient_temperature, position, puissance_calcul
import matplotlib.pyplot as plt
import matplotlib, sys
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from tkinter.messagebox import askyesno
import tkinter as tk
from tkinter import ttk
from app import App
from bindable import Bindable
from base import Base
from AcquisitionClass import Acquisition 
import threading
import time
from Algorithm_wavelength import trouver_longueurs_donde, longueur_donde_commune, plot_graph, adjust_value, wavelength_calculator
import numpy as np
import nidaqmx


class PowerMeterApp(App):
    def __init__(self):
        App.__init__(self)

        self.device = PowerMeterDevice()
        self.is_refreshing = False

        self.ct = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.historique_puissance = []
        self.historique_temps_mesure = []
        self.historique_position_x = []
        self.historique_position_y = []

        
        self.root.title("PowerMeter")

        # Configure the root window to allow expansion
        self.root.grid_rowconfigure(0, weight=1)  # Make row 0 expandable
        self.root.grid_columnconfigure(0, weight=1)  # Make column 0 expandable

        # Create a Notebook widget
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)  # Use sticky + no padding

        # Add tabs to the notebook
        self.tab_puissance = tk.Frame(self.notebook)
        self.notebook.add(self.tab_puissance, text="Puissance")
        self.tab_puissance.grid_rowconfigure(0, weight=1)  # Make row 0 expandable
        self.tab_puissance.grid_columnconfigure(0, weight=1)  # Make column 0 expandable

        self.tab_longeur_onde = tk.Frame(self.notebook)
        self.notebook.add(self.tab_longeur_onde, text="Longueur d'onde")
        self.tab_longeur_onde.grid_rowconfigure(0, weight=1)  # Make row 0 expandable   
        self.tab_longeur_onde.grid_columnconfigure(0, weight=1)  # Make column 0 expandable




        
        # Frame pour les entrées de puissances et les cases
        top_frame = tk.Frame(self.tab_longeur_onde)
        top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        #self.ask_wavelength = tk.LabelFrame(self.tab_longeur_onde, text=" Calcul longueur d'onde")
        #self.ask_wavelength.grid(row=0, column=0, columnspan=1, sticky="ew", padx=10, pady=5)

        # Ajouter un label : Message sur le fonctionenment au besoin (TO-DO)
        label = tk.Label(top_frame, text="Cliquez sur 'Lancer les calculs'", font=("Arial", 12))
        label.grid(row=0, column=0, columnspan=1, padx=10, pady=10)





        main_frame = tk.Frame(self.tab_longeur_onde)
        main_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="n")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        puissance_wavelength = [500, 55, 499, 250] # Cette liste deviendra dans le futur les données de puissance des thermistances où les filtres

        # Variables pour les trois cases
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

        self.ST = Acquisition()
       
        def on_button_click():
                    Powers = self.ST.Wavelength_thermistor()
                    print(Powers)
                    iterations = 0
                    ytols = np.array([2.0, 2.0, 2.0])
                        
                    while wavelength_calculator(Powers, ytols, canvas_frame, result_value_label) == 0 and iterations < 99:
                        ytols+=1
                        iterations += 1
                        if wavelength_calculator(Powers, ytols, canvas_frame, result_value_label) != 0 or iterations == 98:
                            break
                    final_result, incertainty, wl_individuelles = wavelength_calculator(Powers, ytols, canvas_frame, result_value_label)
                    graphe = plot_graph(wl_individuelles[0], wl_individuelles[1], wl_individuelles[2], canvas_frame)
                    messagebox.showinfo("Info", "La mesure de longueur d'onde est finie")
                    return final_result, incertainty, graphe, ytols



        # Bouton pour lancer les calculs
        button = tk.Button(top_frame, text="Lancer les calculs", command=on_button_click, font=("Arial", 12), bg="lightblue")
        button.grid(row=0, column=1, padx=10, pady=10)

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
        plot_graph(None, None, None, canvas_frame)














        self.Évènements = ['', '', '',''] # Liste des communications à enregistrer dans un fichier

        self.actions_frame = tk.LabelFrame(self.tab_puissance, text="Actions")
        self.actions_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        # Démarrer/Arrêter
        self.start_button = tk.Button(self.actions_frame, text = "Démarrer", command=self.click_start)
        self.start_button.grid(row=0, column=1, pady=15, padx=5, sticky="w")

        # Indicateur marche/arret
        #self.running_indicator = BooleanIndicator(self.actions_frame,diameter=25)
        #self.running_indicator.grid(self.box, row=0, column=0, pady=15, padx=5)

        # Mise à zéro : Initialisation prise de donnée ? Détecte si la température est trop élevée ?
        self.misea0 = tk.Button(self.actions_frame, text="Mise à zéro", command=self.click_clear)
        self.misea0.grid(row=0, column=2, pady=15, padx=5)

        # Paramètre : Permet d'aller choisir un fichier avec les valeurs ?
        self.paramètre = tk.Button(self.actions_frame, text="Paramètres", command=self.click_chose_parametres)
        self.paramètre.grid(row=0, column=3, pady=15, padx=5)

        # Connexion : Permet de se connecter en un clic peut importe le port de connexion utilisé
        # Ouverture d'une autre fenêtre ?  radiobutton
        self.connexion = tk.Button(self.actions_frame, text="Connexion")
        self.connexion.grid(row=0, column=4, pady=15, padx=5)

        self.save_button = tk.Button(self.actions_frame, text="Enregister les données", command=self.click_save)
        self.save_button.grid( row=0, column=5, padx=10, pady=10)




        # ajouter fonction zoomed in ? + save graph as is  (TO DO)
        # http://pythonguis.com/tutorials/plotting-matplotlib/

        # Graphique de puissance
        self.graphs_frame = tk.Frame(self.tab_puissance)
        self.graphs_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        
        self.power_frame = tk.LabelFrame(self.graphs_frame, text="Puissance dans le temps")
        self.power_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.plot_puissance = plt.figure(figsize=(5, 4))
        self.ax_puissance = self.plot_puissance.add_subplot(111)
        self.ax_puissance.plot(self.historique_temps_mesure, self.historique_puissance)

        self.canvas = FigureCanvasTkAgg(self.plot_puissance, master=self.power_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, pady=15, padx=5, sticky="nsew")



        


        # Graphique de position
        self.pos_frame = tk.LabelFrame(self.graphs_frame, text="Position dans le temps")
        self.pos_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        values = self.device.get_temperature_from_device()
        #fig = plt.figure(figsize=(5, 4))
        #self.ax = fig.add_subplot(111)
        self.fig = plt.figure(figsize=(5, 4))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(-15, 15)
        self.ax.set_ylim(-15, 15)
        self.ax.imshow(values[1], origin='lower', extent=(-15, 15, -15, 15), cmap='coolwarm')
        self.pos_canvas = FigureCanvasTkAgg(self.fig, master=self.pos_frame)
        self.pos_canvas_widget = self.pos_canvas.get_tk_widget()
        self.pos_canvas_widget.grid(row=0, column=0, pady=15, padx=5, sticky="nsew")
        
        
        size = 15
        #self.bigb_font = tk tkFont.Font(family='Helvetica', size=size, weight='bold')
        #self.big_font = tkFont.Font(family='Helvetica', size=size)
        self.measurement_label = tk.Label(self.power_frame, text="--- mW") #, font=self.big_font)
        self.measurement_label.grid(row=2, column=0, pady=15, padx=5)

        self.position_label = tk.Label(self.pos_frame, text="---")
        self.position_label.grid(row=2, column=0, pady=15, padx=5, sticky='nsew')




        self.communication_frame = tk.Frame(self.tab_puissance)
        self.communication_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        # GRaphique de puissance
        self.com_label_frame = tk.LabelFrame(self.communication_frame, text="Communication")
        self.com_label_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Communication
        self.Évènements.append(self.get_time() + ' : ' + 'Démarrage Interface')
        self.label_com = tk.Label(self.com_label_frame, text=self.get_time() + ' : ' + 'Démarrage Interface')
        self.label_com.grid( row=0, column=0, columnspan=1, padx=25, pady=10, sticky="nsew")
        #Changer la couleur du box3, ou trouver élément pour communiquer avec l'usager
        

        


        '''''

        self.autre = View(width=800, height=300)
        self.autre.grid_into(self.window, row=2, column=0, pady=5, padx=5, sticky="nsew")

        self.wavelength_entry = LabelledEntry("Wavelength:", character_width=6)
        self.wavelength_entry.grid_into(self.button_group2, row=0, column=0, sticky="e")
            
        self.firmware_label = Label()
        self.firmware_label.grid_into(self.button_group2, row=1, column=0, padx=25, pady=10, sticky="w")

        # Barre de progression
        self.progression = Level(width=800, height=30)
        self.progression.grid_into(self.window, row=3, column=0, pady=25, padx=15)
        # bindable pour lier l'avancement des fonction avec la barre de progression 

    

        '''

        
        #self.wavelength_entry = LabelledEntry("Wavelength:", character_width=6)
        #self.wavelength_entry.grid_into(self.window, row=1, column=4, sticky="e")
        #self.firmware_label = Label()
        #self.firmware_label.grid_into(self.window, row=3, column=0, columnspan=3, padx=25, pady=10, sticky="w")
        
        

        #self.device.bind_properties("wavelength", self.wavelength_entry.entry, "value_variable")
        #self.device.bind_properties("firmware", self.firmware_label, "value_variable")
        #self.bind_properties("is_refreshing", self.running_indicator, "value_variable")
        #self.bind_properties("is_refreshing", self.start_button, "is_disabled") # Permet de désactiver les boutons 
        #self.bind_properties("is_refreshing", self.wavelength_entry.entry, "is_disabled")
        
        #self.update_loop() # We update once at least
    def angle_to_pulse_width_ms(self, angle_rad):
            return 1.5 + (angle_rad / np.pi) * 0.5

    def send_software_pwm(self, angle_rad=0.0, duration=0.5, channel="Dev1/port1/line0"):
        pulse_width_ms = self.angle_to_pulse_width_ms(angle_rad)
        period_ms = 20
        high_time = pulse_width_ms / 1000
        low_time = (period_ms - pulse_width_ms) / 1000

        with nidaqmx.Task() as task:
            task.do_channels.add_do_chan(channel)
            start_time = time.time()

            while time.time() - start_time < duration:
                task.write(True)
                time.sleep(high_time)
                task.write(False)
                time.sleep(low_time)

    def on_tab_change(self, event):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
    
        if tab_text == "Longueur d'onde":
            print("Longueur d'onde sélectionnée → Servo vers 180°")
            self.send_software_pwm(angle_rad=np.pi)  # ≈ 180°
        elif tab_text == "Puissance":
            print("Puissance sélectionnée → Servo vers 0°")
            self.send_software_pwm(angle_rad=0)  # Retour à 0°

    def get_time(self):
        return(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def click_start(self):

        if not self.is_refreshing:
            self.is_refreshing = True
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
            
        else:
            self.is_refreshing = False
            self.start_button.config(text="Démarrer")
            # Historique communication
            self.Évènements.append(self.get_time()+ ' : '+'La prise de donnée est mise en pause')
            #self.label_com.value_variable.set(self.get_time()+ ' : '+'La prise de donnée est mise en pause')
            self.label_com.config(text=self.Évènements[len(self.Évènements)-1]
                                          + '\n' + self.Évènements[len(self.Évènements)-2]
                                          + '\n' + self.Évènements[len(self.Évènements)-3]
                                          + '\n' + self.Évènements[len(self.Évènements)-4]
                                          + '\n' + self.Évènements[len(self.Évènements)-5]) 
            

    #def communication(self, étape):
    #    if étape == 'start':
    #        print('Démarrage')

    '''
    def window_size(self):
        w = Tk()
        w.attributes('-fullscreen', True)
        size = (w.winfo_screenmmwidth(), w.winfo_screenmmheight())
        w.quit()
        print(size)
    '''


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
        # with plt.style.context(self.style):
        #self.first_axis.plot(self.x, self.y, "k-")
        self.ax_puissance.cla()  # Clears the axes
        self.ax_puissance.plot(range(len(self.historique_temps_mesure)), self.historique_puissance)  # modifier axe des x ?
        self.canvas.draw()
        self.canvas.flush_events()

        #Changes
        if hasattr(self, 'colorbar') and self.colorbar:
            self.colorbar.remove() # Clears the colourbars

        values = self.device.z# Modifier pour 

        self.ax.cla()  # Clears the axes
        self.ax.set_xlim(-15, 15)
        self.ax.set_ylim(-15, 15)
        self.ax.set_xlabel("Position X [cm]")
        self.ax.set_ylabel("Position Y [cm]")
        #self.ax.imshow(self.device.get_temperature_from_device()[1], origin='lower', extent=(-15, 15, -15, 15), cmap='coolwarm')
        temperature_data = values[1]
        im = self.ax.imshow(temperature_data, origin='lower', extent=(-15,15,-15,15), cmap='coolwarm')
        self.ax.plot(values[2], values[3], 'kx', markersize=10, markeredgewidth=3)
        self.colorbar = self.fig.colorbar(im, ax=self.ax)
        self.colorbar.set_label("Température [°C]") 
        self.pos_canvas.draw()
        self.pos_canvas.flush_events()



       
        
        
        


    def update_loop(self):
        
        self.device.update_from_device() # modif ici
        power = self.device.power
        #thermistor_values = self.device.get_temperature_from_device() # modifier pour données en temps réel
        _, _2, x_peak, y_peak = self.device.get_temperature_from_device() # maybe juste self.device.temperature
        d = time.time()
        
        self.historique_temps_mesure.append(self.get_time())
        self.historique_position_x.append(x_peak)      # modifier pour données en temps réel
        self.historique_position_y.append(y_peak)        # modifier pour données en temps réel
        self.historique_puissance.append(power)
        #self.after(0, self.update_plot)  # Update the plot
        self.update_plot()

        self.measurement_label.config(text=f"{power:.2f} mW")
        
        self.position_label.config(text=f"(x={x_peak:.2f}, "f"y={y_peak:.2f})")
       
        f = time.time()
        print('total', f-d)
        
        if self.is_refreshing:
            self.after(300, self.update_loop)   # To-Do ajouter bouton pour modifier rate

        #last_pos = data_gradient_temperature()
        #self.plot_position.append(last_pos[0], last_pos[1])
        #self.plot_position.update_plot()
        
        
    def click_save(self):

        filepath = filedialog.asksaveasfilename(
            parent=self.root,
            title="Choisissez un nom de fichier:",
            filetypes=[('Data file','.dat'),('CSV file','.csv')],
        )
        
        if filepath != "":
            with open(filepath, 'w') as file:
                file.write('Temps' + '' +  'Puissance' + '' + 'Position_X' + '' + 'Position_Y' + '' +  '\n')
                for i in range(len(self.historique_puissance)):
                    file.write((str(self.historique_temps_mesure[i]) + ' ' + str(self.historique_puissance[i])) + ' ' + str(self.historique_position_x[i]) +  str(self.historique_position_y[i])  + '\n')
            
            pass # Do something with x,

        # Historique des actions à enregistrer dans un fichier
        filepath_action = filepath + '_actions'

        if filepath_action != "":
            with open(filepath_action, 'w') as file:
                for i in range(len(self.Évènements)):
                    file.write(self.Évènements[i] + '\n')

    def on_close(self):
        '''
        Pour quitter l'application et offrir la sauvegrade
        '''
        response = askyesno(
            title="Save Data",
            message="Do you want to save the collected data before quitting?",
        )
        if response is True:
            self.click_save()
        elif response is False:  
            self.quit()  # 

    def click_clear(self):

        
        click = askyesno(title="Confirmation", message="Voulez-vous enregistrer les données aquisitionnées avant de mettre à zéro les données? ")
        if click is True:  # User clicked "Yes"
            self.click_save()
            self.Évènements.append(self.get_time()+ ' : '+'Sauvarde des données aquisitionnées')
            self.label_com.config(text=self.Évènements[len(self.Évènements)-1]
                                          + '\n' + self.Évènements[len(self.Évènements)-2]
                                          + '\n' + self.Évènements[len(self.Évènements)-3]
                                          + '\n' + self.Évènements[len(self.Évènements)-4]
                                          + '\n' + self.Évènements[len(self.Évènements)-5]) 
            #self.save()  # Call the save method (to be implemented in the derived class)
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

        """
        The variables are refreshed by get_xxx commands, which 
        fetch the actual values from the device.
        The variables represent the latest values at all times
        and can be used direectly by the app.
        """
        self.power = 404
        self.wavelength = 1064
        self.firmware = None
        self.temperature = []
        self.z = None 


    # Fonction pour obtenir la dernière valeur de voltage de la thermistance
    def get_thermistane_from_device(self):   
        pass

        # self.power = appel fonction à partir d'aquisition qui retourne une valeur de voltage (la dernière)


    def get_power_from_device(self):
        self.supertest.Power_thermistor()
        self.power = puissance_calcul(self.supertest.data , self.supertest.liste_ref)


        '''
        if self.debug:
            #self.power = random.randrange(800,1000,1)/100
            valeur = self.supertest.Power_thermistor()
            self.power = valeur[0]
            self.ref = valeur[1]
        else:
            pass # Update via USB
        '''
        return self.power

    def get_firmware_from_device(self):
        if self.debug:
            self.firmware = "1.0.0alpha1"
        else:
            pass # Update via USB

        return self.firmware

    def get_temperature_from_device(self):


        self.supertest.Power_thermistor()
        self.z = self.supertest.fitting()


        #self.temperatu
        # self.temperature permet d'avoir la température de toutes les termistance (avant implantation aquisition)
        #self.temperature = [70,71,72,73,74,75,76,77,70] #[random.randrange(90,113,1), random.randrange(60,73,1),random.randrange(50,80,1),random.randrange(70,73,1),random.randrange(70,73,1),74,75, 76,70]  
        #print(self.temperature)
        #print(type(self.temperature))
        #if self.debug:
        #    self.temperature = [random.randrange(70,73,1), random.randrange(70,73,1),random.randrange(70,73,1),random.randrange(70,73,1),random.randrange(70,73,1),72,74, 72,70]  
        #else:
        #    pass # Update via USB
        #temps = timeit.timeit('Acquisition().fitting()', number=1)
        #print(temps)
        return self.z

    def get_wavelength_from_device(self):
        if self.debug:
            pass
        else:
            pass # Update via USB

        return self.wavelength

    def update_from_device(self):
        d = time.time()
        self.get_power_from_device()
        #self.get_firmware_from_device()
        self.get_temperature_from_device()
        self.get_wavelength_from_device()
        f = time.time()
        print(f-d)



