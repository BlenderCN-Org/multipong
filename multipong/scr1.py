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
NUM = 1
TERRAIN = Terrain(NUM)
LINE = TERRAIN.line
NET = TERRAIN.net_line

# Pass variable between python script http://bit.ly/2n0ksWh
from __main__ import *
print("Dans le script scr1.py, ")
print("    coefficient de résolution écran:", COEF)


class Screen1(Screen):
    """1 joueur en position 1"""

    # Points du terrain carre accessible avec root.points dans kv
    points = ListProperty(LINE)
    net = ListProperty(NET)
    ball     = ObjectProperty(None)
    paddle_0 = ObjectProperty(None)
    paddle_1 = ObjectProperty(None)
    score_0 = NumericProperty(10)
    score_1 = NumericProperty(5)
    
    def __init__(self, **kwargs):

        super(Screen1, self).__init__(**kwargs)

        self.coef = COEF
        self.score_0 = 10
        self.score_1 = 10
        print("Initialisation de Screen1 ok")
        
    def apply_score(self, score):
        """Set les scores"""
        
        pass  #score[0]
        
    def apply_ball_position(self, ball_pos):
        """Positionne la balle avec position du serveur."""

        try:
            #if len( ball_pos) == 2:
            # Transformation en coordonnées kivy
            # TODO [-6, -6] à corriger avec coef
            # hauteur, largeur balle = height / 66
            h = int(720 * COEF / 66)  # 12 pour 720
            x, y = TERRAIN.get_kivy_coord(ball_pos, [-h, -h])
            self.ball.pos = [int(x), int(y)]
        except:
            pass

    def apply_my_paddle_position(self, y):
        """my paddle soit0, avec la capture de position sur l'écran"""

        self.paddle_0.pos[0] = int(12 * self.coef)
        self.paddle_0.pos[1] = int( y * self.coef)

    def apply_other_paddles_position(self, paddle_pos, my_num):
        """ paddle auto soit 1
             moi       paddle auto
        [[-9.5, 0.0], [9.5, -1.81], [0, 0], [0, 0], ....]
        """
        try:
            #if len(paddle_pos) == 2:
            # Transformation en coordonnées kivy
            x, y = TERRAIN.get_kivy_coord(paddle_pos[1], [-6, -52])
            self.paddle_1.pos[0] = int(x)
            self.paddle_1.pos[1] = int(y)
        except:
            pass

    def on_touch_move(self, touch):

        # scale décalage
        y = int((((touch.y/700)*840) - 80)/self.coef)

        #print("y sur bouton",y)
        self.apply_my_paddle_position(y)

    def get_my_blender_paddle_pos(self, my_pad):

        return TERRAIN.get_blender_coord([my_pad.pos[0],
                                          my_pad.pos[1]],
                                          [-6, -52])


class Scr1App(App):
    # marche pas pb avec coef
    def build(self):
        coef = 1
        Window.size = (1280, 720)
        game = Screen1(coef)
        return game


if __name__ == '__main__':
    # marche pas pb avec coef
    Scr1App().run()
