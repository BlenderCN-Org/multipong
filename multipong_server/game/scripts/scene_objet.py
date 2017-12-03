#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

## scene_objet.py

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
    # Reset
    gl.ball = None
    gl.goal = { 0 : None,
                1 : None,
                2 : None,
                3 : None,
                4 : None,
                5 : None,
                6 : None,
                7 : None,
                8 : None,
                9 : None }
    gl.paddle = {   0 : None,
                    1 : None,
                    2 : None,
                    3 : None,
                    4 : None,
                    5 : None,
                    6 : None,
                    7 : None,
                    8 : None,
                    9 : None }

    l = gl.level
    if gl.level == 1:
        l = 2

    scenes = gl.getSceneList()
    for scn in scenes:
        if "_players" in scn.name:
            for obj in scn.objects:
                # Ball
                if "ball" in str(obj):
                    gl.ball = obj

                # TODO finir bat to paddle dans blender
                # oter les caches
                for n in range(l):
                    # Get paddle
                    if str(obj) == "paddle" + str(gl.level) + str(n):
                        gl.paddle[n] = obj

                    # Get goal
                    if str(obj) == "goal" + str(gl.level) + str(n):
                        gl.goal[n] = obj

        if "Rank" in scn.name:
            for obj in scn.objects:
                if "Rank_display" in str(obj):
                    gl.rank_obj = obj

        if "Labomedia" in scn.name:
            for obj in scn.objects:
                if "Cube" in str(obj):
                    gl.cube_obj = obj
                if "Help" in str(obj):
                    gl.help_obj = obj
