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
NUM = 2
TERRAIN = Terrain(NUM)
LINE = TERRAIN.line
NET = TERRAIN.net_line

# Pass variable between python script http://bit.ly/2n0ksWh
from __main__ import *
print("Dans le script scr1.py, ")
print("    coefficient de résolution écran:", COEF)


class Screen2(Screen):
    """Ecran pour 2 joueurs en position 0 et 1"""

    points = ListProperty(LINE)
    net = ListProperty(NET)
    ball = ObjectProperty()
    paddle_0 = ObjectProperty()
    paddle_1 = ObjectProperty()
    score_0 = ObjectProperty()
    score_1 = ObjectProperty()
    titre = ObjectProperty()
    classement = ObjectProperty()


    def __init__(self, **kwargs):

        super(Screen2, self).__init__(**kwargs)

        self.coef = COEF
        self.score_0.text = str(10)
        self.score_1.text = str(5)
        self.titre.text = "test"
        self.classement.text = ""

        # mon numéro dans
        self.my_num = 0

        print("Initialisation de Screen2 ok")

    def apply_my_num(self, my_num):
        """Appelé dans main"""
        #TODO trouver mieux !
        self.my_num = my_num

    def apply_paddle_red_color(self):
        if self.my_num == 0:
            self.paddle_0.rect_color = 1, 0, 0
        if self.my_num == 1:
            self.paddle_1.rect_color = 1, 0, 0

    def apply_classement(self, classement):
        """Applique le classement
        classement = {'pierre': 1, 'AI': 2}
        str = 'pierre': 1, 'AI': 2
        """

        if classement:
            self.titre.text = "Classement"
            t = ""
            # Pour réordonner, le json perd le OrderedDict()
            n = 1
            for k, v in classement.items():
                if v == n:
                    t += ". " + str(v) + "   " + k + "\n\n"
                n += 1
            self.classement.text = t
        else:
            self.titre.text = ""
            self.classement.text = ""

    def apply_score(self, score):
        """Set les scores
        apply_score(score)
        score = [4, 2]
        """

        self.score_0.text = str(score[0])
        self.score_1.text = str(score[1])

    def apply_ball_pos(self, ball_pos):
        """Positionne la balle avec position du serveur."""

        try:
            # ball = [12, 512]
            x, y = TERRAIN.get_kivy_coord(ball_pos, [16, 16])
            x, y = x * self.coef, y * self.coef

            self.ball.pos = [int(x), int(y)]
        except:
            pass

    def apply_my_paddle_pos(self, y):
        """my paddle soit0, avec la capture de position sur l'écran"""

        if self.my_num == 0:
            self.paddle_0.pos = (   int(12 * self.coef),
                                    int( y * self.coef))
        if self.my_num == 1:
            self.paddle_1.pos = (   int(700 * self.coef),
                                    int(  y * self.coef))

    def apply_other_paddles_pos(self, paddle_pos):
        """  Toutes les paddles sauf la mienne
             moi         l'autre
        [[-9.5, 0.0], [9.5, -1.81], [0, 0], [0, 0], ....]
        """

        for pp in range(len(paddle_pos)):
            if pp != self.my_num:
                if pp == 0:
                    x, y = TERRAIN.get_kivy_coord(paddle_pos[0],
                                                    [10, 52])
                    x, y = x * self.coef, y * self.coef
                    self.paddle_0.pos = [int(x), int(y)]
                if pp == 1:
                    x, y = TERRAIN.get_kivy_coord(paddle_pos[1],
                                                    [10, 52])
                    x, y = x * self.coef, y * self.coef
                    self.paddle_1.pos = [int(x), int(y)]

    def on_touch_move(self, touch):

        # scale décalage
        y = int((((touch.y/700)*840) - 80)/self.coef)
        self.apply_my_paddle_pos(y)

    def get_my_blender_paddle_pos(self, my_pad):

        return TERRAIN.get_blender_coord([my_pad.pos[0],
                                          my_pad.pos[1]],
                                          [-6, -52])
