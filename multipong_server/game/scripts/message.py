#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## message.py

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


"""Envoi des messages en TCP"""


from bge import logic as gl
import json


def main():

    gl.msg_to_send = create_msg_to_send()
    send_tcp_message()

def send_tcp_message():
    if gl.msg_to_send:
        msg = json.dumps(gl.msg_to_send).encode("utf-8")
        try:
            gl.tcp_client.send(msg)
        except:
            print("Client TCP déconnecté")

def create_msg_to_send():
    """Retourne le message à envoyer au server.

        msg = {"blend": {"ball": (1,1), "reset": 0}}
    """

    msg = {"blend": {"ball":  get_ball_position(),
                     "paddle_1_pos": get_paddle_1_position(),
                     "score": get_score(),
                     "reset": get_reset() }}
    return msg

def get_paddle_1_position():
    """Retourne la position de la paddle1 à level 1."""

    if gl.level == 1:
        if gl.paddle[1]:
            x = gl.paddle[1].localPosition[0]
            y = gl.paddle[1].localPosition[1]
            return  [x, y]
    else:
        return [0, 0]

def get_score():
    """Reourne la liste des scores
    [2,3,4]
    """

    score = []
    l = gl.level
    if l == 1: l = 2

    for p in range(l):
        if gl.goal[p]:
            s = gl.goal[p]["score"]
            score.append(s)

    return score

def get_ball_position():
    """Retourne la position x, y de la balle
    donnée par le moteur physique.
    """

    try:
        x = gl.ball.localPosition[0]
        y = gl.ball.localPosition[1]
    except:
        x, y = 2, 2
    return [x, y]

def get_reset():
    """Avec la touches R, envoi sur capture name et rank."""

    if gl.cube_obj["reset"]:
        gl.reset = 1
        print("Demande de reset au serveur")
        gl.cube_obj["reset"] = False
        # Envoi au server de {"reset": 1}
        return 1
    else:
        return 0
