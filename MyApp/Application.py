
from tkinter import filedialog, messagebox
import random
from testChloe import data_gradient_temperature, position
import matplotlib.pyplot as plt
import matplotlib, sys
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from datetime import datetime
from tkinter.messagebox import askyesno
import tkinter as tk
from tkinter import ttk
from app import App
from bindable import Bindable
from base import Base

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



        self.Évènements = ['', '', '',''] # Liste des communications à enregistrer dans un fichier

        self.actions_frame = tk.LabelFrame(self.tab_puissance, text="Actions")
        self.actions_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        #lumière indicatif
        self.status_light = tk.Canvas(self.actions_frame, width=24, height=24, bg='white', highlightthickness=0)
        self.light_id = self.status_light.create_oval(4, 4, 20, 20, fill="red", outline="gray")
        self.status_light.grid(row=0, column=0, padx=10, pady=15)
        
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
        self.ax_puissance.set_xlabel("Temps [s]")
        self.ax_puissance.set_ylabel("Puissance [mW]")
        self.ax_puissance.plot(self.historique_temps_mesure, self.historique_puissance)

        self.canvas = FigureCanvasTkAgg(self.plot_puissance, master=self.power_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, pady=15, padx=5, sticky="nsew")

        self.toolbar_frame_puissance = tk.Frame(self.power_frame)
        self.toolbar_frame_puissance.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.toolbar_puissance = NavigationToolbar2Tk(self.canvas, self.toolbar_frame_puissance)
        self.toolbar_puissance.update()
        self.toolbar_puissance.grid(row=0, column=0, sticky="ew")




        # Graphique de position
        self.pos_frame = tk.LabelFrame(self.graphs_frame, text="Position dans le temps")
        self.pos_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        fig = plt.figure(figsize=(5, 4))
        self.ax = fig.add_subplot(111)
        self.ax.imshow(data_gradient_temperature(self.device.get_temperature_from_device()), origin='lower', extent=(0, 5, 0, 5), cmap='coolwarm')
        self.ax.set_xlabel("Position X [cm]")
        self.ax.set_ylabel("Position Y [cm]")
        
        self.pos_canvas = FigureCanvasTkAgg(fig, master=self.pos_frame)
        self.pos_canvas_widget = self.pos_canvas.get_tk_widget()
        self.pos_canvas_widget.grid(row=0, column=0, pady=15, padx=5, sticky="nsew")

        self.toolbar_frame_position = tk.Frame(self.pos_frame)
        self.toolbar_frame_position.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.toolbar_position = NavigationToolbar2Tk(self.pos_canvas, self.toolbar_frame_position)
        self.toolbar_position.update()
        self.toolbar_position.grid(row=0, column=0, sticky="ew")

        
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
        
        self.update_loop() # We update once at least
        

    def get_time(self):
        return(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def click_start(self):

        if not self.is_refreshing:
            self.is_refreshing = True
            self.update_loop()
            self.start_button.config(text="Arrêter")
            self.status_light.itemconfig(self.light_id, fill="green")
            # Historique communication
            self.Évènements.append(self.get_time() + ' : '+'La prise de donnée est en cours')
            #self.label_com.value_variable.set(self.get_time() + ' : '+'La prise de donnée est en cours')
            self.label_com.config(text=self.Évènements[len(self.Évènements)-1]
                                          + '\n' + self.Évènements[len(self.Évènements)-2]
                                          + '\n' + self.Évènements[len(self.Évènements)-3]
                                          + '\n' + self.Évènements[len(self.Évènements)-4]
                                          + '\n' + self.Évènements[len(self.Évènements)-5]) 
           
            
        else:
            self.is_refreshing = False
            self.start_button.config(text="Démarrer")
            self.status_light.itemconfig(self.light_id, fill="red")
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

        print(self.dico_parameters['parametre1'])
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
        self.ax_puissance.set_xlabel("Temps [s]")
        self.ax_puissance.set_ylabel("Puissance [mW]")
        self.canvas.draw()
        self.canvas.flush_events()

        self.ax.cla()  # Clears the axes
        self.ax.imshow(data_gradient_temperature(self.device.get_temperature_from_device()), origin='lower', extent=(0, 5, 0, 5), cmap='coolwarm')
        self.ax.set_xlabel("Position X [cm]")
        self.ax.set_ylabel("Position Y [cm]")
        self.pos_canvas.draw()
        self.pos_canvas.flush_events()

    def update_loop(self):

        self.device.update_from_device()

        power = self.device.power
        thermistor_values = self.device.get_temperature_from_device()

        self.historique_temps_mesure.append(self.get_time())
        self.historique_position_x.append(position(thermistor_values)[0])      # modifier pour données en temps réel
        self.historique_position_y.append(position(thermistor_values)[1])      # modifier pour données en temps réel
        self.historique_puissance.append(power)    
        self.update_plot()

        self.measurement_label.config(text=f"{power:.2f} mW")
        self.position_label.config(text=f"(x={position(thermistor_values)[0]:.2f}, "f"y={position(thermistor_values)[1]:.2f})")
       

        #last_pos = data_gradient_temperature()
        #self.plot_position.append(last_pos[0], last_pos[1])
        #self.plot_position.update_plot()
        
        if self.is_refreshing:
            self.after(300, self.update_loop)   # To-Do ajouter bouton pour modifier rate
        


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



    def click_clear(self):
        self.historique_temps_mesure = []
        self.historique_puissance = []
        # Modifier axis selon tkinter
        #self.plot_puissance.first_axis.clear()
        self.update_plot()

        # Historique communication
        self.Évènements.append(self.get_time()+ ' : '+'Mise à zéro effectuée')
        self.label_com.config(text=self.Évènements[len(self.Évènements)-1]
                                          + '\n' + self.Évènements[len(self.Évènements)-2]
                                          + '\n' + self.Évènements[len(self.Évènements)-3]
                                          + '\n' + self.Évènements[len(self.Évènements)-4]
                                          + '\n' + self.Évènements[len(self.Évènements)-5]) 
        #self.label_com.value_variable.set(self.get_time()+ ' : '+'Mise à zéro effectuée')
        
        
        #self.x_range = 10


    # suggéré la sauvegarde avant de clear    
    '''
    def save(self):
        # Implement the logic to save the collected data
        filepath = filedialog.asksaveasfilename(
            title="Save Data",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if filepath:
            with open(filepath, "w") as file:
                # Write the collected data to the file
                file.write("Collected data goes here")
            Dialog.showinfo(title="Save Successful", message="Data saved successfully!")
    '''

class PowerMeterDevice(Bindable):
    debug = True

    def __init__(self):
        super().__init__()

        """
        The variables are refreshed by get_xxx commands, which 
        fetch the actual values from the device.
        The variables represent the latest values at all times
        and can be used direectly by the app.
        """
        self.power = 0
        self.wavelength = 1064
        self.firmware = None
        self.temperature = []



    # Fonction pour obtenir la dernière valeur de voltage de la thermistance
    def get_thermistane_from_device(self):   
        pass

        # self.power = appel fonction à partir d'aquisition qui retourne une valeur de voltage (la dernière)


    def get_power_from_device(self):
        if self.debug:
            self.power = random.randrange(800,1000,1)/100
        else:
            pass # Update via USB

        return self.power

    def get_firmware_from_device(self):
        if self.debug:
            self.firmware = "1.0.0alpha1"
        else:
            pass # Update via USB

        return self.power

    def get_temperature_from_device(self):

        # self.temperature permet d'avoir la température de toutes les termistance (avant implantation aquisition)
        #self.temperature = [70,71,72,73,74,75,76,77,70] #[random.randrange(90,113,1), random.randrange(60,73,1),random.randrange(50,80,1),random.randrange(70,73,1),random.randrange(70,73,1),74,75, 76,70]  
        #print(self.temperature)
        #print(type(self.temperature))
        if self.debug:
            self.temperature = [random.randrange(70,73,1), random.randrange(70,73,1),random.randrange(70,73,1),random.randrange(70,73,1),random.randrange(70,73,1),72,74, 72,70]  
        else:
            pass # Update via USB

        return self.temperature

    def get_wavelength_from_device(self):
        if self.debug:
            pass
        else:
            pass # Update via USB

        return self.wavelength

    def update_from_device(self):
        self.get_power_from_device()
        self.get_firmware_from_device()
        self.get_temperature_from_device()
        self.get_wavelength_from_device()



