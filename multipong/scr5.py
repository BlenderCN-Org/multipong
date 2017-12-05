#! /usr/bin/env python3
# -*- coding: utf-8 -*-


from kivy.properties import ListProperty
from kivy.properties import ReferenceListProperty
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty

from terrain import get_points_dict, get_ratio, lines_points
from kivy.uix.screenmanager import Screen

points_dict = get_points_dict()
PENTA = points_dict["PENTA"]

ratio = get_ratio()
PENTA_RATIO = ratio["PENTA"]


class Screen5(Screen):
    """Ecran pour 5 joueurs"""

    p = lines_points(PENTA, PENTA_RATIO)
    points = ListProperty(p)

    def __init__(self, **kwargs):

        super(Screen5, self).__init__(**kwargs)
        print("Initialisation de Screen5 ok")
