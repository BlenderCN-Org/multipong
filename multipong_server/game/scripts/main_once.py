#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

## main_once.py

'''Ne jamais modifier ce script.
Les scripts:
- main_once.py
- main_always.py
sont les seuls scripts importer directement dans Blender.
Les autres scripts sont importés en temps que modules.

Il est alors possible de les modifier dans un éditeur externe
sans avoir à les recharger dans Blender.
'''

# imports locaux
from scripts import once


def main():
    """Fonction lancée à chaque frame dans blender en temps que module"""
    once.main()
