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

    msg = {"blend": {"ball":  get_ball_position(),
                     "reset": get_reset() }}
    #print("envoi de blend msg", msg)
    return msg


def get_ball_position():
    """Retourne la position x, y de ma balle donnée par le moteur physique.
    Le joueur 0 du server donne la position pour tous les autres.
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
