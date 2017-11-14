#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

## scene_objet.py


"""
Récupère:
    - dans les scènes _players :
        les objets ball, goal, paddle quelque soit le niveau
    - dans Labomedia
        l'objet Cube
    - dans Rank
        l'objet Rank_display

Fort de café !
"""


from bge import logic as gl


def main():
    # Get all scenes
    scenes = gl.getSceneList()
    for scn in scenes:
        if "_players" in scn.name:
            for obj in scn.objects:
                # Ball
                if "ball" in str(obj):
                    gl.ball = obj

                # Pour tous les niveaux, y compris le 1
                if gl.level == 1:
                    level_corrected = 2 # 2 raquettes et 2 joueurs même au niveau 1
                else :
                    level_corrected = gl.level

                for n in range(level_corrected):
                    # Get paddle
                    # TODO changer les noms bat dans blender
                    if str(obj) == "bat" + str(gl.level) + str(n):
                        gl.paddle[n] = obj
                    # Get goal
                    if str(obj) == "goal" + str(gl.level) + str(n):
                        gl.goal[n] = obj

        if "Rank" in scn.name:
            for obj in scn.objects:
                ## "Rank_display"
                if "Rank_display" in str(obj):
                    gl.rank_obj = obj

        if "Labomedia" in scn.name:
            for obj in scn.objects:
                if "Cube" in str(obj):
                    gl.cube_obj = obj
                if "Help" in str(obj):
                    gl.help_obj = obj
