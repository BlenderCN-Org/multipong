#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import subprocess
from time import sleep
import threading


def server():
    subprocess.Popen(   [   'python3',
                            './multipong_server/server.py'])

def blender():
    subprocess.Popen(   [   'blenderplayer',
                            './multipong_server/game/mp.blend'])

def kivy():
    subprocess.Popen(   [   'python3',
                            './multipong/main.py'])

def always():
    while 1:
        sleep(1)
        #print("ok")

thread_s = threading.Thread(target=server)
thread_s.start()
sleep(0.2)

thread_b = threading.Thread(target=blender)
thread_b.start()
sleep(0.2)

# Nombre de joueurs
N = 4

l = []
for i in range(N):
    t = threading.Thread(target=kivy)
    t.start()
    l.append(t)
    sleep(0.1)


thread_a = threading.Thread(target=always)
thread_a.start()
