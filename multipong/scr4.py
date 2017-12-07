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
NUM = 4
TERRAIN = Terrain(NUM)
LINE = TERRAIN.line
NET = TERRAIN.net_line

# Pass variable between python script http://bit.ly/2n0ksWh
from __main__ import *
print("Dans le script scr1.py, ")
print("    coefficient de résolution écran:", COEF)


class Screen3(Screen):
    """Ecran pour 3 joueurs en position 0 1 2"""

    points = ListProperty(LINE)
    net = ListProperty(NET)
    ball = ObjectProperty()
    titre = ObjectProperty()
    classement = ObjectProperty()

    paddle_0 = ObjectProperty()
    paddle_1 = ObjectProperty()
    paddle_2 = ObjectProperty()
    paddle_3 = ObjectProperty()

    score_0 = ObjectProperty()
    score_1 = ObjectProperty()
    score_2 = ObjectProperty()
    score_3 = ObjectProperty()


    def __init__(self, **kwargs):

        super(Screen3, self).__init__(**kwargs)

        self.coef = COEF
        self.titre.text = "test"
        self.classement.text = ""

        # mon numéro dans
        self.my_num = 0

        # Dict des paddles appelés ensuite
        self.paddle_d = {   0: self.paddle_0,
                            1: self.paddle_1,
                            2: self.paddle_2,
                            3: self.paddle_3}

        # Dict des scores
        self.score_d = {    0: self.score_0,
                            1: self.score_1,
                            2: self.score_2,
                            3: self.score_3}

        print("Initialisation de Screen3 ok")

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

        try:
            x, y = TERRAIN.get_kivy_coord(ball_pos, [16, 16])
            x, y = x*self.coef + 5, y*self.coef - 50

            self.ball.pos = [int(x), int(y)]
        except:
            pass

    def apply_my_paddle_pos(self, y):
        """my paddle soit0, avec la capture de position sur l'écran"""

        for i in range(len(self.paddle_d)):
            if self.my_num == i:
                self.paddle_d[i].pos = (int(12 * self.coef),
                                        int( y * self.coef))

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

        # scale décalage
        y = int((((touch.y/700)*840) - 80)/self.coef)
        self.apply_my_paddle_pos(y)

    def get_my_blender_paddle_pos(self, my_pad):

        return TERRAIN.get_blender_coord([my_pad.pos[0],
                                          my_pad.pos[1]],
                                          [-6, -52])
