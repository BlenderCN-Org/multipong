#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

## always.py


"""
Lancé à chaque frame durant tout le jeu.
"""


from time import time
from bge import logic as gl
from scripts import message
from scripts import game
from scripts import scene_objet
from scripts import rank_display


def main():
    """Lancé à chaque frame à partir de la 2ème frame.
    Cette fonction est appelée par main_init.main dans blender.
    """

    # Première chose à faire en tout temps
    # Récupère tous les objets blender des scenes en cours
    scene_objet.main()

    # Update des tempo
    gl.tempoDict.update()

    if gl.tempoDict["frame_60"].tempo == 10:
        gl.scene = "play"

    # Update des messages
    message.main()

    # Update du jeu
    game.main()
