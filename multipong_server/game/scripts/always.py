#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

## always.py

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
Lancé à chaque frame durant tout le jeu.
'''


from time import time
from bge import logic as gl
from scripts import message
from scripts import game
from scripts import scene_objet
from scripts import rank_display


def main():
    '''Lancé à chaque frame à partir de la 2ème frame.
    Cette fonction est appelée par main_init.main dans blender.
    '''

    # Première chose à faire en tout temps
    # Récupère tous les objets blender des scenes en cours
    scene_objet.main()

    # Si scène name_capture
    name_capture()

    # Update des tempo
    gl.tempoDict.update()

    # Update des messages
    message.main()

    # Update du jeu
    game.main()

def name_capture():
    '''Si le prop captured de l'objet Blender Name à True,
    Capture le nom et le sauve dans gl.my_name.
    '''

    if not gl.my_name_ok:
        if gl.name_capture:
            if gl.name_obj['captured']:
                # Get your name in Text prop
                name = gl.name_obj['yourName']

                # delete \n = Return
                name = name.rstrip()

                # je suis à peu près sûr qu'il n'y aura pas 2 noms identiques
                gl.my_name = name + str(int(time()))[-4:]
                gl.my_name_ok = 1
                gl.scene = "play"
                print("Mon nom est {}".format(gl.my_name[:-4]))

        else:
            # nom automatique uniquement avec le temps
            # je suis à peu près sûr qu'il n'y aura pas 2 noms identiques
            gl.my_name = str(int(time()))[-4:]
            gl.my_name_ok = 1
            gl.scene = "play"
            print("Mon nom est {}".format(gl.my_name[:-4]))
