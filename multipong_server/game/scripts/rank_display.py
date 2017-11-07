#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

## rank_display.py

#############################################################################
# Copyright (C) Labomedia November 2012
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franproplin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#############################################################################

'''
Ce script est lancé avec la scène Rank

Crée et applique le texte du classement à chaque frame
'''



from bge import logic as gl

# avec
# gl.classement = {'toto': 3, 'labomedia': 2, 'gddgsg': 1}
# on doit avoir
# 1.    gddgsg + "\n\n"
# 2 .   labomedia  + "\n\n"
# 3 .   toto + "\n\n"

def main():
    create_text()
    apply_text()

def create_text():
    # Pour tous les niveaux, y compris le 1
    if gl.level == 1:
        level_corrected = 2 # 2 joueurs même au niveau 1
        gl.classement = gl.classement_level1
    else :
        level_corrected = gl.level

    # Création d'une liste avec 1 élément = 1 joueur
    text_list = [0] * level_corrected # exemple c=3 donne [0, 0, 0]

    # Si value=0, le joueur est en cours et non classé,
    # le texte sera vide, affichage du rang seulement
    a = 0
    for key, value in gl.classement.items():
        if value == 0:
            # \n\n crée les sauts de ligne
            text_list[a] = str(a+1) + ".  \n\n"
            a += 1

    # Si value!=0, le joueur est classé,
    b = 0
    for key, value in gl.classement.items():
        if value > 0:
            if key != "machine":
                # je coupe les entiers du time(), machine n'a pas de time()
                key = key[:-4]
            if len(key) > 11:
                key = key[:-10]
            # \n\n crée les sauts de ligne
            text_list[value - 1] = str(value) + " .   " + str(key) + "\n\n"
            b += 1

    # String de l'ensemble du texte à afficher
    gl.text = ""

    for c in range(level_corrected):
        gl.text = gl.text + str(text_list[c])

def apply_text():
    '''Récupération de l'objet Rank_display et sa prop Text'''

    a = "L'objet rank_obj n'est pas accesssible pour application du texte"
    try:
        gl.rank_obj["Text"] = gl.text
    except:
        print(a)
