#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#  server_new.py


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


import os, sys
from time import time, sleep
import threading
import json
import ast
import queue

from twisted.internet.protocol import DatagramProtocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor

from mylabotools.labconfig import MyConfig
from mylabotools.labsometools import get_my_ip

from game_dictator import Game


# Variable globale
scr = os.path.dirname(os.path.abspath(__file__))
conf = MyConfig(scr + "/mp.ini")
my_conf = conf.conf
print("Configuration du serveur: {}\n".format(my_conf))

MULTICAST_IP = my_conf["multicast"]["ip"]
MULTICAST_PORT = my_conf["multicast"]["port"]
TCP_PORT = my_conf["tcp"]["port"]

TO_BLEND = queue.Queue()


class MyMulticastSender(DatagramProtocol):
    """Envoi en continu à 60 fps à tous les joueurs, ip et data."""

    def __init__(self):

        self.tempo = time()
        self.count = 0
        self.ip_server = get_my_ip()

        print("Envoi en multicast sur", MULTICAST_IP,
                                        MULTICAST_PORT, "\n")

    def startProtocol(self):
        """Called after protocol has started listening."""

        # Set the TTL>1 so multicast will cross router hops:
        # https://www.rap.prd.fr/pdf/technologie_multicast.pdf

        # préconise TTL = 1
        self.transport.setTTL(1)

        # Join a specific multicast group:
        self.transport.joinGroup(MULTICAST_IP)

        # Boucle infinie pour envoi continu à tous les joueurs
        self.send_loop_thread()

    def create_multi_msg(self, data):
        """Retourne msg encodé à envoyer en permanence, dès __init__
        {"dictat":   {  }}
            ou None
        """

        if data: # data est un dict ou None
            lapin = {"svr_msg": {"ip": self.ip_server, "dictat": data}}
        else:
            lapin = {"svr_msg": {"ip": self.ip_server, "dictat": {'rien': 0}}}

        lapin_enc = json.dumps(lapin).encode("utf-8")
        # #try:
            # #print("dictat", lapin["svr_msg"]["dictat"]["ball"])
        # #except:
            # #pass
        return lapin_enc

    def send_loop(self):
        """{'svr_msg': {'dictat': {   'ball': [-4.2, -4.1],
                                        'reset': 0,
                                        'score': [],
                                        'level': 1,
                                        'rank_end': 0,
                                        'who_are_you': {},
                                        'paddle': {},
                                        'scene': 'play',
                                        'classement': {},
                                        'transit': 0},
                                        'ip': '192.168.1.17'}}
        """

        addr = MULTICAST_IP, MULTICAST_PORT

        while 1:
            # récup dans la pile, un chouilla plus rapide que 60 fps,
            # pour ne pas prendre de retard sur le put() et remplir la queue
            sleep(0.016)  # TO_BLEND maj à 60 fps
            try:
                data = TO_BLEND.get(block=False, timeout=0.001)
            except:
                data = None

            # envoi
            lapin = self.create_multi_msg(data)
            try:
                self.transport.write(lapin, addr)
            except OSError as e:
                if e.errno == 101:
                    print("Network is unreachable")

    def send_loop_thread(self):
        thread_s = threading.Thread(target=self.send_loop)
        thread_s.start()

    def print_some(self, msg):
        data = datagram_decode(msg)
        self.count += 1
        tt = 1
        if time() - self.tempo > tt:
            self.count = 0
            self.tempo = time()
            env = data["svr_msg"]["dictat"]
            #print("\nFréquence d'envoi multicast", int(self.count/tt))
            os.system('clear')
            print("\nMessage envoyé par le serveur:")
            for k, v in env.items():
                print("    ", k, v)


class MyTcpServer(Protocol):
    """Reception de chaque joueur en TCP."""

    def __init__(self, factory):
        self.factory = factory

        # Permet de distinguer les instances des joueurs et de blender
        self.create_user()

        self.tempo = time()

    def create_user(self):
        """Impossible d'avoir 2 user identiques"""

        self.user = "TCP" + str(int(10000* time()))[-8:]
        print("Un user créé: ", self.user)

    def connectionMade(self):
        self.addr = self.transport.client
        print("Une connexion établie par le client {}".format(self.addr))

    def connectionLost(self, reason):
        print("Connection lost, reason:", reason)
        print("Connexion fermée avec le client {}".format(self.addr))
        self.factory.game.delete_disconnected_players(self.user)

    def dataReceived(self, data):
        """ TODO: rajouter decode sorting"""

        # Retourne un dict ou None
        data = datagram_decode(data)

        if data:
            # data = {'joueur': {'name': 'toto', 'paddle': [-9.5, 3]}}
            if "joueur" in data:
                joueur = data["joueur"]
                self.add_data(joueur)
                if time() - self.tempo > 5:
                    # Des joueurs
                    a = "\nReçu de {}:\n{}"
                    print(a.format(joueur["name"], joueur))
                    self.tempo = time()

            # {'blend': {'reset': 0, 'ball': [-8.7, 9.0]}}
            if "blend" in data:
                blend = data["blend"]
                self.update_blend(blend)
                if time() - self.tempo > 5:
                    print("\nReçu de Blender:\n{}".format(blend))
                    self.tempo = time()

    def update_blend(self, blend):
        """Update des datas issues de blender."""

        self.factory.game.update_blend(blend)

    def add_data(self, joueur):
        """Insère la dernière data reçue dans le dict du user."""

        self.factory.game.add_data_in_players(self.user, joueur)

    def reset_game(self) :
        """Insère la dernière data reçue dans la pile du user."""

        print("Reset demandé sur serveur")
        self.factory.game.t_reset = time()
        self.factory.game.reset_data()


class MyTcpServerFactory(Factory):
    """self ici sera self.factory dans les objets MyTcpServer."""

    def __init__(self):
        """L'objet gestion du jeu est construit ici.
        Il est accessible dans MyTcpServer avec self.factory.game."""

        self.game = Game(my_conf)
        self.get_and_queued_msg_thread()

        # Serveur
        self.numProtocols = 1
        print("Serveur twisted réception TCP sur {}\n".format(TCP_PORT))

    def buildProtocol(self, addr):
        print("Nouveau protocol crée dans l'usine: factory")
        print("Nombre de protocol dans factory", self.numProtocols)

        # le self permet l'accès à self.factory dans MyTcpServer
        return MyTcpServer(self)

    def get_and_queued_msg(self):
        """Le message dictat est créé dans Game,
        le mettre dans la pile et à envoyer aux joueurs en Multicast.
        La pile est une variable globale qui sera récupérée par l'object
        MyMulticastSender.

        create_msg_for_all_players() demande d'abord la mise à jour
        de Game à 60 fps.
        """

        while 1:
            # 60 fps pile poil, get se fera un peu plus vite, pour avoir une
            # queue vide àprès chaque lecture
            sleep(0.0166)

            # get message
            msg = self.game.create_msg_for_all_players()

            # Le met dans la variable globale
            # qui sera lue par le thread de MyMulticastSender
            TO_BLEND.put(msg)  # msg est dict ou None

    def get_and_queued_msg_thread(self):
        """Thread qui tourne dans Factory pour récupérer le message
        généré dans Game.
        """

        thread_msg = threading.Thread(target=self.get_and_queued_msg)
        thread_msg.start()


def datagram_decode(data):
    """Decode le message.
    Retourne un dict ou None
    """

    try:
        dec = data.decode("utf-8")
    except:
        #print("Décodage UTF-8 impossible")
        dec = data

    try:
        msg = ast.literal_eval(dec)
    except:
        #print("ast.literal_eval impossible")
        msg = dec

    if isinstance(msg, dict):
        return msg
    else:
        #print("Message reçu: None")
        return None

def print_dict(d):
    """Pas utilisé"""

    if isinstance(d, dict):
        for k, v in d.items():
            print(k, "\n", v)
        print()


if __name__ == "__main__":
    ## Receive
    endpoint = TCP4ServerEndpoint(reactor, TCP_PORT)
    endpoint.listen(MyTcpServerFactory())

    ## Send: je reçois aussi ce que j'envoie
    reactor.listenMulticast(MULTICAST_PORT, MyMulticastSender(), listenMultiple=True)

    ## Pour les 2
    reactor.run()
