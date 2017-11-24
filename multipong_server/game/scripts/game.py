#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

## game.py

"""
game.py

Définit le Game Play
"""

from bge import logic as gl
from time import sleep
from scripts import rank_display
from scripts import message


def main():
    scenes = gl.getSceneList()
    B_keys()
    print_some()
    set_help_resolution()

    if gl.scene == "play":
        set_scene_play(scenes)
        set_positive_score()
        set_score()
        set_paddle_position()
        automatic_paddle(scenes)
        ball_out()

    if gl.scene == "rank":
        overlay_scene_rank(scenes)
        rank_display.main()

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
                    print("Suppression de la scène", str(n) + "_players")

        # Lancement du bon niveau
        overlay_scene(str(gl.level) + "_players")

        # Je viens de demander l'ajout de la scène,
        # elle ne sera effective qu'à la frame suivante
        print("Ajout de la scène ", str(gl.level))

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

def del_rank_scene(scenes):
    """Supprime la scène rank."""

    for scn in scenes :
        if "Rank" in scn.name:
            scn.end()
            print("Suppression de Rank")

def reset_variables():
    """Reset de variables pour repartir à zéro."""

    print("Reset variables in game.py")
    l = gl.level
    if l == 1:
        l = 2
    try:
        for i in range(l):
            gl.goal[i]["score"] = 10
    except:
        print("Goal non accessible")

    gl.tempo_globale = 0
    gl.level1_rated = 0
    gl.classement_level1 = {}
    gl.tempo_rank_level1 = 0
    gl.classement = {}
    gl.block = 0
    gl.transit = 0
    gl.scene = "play"
    gl.level = 1

def ball_out():
    """Remet la Ball dans le jeu si la balle sort du jeu."""

    #try:
    if gl.ball :
        if gl.ball.localPosition[0] < -15:
            gl.ball.localPosition = [3, -3, 1]
        elif gl.ball.localPosition[0] > 15:
            gl.ball.localPosition = [3, -3, 1]
        elif gl.ball.localPosition[1] < -15:
            gl.ball.localPosition = [3, -3, 1]
        elif gl.ball.localPosition[1] > 15:
            gl.ball.localPosition = [3, -3, 1]
    ##except:
        ##print("Balle non accessible")

def automatic_paddle(scenes):
    """Seulement niveau 1. Mouvement auto de la raquette machine."""

    for scn in scenes :
        if scn.name == "1_players":
            try:
                y = 0.7 * gl.ball.localPosition[1]
                gl.paddle[1].localPosition = [9.5, y, 1]
            except:
                print("Automatic paddle non accessible")

def set_score():
    """Maj des scores avec les valeurs du server."""

    if gl.level > 1:
        for player in range(gl.level):
            if gl.goal:
            #try:
                gl.goal[player]["score"] = gl.score[player]
            ##except:
                ##print("Goal non accessible")

def set_paddle_position():
    """Définit les positions des raquettes avec valeur du serveur.
    level 1 paddle 0
    level 2 paddle 0 et 1
    """

    for player in range(gl.level):
        if len(gl.paddle_pos) > 1:
            pos = [gl.paddle_pos[player][0],
                   gl.paddle_pos[player][1],
                   1]
            if gl.paddle:
                gl.paddle[player].localPosition = pos

def set_positive_score():
    """Tous les scores doivent être >= 0"""

    if gl.level == 1:
        b = 2 # le niveau 1 a 2 joueurs
    else:
        b = gl.level

    for g in range(b):
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
            try: # pb si b dans name capture
                gl.ball.localPosition = [3, -3, 1]
            except:
                print("Accès balle impossible")

def print_some():
    """Print toutes les s des valeurs permettant de debugguer."""

    if gl.tempoDict["print"].tempo == 0:
        print("Dans Blender:")

        print(  "    Envoi:\n", gl.msg_to_send)

        print(  "    Réception",
                "\n    transit", gl.transit,
                "\n    level", gl.level,
                "\n    rank_end", gl.rank_end,
                "\n    scene", gl.scene,
                "\n    score", gl.score,
                "\n    paddle_position", gl.paddle_pos,
                "\n    classement", gl.classement,
                "\n")

def set_help_resolution():
    """Text resolution."""
    gl.help_obj.resolution = 16.0 # resolution is normaly 1.0 / 72 dpi
