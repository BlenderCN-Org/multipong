#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# once.py

# #####################################################################
# Copyright (C) Labomedia November 2017
#
# This file is part of multipong.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# #####################################################################


"""
Ce script est appelé par main_init.main dans blender
Il ne tourne qu'une seule fois pour initier les variables
qui seront toutes des attributs du bge.logic (gl)
Seuls les attributs de logic sont stockés en permanence.

Un thread est crée pour recevoir le multicast.
Lancement d'un socket TCP pour envoyer au serveur sur la même machine.

Le thread oblige a lancer le jeu avec le blenderplayer, sinon si il est
lancé dans blender avec "P", le thread continuera lorsque le jeu sera
terminé avec Echap.
"""


import os
import ast
import json
import threading
from time import sleep, time

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

from mylabotools.labconfig import MyConfig
from mylabotools.labtempo import Tempo
from mylabotools.labtcpclient import LabTcpClient
from scripts import game
from bge import logic as gl

# Variable globale
ini_file = "scripts/mp.ini"


class MulticastClient(DatagramProtocol):
    """Ce client reçoit les datas du serveur."""

    def startProtocol(self):
        """Ticket sur le groupe multicast."""

        # Join the multicast address, so we can receive replies:
        self.transport.joinGroup(gl.multi_ip)

        print("\nClient Multicast sur {}\n".format(gl.multi_addr))

    def datagramReceived(self, datagram, address):
        """Réception, demande de traitement."""

        data = datagram_decode(datagram)

        if data:
            self.datagram_sorting(data)

    def datagram_sorting(self, data_dict):
        """Met à jour les variables avec les valeurs reçues. data=dict=

        {"svr_msg": {"ip": self.ip_server, "dictat": {"level": 1,
                                                        etc..}}}
        """

        data = data_dict["svr_msg"]

        if "ip" in data:
            gl.ip_server = data["ip"]

        if "dictat" in data:
            data = data["dictat"]

            if data:
                if gl.scene == "play" or gl.scene == "rank":
                    if isinstance(data, dict):
                        self.tri_msg(data)

    def tri_msg(self, data):
        """Set des variables attributs du game logic."""

        if "level" in data:
            gl.level = data["level"]

        if "reset" in data:
            if data["reset"]:
                print("Reset reçu du serveur")
                init_variable()
                reset_scores()

        if "match_end" in data:
            gl.rank_end = data["match_end"]

        if "scene" in data:
            gl.scene = data["scene"]

        if "who_are_you" in data:
            gl.who = data["who_are_you"]

        if "paddle" in data:
            gl.paddle_pos = data["paddle"]
            sorted_paddle()

        if "classement" in data:
            gl.classement = data["classement"]

        if "transit" in data:
            gl.transit = data["transit"]


def sorted_paddle():
    """Crée une liste avec les paddles des joueurs 0, 1, 2, ....
    gl.paddle_pos = {   'toto': [1.2, 5.6],
                        'qui': [],
                        'quoi': []}
    gl.who = {'toto':1, 'qui':2, 'quoi':0}
    """

    p_pos = []
    l = gl.level
    if l == 1: l = 2

    for i in range(l):
        for k, v in gl.who.items():
            if v == i:
                p_pos.append(gl.paddle_pos[v])

    gl.paddle_pos = p_pos

def reset_scores():
    """Reset de variables pour repartir à zéro."""

    print("Reset variables in game.py")
    l = gl.level
    if l == 1:
        l = 2

    for i in range(l):
        if gl.goal[i]:
            gl.goal[i]["score"] = 10
            print("Tous les scores = 10")

def datagram_decode(datagram):
    """Decode la réception qui est des bytes, pour obtenir un dict.
    Ne fonctionne qu'avec un msg contenant un dict.
    """

    try:
        dec = datagram.decode("utf-8")
    except:
        print("Décodage UTF-8 inutile !")
        dec = datagram

    try:
        msg_dict = ast.literal_eval(dec)
    except:
        print("ast.literal_eval raté")
        msg_dict = None

    if isinstance(msg_dict, dict):
        return msg_dict
    else:
        print("Mauvais message reçu")
        return None

def get_conf():
    """Récupère la configuration depuis le fichier *.ini."""

    # Le dossier courrant est le dossier dans lequel est le *.blend
    current_dir = gl.expandPath("//")
    print("Dossier courant depuis once.py {}".format(current_dir))
    gl.once = 0

    gl.ma_conf = MyConfig(current_dir + ini_file)
    gl.conf = gl.ma_conf.conf

    print("\nConfiguration du jeu multipong:")
    print(gl.conf, "\n")

def init_variable():
    """Valeurs par défaut de tous les attributs du bge.logic"""

    # state possible:play rank labo
    gl.scene = "labo"

    # msg à envoyer
    gl.msg_to_send = None

    # Défini par le serveur
    gl.level = 1
    gl.block = 0
    gl.rank_end = 0
    gl.who = {}

    # Rank
    gl.text = ""
    gl.classement =  {}  # {'toto': 3, 'labomedia': 2, 'gddgsg': 1}

    # vient du server
    gl.ball_position = [0, 0] # liste
    gl.score = []

    # de la réception
    gl.paddle_pos = [[0, 0]] * 10

    gl.ip_server = None
    gl.multi_ip = gl.conf["multicast"]["ip"]
    gl.multi_port = gl.conf["multicast"]["port"]
    gl.multi_addr = gl.multi_ip, gl.multi_port
    gl.tcp_port = gl.conf["tcp"]["port"]

    gl.reset = 0

    # gestion du changement du nombre de joueur
    gl.transit = 0

def init_blender_obj():
    """Définit les variables qui permettront d'accéder aux objects de blender.
    """

    # Cube de Labomedia
    gl.cube_obj = 0
    # L'objet qui permet d'afficher le texte du classement
    gl.rank_obj = 0
    # L'objet du bas de Labomedia
    gl.help_obj = 0

    gl.land = None
    gl.filet = None

    # permet accès aux objet blender score et leur score
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

    # All paddle
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

    gl.ball = 0  # objet blender ball
    gl.ball_start = 0

def init_tempo():
    """ * tempo_liste = [("intro", 60), ("print", 12), ("sound", 6)]
        * tempoDict = Tempo(tempo_liste)
        * tempoDict.update()
    """

    tempo_liste = [("always", 100000000), ("frame_60", 60), ("print", 300)]
    gl.tempoDict = Tempo(tempo_liste)

def multicast():
    """Lance le reator pour multicast"""

    reactor.listenMulticast(gl.multi_port, MulticastClient(), listenMultiple=True)
    reactor.run(installSignalHandlers=False)

def multicast_thread():
    """Le client est dans un thread."""

    thread_s = threading.Thread(target=multicast)
    thread_s.start()

def create_tcp_socket():
    """Client TCP connecté"""

    gl.tcp_client = LabTcpClient(gl.ip_server, gl.tcp_port)

def main():
    """Lancé une seule fois
    à la 1ère frame au début du jeu par main_once.
    """

    print("Initialisation du jeu lancé un seule fois.")

    get_conf()
    init_variable()
    init_blender_obj()
    init_tempo()

    # Lancement du thread multicast
    multicast_thread()

    t0 = time()
    t1 = t0 + 10
    # Récupération de ip serveur sur multicast
    while not gl.ip_server:
        sleep(0.5)
        print("\nAttente ip du serveur ...")
        print(".........................\n")

        if time() - t1 > 0:
            print("\nVous devez lancer un serveur avant de lancer un jeu.")
            print("Le serveur et les joueurs doivent être")
            print("sur le même réseau local.")
            os._exit(0)

    print("Ip serveur:", gl.ip_server)
    create_tcp_socket()
