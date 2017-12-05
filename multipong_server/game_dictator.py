#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

## game_dictator.py

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

from collections import OrderedDict
from time import time, sleep


class Game():
    """Gestion du jeu avec les datas envoyés par tous les joueurs
    et blender.
    """

    def __init__(self, conf):

        # Config du jeu
        self.conf = conf

        t = time()
        self.reset = 0

        # Dict avec dernière valeur reçue de chaque joueur
        self.players = OrderedDict()

        # Classement
        self.classement = OrderedDict()

        # Jeu
        self.scene = "play"
        self.level = 1
        self.ball = [2, 2]
        self.paddle = [[0, 0]] * 10
        self.paddle_auto = [9.5, 0]
        self.score = [10] * 10

        # Nouveau classement
        self.match_end = 0
        self.match_end_tempo = time()
        self.loser = {}

        # Suivi fréquence
        self.t_count = t
        self.count = 0

    def update_game(self):
        """Appelé par create_msg_for_all_players, tourne donc à 60 fps.
        """

        if self.reset:
            self.reset_data()

        self.update_level()
        self.update_paddle()

        if self.level == 1:
            self.update_paddle_auto()

        if not self.match_end:
            # d'abord qui a perdu
            self.update_loser()
            # puis classement
            self.get_match_end()
            # On ne passe plus ici si self.match_end=1
        else:
            self.update_match_end_tempo()

    def get_name_with_index(self, index):
        """Retourne le nom du joueur
        self.players = {
        'TCP117', {'name': 'p117', 'paddle': [-9.5, 3.44]}),
        'TCP122', {'name': 'p122', 'paddle': [9.6, 1.30]})]}

        list = [ {'paddle': [-9.5, 7.5], 'name': 'pierre14'},
                 {'paddle': [ 9.6, 5.3], 'name': 'pierre53'} ]
        """

        # TODO delete try
        try:
            l = list(self.players.values())
            d =  l[index]
            name = d['name']
            return name
        except:
            return "Isac  Asimov"

    def update_loser(self):
        """Enregistrement du time des loser dans self.loser
             joueur1   time    joueur4 ...
        = {    1:    345.123,   4:       345.457, 3: 363.729}

        players_list = [['pierre', score], ['AI', score]]
        Il ne faut l'ajouter dans la liste qu'une seule fois
        """

        for i in range(len(self.score)):
            if self.score[i] <= 0:
                # Si pas encore dans le dict
                if not i+1 in self.loser:
                    self.loser[i + 1] = time()

    def get_winner(self):
        """ Qui a gagné ? celui qui n'est pas dans loser"""

        winner = 0
        print("self.loser", self.loser)
        loser_nums = list(self.loser.keys())
        print("loser_nums", loser_nums)
        for i in range(len(loser_nums)):
            if i not in loser_nums:
                print(i, "a gagné")
                winner = i
        return winner

    def get_classement(self):
        """retourne le classement dans un dict non ordonné
        le json perd l'ordre

        self.loser = { 0: 345.9, 3: 345.4, 2: 345.8}
        winner_index = 1
        self.classement = {'pierre':1, 'AI':2, 'toi':4,'moi':3}
        blender attend {'toto': 3, 'labomedia': 2, 'gddgsg': 1}
        """

        self.classement = {}

        winner_index = self.get_winner()
        winner_name = self.get_name_with_index(winner_index)
        self.classement[winner_name] = 1

        time_list = list(self.loser.values())

        # Le time le plus grand est le 2ème
        time_list_sort = sorted(time_list, reverse=True)

        n = 2
        for t in time_list_sort:
            for k, v in self.loser.items():
                if v == t:
                    # k est le suivant
                    print("k", k)
                    k_name = self.get_name_with_index(k)
                    print("k_name", k_name)
                    self.classement[k_name] = n
                    n += 1

    def get_match_end(self):
        """Obtenu avec self.score qui vient blender
        self.match_end=1 dès que reste un seul score non nul dans
        self.score
        self.match_end=1 pendant tout l'affichage du classement
        et reste à 1 pendant 3 secondes après le temps d'affichage
        """

        a = 0
        # a = nombre de 0 ou <0
        for scor in self.score:
            if scor <= 0:
                a += 1
        l = self.level
        if l == 1: l = 2
        # Comparaison de a avec level corrrigé
        # un seul non nul si
        if a == l-1:
            self.match_end = 1
            # Lancement de la tempo
            self.match_end_tempo = time()
            # Calcul de classement une seule fois
            self.get_classement()
            print("Classement", self.classement)
        else:
            self.match_end = 0

    def update_match_end_tempo(self):
        """Tourne pendant 6 secondes
        3 secondes d'affichage,
        3 secondes de bloquage avant reset de self.match_end
        """

        self.scene = "rank"

        if time() - self.match_end_tempo < 5:
            print("Classement", self.classement)

        if time() - self.match_end_tempo > 5:
            self.scene = "play"
            self.reset_data()

        if time() - self.match_end_tempo > 6:
            # Le jeu a repris depuis longtemps
            # je peux rescanner les scores
            self.match_end = 0

    def add_data_in_players(self, user, data):
        """Ajoute les datas reçues d'un joueur.
        self.players = {
        'TCP117', {'name': 'p117', 'paddle': [-9.5, 3.44]}
        """

        self.players[user] = data

        # Affichage de la fréquence d'appel de cette méthode
        self.frequency()

    def update_paddle(self):
        """Set les positions des paddles des joueurs dans self.paddle
        """

        self.paddle = []
        for k, v in self.players.items():
            if "paddle" in v:
                self.paddle.append(v["paddle"])

    def frequency(self):
        self.count += 1
        t = time()
        if t - self.t_count > 5:
            print("Fréquence d'accès par les clients", int(self.count/5))
            self.count = 0
            self.t_count = t

    def update_level(self):
        """Mise à jour du level.
        1 joueur = level 1, pas de joueur level 1
        """

        l = len(self.players)
        if l == 0: l = 1

        # Maxi 10 joueurs
        if l > 10:
            l=10
            print("10 joueurs maxi")

        self.level = l

    def get_players_list(self):
        """Retourne la liste des joueurs
        players_list = [['pierre', score], ['AI', score]]
        avec AI pour level 1 et
        self.players = o('pierre': {    'name': 'pierre',
                                        'paddle': [2, 5]})
        self.score = [3, 4]

        """

        players_list = []
        l = self.level
        if l == 1: l = 2

        if len(self.score) == l :
            if len(self.players) > 0:
                n = 0
                for key, val in self.players.items():
                    joueur = [key, self.score[n]]
                    players_list.append(joueur)
                    # Ajout de AI level 1
                    if self.level == 1:
                        # Ajout de AI
                        players_list.append(['AI', self.score[1]])

                # joueur suivant
                n += 1

        return players_list

    def update_blend(self, blend):
        """Maj de la position de la balle et du reset
        avec valeurs reçues de blender
         blend = {"ball": (1,1), "reset": 0}
        """

        self.ball = blend["ball"]
        self.paddle_auto = blend["paddle_1_pos"]
        self.reset = blend["reset"]
        self.score = blend["score"]

    def update_paddle_auto(self):
        """Modifie la liste self.paddle
        paddle_auto est indice 1
        """

        # Si blend_paddle_1 valide
        if len(self.paddle_auto) == 2:
            if len(self.paddle) == 0:
                self.paddle = [[-9.5, 0], self.paddle_auto]
            elif len(self.paddle) == 1:
                self.paddle.append(self.paddle_auto)
        else:
            self.paddle = [[-9.5, 0], [9.5, 0]]

    def get_who(self):
        """Retourne le numéro de tous les joueurs dans un dict
        {"toto":0, "tata":1}
        """

        who = {}
        a = 0
        # le dict est ordonné
        for k, v in self.players.items():
            if "name" in v:
                who[v["name"]] = a
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
                "paddle": [[-9.4, 2.5], [-9.4, 0.40]],
                "who_are_you": {'moi': 0, 'toi': 1},
                "match_end":  0,
                "reset": 0,
                "transit": 0 }
        """

        # Maj
        self.update_game()

        # Je regroupe tout
        msg = { "level": self.level,
                "scene" : self.scene,
                "classement": self.classement,
                "ball": self.ball,
                "score": self.score,
                "paddle": self.paddle,
                "who_are_you": self.get_who(),
                "match_end":  self.match_end,
                "reset": self.reset,
                "transit": self.match_end  }

        return msg

    def reset_data(self):
        """Si reset demandé par blender
        self.players n'est pas reseter
        """

        print("Reset in Game")

        # Classement
        self.classement = OrderedDict()
        self.loser = {}

        # Jeu
        self.scene = "play"
        self.level = 1
        self.ball = [2, 2]
        self.paddle = [[0, 0]] * 10
        self.paddle_auto = [9.5, 0]
        self.score = [10] * 10

    def delete_disconnected_players(self, user):
        """Appelé depuis MyTcpServer si conection lost."""

        try:
            del self.players[user]
            print("{} supprimé dans players".format(user))
        except:
            a = "Le joueur {} n'est plus dans le dictionnaire"
            print(a.format(user))

        print("Vérification de la cohérence du dict des joueurs")
        for key, val in self.players.items():
            try:
                if val["user"] == user:
                    del self.players[key]
                    break
                print("{} supprimé dans players".format(key))
            except:
                print("{} vérifié".format(key))
