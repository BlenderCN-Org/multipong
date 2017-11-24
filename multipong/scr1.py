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
print(Window.size)

class Screen1(Screen):
    """Le joueur est 'Joueur 1'.
    Attibuts de classe
    """

    # Points du terrain carre accessible avec root.points dans kv
    points = ListProperty(LINE)
    net = ListProperty(NET)
    ball     = ObjectProperty(None)
    paddle_0 = ObjectProperty(None)
    paddle_1 = ObjectProperty(None)

    def __init__(self, **kwargs):

        super(Screen1, self).__init__(**kwargs)

        self.coef = 0.5
        ##scr_manager = .get_running_app().screen_manager
        ##print(scr_manager)

        print("Initialisation de Screen1 ok")

    def apply_ball_position(self, ball_pos):
        """Positionne la balle avec position du serveur."""

        bp = ball_pos
        self.ball.pos[0] = int((bp[0]*self.Ratio[2]) + self.Ratio[0] - 6*self.coef)
        self.ball.pos[1] = int((bp[1]*self.Ratio[2]) + self.Ratio[1] - 6*self.coef)

    def apply_other_paddles_position(self, paddle_pos, my_num):
        """paddle auto soit 1
             moi       paddle auto
        [[-9.5, 0.0], [9.5, -1.81], [0, 0], [0, 0], ....]
        """

        pp = paddle_pos
        try:
            a = (pp[1][0]*self.Ratio[2]) + self.Ratio[0] -6  * self.coef
            self.paddle_1.pos[0] = int(a)
            b = (pp[1][1]*self.Ratio[2]) + self.Ratio[1] -52 * self.coef
            self.paddle_1.pos[1] = int(b)
        except:
            pass

    def apply_my_paddle_position(self, y):
        """my paddle soit0"""

        self.paddle_0.pos[0] = int(12*self.coef)
        self.paddle_0.pos[1] = int(y*self.coef)

    def on_touch_move(self, touch):

        # scale décalage
        y = int((((touch.y/700)*840) - 80)/self.coef)

        #print("y sur bouton",y)
        self.apply_my_paddle_position(y)

    def get_my_blender_paddle_pos(self, my_pad):

        return TERRAIN.get_blender_coord([my_pad.pos[0],
                                          my_pad.pos[1]])


class PongApp(App):
    def build(self):
        game = Screen1()
        return game

if __name__ == '__main__':
    # marche pas, pas de *.kv
    PongApp().run()
