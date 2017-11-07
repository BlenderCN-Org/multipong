#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

## once.py

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
Ce script est appelé par main_init.main dans blender
Il ne tourne qu'une seule fois pour initier las variables
qui seront toutes des attributs du bge.logic (gl)
Seuls les attributs de logic sont stockés en permanence.

Un thread est crée pour recevoir le multicast, puis après avoir reçu l'adresse
ip du serveur sur ce multicast, lancement d'un socket TCP pour envoyer.

'''


import os
import ast
import json
import threading
from time import sleep, time

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

from scripts.labtools.labconfig import MyConfig
from scripts.labtools.labtempo import Tempo
from scripts.labtools.labtcpclient import LabTcpClient
from scripts import game
from bge import logic as gl


class MulticastClient(DatagramProtocol):
    '''Ce client reçoit les datas du serveur.'''

    def startProtocol(self):
        '''Ticket sur le groupe multicast.'''

        # Join the multicast address, so we can receive replies:
        self.transport.joinGroup(gl.multi_ip)

        print("\nClient Multicast sur {}\n".format(gl.multi_addr))

    def datagramReceived(self, datagram, address):
        '''Réception, demande de traitement.'''

        data = datagram_decode(datagram)

        if data:
            self.datagram_sorting(data)

    def datagram_sorting(self, data_dict):
        '''Met à jour les variables avec les valeurs reçues. data = dict =
        {"paradis": {"ip": self.ip_server, "dictat": data}}
        ou
        {"paradis": {"ip": self.ip_server, "dictat": {"level": 1}}}
        '''

        data = data_dict["paradis"]

        if "ip" in data:
            gl.ip_server = data["ip"]

        if "dictat" in data:
            data = data["dictat"]

            if data:
                if gl.scene == "play" or gl.scene == "rank":
                    self.tri_msg(data)

    def tri_msg(self, data):
        '''Set des variables attributs du game logic.'''

        if "level" in data:
            gl.level = data["level"]
            # TODO fonction dans game
            # seulement 10 scenes de jeu
            if gl.level < 1:
                gl.level = 1

            if gl.level == 1:
                # Correction bug retour level 1
                gl.I_am = 0

            if gl.level > 10:
                gl.level = 10

        if "reset" in data:
            if data["reset"]:
                game.reset_variables()

        if "rank_end" in data:
            gl.rank_end = data["rank_end"]
            # TODO fonction dans game
            if gl.rank_end:
                print("Fin de rank:", gl.rank_end)
                try:
                    for i in range(gl.level):
                        gl.goal[i]["score"] = 10
                except:
                    print("Goal non accessible pour reset score")

        if "scene" in data:
            gl.scene = data["scene"]

        if "ball_position_server" in data:
            gl.ball_position_server = data["ball_position_server"]

        if "score" in data:
            gl.score = data["score"]

        if "other_bat_position" in data:
            gl.bat_position = data["other_bat_position"]

        if "who_are_you" in data:
            # TODO fonction dans game
            # {"toto":0, "tata":1}
            who = data["who_are_you"]
            for k, v in who.items():
                if gl.my_name == k:
                    gl.I_am = v

        if "classement" in data:
            gl.classement = data["classement"]

        if "transit" in data:
            gl.transit = data["transit"]


def datagram_decode(datagram):
    '''Decode la réception qui est des bytes, pour obtenir un dict.
    Valable pour python3.
    Cette fonction doit être revue pour être en béton.
    '''

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
    '''Récupère la configuration depuis le fichier *.ini.'''

    print("Initialisation des scripts lancée un seule fois au début du jeu.")

    # Le dossier courrant est le dossier dans lequel est le *.blend
    current_dir = gl.expandPath("//")
    print("Dossier courant depuis once.py {}".format(current_dir))
    gl.once = 0

    # TODO: trouver le *.ini en auto
    gl.ma_conf = MyConfig(current_dir + "scripts/mpff.ini")
    gl.conf = gl.ma_conf.conf

    print("\nConfiguration du jeu MPFF:")
    print(gl.conf, "\n")

def init_variable():
    '''Valeurs par défaut de tous les attributs du bge.logic'''

    # state possible:play rank labo
    gl.scene = "labo"

    # msg à envoyer
    gl.msg_to_send = None

    # Défini par le serveur
    gl.level = 1
    gl.block = 0
    gl.rank_end = 0

    # Rank
    gl.text = ""
    gl.classement =  {}  # {'toto': 3, 'labomedia': 2, 'gddgsg': 1}

    # vient du server
    gl.ball_position_server = [0, 0] # liste
    gl.score = [0] * 10 # liste
    gl.bat_position = { 0: [0, 0],   # dict !!
                        1: [0, 0],
                        2: [0, 0],
                        3: [0, 0],
                        4: [0, 0],
                        5: [0, 0],
                        6: [0, 0],
                        7: [0, 0],
                        8: [0, 0],
                        9: [0, 0]}

    # Scene Name
    gl.my_name = ""
    gl.my_name_ok = 0
    gl.name_obj = 0

    gl.I_am = 0
    gl.ip_server = None

    gl.multi_ip = gl.conf["multicast"]["ip"]
    gl.multi_port = gl.conf["multicast"]["port"]
    gl.multi_addr = gl.multi_ip, gl.multi_port
    gl.tcp_port = gl.conf["tcp"]["port"]

    # level 1 only
    gl.level1_rated = 0 # si classement du level 1 fait dans game.py
    gl.classement_level1 = {}
    gl.tempo_rank_level1 = 0
    gl.reset = 0

    # capture du nom
    gl.name_capture = gl.conf["game"]["name_capture"]

    # gestion du changement du nombre de joueur
    gl.transit = 0

def init_blender_obj():
    '''Définit les variables qui permettront d'accéder aux objects de blender.
    '''

    #Cube de Labomedia
    gl.cube_obj = 0
    # L'objet qui permet d'afficher le texte du classement
    gl.rank_obj = 0
    # L'objet dn bas de Labomedia
    gl.help_obj = 0

    # permet accès aux objet blender score et leur score
    gl.goal = {  0 : 0,
                1 : 1,
                2 : 2,
                3 : 3,
                4 : 4,
                5 : 5,
                6 : 6,
                7 : 7,
                8 : 8,
                9 : 9   }

    # All bat
    gl.bat = {  0 : 0,
                1 : 1,
                2 : 2,
                3 : 3,
                4 : 4,
                5 : 5,
                6 : 6,
                7 : 7,
                8 : 8,
                9 : 9}

    # All cache
    gl.cache = {    0 : 0,
                    1 : 1,
                    2 : 2,
                    3 : 3,
                    4 : 4,
                    5 : 5,
                    6 : 6,
                    7 : 7,
                    8 : 8,
                    9 : 9}

    gl.ball = 0  # mon objet blender ball

def init_tempo():
    ''' * tempo_liste = [("intro", 60), ("print", 12), ("sound", 6)]
        * tempoDict = Tempo(tempo_liste)
        * tempoDict.update()
    '''

    tempo_liste = [("always", 1), ("frame_60", 60)]
    gl.tempoDict = Tempo(tempo_liste)

def simple():
    reactor.listenMulticast(gl.multi_port, MulticastClient(), listenMultiple=True)
    reactor.run(installSignalHandlers=False)

def simple_thread():
    '''Le client est dans un thread.'''

    thread_s = threading.Thread(target=simple)
    thread_s.start()

def create_tcp_socket():
    '''Client TCP connecté'''

    gl.tcp_client = LabTcpClient(gl.ip_server, gl.tcp_port)

def main():
    '''Lancé une seule fois à la 1ère frame au début du jeu par main_once.'''

    get_conf()
    init_variable()
    init_blender_obj()
    init_tempo()

    # Lancement du thread multicast
    simple_thread()

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
