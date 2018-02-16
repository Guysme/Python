#------------- Importation des bibliothèques ----------------
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from serial import *
#-------------------------------------------------------------

#print("Choisir le temps d'aquisition du capteur (second)")
#temps_aquisition=int(input())

#-------------------------------------------------------------
#                          VARIABLES
#-------------------------------------------------------------
#------------- Variable global pour le graphe ----------------
i = 0
donnee_USB = 0
# Initialisation des variable de temps
fin = 0
debut = 0
temps = 0
# Valeur max de x du graphe initial
xmax = 2
# Valeur min de x du graphe
xmin = 0
# Valeur min de y du graphe
ymin = -1
# Valeur max de y du graphe
ymax = 100


liste_donnees = []
liste_angle = []
liste_temps_relatif = []

# Temps entre deux lectures du port USB (s):
resolution_echantillon = 0.1
# Nombres d'échantillons
nombre_echantillons = 10



#-------------------------------------------------------------
#                          FONCTIONS
#-------------------------------------------------------------
#------------------ Fonctions pour le graphe -----------------
# Initialisation de l'affichage graphique
def init():
    # Titre du graphe
    plt.title("Capteur Ultra_son")
    plt.ylabel('Distance')
    plt.xlabel("Numero échantillon")
    # Configuration initiale des axes x y
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    return ln,

# Agrandissement de la fenetre pour l'affichage graphique
def agrandissement_fenetre(xmax,facteur_agrandissement):
    ax.set_xlim(xmin, facteur_agrandissement * xmax)
    ax.figure.canvas.draw()
    return facteur_agrandissement * xmax

# Fonction pour la génération des échantillons en Y de la courbe
def update(frame):
    # Variable global pour parcourir la liste de données
    global i
    global xmax
    global xmin
    global fin
    global debut
    global liste_donnees
    global temps

    # Vecteur de donnees x
    xdata.append(frame)

    # Vecteur de doonees y
    # Récupération des données sur le port USB
    if i < len(np.arange(0,nombre_echantillons,resolution_echantillon)):
        # Fin du temps entre deux aquisitions du port USB
        fin = time.time()
        temps = round(fin - debut,3)
        #print(temps)

        # Récupération des données sur le port USB en binaire
        donnee_USB_bit = serial_port.readline()

        # Debut du temps entre deux aquisitions du port USB
        debut=time.time()

        # Decodage des données binaires du port USB
        donnees_USB = donnee_USB_bit.decode(encoding='utf-8')

        # Separation des données par la virgule
        liste_donnees = donnees_USB.split(",")

        # Recuperation et affichage des donnees
        ydata.append(int(liste_donnees[0]))
        # Récupération de la données angles
        liste_angle.append(int(liste_donnees[1]))
        # Récupération de la données temps relatif
        liste_temps_relatif.append(int(liste_donnees[2]))
        #print(liste_temps_relatif)

        i += 1
    else:
        # Donnees erronees
        ydata.append(-1)
        serial_port.close()
        i += 1
    # Agrandissement de la fenetre du graphe
    if i*resolution_echantillon >= xmax:
        xmax = agrandissement_fenetre( xmax , 1.5 )
    ln.set_data(xdata, ydata)

    if i == nombre_echantillons-2*resolution_echantillon:
        quit()

    return ln,

# Fonction pour la génération des échantillons en X de la courbe
def gen_function(nombre_echantillons,resolution_echantillon):
    return np.arange(0, nombre_echantillons, resolution_echantillon)

#------------------------- Fonctions -------------------------

def parametrage_port_USB():

    numero_du_port_serie=0

    while(numero_du_port_serie == 0):
        numero_du_port_serie = int(input('Entrez le numero du port USB : '))
        port_serie = 'COM' + str(numero_du_port_serie)
        print("Vous avez sélectionner le port {0}".format(port_serie))

        if (numero_du_port_serie > 0 and numero_du_port_serie <= 6):
            try:
                serial_port = Serial(port=port_serie)
            except:
                print("Erreur de l'ouverture du port USB")
                print("Veulliez selectionner un autre port de communication\r\n")
                continue
        else:
                print("Le port de communication {0} n'existe pas".format(port_serie))
                print("Veuillez selectionner un autre port de communication\r\n")
                numero_du_port_serie = 0


    if serial_port.isOpen() is True:
        print("Le port de communication est ouvert\r\n")
        #information sur le port serie
        print(serial_port.getSettingsDict())

    return serial_port

def parametrage_arduino():
    resolution='0'
    while (resolution=='0'):
        resolution = input('Entrer la résolution souhaité 10<(ms)<1000  : ')

        if int(resolution)> 10 and int(resolution)<1000:
            serial_port.write(resolution.encode('ascii'))
        else:
            print('La résolution est incorecte')
            print('Veuillez sélectionner une autre résolution\r\n')
            continue
    # retourne la résolution de l'aquisition en seconde
    return int(resolution)/1000


def lanceprog():
    global ax
    global xdata
    global ydata
    global serial_port
    global ln

    # Pour la configuration du port USB
    #serial_port = parametrage_port_USB()
    # Valeur par défaut
    serial_port=Serial(port="COM4")

    #Pour la configuration de l'arduino
    #resolution_lecture_USB = parametrage_arduino()
    # Valeur par défaut défini dans les variables

    plt.style.use('ggplot')
    fig, ax = plt.subplots(nrows=1, ncols=1)
    xdata, ydata = [], []

    #type(ln)=matplotlib.lines.Line2D
    ln, = plt.plot([], [],'r+', animated=True)
    ani = FuncAnimation(fig, update,gen_function(nombre_echantillons,resolution_echantillon),
                        interval=resolution_echantillon*1000,repeat=False,init_func=init, blit=True)

    plt.show()

def exitprog():
    print(liste_angle)
    print(liste_temps_relatif)
    print(len(liste_temps_relatif))
    print(len(liste_angle))


if __name__ == "__main__":
    try:
        print('Utilisez Control-C pour fermer la fenetre du graph ou arreter l\'aquisition\r\n')
        lanceprog()
    except KeyboardInterrupt:
        exitprog()

