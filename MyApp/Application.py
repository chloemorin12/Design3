from mytk import *
#from mytk.figures import HeatMap
from mytk.indicators import *
from mytk import Figure
from tkinter import filedialog, messagebox
import random
from testChloe import data_gradient_temperature, position
import matplotlib.pyplot as plt
import matplotlib, sys
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime


class PowerMeterApp(App):
    def __init__(self):
        App.__init__(self)

        
        self.ct = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.historique_puissance = []
        self.historique_temps_mesure = []
        self.historique_position_x = []
        self.historique_position_y = []



        self.window.widget.title("Powermeter")
        

        #self.window.row_resize_weight(0,0) 
        #self.window.row_resize_weight(1,0)
        #self.window.row_resize_weight(2,1)
        #self.window.column_resize_weight(0,1) 
        #self.window.column_resize_weight(1,1)

        self.window.column_resize_weight(index=0, weight=1)
        #self.window.column_resize_weight(index=0, weight=5)
        # Commandes 
        Position_row1_X = 20
        Position_row1_Y = 20
        Longueur_bouton = 150
        Hauteur_bouton = 35
        intersite_X = 15
        intersite_Y = 15


        self.Évènements = ['', '', '', ''] # Liste des communications à enregistrer dans un fichier

        # GRID version
        
        #self.button_group = View(width=800, height=1000)
        #self.button_group.grid_into(self.window, row=0, column=0, pady=5, padx=5, sticky="nsew")

        self.button_group2 = View(width=90, height=200)
        self.button_group2.grid_into(self.window, row=0, column=1, pady=5, padx=5, sticky="nsew")

        self.box_longueur_onde = Box("Longueur d'onde")
        self.box_longueur_onde.grid_into(self.window, row=0, column=1, columnspan=1, padx=5, pady=5, sticky="nsew")

        self.box = Box("Actions")
        self.box.grid_into(self.window, row=0, column=0, columnspan=1, padx=25, pady=10, sticky="nsew")


        self.box2 = Box("Puissance dans le temps")
        self.box2.grid_into(self.window, row=1, column=0, columnspan=1, padx=25, pady=10, sticky="nsew")
        
        self.box4 = Box("Position")
        self.box4.grid_into(self.window, row=1, column=1, columnspan=1, padx=25, pady=10, sticky="nsew")



        #self.puissance_group = View(width=1000, height=300)
        #self.puissance_group.grid_into(self.window, row=1, column=0, pady=5, padx=5, sticky="nsew")



        # Démarrer/Arrêter
        self.start_button = Button("Démarrer", user_event_callback=self.click_start)
        self.start_button.grid_into(self.box, row=0, column=1, pady=15, padx=5, sticky="w")

        # Indicateur marche/arret
        self.running_indicator = BooleanIndicator(diameter=25)
        self.running_indicator.grid_into(self.box, row=0, column=0, pady=15, padx=5)

        # Mise à zéro : Initialisation prise de donnée ? Détecte si la température est trop élevée ?
        self.misea0 = Button("Mise à zéro", user_event_callback=self.click_clear)
        self.misea0.grid_into(self.box, row=0, column=2, pady=15, padx=5)

         # Paramètre : Permet d'aller choisir un fichier avec les valeurs ?
        self.paramètre = Button("Paramètres", user_event_callback=self.click_chose_parametres)
        self.paramètre.grid_into(self.box, row=0, column=3, pady=15, padx=5)

        # Connexion : Permet de se connecter en un clic peut importe le port de connexion utilisé
        # Ouverture d'une autre fenêtre ?  radiobutton
        self.connexion = Button("Connexion")
        self.connexion.grid_into(self.box, row=0, column=4, pady=15, padx=5)
        
        # Graphique puissance dans le temps
        self.plot_puissance = XYPlot(figsize=(9,4))
        self.plot_puissance.grid_into(self.box2, row=1, column=0, pady=15, padx=5)

        self.autre = View(width=800, height=300)
        self.autre.grid_into(self.window, row=2, column=0, pady=5, padx=5, sticky="nsew")

        # Graphique position
        #self.plot_position = XYPlot(figsize=(5,4))
        #self.plot_position.grid_into(self.puissance_group, row=0, column=1, pady=15, padx=5)

        # À enlever lorsque la fonction data_gradient_temperature sera fonctionnelle
        self.plot_position = XYPlot(figsize=(5,4))
        #self.plot_position.axes = 'Y'
        #self.plot_position.first_axis.set_y
        self.plot_position.grid_into(self.box4, row=0, column=0, pady=5, padx=5)
        
        self.wavelength_entry = LabelledEntry("Wavelength:", character_width=6)
        self.wavelength_entry.grid_into(self.button_group2, row=0, column=0, sticky="e")
            
        self.firmware_label = Label()
        self.firmware_label.grid_into(self.button_group2, row=1, column=0, padx=25, pady=10, sticky="w")

        size = 15
        self.bigb_font = tkFont.Font(family='Helvetica', size=size, weight='bold')
        self.big_font = tkFont.Font(family='Helvetica', size=size)
        self.measurement_label = Label("--- mW", font=self.big_font)
        self.measurement_label.grid_into(self.box2, row=2, column=0, pady=15, padx=5)


        self.position_label = Label("---", font=self.big_font)
        self.position_label.grid_into(self.box4, row=2, column=0, pady=15, padx=5)

        self.save_button = Button("Enregister les données", user_event_callback=self.click_save)
        self.save_button.grid_into(self.box, row=0, column=5, padx=10, pady=10)

        
        # Quitter l'interface: Voir directement dans dans app.py quit()
        # Ajouter pop-up : suggérer sauvegarde des données
        #self.quitter = Button("Quitter", user_event_callback=self.Suggest_save)
        #self.quitter.grid_into(self.box, row=0, column=6, pady=15, padx=5)

        # Communication
        self.box3 = Box("Communication")
        self.box3.grid_into(self.autre, row=0, column=0, columnspan=1, padx=25, pady=10, sticky="nsew")
        self.Évènements.append(self.get_time() + ' : ' + 'Démarrage Interface')
        self.label_com = Label(self.get_time() + ' : ' + 'Démarrage Interface')
        self.label_com.grid_into(self.box3, row=0, column=0, columnspan=1, padx=25, pady=10, sticky="nsew")
        #Changer la couleur du box3, ou trouver élément pour communiquer avec l'usager

        # Barre de progression
        self.progression = Level(width=800, height=30)
        self.progression.grid_into(self.window, row=3, column=0, pady=25, padx=15)
        # bindable pour lier l'avancement des fonction avec la barre de progression 

    






        #heatmap = HeatMap(figsize=(5, 4))
        #heatmap.create_widget(self.box4, data_gradient_temperature)
        #heatmap.widget.grid(row=0, column=0, pady=15, padx=5)

        
        #fig = plt.figure(figsize=(5, 4))
        #ax = fig.add_subplot(111)
        #ax.imshow(data_gradient_temperature(), origin='lower', extent=(0, 5, 0, 5), cmap='coolwarm')
        #self.canvas.draw()
        #fig.widget.grid(row=0, column=0, pady=15, padx=5)

        '''
        Last try
        fig = Figure(figsize=(5, 4))
        fig.create_widget(self.box4, data_gradient_temperature)
        fig.widget.grid(row=0, column=0, pady=15, padx=5)
        '''

        #plt.colorbar(label='Temperature (°C)')
        #plt.title("Heat Source Localization using Gaussian Fit")
        #ax.set_xticklabels(["X Position"])
        #ax.set_yticklabels(["Y Position"])

        #canvas = FigureCanvasTkAgg(fig, self.window.widget)
        #canvas.draw()
        #canvas.get_tk_widget().grid(row=0, column=0, pady=15, padx=5)
        #canvas.grid_into(self.box4, row=0, column=0, pady=15, padx=5)




        #self.box = Box("Puissance")
        #self.box2 = Box("Position", width=250)
        #self.box.grid_into(self.window, row=2, column=0, padx=10, pady=10, sticky="nsew")
        #self.box2.grid_into(self.window, row=0, column=1, columnspan=1, padx=10, pady=10, sticky="nsew")



        
        #self.clear_button = Button("Mise à zéro", user_event_callback=self.click_clear)
        #self.clear_button.grid_into(self.box, row=0, column=5, padx=10, pady=10)
        '''
        self.wavelength_entry = LabelledEntry("Wavelength:", character_width=6)
        self.wavelength_entry.grid_into(self.window, row=1, column=4, sticky="e")
        self.firmware_label = Label()
        self.firmware_label.grid_into(self.window, row=3, column=0, columnspan=3, padx=25, pady=10, sticky="w")
        '''
        self.device = PowerMeterDevice()
        self.is_refreshing = False

        self.device.bind_properties("wavelength", self.wavelength_entry.entry, "value_variable")
        self.device.bind_properties("firmware", self.firmware_label, "value_variable")
        self.bind_properties("is_refreshing", self.running_indicator, "value_variable")
        #self.bind_properties("is_refreshing", self.start_button, "is_disabled") # Permet de désactiver les boutons 
        self.bind_properties("is_refreshing", self.wavelength_entry.entry, "is_disabled")
        
        self.update_loop() # We update once at least

    def get_time(self):
        return(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def click_start(self, event, button):

        if not self.is_refreshing:
            self.is_refreshing = True
            self.update_loop()
            button.label = "Arrêter"
            # Historique communication
            self.Évènements.append(self.get_time() + ' : '+'La prise de donnée est en cours')
            #self.label_com.value_variable.set(self.get_time() + ' : '+'La prise de donnée est en cours')
            self.label_com.value_variable.set(self.Évènements[len(self.Évènements)-1]
                                          + '\n' + self.Évènements[len(self.Évènements)-2]
                                          + '\n' + self.Évènements[len(self.Évènements)-3]
                                          + '\n' + self.Évènements[len(self.Évènements)-4]
                                          + '\n' + self.Évènements[len(self.Évènements)-5]) 
           
            
        else:
            self.is_refreshing = False
            button.label = "Démarrer"
            # Historique communication
            self.Évènements.append(self.get_time()+ ' : '+'La prise de donnée est mise en pause')
            #self.label_com.value_variable.set(self.get_time()+ ' : '+'La prise de donnée est mise en pause')
            self.label_com.value_variable.set(self.Évènements[len(self.Évènements)-1]
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


    def Suggest_save(self, event, button):        

        # To Do : Empêcher d'autres action lorsque cette fenêtre est ouverte

        # Autre option : Dialog.showinfo
        self.Message = Dialog(dialog_type='warning' ,title="Sauvegarde", message = "Souhaitez-vous enregistrer les données de la dernière aquisition avant de quitter ?", buttons_labels= ['Save', 'Cancel', 'Quit without saving'])
        
        #print(self.Message.buttons)
        #print(self.Message.buttons_labels)
        #self.Message_enregistrement = Dialog.showwarning( "Souhaitez-vous enregistrer les données de la dernière aquisition avant de quitter ?", "Sauvegarde") # auto_click=('Save', 'cancel'))
        #self.Message.button_labels = ['Enregistrer les données', 'Quitter sans enregistrer les données']
        #self.wid = self.Message.create_widget(self.window)
        #self.wid.title = "Sauvegarde"
        
        #self.Message_enregistrement.create_behavior_buttons()
        #Dialog(dialog_type=NONE ,title='test', message = 'save?', buttons_labels=['Save', 'Cancel', 'Quit without saving'])
        
        
        #(dialog_type=NONE ,title='test', message = 'save?', buttons_labels=['Save', 'Cancel', 'Quit without saving']) 



        #self.Message_enregistrement.
        
        #self.Message_replies = self.Message_enregistrement.Replies( 
        # auto_click = save, timout = go
        #dialog() : méthode button_labels = []


        #Dialog(dialog_type=Warning, title="Sauvegarde", message="Souhaitez-vous enregistrer les données de la dernière aquisition avant de quitter ?", buttons_labels = 'Enregistrer les données', auto_click=(None, None)))



        #self.Message_enregistrement.bind_properties("reply", self, "reply")
       
        #self.suggest_save_window = Window("500x300", 'Sauvegarde')
        #self.suggest_save_window.place_into(self.window, 1000, 300, 500, 300)
        #messagebox.Message('TEST')
        #self.avertissemnet = Label("Souhaitez-vous enregistrer les données de la dernière aquisition avant de quitter ?")
        #self.avertissemnet.create_widget(self.suggest_save_window)
        #self.avertissemnet.widget.place(self.suggest_save_window, 0, 150, 100, 50)
        #self.save_2 = Button("Enregistrer les données", user_event_callback=self.click_save)
        #self.save_2.place_into(self.suggest_save_window, 500,100,500,200)
        #self.Quit_2 = Button("Quitter sans enregistrer les données") # Ajouter fonction pour fermer le programme
        #self.Quit_2.place_into(self.suggest_save_window, 300,100,500,200)
        #self.suggest_save_window.place_into()


    def click_chose_parametres(self, event, button):
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
        self.label_com.value_variable.set(self.Évènements[len(self.Évènements)-1]
                                          + '\n' + self.Évènements[len(self.Évènements)-2]
                                          + '\n' + self.Évènements[len(self.Évènements)-3]
                                          + '\n' + self.Évènements[len(self.Évènements)-4]
                                          + '\n' + self.Évènements[len(self.Évènements)-5]) 
       
        file.close()
        
                

    def update_loop(self):

        
        self.device.update_from_device()

        power = self.device.power
        self.historique_temps_mesure.append(self.get_time())
        self.historique_position_x.append(position()[0])      # modifier pour données en temps réel
        self.historique_position_y.append(position()[1])      # modifier pour données en temps réel

        self.measurement_label.value_variable.set(f"{power:.2f} mW")
        self.position_label.value_variable.set(f"(x={position()[0]:.2f}, "f"y={position()[1]:.2f})")
        #self.plot_position.first_axis

        last = len(self.plot_puissance.x)
        self.plot_puissance.append(last, power)
        self.historique_puissance.append(power)    
        self.plot_puissance.update_plot()

        last_pos = data_gradient_temperature()
        self.plot_position.append(last_pos[0], last_pos[1])
        self.plot_position.update_plot()
        #self.measurement_label.value_variable.set(f"({last_pos[0]:.2f}, {last_pos[1]:.2f})") # affichage valeur position
        #plt.imshow(last_pos[2], origin='lower', extent=(0, 5, 0, 5), cmap='coolwarm')
        if self.is_refreshing:
            self.after(300, self.update_loop)



    # Modifier la fonction updat_loop pour les valeur de la thermistance

    
        
    def click_save(self, event, button):

        filepath = filedialog.asksaveasfilename(
            parent=self.window.widget,
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



    def click_clear(self, event, button):
        #print(self.plot_puissance.x, self.plot_puissance.y)
        #self.plot_puissance.clear_plot()
        self.plot_puissance.x = []
        self.plot_puissance.y = []
        self.plot_puissance.first_axis.clear()
        self.plot_puissance.update_plot()

        # Historique communication
        self.Évènements.append(self.get_time()+ ' : '+'Mise à zéro effectuée')
        self.label_com.value_variable.set(self.Évènements[len(self.Évènements)-1]
                                          + '\n' + self.Évènements[len(self.Évènements)-2]
                                          + '\n' + self.Évènements[len(self.Évènements)-3]
                                          + '\n' + self.Évènements[len(self.Évènements)-4]
                                          + '\n' + self.Évènements[len(self.Évènements)-5]) 
        #self.label_com.value_variable.set(self.get_time()+ ' : '+'Mise à zéro effectuée')
        
        
        #self.x_range = 10


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
        self.temperature = None



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
        if self.debug:
            self.temperature = random.randrange(70,73,1)
        else:
            pass # Update via USB

        return self.power

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
