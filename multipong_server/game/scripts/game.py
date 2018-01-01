#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#######################################################################
# Copyright (C) Labomedia November 2017
#
# This file is part of multipong.
#
# multipong is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# multipong is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with multipong.  If not, see <http://www.gnu.org/licenses/>.
#######################################################################

"""
game.py

Définit le Game Play
"""

from bge import logic as gl
from time import sleep
from scripts import rank_display
from scripts import message
from random import uniform
import os


def main():
    scenes = gl.getSceneList()
    B_keys()
    #print_some()
    set_help_resolution()

    if gl.scene == "play":
        set_scene_play(scenes)
        #ball_init()
        set_positive_score()
        set_paddle_position()
        if gl.level == 1:
            automatic_paddle()
        ball_out()

    if gl.scene == "rank":
        overlay_scene_rank(scenes)
        rank_display.main()

def ball_init():
    # pas utilisé
    gl.ball_start += 1
    if gl.ball_start == 10:
        # Lancement de la balle
        if gl.ball:
            print("Lancement de la balle")
            gl.ball.setLinearVelocity((0.2, 0.2, 0.0), True)

def set_paddle_position():
    """Définit les positions des raquettes avec valeur du serveur.
    si level 1,  paddle_auto overwrite ensuite
    """

    for p in range(len(gl.paddle_pos)):
        pos = [gl.paddle_pos[p][0],
               gl.paddle_pos[p][1],
               1]
        if gl.paddle[p]:
            gl.paddle[p].localPosition = pos

def automatic_paddle():
    """Seulement niveau 1. Mouvement auto de la raquette machine."""

    if gl.paddle[1] and gl.ball:
        y = 0.7 * gl.ball.localPosition[1]
        gl.paddle[1].localPosition = [9.5, y, 1]

def set_scene_play(scenes):
    """Ajoute les scenes."""

    # Sécurité, plus de rank
    for scn in scenes:
        if "Rank" in scn.name:
            scn.end()
    # Ajout de la scène de jeu au bon niveau
    set_good_level_scene(scenes)

def set_good_level_scene(scenes):
    """Lance la scene au bon niveau si un joueur arrive
    ou quitte le jeu.
    """

    # La bonne scène est-elle affichée ?
    scene_ok = 0
    for scn in scenes :
        if scn.name == str(gl.level) + "_players" :
            scene_ok = 1

    # Si la scène n'est pas ok
    if scene_ok == 0:

        # Suppression de la mauvaise scène en cours,
        # c'est forcément une scène avec "_players"
        for n in range(1, 11):
            for scn in scenes :
                if scn.name == str(n) + "_players" :
                    scn.end()
                    #print("Suppression de la scène",str(n)+"_players")

        # Lancement du bon niveau
        overlay_scene(str(gl.level) + "_players")
        gl.ball_start =0

        # Je viens de demander l'ajout de la scène,
        # elle ne sera effective qu'à la frame suivante
        #print("Ajout de la scène ", str(gl.level))

def overlay_scene(scn, overlay=1):
    """Note de la doc:
    This function is not effective immediately, the scene is queued and
    added on the next logic cycle where it will be available from
    getSceneList.
    Overlay = 1: overlay
    Overlay = 0: underlay
    """

    gl.addScene(scn, overlay)

def overlay_scene_rank(scenes):
    """Ajoute la sceène rank en overlay."""

    scene_list = []
    for scn in scenes :
        scene_list.append(scn.name)

    if not "Rank" in scene_list:
        # Overlay la scène rank
        gl.addScene("Rank", 1)

    if gl.rank_end:
        #print("Fin de rank:", gl.rank_end)
        l = gl.level
        if l == 1: l = 2
        for i in range(l):
            if gl.goal[i]:
                gl.goal[i]["score"] = 10

def del_rank_scene(scenes):
    """Supprime la scène rank."""

    for scn in scenes :
        if "Rank" in scn.name:
            scn.end()
            print("Suppression de Rank")

def ball_out():
    """Remet la Ball dans le jeu si la balle sort du jeu."""

    if gl.ball :
        if gl.ball.localPosition[0] < -15:
            gl.ball.localPosition = [3, -3, 1]
        elif gl.ball.localPosition[0] > 15:
            gl.ball.localPosition = [3, -3, 1]
        elif gl.ball.localPosition[1] < -15:
            gl.ball.localPosition = [3, -3, 1]
        elif gl.ball.localPosition[1] > 15:
            gl.ball.localPosition = [3, -3, 1]

def set_positive_score():
    """Tous les scores doivent être >= 0"""

    l = gl.level
    if l == 1: l = 2

    for g in range(l):
        if gl.goal[g]:
            if gl.goal[g]["score"] <= 0:
                gl.goal[g]["score"] = 0

def B_keys():
    """Pour la touches B, replacement de la balle.
    Pas de B sur capture name"""

    if gl.scene == "play":
        if gl.cube_obj["ball"]:
            gl.cube_obj["ball"] = False
            print("Balle au centre")
            if gl.ball:
                x = uniform(-8, 8)
                y = uniform(-8, 8)
                gl.ball.localPosition = [x, y, 1]

def print_some():
    """Print toutes les s des valeurs permettant de debugguer."""

    if gl.tempoDict["print"].tempo == 0:
        #os.system('clear')
        print("Dans Blender:")

        print(  "    Envoi:\n", gl.msg_to_send)

        print(  "\n    Réception",
                "\n    transit", gl.transit,
                "\n    level", gl.level,
                "\n    rank_end", gl.rank_end,
                "\n    scene", gl.scene,
                "\n    paddle_position", gl.paddle_pos,
                "\n    classement", gl.classement,
                "\n")

def set_help_resolution():
    """Text resolution."""
    gl.help_obj.resolution = 16.0 # resolution is normaly 1.0 / 72 dpi
