# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 23:21:54 2022

@author: Maxfo
"""

import os
import datetime


def importCoordinates(path, sepa = "\t") :
    """
    Import des points a partir d'un fichier

    Parameters
    ----------
    path : str
        chemin et/ou nom du fichier ou sont stockes les donnees
    sepa : str, optional
        Separateur. The default is "\t".

    Returns
    -------
    pts : dict
        dictionnaire avec les coordonnees des sessions

    """
    pts = {}
    file = open(path, 'r')
    line = file.readline()
    while line :
        if len(line) > 0 :
            if line[0] != ("#" or "?" or "*" or "%") :
                data = line.strip().split(sepa)
                if len(data) >= 4 :
                    pts.update({data[0]:{'E_MN95':float(data[1]),
                                         'N_MN95':float(data[2]),
                                         'H_RAN95':float(data[3])}})
        line = file.readline()
    file.close()
    return pts


def createFileLTOPGNSS(path, options={}) :
    """
    Lecture des repertoires de sessions pour creer les fichiers pour LTOP

    Parameters
    ----------
    path : str
        Chemin du repertoire ou sont stockes les dossiers des divers sessions
    options : dict, optional
        dictionnaire d'options. The default is {}.
        
        options = {'MES':True,
                   'path_MES':None,
                   'KOO':True,
                   'path_KOO':None,
                   'points_fixes':None}

    Returns
    -------
    res : dict
        Dictionnaire de resultat

    """
    
    ## Creations des listes de repertoires
    dir_list = os.listdir(path)
    sessions = {}
    for element in dir_list :
        if "session" in element : 
            new_path = os.path.join(path, element)
            if os.path.isdir(new_path):
                new_dir_list = os.listdir(new_path)
                session_temp = []
                for subelement in new_dir_list :
                    if os.path.isdir(os.path.join(new_path, subelement)) == False and "session" in subelement and "MN95" in subelement and "RAN95" in subelement and ".txt" in subelement :
                        session_temp.append(subelement)
                    sessions.update({element:session_temp})
                
    ## Parcours des sessions pour recuperer les coordonnees dans les fichier
    coordinates = {}
    for key in sessions.keys() :
        folder = os.path.join(path, key)
        if len(sessions[key]) == 1 :
            file = sessions[key][0]
            file_path = os.path.join(folder, file)
            coord_temp = importCoordinates(file_path)
            coordinates.update({key:coord_temp})
    
    # Creation du fichier d'observations
    if "MES" in options.keys() :
        if options["MES"] == True :
            path_export = os.path.join(path, "GNSS.MES")
            
            if "path_MES" in options.keys() :
                if options["path_MES"] != None :
                    path_export = options["path_MES"]
                    
            createFileLTOPGNSS_MES(path_export, coordinates)

    # Creation du fichier des coordonnees
    if "KOO" in options.keys() :
        if options["KOO"] == True :
            path_export = os.path.join(path, "GNSS.KOO")
            
            if "path_KOO" in options.keys() :
                if options["path_KOO"] != None :
                    path_export = options["path_MES"]
                    
            if "points_fixes" in options.keys() :
                points_fixes = {}
                if options["points_fixes"] != None :
                    points_fixes = options["points_fixes"]
            
            createFileLTOPGNSS_KOO(path_export, coordinates, points_fixes)
    
    # dictionnaire de resultat
    res = {}
    res.update({'list_sessions':sessions})
    res.update({'sessions_coordinates':coordinates})
    return res


def createFileLTOPGNSS_MES(path, coordinate) :
    """
    Creation du fichier des observations avec toutes les sessions

    Parameters
    ----------
    path : str
        chemin et/ou nom du fichier ou l'on veut enregistrer le fichier
    coordinate : dict
        dictionnaire des coordonnees par session
        {cle:donnee}
        cle : str
            numero de point
        donnee : dict
            coordonnees des points
            {'E_MN95':X,
             'N_MN95':X,
             'H_RAN95':X}

    Returns
    -------
    None.

    """
    file = open(path, "w")
    file.write("**File created "+datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")+" @"+os.getlogin()+'\n')
    file.write("$$ME\n")
    for key, data in coordinate.items() :
        file.write("SL{:20s}            {:6s}{:4s}\n".format(key.upper(),"","-------"))
        ecart_plani = 2.0
        ecart_haut = ecart_plani*3
        for cle, donne in data.items() :
            file.write("LY{:18s}{:>16.4f}{:>6.3f}\n".format(cle,donne['E_MN95'],ecart_plani))
            file.write("LX{:18s}{:>16.4f}{:>6.3f}\n".format(cle,donne['N_MN95'],ecart_plani))
            file.write("LZ{:18s}{:>16.4f}{:>6.3f}\n".format(cle,donne['H_RAN95'],ecart_haut))
        file.write("*"*50+"\n")
    file.close()
    print("FILE CREATED : ",path)


def createFileLTOPGNSS_KOO(path, coordinate, pt_fixe={}) :
    """
    Creation d'un fichier de coordonnees (fixes ou approchees)

    Parameters
    ----------
    path : str
        chemin et/ou nom du fichier ou l'on veut enregistrer le fichier
    coordinate : dict
        dictionnaire des coordonnees par session
        {cle:donnee}
        cle : str
            numero de point
        donnee : dict
            coordonnees des points
            {'E_MN95':X,
             'N_MN95':X,
             'H_RAN95':X}
    pt_fixe : dict, optional
        dictionnaire des coordonnees par session. Par defaut : {}.
        {cle:donnee}
        cle : str
            numero de point
        donnee : dict
            coordonnees des points
            {'E_MN95':X,
             'N_MN95':X,
             'H_RAN95':X}

    Returns
    -------
    None.

    """
    ## Creation d'un dictionnaire avec les points et points fixes
    res = {}
    if len(pt_fixe) > 0 :
        for key, data in pt_fixe.items() :
            if key not in res.keys() :
                res.update({key:{'E_MN95':data['E_MN95'],
                                 'N_MN95':data['N_MN95'],
                                 'H_RAN95':data['H_RAN95']}})
    
    for key, data in coordinate.items() :
        for cle, donne in data.items() :
            if cle not in res.keys() :
                res.update({cle:{'E_MN95':donne['E_MN95'],
                                 'N_MN95':donne['N_MN95'],
                                 'H_RAN95':donne['H_RAN95']}})
    
    file = open(path, "w")
    file.write("**File created "+datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")+" @"+os.getlogin()+'\n')
    file.write("$$PK\n")
    if len(pt_fixe) == 0 :
        file.write("**ATTENTION aux coordonnées des points fixes !! Elles ne sont pas renseignées !!\n")
    for key, data in res.items() :
        file.write("{:10s}{:4s} {:2s}               {:12.4f}{:12.4f}    {:10.4f}    LV\n".format(key,"","",data['E_MN95'],data['N_MN95'],data['H_RAN95']))
    file.close()
    print("FILE CREATED : ",path)
