#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

## game.py

"""
game.py

Définit le Game Play

Les try sont nécessaires car les objets appelés ne sont pas toujours
présents dans les scènes à l'instant où ils sont appelés.
L'important est qu'il n'y ait pas de pass
"""

from bge import logic as gl
from time import sleep
from scripts import rank_display
from scripts import message


def main():
    """La scène Labomedia est toujours en background.
    Toujours excécuté, pour main et level_1_main"""

    scenes = gl.getSceneList()

    # Balle au centre
    B_keys()

    print_some()
    set_help_resolution()

    if gl.level == 1:
        level_1_main(scenes)
    else:
        all_level_not_1_main(scenes)

def all_level_not_1_main(scenes):
    """Tous les niveaux sauf le 1 qui n'est pas géré par le serveur."""

    if gl.scene == "play":
        set_scene_play(scenes)
        positive_score()
        set_score()
        paddle_position()
        ball_position()
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

def level_1_main(scenes):
    """Machine n'est pas géré par le serveur
    donc main() particulier pour le level 1.
    """

    if gl.scene == "play":
        set_scene_play(scenes)

    if gl.scene == "rank":
        overlay_scene_rank(scenes)
        rank_display.main()
        display_rank_level1(scenes)

    positive_score()
    set_score()
    ball_out()
    classement_level1(scenes)

    # La paddle auto est active si pas de scène rank
    if gl.level1_rated == 0:
        automatic_paddle(scenes)

    # Retour au level 1 sans bug
    if gl.reset:
        reset_variables()

def classement_level1(scenes):
    """Classement du joueur et de la machine au niveau 1.
    2 Cas:
    """

    if gl.goal[0] and gl.goal[1]:
        if gl.level1_rated == 0:
            # Cas 1: je gagne, machine perds
            if gl.goal[1]["score"] == 0: # score machine
                gl.classement_level1['machine']  = 2
                gl.classement_level1["moi"] = 1
                # Je ne repasserai plus par ici
                gl.level1_rated = 1
                # demande de la scènerank
                gl.scene = "rank"
                print("Dans niveau 1, j'ai gagné")

            # Cas 2: je perds, machine gagne
            if gl.goal[0]["score"] == 0: # mon score
                gl.classement_level1['machine']  = 1
                gl.classement_level1["moi"] = 2
                # Je ne repasserai plus par ici
                gl.level1_rated = 1
                # demande de la scènerank
                gl.scene = "rank"
                print("Dans niveau 1, machine a gagné")
        else:
            # calcul du temps d'affichage
            display_rank_level1(scenes)

def display_rank_level1(scenes):
    """Comptage du temps d'affichage seulement level 1."""

    gl.tempo_rank_level1 += 1
    if gl.tempo_rank_level1 == 2:
        print("rank Text \n{}".format(gl.text))

    if gl.tempo_rank_level1 > 240:
        # Fin de la scène rank
        del_rank_scene(scenes)
        reset_variables()

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

    try:
        if gl.ball.localPosition[0] < -15:
            gl.ball.localPosition = [3, -3, 1]
        elif gl.ball.localPosition[0] > 15:
            gl.ball.localPosition = [3, -3, 1]
        elif gl.ball.localPosition[1] < -15:
            gl.ball.localPosition = [3, -3, 1]
        elif gl.ball.localPosition[1] > 15:
            gl.ball.localPosition = [3, -3, 1]
    except:
        print("Balle non accessible")

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
            try:
                gl.goal[player]["score"] = gl.score[player]
            except:
                print("Goal non accessible")

def paddle_position():
    """Définir les positions des raquettes avec valeur du serveur."""

    for player in range(gl.level):
        try:
            # les clés de gl.paddle_position du serveur sont des str
            pos = [gl.paddle_position[str(player)][0],
                   gl.paddle_position[str(player)][1],
                   1]
            gl.paddle[player].localPosition = pos
        except:
            print("paddle non accessible")

def positive_score():
    """Tous les scores doivent être >= 0"""

    if gl.level == 1:
        b = 2 # le niveau 1 a 2 joueurs
    else:
        b = gl.level

    for g in range(b):
        try:
            if gl.goal[g]["score"] <= 0:
                gl.goal[g]["score"] = 0
        except:
            print("Goal non accessible")

def ball_position():
    """Placer la balle."""

    # Set position
    gl.ball.localPosition = [   gl.ball_position[0],
                                gl.ball_position[1],
                                1]

    if gl.transit:
        # bloquage de la balle à 1, 1
        gl.ball.localPosition = [1, 1, 1]

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

    if gl.tempoDict["frame_60"].tempo == 60:
        print(  "Envoi:", gl.msg_to_send, "\n",
                "Réception", "\n",
                "transit", gl.transit,
                "level", gl.level,
                "rank_end", gl.rank_end,
                "scene", gl.scene,
                "score", gl.score,
                "paddle_position", gl.paddle_position,
                "classement", gl.classement)


def set_help_resolution():
    """Text resolution."""
    gl.help_obj.resolution = 16.0 # resolution is normaly 1.0 / 72 dpi
