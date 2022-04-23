# -*- coding: utf-8 -*-
import csv
import os
import sys
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from pandas import DataFrame
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

import tkinter as tk
from tkinter import filedialog

# Permet de générer la carte, début du fichier html
start_map = """<!DOCTYPE html>
<html>
<head>
	<title>Map Badges</title>
	<meta charset="utf-8" />
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<link rel="shortcut icon" type="image/x-icon" href="docs/images/favicon.ico" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" integrity="sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A==" crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js" integrity="sha512-XQoYMqMTK8LvdxXYG3nZ448hOEQiglfqkJs1NOQV44cWnUrBc8PkAOcXy20w0vlaXaVUearIOBhiXZ5V3ynxwA==" crossorigin=""></script>
</head>
<body>
	<div id="mapid" style="width: 1200px; height: 800px;"></div>
<script>
	var mymap = L.map('mapid').setView([42.48, 3.028], 13);
	L.tileLayer('https://api.mapbox.com/styles/v1/\{id\}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
		maxZoom: 18,
		attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, ' +
			'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
		id: 'mapbox/streets-v11',
		tileSize: 512,
		zoomOffset: -1
	}).addTo(mymap);"""
# Marqueur 
marker_map = 'L.marker([{}, {}]).addTo(mymap).bindPopup("<b>{}</b></br> N: {}, E: {}").openPopup();\n'
# Fin du fichier html
end_map = '</script></body></html>'
# Nom du fichier sélectionner
filename = ''
# Nom du dossier cible
foldername = ''

# Selection du fichier
def UploadAction(event=None):
    global filename 
    filename = filedialog.askopenfilename()
    L1['text'] = filename
    print('Selected:', filename)

# Selection du dossier
def UploadActionFolder(event=None):
    global foldername
    foldername = filedialog.askdirectory() + '/'
    L3['text'] = foldername
    print('Selected:', foldername)

# fermeture de la fenêtre
def Destroy(event=None):
    root.destroy()

# Verifie si une chaine de caracteres est valide (pas de lettres grecques ou autre)
def is_ascii(s):
    return all(ord(c) < 128 for c in s)

# Fonction principale
def Computing(event=None):
    # Recuperation de la date et modification pour avoir la forme YYYYMMDD-hh-mm-ss
    date = str(datetime.now()).split('.')[0].replace('-','').replace(':','-').replace(' ','-')
    # Creation du dossier horodate
    os.mkdir(foldername+'/traitement_'+date)
    dirname = foldername+'/traitement_'+date+'/'
    L4['text'] = 'Calcul en cours ...'
    #Ouverture du fichier
    f = open(filename,'r')

    klines = f.readlines() # stockage des lignes du fichier dans une liste

    f.close() # fermeture du fichier

    # Nettoyage rapide des lignes du fichiers
    lines = []
    for i in klines:
        #print(i)
        # On elimine les lignes vides "", trop longue >= 12, les badges buggués [ ] et les lignes du début qui ont des ""
        if i.strip() == "" or len(i.strip()) >= 12 or '[' in i or ']' in i  or not is_ascii(i): 
            #print(i)
            klines.remove(i)
        # On retire les . , les N et E en fin de ligne 
        elif i.strip()[-1] == '.' or i.strip()[-1] == 'N' or i.strip()[-1] == 'E' :
            #print(i.strip()[:-1])
            lines.append(i.strip()[:-1])
        elif '"' in i:
            i = i.replace('"','')
            lines.append(i.strip())
        else:
            lines.append(i.strip())
    #print(lines)
    # lines est la liste des lignes "propres"

    #Recherche des indices des lignes correspondant à des heures
    ind = [] # liste des indices des lignes des heures
    for i in range(len(lines)):
        if ':' in lines[i]:
            ind.append(i)
    #print(len(ind))

    #elimination des indices des lignes non valides
    ind_cleaned = []

    for i in range(len(ind)-1):
        if ind[i + 1] - ind[i] >= 5: # Ne garde que les indices séparés de >4 lignes
            ind_cleaned.append((ind[i], ind[i+1]-ind[i])) #Stocke la paire (indice, nb de lignes d'informations)


    lines_cleaned = [] # lignes nettoyées des imponderables
    # On parcourt les lignes valides 
    for r in ind_cleaned:
        
        i, l = r[0], r[1] # i indice de la ligne et l la ligne
        t = [] # tableau qui va contenir la ligne complete (pour le moment elle est encore en petit morceaux)

        test_annee = '202' in lines[i+1]# On vérifie que l'année est 2021
        test_longueur_gps = len(lines[i+2]) <= 10 and len(lines[i+3]) <=10 # On vérifie la longueur des coordonnées GPS
        test_gps = '.' in lines[i+2] and '.' in lines[i+3] # On vérifie que ce sont des coordonnées GPS

        if test_annee and test_longueur_gps and test_gps : #elimination des lignes avec des dates non valides
            if l == 5: # si il n'y a qu'un seul badge on remplit la ligne
                for j in range(l-1):
                    t.append(lines[i+j])
                #On coupe l'element badge en deux : badge et rssi
                if ';' in lines[i+l-1]:
                    badge = lines[i+l-1].split(';')[0]
                    rssi = lines[i+l-1].split(';')[1]
                    t.append(badge)
                    t.append(rssi)
                    lines_cleaned.append(t) # On ajoute la ligne reconstituee à l'ensemble
                else:
                    pass
            else: # sinon cas ou il y a plusieurs badges, on cree une ligne par badge
                for j in range(4): # on remplit le début de la ligne (vu que les données ne changent pas)
                    t.append(lines[i+j])
                for k in range(l-4): # Puis on crée une ligne par badge 
                    t_temp = t.copy() # on copie le début de la ligne
                    if ';' in lines[i+k+4]:
                        badge = lines[i+k+4].split(';')[0]
                        rssi = lines[i+k+4].split(';')[1]
                        t_temp.append(badge) # on rajoute le badge
                        t_temp.append(rssi) # on rajoute le rssi
                        #print(t_temp)
                        lines_cleaned.append(t_temp) # On ajoute la ligne reconstituee à l'ensemble
                    else:
                        pass
                

    # On a une liste contenant les lignes stockees en liste, on organise les donnees
    header = ['Heure','Date','Coordonnee N', 'Coordonnee E', 'Badge', 'RSSI'] # noms de colonnes
    # On utilise la structure DataFrame de pandas parce que ça permet de manipuler facilement beaucoup de donnees en même temps et de faire des operations sur des colonnes entieres
    data = DataFrame(lines_cleaned, columns = header) 
    data = data.astype({'Coordonnee N': float, 'Coordonnee E': float,'RSSI': float,}) # On donne les bons types aux colonnes
    # On transforme les coordonnees en degree decimaux
    data['Coordonnee N'] = data['Coordonnee N'].apply(lambda a: ( a // 100 ) + (( a % 100 ) / 60 ))
    data['Coordonnee E'] = data['Coordonnee E'].apply(lambda a: ( a // 100 ) + (( a % 100 ) / 60 ))
    # On ajoute la colonne avec le RSSI en negatif
    data['RSSI en -dBm'] = data['RSSI']* -1
    # On trie les donnees par Badge et par RSSI 
    data = data.sort_values(by=['Badge', 'RSSI'])
    # badges_list permet d'avoir le nom de tous les badges reconnus
    badges_list = list(set(data['Badge'].tolist()))
    r = 6371000 # rayon de la Terre
    fmap = open(dirname + 'map_'+date+'.html','w') # Ouverture du fichier map
    fmap.write(start_map)
    for b in badges_list:
        mask = data['Badge'] == b
        df = data[mask]
        phi_1 = df['Coordonnee N'].values[0]
        lambda_1 = df['Coordonnee E'].values[0]
        fmap.write(marker_map.format(phi_1,lambda_1,b,phi_1,lambda_1)) # ajout du marqueur sur la carte
        # Creation des colonnes de distances
        df['Distance relative'] = 2 * r * np.arcsin(np.sqrt(np.sin((np.radians(df['Coordonnee N'] - phi_1))/2)**2 + np.cos(np.radians(df['Coordonnee N']))*np.cos(np.radians(phi_1))*np.sin((np.radians(df['Coordonnee E'] - lambda_1))/2)**2 ))
        df['Distance exacte'] = df['Distance relative'] + 1
        df['Distance estimée'] = 10 ** ((np.abs(df['RSSI en -dBm']) - 89)/ ( 10 * 5.5 ))
        
        df.to_csv( dirname + b +'.csv', index = False) # Generation des fichiers csv
    fmap.write(end_map)
    fmap.close()
    data.to_csv(dirname+'data.csv', index=False)
    L4['text'] = 'Terminé !'
    button3['text'] = 'Fermer'
    button3['command'] = Destroy


# Partie interface graphique
root = tk.Tk()
root.geometry("400x200")
root.title('Nettoyage RFID')
L = tk.Label(root, text = "Fichier de données")
L1 = tk.Label(root, text='Choisissez un fichier', fg='grey')
L.pack()
L1.pack()

button = tk.Button(root, text='Choisir',fg="blue", command=UploadAction)
button.pack()

L2 = tk.Label(root, text = "Dossier de destination")
L3 = tk.Label(root, text='Choisissez un dossier', fg='grey')
L2.pack()
L3.pack()

button2 = tk.Button(root, text='Choisir',fg="blue", command=UploadActionFolder)
button2.pack()



button3 = tk.Button(root, text="Nettoyer", fg='darkred', command=Computing)
button3.pack()

L4 = tk.Label(root, text='', fg='red')
L4.pack()

root.mainloop()

'''
# fonction de recherche d'un fichier dans tout le disque
def find_files(filename, search_path):
   result = []

   for root, dir, files in os.walk(search_path):
      if filename in files:
         result.append(os.path.join(root, filename))
   return result
'''
# Recherche du fichier RFID.TXT
#path = find_files('RFID.TXT','C:')
