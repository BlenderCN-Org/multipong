#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## message.py

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
* crée le message dans un dict avec les attributs du gl

* à chaque frame, decode, dejson, puis maj des attibuts du gl
'''


from bge import logic as gl
import json
import ast


def main():

    gl.msg_to_send = create_msg_to_send()
    # à commenter pour test twisted
    send_tcp_message()

def send_tcp_message():
    if gl.msg_to_send:
        msg = json.dumps(gl.msg_to_send).encode("utf-8")
        try:
            gl.tcp_client.send(msg)
        except:
            print("Client TCP déconnecté")

def create_msg_to_send():
    '''Retourne le message à envoyer au server.

        msg = {"joueur":    {   'ball_position': [0.5, 3.3],
                                'bat_position': [-9.4, 0.0],
                                'my_score': 9,
                                'my_name': 'ggffg1456048730'}
    '''

    msg = {"joueur": {  "my_name":       gl.my_name,
                        "ball_position": get_ball_position(),
                        "my_score":      get_my_score(),
                        "bat_position":  get_bat_position(),
                        "reset":         get_reset()
                     }}

    return msg

def get_my_score():
    '''Retourne mon score, je suis 0.'''
    try:
        score = gl.goal[gl.I_am]["score"]
    except:
        score = 10
    return score

def get_bat_position():
    '''Retourne la position x, y de ma bat, je suis 0.'''

    try:
        x = gl.bat[0].localPosition[0]
        y = gl.bat[0].localPosition[1]
    except:
        x, y = 0, 0
    #return [round(x, 2), round(y, 2)]
    return [x, y]

def get_ball_position():
    '''Retourne la position x, y de ma balle donnée par le moteur physique.
    Le joueur 0 du server donne la position pour tous les autres.
    '''
    try:
        x = gl.ball.localPosition[0]
        y = gl.ball.localPosition[1]
    except:
        x, y = 2, 2
    #return [round(x, 2), round(y, 2)]
    return [x, y]

def get_bat_position():
    '''Position x, y de ma bat.'''

    try:
        x = gl.bat[gl.I_am].localPosition[0]
        y = gl.bat[gl.I_am].localPosition[1]
    except:
        x, y = 0, 0
    #return [round(x, 2), round(y, 2)]
    return [x, y]

def get_reset():
    '''Avec la touches R, envoi sur capture name et rank.'''

    if gl.cube_obj["reset"]:
        gl.reset = 1
        print("Demande de reset au serveur")
        gl.cube_obj["reset"] = False
        # Envoi au server de {"reset": 1}
        return 1
    else:
        return 0
