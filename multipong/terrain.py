#! /usr/bin/env python3
# -*- coding: utf-8 -*-


# Pass variable between python script http://bit.ly/2n0ksWh
from __main__ import *
print("Dans le script terrain.py")
print("Coefficient de résolution écran:", COEF)


# TODO finir les poly de 5 à 10
def get_poly_name(num):
    """Retourne le polygone a utiliser en fonction du numéro de Screen
    """

    poly = {1: "CARRE",
            2: "CARRE",
            3: "TRIANGLE",
            4: "CARRE",
            5: "PENTA",
            6: "HEXA",
            7: "HEPTA",
            8: "OCTA",
            9: "ENNEA",
           10: "DECA"}

    return poly[num]

def get_points_dict(num):
    """Points des polygones en coordonnees blender"""

    points = {}

    points["CARRE"] = [  -9.93542,  9.935437,
                          9.93543,  9.93543,
                          9.93543, -9.93543,
                         -9.93543, -9.93543]

    points["TRIANGLE"] = [   0,        12.12306,
                           -14.22068, -12.50787,
                            14.22068, -12.50787]

    points["PENTA"] = [ 0,        9.34335,
                        9.74,     2.26683,
                        6.01965, -9.18323,
                       -6.01965, -9.18323,
                       -9.74,     2.26683]

    points["HEXA"] = []
    points["HEPTA"] = []
    points["OCTA"] = []
    points["ENNEA"] = []
    points["DECA"] = []

    return points[num]

def get_ratio(num):
    """[360, 360, 36] [décalage x, décalage y, scale] """

    ratio = {}

    ratio["CARRE"]    = [360, 360, 36]
    ratio["TRIANGLE"] = [418, 366, 29]
    ratio["PENTA"]    = [380, 358, 38.6]
    # TODO

    name = get_poly_name(num)
    return ratio[name]

def get_net_scale(num):
    """Retourne le scale sur terrain,
    0.03 pour 1 et 2, 0.07 pour 3 à 10
    """

    if num == 1 or num == 2 or num == 4:
        return 0.03
    else:
        return 0.07


class Terrain:

    def __init__(self, num):

        global COEF

        # Numéro du terrain = level = Numéro du Screen
        self.num = num

        # Nom du polygone
        self.poly_name = get_poly_name(self.num)

        # get ratio et coef écran
        self.ratio = get_ratio(self.num)
        self.coef = COEF

        # Points pour ligne terrain et filet
        self.line = self.line_points()
        self.net_line = self.get_net_line()

    def line_points(self):
        """Retourne la liste des coordonnées des points
        pour dessiner le polygone dans kivy,
        corrigés par ratio blender to kivy et résolution écran
        """

        line = []
        points = get_points_dict(self.poly_name)

        for i in range(len(points)):
            # size
            pt =  points[i] * self.ratio[2]

            # Offset
            if i % 2 == 0:
                pt += self.ratio[0]
                pt *= self.coef
            if i % 2 != 0:
                pt += self.ratio[1]
                pt *= self.coef
            line.append(int(pt))

        return line

    def get_net_line(self):
        """TODO avec scale"""

        net_line = []
        net_scale = get_net_scale(self.num)
        # Scale de chaque coordonnée
        for co in self.line:
            net_line.append(co * net_scale)
        # Mais il n'est pas au bon endroit

        return net_line

    def get_score_pos(self):
        """Retourne la position des scores"""

        return None

    def get_blender_coord(self, point, centre):
        """Transforme les coordonnées de kivy pour blender
        point = [x, y]
        widget kivy
        centre = [6, 52] par rapport au coin inf gauche
        """

        r = self.ratio
        x = (point[0] - r[0] - centre[0]) / r[2]
        y = (point[1] - r[1] - centre[1]) / r[2]

        return x, y

    def get_kivy_coord(self, point, centre):
        """Transforme les coordonnées de blender pour kivy
        point = [x, y]
        widget kivy
        centre = [6, 52] par rapport au coin inf gauche
        """

        r = self.ratio
        x = (point[0]*r[2]) + r[0] + centre[0]
        y = (point[1]*r[2]) + r[1] + centre[1]

        return x, y

if __name__ == '__main__':

    num = 1
    terrain = Terrain(num)

    # Nom du terrain
    name = terrain.poly_name
    print("Polygone", name)

    # Le terrain pour kivy
    line = terrain.line
    print("\nPoints pour kivy du polygone", name)
    print("line\n", line)

    # Conversion d'un point
    point = [12, 400]
    cb = terrain.get_blender_coord(point)
    print("\nCoordonnées du point ", point, " pour blender")
    print("    ", cb)

    # Création de la ligne du filet
    net_line = terrain.net_line
    print("\nPoints pour kivy du polygone du filet")
    print("net_line\n", net_line)
