#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

## game_dictator.py

#############################################################################
# Copyright (C) Labomedia November 2017
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

"""
De msg =
{"joueur": {    "my_name":       gl.my_name,
                "ball_position": get_ball_position(),
                "my_score":      get_my_score(),
                "paddle_position":  get_paddle_position(),
                "reset":         get_reset()}}

Vers
players = [
('gg1456048982', {  'ball_position': [2.1, 4.8],
                    'my_score': 9,
                    'time': 1456048988.52,
                    'classement': 0,
                    'paddle_position': [-9.4, 0.0],
                    'my_name': 'gg1456048982'}),

('gg1456048985', {  'ball_position': [7.4, 9.1],
                    'my_score': 8,
                    'time': 1456048987.50,
                    'classement': 0,
                    'paddle_position': [9.4, 0.0],
                    'my_name': 'gg1456048985'})
]

msg envoyé:
lapin = {"svr_msg": {"ip": self.ip_server, "dictat": data}}
et
msg =   {   "level": self.level,
            "scene" : self.scene,
            "classement": self.classement,
            "ball_position_server": self.get_ball(),
            "score": self.get_score(),
            "other_paddle_position": self.get_paddle(),
            "who_are_you": self.get_who(),
            "rank_end":   self.rank_end,
            "reset": self.get_reset(),
            "transit": self.transit  }

lapin = {"svr_msg": {"ip": self.ip_server, "dictat": msg}}
        ou
lapin = {"svr_msg": {"ip": self.ip_server, "dictat": {'rien': 0}}}
"""


from collections import OrderedDict
from time import time, sleep
import threading
import json

from mylabotools.labfifolist import PileFIFO


class GameManagement():
    """Gestion du jeu avec les datas envoyés par tous les joueurs."""

    def __init__(self, conf):

        # Config du jeu
        self.conf = conf

        t = time()

        # Dict des datas de tous les joueurs
        self.players = OrderedDict()

        # Gestion du jeu
        self.winner = ""
        self.ranked = []
        self.scene = "play"
        self.rank_end = 0
        self.t_rank = 0 # actualisé avec winner
        self.classement = {}
        self.level = 0
        self.t_reset = 0
        self.transit = 0 # pour bloquage des jeux si level change
        self.t_transit = t
        self.tempo_transit = 2
        self.ball = [2,2]
        self.reset = 0

        # Spécifique protocol twisted 3
        self.t_print = t  # print régulier
        self.t_count = t  # Affichage fréquence régulier
        self.count = 0
        self.pile_dict = {}
        self.len_pile = self.conf["pile"]["len_pile"]

    def reset_data(self):
        """Reset si demandé par un joueur avec R
        ou à la fin de rank
        """

        print("Reset in Game Dictator")
        self.players = OrderedDict()
        self.ranked = []
        self.scene = "play"
        self.winner = ""
        self.rank_end = 0
        self.t_rank = 0
        self.classement = {}
        self.level = 0
        self.pile_dict = {}

    def add_data_in_pile(self, user, data):
        """Ajoute les datas reçues d'un user dans sa pile,
        Demande de la mise à jour de la gestion du jeu à 60 Hz.
        """

        try:
            self.pile_dict[user].append(data)
        except:
            self.pile_dict[user] = PileFIFO(self.len_pile)
            print("Création de la pile de:", user)

        # Affichage de la fréquence d'appel de cette méthode
        self.frequency()

    def update_blend(self, blend):
        """Maj de la position de la balle et du reset
        avec valeurs reçues de blender.
        {"blend": {"ball": (1,1), "reset": 0}}
        blend = {"ball": (1,1), "reset": 0}
        """

        self.ball = blend["ball"]
        self.reset = blend["reset"]

    def pile_to_players(self):
        """Appelé par create_msg_for_all_players
        Passe la dernière valeur des piles dans players dict.
        msg = {'my_score': 10, 'ball_position': [4.39, 9.99],
        'my_name': 'n1654453', 'paddle_position': [1.16, -0.16]}
        """

        # copie du dict pour le libérer
        all_data = self.pile_dict.copy()
        for cle, valeur in all_data.items():
            # cle = user de TCP, valeur = pile, queue = list
            try:
                # valeur est un object PileFIFO
                i = len(valeur.queue) - 1
                msg = valeur.queue[i]
            except:
                msg = None
            self.update_data_in_players_dict(msg, cle)

    def frequency(self):
        self.count += 1
        t = time()
        if t - self.t_count > 5:
            print("Fréquence d'accès par les clients", int(self.count/5))
            self.count = 0
            self.t_count = t

    def update_data_in_players_dict(self, msg, user):
        """A chaque reception de msg par le server, insère in dict.
        Ajout seulement si name créé dans blender.
                """

        # Seulement si le nom est valide, donc saisi
        try:
            if msg and msg["my_name"] != "":
                if msg["my_name"] in self.players:
                    self.players[msg["my_name"]]["ball_position"] = msg["ball_position"]
                    self.players[msg["my_name"]]["paddle_position"] = msg["paddle_position"]
                    self.players[msg["my_name"]]["my_score"] = msg["my_score"]
                    self.players[msg["my_name"]]["time"] = time()
                else:
                    self.players[msg["my_name"]] = {}
                    self.players[msg["my_name"]]["ball_position"] = msg["ball_position"]
                    self.players[msg["my_name"]]["paddle_position"] = msg["paddle_position"]
                    self.players[msg["my_name"]]["my_score"] = msg["my_score"]
                    self.players[msg["my_name"]]["my_name"] = msg["my_name"]
                    self.players[msg["my_name"]]["time"] = time()
                    self.players[msg["my_name"]]["classement"] = 0
                    self.players[msg["my_name"]]["user"] = user
                    print("Dans players, création de:", user)
        except:
            print("Pb dans update_data_in_players_dict")

    def update_game_management(self):
        """Appelé par create_msg_for_all_players, tourne donc à 60 fps."""

        self.pile_to_players()
        self.update_level()
        self.update_transit()
        self.update_classement()
        self.update_rank()

    def update_transit(self):
        """Si transit:
        - bloquage des scores à 10
        - bloquage balle à 1, 1
        - pas de bloquage des paddles
        - question ? ajout d'une scène black en overlay ?
        """

        if self.transit:
            if time() - self.t_transit > self.tempo_transit:
                self.transit = 0

    def update_level(self):
        """Mise à jour du level."""

        level_old = self.level
        l = len(self.players)

        if l == 0:
            l = 1

        if level_old != l:
            self.transit = 1
            self.t_transit = time()

        # Maxi 10 joueurs
        if l > 10:
            l=10
            print("Nombre de joueurs supérieur à 10 soit", l)

        self.level = l

    def update_rank(self):
        """Gère le temps d'affichge de rank."""

        if self.scene == "rank":
            if time() - self.t_rank > 2:
                self.rank_end = 1
            if time() - self.t_rank > 2.1: # 5 ou 6 envoi
                self.rank_end = 1
                self.reset_data()

    def update_classement(self):
        """TODO: Fonction trop longue donc pas clair"""

        self.ranked = []

        # Je récupère ceux qui sont déjà classés
        for k, v in self.players.items():
            if v["classement"] != 0:
                self.ranked.append(v["classement"])
        self.ranked.sort()

        # Je récupère ceux qui viennent de perdre
        # mais le nb de classés doit être inf au nb de joueurs, pas de 1:
        if len(self.ranked) < self.level:
            for k, v in self.players.items():
                # Ceux qui viennent de perdre et ne ne sont pas encore classés
                if v["classement"] == 0 and v["my_score"] == 0:
                    if len(self.ranked) == 0:
                        cl = len(self.players)
                    else:
                        cl = self.ranked[0] - 1
                    if cl != 1: # le gagnant est gérer ci-dessous
                        v["classement"] = cl
                        self.ranked.append(cl)
                        self.ranked.sort()

        # Si il y a un 2ème, c'est fini, le restant est le 1er
        # le score du dernier ne va pas à 0, et si il y va, il a gagné
        if 2 in self.ranked:
            # Qui a un classement = 0 ?
            for k, v in self.players.items():
                if v["classement"] == 0:
                    v["classement"] = 1
                    self.winner = v["my_name"]
                    self.scene = "rank"
                    self.t_rank = time()
                    print("The winner is {}".format(self.winner))

        # Maj du dict du classement final, car un joueur est 1
        # mais 1 seul 1, parfois plus car le jeu continue à tourner
        verif = 0
        for i in self.ranked:
            if i == 1:
                verif += 1
        if 1 in self.ranked and verif == 1:
            clst = {}
            for k, v in self.players.items():
                clst[v["my_name"]] = v["classement"]
            self.classement = clst
        else:
            self.classement = {}

    def get_score(self):
        """Retourne les scores de tous les joueurs, dans une liste.
        Le dict est ordonné, j'ajoute les scores dans l'ordre.
        """

        score = []  # liste
        for k, v in self.players.items():
            score.append(v["my_score"])

        if self.transit: # sert à rien fait dans le jeu
            score = [10] * self.level

        return score

    def get_paddle(self):
        """Retourne la position des paddles de tous les joueurs.
        Le dict est ordonné, j'ajoute les paddles dans l'ordre.
        Level 10: paddle en auto. TODO méthode spéciale.
        Les paddle en auto n'ont pas d'ordre, il y en a 10,
        donc plus de paddle manuelle.
        """

        paddle = {}  # dict

        if self.level != 10:
            b = 0
            for k, v in self.players.items():
                paddle[b] = v["paddle_position"]
                b += 1
        else:
            if self.conf["simul"]["paddle_simul"]:
                for num in range(10):
                    paddle[num] = self.paddle_simul[num].paddle
            else:  # TODO nul répétition
                b = 0
                for k, v in self.players.items():
                    paddle[b] = v["paddle_position"]
                    b += 1

        return paddle

    def get_who(self):
        """Retourne le numéro de tous les joueurs dans un dict
        {"toto":0, "tata":1}
        """

        who = {}
        a = 0
        for k, v in self.players.items():
            who[v["my_name"]] = a
            a += 1
        return who

    def create_msg_for_all_players(self):
        """Appelé à 60 fps par le serveur dans MyTcpServerFactory.
        Commence par demander une mise à jour du jeu.
        Message à créer:
            {   "level": 2,
                "scene" : 'play',
                "classement": {},
                "ball": [7.19, 7.19],
                "score": [9, 7],
                "paddle": {0: [-9.4, 0.0], 1: [-9.4, 0.40]},
                "who_are_you": {'moi': 0, 'toi': 1},
                "rank_end":  0,
                "reset": 0,
                "transit": 0 }
        """

        # Maj
        self.update_game_management()

        # Je regroupe tout
        msg = { "level": self.level,
                "scene" : self.scene,
                "classement": self.classement,
                "ball": self.ball,
                "score": self.get_score(),
                "paddle": self.get_paddle(),
                "who_are_you": self.get_who(),
                "rank_end":   self.rank_end,
                "reset": self.reset,
                "transit": self.transit  }

        return msg

    def delete_disconnected_players(self, user):
        """Appelé depuis MyTcpServer si conection lost.
        TODO try a revoir pas normal"""

        try:
            del self.pile_dict[user]
            print("{} supprimé dans pile_dict".format(user))
        except:
            a = "Le joueur {} n'est plus dans le dictionnaire"
            print(a.format(user))

        for key, val in self.players.items():
            try:
                if val["user"] == user:
                    del self.players[key]
                    break
                print("{} supprimé dans players".format(key))
            except:
                print("{} n'est pas dans players".format(key))

    def print_some(self, msg):
        if time() - self.t_print > 2:
            print("\nMessage to send:")
            for k, v in msg.items():
                print(k, v)
            print()

            ##print("Joueurs en cours:")
            ##for k, v in self.players.items():
                ##print(v)
            ##print()

            self.t_print = time()
