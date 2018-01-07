#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import subprocess
from time import sleep
import threading


def server():
    subprocess.Popen(   [   'python3',
                            './multipong_server/server.py'])

def kivy():
    subprocess.Popen(   [   'python3',
                            './multipong/main.py'])

def always():
    while 1:
        sleep(1)

# Server et blender
server()

# Nombre de joueurs
N = 1

l = []
for i in range(N):
    kivy()
    sleep(0.1)


thread_a = threading.Thread(target=always)
thread_a.start()
