#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

## scene_objet.py

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
Récupère:
    - dans les scene _players :
        les objets ball, goal, bat quelque soit le niveau
    - dans Name:
        l'objet name
    - dans Labomedia
        l'objet Cube
    - dans Rank
        l'objet Rank_display

Fort de café !
'''


from bge import logic as gl


def main():
    # Get all scenes
    scenes = gl.getSceneList()
    for scn in scenes:
        if "_players" in scn.name:
            for obj in scn.objects:
                ## Ball
                if "ball" in str(obj):
                    gl.ball = obj

                # Pour tous les niveaux, y compris le 1
                if gl.level == 1:
                    level_corrected = 2 # 2 raquettes et 2 joueurs même au niveau 1
                else :
                    level_corrected = gl.level

                for n in range(level_corrected):
                    # Get bat
                    if str(obj) == "bat" + str(gl.level) + str(n):
                        gl.bat[n] = obj
                    # Get goal
                    if str(obj) == "goal" + str(gl.level) + str(n):
                        gl.goal[n] = obj
                    # Get cache
                    if str(obj) == "cache" + str(gl.level) + str(n):
                        gl.cache[n] = obj

        if "Name" in scn.name:
            for obj in scn.objects:
                ## Ball
                if "Name" in str(obj):
                    gl.name_obj = obj

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
