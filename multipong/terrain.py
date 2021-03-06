#! /usr/bin/env python3
# -*- coding: utf-8 -*-


# #####################################################################
# Copyright (C) Labomedia November 2017
#
# This file is part of multipong.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# #####################################################################


from __main__ import *

# coeff ecran fait dans kv
# sauf get_kivy_coord() et triangle_correction
COEF = 1


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
    """Points des polygones en coordonnees blender."""

    points = {}

    points["CARRE"] = [  -9.93542,  -9.935437,
                         -9.93543,   9.93543,
                          9.93543,   9.93543,
                          9.93543,  -9.93543]

    points["TRIANGLE"] = [ 9.71809,  -8.43440,
                          -9.71809,  -8.43440,
                            0,        8.40137]

    points["PENTA"] = [ 6.01965, -9.18323,
                       -6.01965, -9.18323,
                       -9.74,     2.26683,
                        0,        9.374335,
                        9.74,     2.26683]

    points["HEXA"] = [         0,  -9.80139,
                        -8.48826,  -4.9007,
                        -8.48826,   4.9007,
                               0,   9.8014,
                         8.48826,   4.9007,
                         8.48825,  -4.9007 ]

    return points[num]

def get_paths_dict(num):
    """Points des polygones des paths en coordonnees blender.
    Les paddles se déplacent sur les paths
    """

    path = {}

    path["CARRE"] = [   -9.51, -9.51,
                        -9.51,  9.51,
                         9.51,  9.51,
                         9.51, -9.51 ]

    path["TRIANGLE"] = [ 9.08408, -8.06835,
                        -9.08408, -8.06835,
                              0,  7.66928 ]

    path["PENTA"] = [    5.780, -8.854,
                        -5.780, -8.854,
                        -9.353,  2.141,
                             0,  8.937,
                         9.353,  2.141 ]

    path["HEXA"] = [           0, -9.49087,
                        -8.21934, -4.74543,
                        -8.21934,  4.74544,
                               0,  9.49087,
                         8.21933,  4.74544,
                         8.21933, -4.74544]

    return path[num]

def get_ratio(num):
    """[360, 360, 36] [décalage x, décalage y, scale] """

    ratio = {}

    ratio["CARRE"]    = [360, 360, 36]
    ratio["TRIANGLE"] = [360, 360, 36]
    ratio["PENTA"]    = [370, 356, 36]
    ratio["HEXA"]     = [370, 360, 36]

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

        # Numéro du terrain = level = Numéro du Screen
        self.num = num

        # Nom du polygone
        self.poly_name = get_poly_name(self.num)

        # get ratio du level
        self.ratio = get_ratio(self.num)

        # Points pour ligne terrain, filet, path
        self.line = self.line_points()
        self.net_line = self.get_net_line()
        self.path_line = self.get_line_path()

    def line_points(self):
        """Retourne la liste des coordonnées des points
        pour dessiner le polygone dans kivy,
        corrigés par ratio blender to kivy
        """

        line = []
        points = get_points_dict(self.poly_name)

        for i in range(len(points)):
            # size
            pt =  points[i] * self.ratio[2]

            # Offset
            if i % 2 == 0:
                pt += self.ratio[0]
            if i % 2 != 0:
                pt += self.ratio[1]
            line.append(int(pt))

        return line

    def get_line_path(self):
        """Retourne la liste des coordonnées des points
        pour définir le polygone du path (chemin de déplacement des
        paddles) dans kivy,
        corrigés par ratio blender to kivy
        """

        path = []
        points = get_paths_dict(self.poly_name)

        for i in range(len(points)):
            # size
            pt =  points[i] * self.ratio[2]

            # Offset
            if i % 2 == 0:
                pt += self.ratio[0]
            if i % 2 != 0:
                pt += self.ratio[1]
            path.append(int(pt))

        return path

    def get_net_line(self):
        """Le filet est le terrain multiplié
        par un coeff = net_scale < 1
        Il est centré dans le terrain dans le kv avec
        [(x + (root.top/2)-10) for x in root.net]

        Mais ce n'est pas toujours centré !!
        carré:      root.top/2 ok
        triangle:   les x + root.top/10
                    les y - root.top/6
        10 correspond en gros à l'épaisseur du filet
        """

        net_line = []

        # Multiplicateur à appliquer sur le terrain
        # pour obtenir le filet
        net_scale = get_net_scale(self.num)

        # Scale de chaque coordonnée pour compenser l'épaisseur
        # de ligne de 3 pixels
        k = 0.85

        # Application de self.ratio
        for coord in self.line:
            net_line.append(coord * net_scale * k)

        # le centre du triangle est décalé
        if self.num == 3:
            net_line = self.triangle_correction(net_line)

        return net_line

    def triangle_correction(self, net_line):

        line = []
        for i in range(len(net_line)):
            if i % 2 == 0:
                net_line[i] -= 25*COEF
            if i % 2 != 0:
                net_line[i] -= 109*COEF
            line.append(int(net_line[i]))
        return line

    def get_blender_coord(self, point):
        """Transforme les coordonnées de kivy pour blender
        point = [x, y]
        widget kivy scr 1 et 2
        centre = [6, 52] par rapport au coin inf gauche
        """

        r = self.ratio
        x = (point[0] - r[0]) / r[2]
        y = (point[1] - r[1]) / r[2]

        return x, y

    def get_kivy_coord(self, point):
        """Transforme les coordonnées de blender pour kivy
        point = [x, y]
        self.ratio = [360, 360, 36] [décalage x, décalage y, scale]
        """

        r = self.ratio
        x = int(point[0]*r[2] + r[0])
        y = int(point[1]*r[2] + r[1])

        return x, y


if __name__ == '__main__':

    num = 6
    terrain = Terrain(num)

    # Nom du terrain
    name = terrain.poly_name
    print("Polygone", name)

    # Le terrain pour kivy
    line = terrain.line
    print("\nPoints pour kivy du polygone", name)
    print("line\n", line)

    # Le terrain pour kivy
    path_line = terrain.path_line
    print("\nPoints pour kivy du polygone", name)
    print("path_line\n", path_line)

    # Conversion d'un point
    point = [12, 400]
    cb = terrain.get_blender_coord(point)
    print("\nCoordonnées du point ", point, " pour blender")
    print("    ", cb)

    # Création de la ligne du filet
    net_line = terrain.net_line
    print("\nPoints pour kivy du polygone du filet")
    print("net_line\n", net_line)
