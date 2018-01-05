#! /usr/bin/env python3
# -*- coding: utf-8 -*-

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



def projection(x1, y1, x2, y2, m1, m2):
    """M' projection sur AB de M
    A(x1,y1), B(x2,y2),M(m1,m2), M'(M1,M2)
    """

    num = (x2-x1)*(m1-x2) + (y2-y1)*(m2-y2)

    denom = (x2-x1)**2 + (y2-y1)**2

    if denom == 0:
        # x2-x1=0 et y2-y1=0
        M1, M2 = y1 - x1, y1 - x1
    else:
        X = num/denom
        M1 = x2 + (x2 - x1)*X
        M2 = y2 + (y2 - y1)*X

    M1 = int(M1)
    M2 = int(M2)

    return M1, M2

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


if __name__ == '__main__':

    x1, y1 = 600, 200
    x2, y2 = 1200, 600

    m1, m2 = 500, 600

    M1, M2 = projection(x1, y1, x2, y2, m1, m2)

    print(M1, M2)
