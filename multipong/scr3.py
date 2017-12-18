#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import kivy
kivy.require('1.10.0')

from kivy.app import App
from kivy.properties import ListProperty
from kivy.properties import ReferenceListProperty
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window

from terrain import Terrain


# Points pour kivy
NUM = 3
TERRAIN = Terrain(NUM)
LINE = TERRAIN.line
NET = TERRAIN.net_line

# Pass variable between python script http://bit.ly/2n0ksWh
from __main__ import *
print("Dans le script scr1.py, ")
print("    coefficient de résolution écran:", COEF)


def droite(x1, y1, x2, y2):
    """ Retourne les valeurs de a et b de y=ax+b
        à partir des coordonnées de 2 points.
    """

    if x2 - x1 != 0:
        a = (y2 - y1) / (x2 - x1)
        b = y1 - (a * x1)
    else:
        a, b = 0, 0

    return a, b


class Screen3(Screen):
    """Ecran pour 3 joueurs en position 0 1 2"""

    points = ListProperty(LINE)
    net = ListProperty(NET)
    ball = ObjectProperty()

    paddle_0 = ObjectProperty()
    paddle_1 = ObjectProperty()
    paddle_2 = ObjectProperty()

    score_0 = ObjectProperty()
    score_1 = ObjectProperty()
    score_2 = ObjectProperty()

    titre = ObjectProperty()
    classement = ObjectProperty()

    def __init__(self, **kwargs):

        super(Screen3, self).__init__(**kwargs)

        self.coef = COEF

        # mon numéro dans
        self.my_num = 0

        # Dict des paddles
        self.paddle_d = {   0: self.paddle_0,
                            1: self.paddle_1,
                            2: self.paddle_2}

        # Dict des scores
        self.score_d = {    0: self.score_0,
                            1: self.score_1,
                            2: self.score_2}

        print("Initialisation de Screen3 ok")

    def get_my_blender_paddle_pos(self, my_pad):
        """Retourne la position de ma paddle, pour envoyer au serveur
        """

        return TERRAIN.get_blender_coord([my_pad.pos[0],
                                          my_pad.pos[1]],
                                          [-6, -52])

    def apply_my_num(self, my_num):
        """Appelé par main Game apply_my_num"""

        self.my_num = my_num

    def apply_paddle_red_color(self):
        """J'applique le rouge à ma paddle"""

        if self.my_num != None:
            self.paddle_d[self.my_num].rect_color = 1, 0, 0

    def apply_score(self, score):
        """Set les scores
        apply_score(score)
        score = [4, 2]
        """

        n = min(len(score), NUM)
        for i in range(n):
            self.score_d[i].text = str(score[i])

    def apply_ball_pos(self, ball_pos):
        """Positionne la balle avec position du serveur."""

        if ball_pos:
            x, y = TERRAIN.get_kivy_coord(ball_pos, [16, 16])
            x, y = x*self.coef + 5, y*self.coef - 50

            self.ball.pos = [int(x), int(y)]

    def apply_other_paddles_pos(self, paddle_pos):
        """  Toutes les paddles sauf la mienne
             moi         l'autre
        [[-9.5, 0.0], [9.5, -1.81], [0, 0], [0, 0], ....]
        au reset len(paddle_pos) = 10
        """

        n = min(len(paddle_pos), NUM)
        for pp in range(n):
            if pp != self.my_num and paddle_pos[pp]!= [0, 0]:
                x, y = TERRAIN.get_kivy_coord(paddle_pos[pp], [10, 52])
                x, y = x * self.coef, y * self.coef
                self.paddle_d[pp].pos = [int(x), int(y)]

    def apply_classement(self, classement):
        """Applique le classement
        classement = {'pierre': 1, 'AI': 2}
        str = 'pierre': 1, 'AI': 2
        """

        text = "\n"
        if classement:
            for i in range(len(classement)):
                for name, rank in classement.items():
                    if rank == i + 1:
                        text += ". " + str(i+1) + "  " + name + "\n\n"

            self.classement.text = text
            self.titre.text = "Classement"
        else:
            self.titre.text = ""
            self.classement.text = ""

    def on_touch_move(self, touch):
        """Capture de la position de touch"""

        x = touch.x
        y = touch.y
        self.apply_touch(x, y)

    def apply_touch(self, x, y):
        """Retourne le calcul du déplacement de ma paddle"""

        if self.my_num:
            n = self.my_num
            x1, y1, x2, y2 = LINE[n+0], LINE[n+1], LINE[n+2], LINE[n+3]
            # y = a * x + b
            a, b = droite(x1, y1, x2, y2)
            # correction de x, y
            x = 1.1 * x - 500
            y = int(a * x + b) - 436

            self.apply_my_paddle_pos(x, y)

    def apply_my_paddle_pos(self, x, y):
        """Positionne ma paddle, avec la capture de position x, y
        sur l'écran
        """

        self.paddle_d[self.my_num].pos = [int(x * self.coef),
                                          int(y * self.coef)]
