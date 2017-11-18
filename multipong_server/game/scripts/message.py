#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## message.py

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

    # Récupération des paddle pos
    get_paddle_position()

    msg = {"blend": {"ball":  get_ball_position(),
                     "paddle": gl.paddle_pos,
                     "reset": get_reset() }}
    return msg

def get_paddle_position():
    """Retourne la position de tuotes les paddle
    gl.paddle[1] = blender obj
    paddle_pos[1] = [2, -9]
    """

    l_cor = gl.level
    if l_cor == 1: l_cor = 2

    for i in range(l_cor):
        try:
            x = gl.paddle[i].localPosition[0]
            y = gl.paddle[i].localPosition[1]
        except:
            x, y = 2, 2
        gl.paddle_pos[i] = [x, y]


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
