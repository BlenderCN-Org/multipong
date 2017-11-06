#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

## player_simul.py

#############################################################################
# Copyright (C) Labomedia November 2012
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

'''
Simulation des raquettes pour le niveau 10, les raquettes se déplacent
de x1, y1 à x2, y2 en sec secondes.

'''


from time import sleep
import threading
from decimal import *

#                  x1     y1     x2     y2   sec
BAT_D = {   0 : (-0.45, -8.93, -4.89, -7.49, 0.3),    # cas 2
            1 : (-8.95, -2.35, -5.55, -6.98, 7),    # cas
            2 : (-8.70,  2.29, -8.60, -2.35, 10),  # cas 4
            3 : (-8.34,  3.19, -5.55,  6.97, 0.4),  # cas 1
            4 : (-0.45,  8.94, -4.87,  7.50, 4),    # cas 4
            5 : ( 0.48,  8.92,  4.83,  7.50, 3),
            6 : ( 8.25,  3.26,  5.63,  6.96, 15),
            7 : ( 8.70, -2.35,  8.60,  2.27, 2),  # cas 2
            8 : ( 8.32, -3.18,  5.58, -6.95, 0.5),  # cas 3
            9 : ( 4.83, -7.50,  0.44, -8.94, 20)   } # cas 3


class BatSimul:
    '''Simulation des bats level 10 de MPFF.
    Tourne à 60 Hz
    '''

    def __init__(self, sec, x1, y1, x2, y2):
        '''sec != 0'''

        # Période de mise à jour
        self.periode = 0.015

        # Raquette
        self.bat = [x1, y1]

        # déplacement par frame
        if sec != 0:
            getcontext().prec = 16
            bat_speed = Decimal(1) / Decimal((60 * Decimal(sec)))
        else:
            bat_speed = Decimal(1)

        self.sens_x = 1
        self.sens_y = 1
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.dx = Decimal(abs(x2 - x1)) * bat_speed
        self.dy = Decimal(abs(y2 - y1)) * bat_speed

        self.animation_thread()

    def animation_thread(self):
        self.t = threading.Thread(target=self.animation)
        self.t.start()

    def animation(self):
        while 1:
            sleep(self.periode)
            self.bat_simul()

    def bat_simul(self):
        '''La bat va de x1,y1 à x2,y2 en self.bat_speed secondes par frames
        et retour.'''

        x = Decimal(self.bat[0])
        y = Decimal(self.bat[1])

        x += Decimal(self.sens_x) * self.dx
        y += Decimal(self.sens_y) * self.dy

        # cas 1
        if self.x1 < self.x2 and self.y1 < self.y2:

            if x > self.x2 or y > self.y2:
                self.sens_x = -1
                self.sens_y = -1

            if x < self.x1 or y < self.y1:
                self.sens_x = 1
                self.sens_y = 1

        # cas 2
        if self.x1 > self.x2 and self.y1 < self.y2:

            if x < self.x2 or y > self.y2:
                self.sens_x = 1
                self.sens_y = -1

            if x > self.x1 or y < self.y1:
                self.sens_x = -1
                self.sens_y = 1

        # cas 3
        if self.x1 > self.x2 and self.y1 > self.y2:

            if x < self.x2 or y < self.y2:
                self.sens_x = 1
                self.sens_y = 1

            if x > self.x1 or y > self.y1:
                self.sens_x = -1
                self.sens_y = -1

        # cas 4
        if self.x1 < self.x2 and self.y1 > self.y2:

            if x > self.x2 or y < self.y2:
                self.sens_x = -1
                self.sens_y = 1

            if x < self.x1 or y > self.y1:
                self.sens_x = 1
                self.sens_y = -1

        self.bat[0] = float(x)
        self.bat[1] = float(y)


if __name__ == "__main__":

    bat_simul = []
    for num in range(10):
        sim = BatSimul(BAT_D[num][4], BAT_D[num][0], BAT_D[num][1],
                                      BAT_D[num][2], BAT_D[num][3])
        bat_simul.append(sim)

    while 1:
        for p in range(10):
            print(  bat_simul[0].bat, bat_simul[1].bat, bat_simul[2].bat,
                    bat_simul[3].bat, bat_simul[4].bat, bat_simul[5].bat,
                    bat_simul[6].bat, bat_simul[7].bat, bat_simul[8].bat,
                    bat_simul[9].bat)
            sleep(0.0051)
