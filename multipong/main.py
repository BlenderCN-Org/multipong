#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = '0.021'

"""
pas d'accent dans les fichiers !!!!!!!!!!!!!!!

version
0.022 fullscreen
0.021 landscape
0.020 avec balle
0.019 sans window size
0.018 sans utf-8
0.017 avec utf-8
0.016 plus utf8
0.015 test labo
0.014 ajout android.permissions
0.013 try sur multicast receive
0.012 print multicast
0.011 tcp addr fixe
0.010 avec print
0.009 frequence 30
0.008 envoi en tcp, réception en multicast, test débit fréquence
0.007 sans window size
0.006 avec import labmulticast
0.005 avec réception
0.004 avec Multicast()
0.003 avec twisted
0.002 pas d'accent dans kv
0.001 sans import autre que kivy
"""


import kivy
kivy.require('1.10.0')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import ListProperty
from kivy.properties import ReferenceListProperty
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.config import Config
from kivy.lang import Builder
from kivy.vector import Vector
from kivy.clock import Clock

import os
from time import time, sleep
import socket
import json
import ast
from threading import Thread

# Les fichiers de ces modules sont dans le dossier courrant
# Réception en multicast
from labmulticast import Multicast
# Envoi en TCP
from labtcpclient import LabTcpClient

Window.size = (1280, 720)

"""
1 joueur carre
2 joueur carre
3 joueur triangle
4 joueur carre
5 joueur penta
6 joueur hexa
7 joueur hepta
8 joueur octa
9 joueur ennea
10 joueur deca
"""

# Variables globales

# Points des polygones = coordonnées blender
# et correction [offset_x, offset_y, size]

carre = [-9.93542,  9.935437,
          9.93543,  9.93543,
          9.93543, -9.93543,
         -9.93543, -9.93543]

carre_correction = [360, 360, 36]

triangle = [0, 12.12306,
            -14.22068, -12.50787,
            14.22068, -12.50787]

triangle_correction = [418, 366, 29]

penta = [   0,        9.34335,
            9.74,     2.26683,
            6.01965, -9.18323,
           -6.01965, -9.18323,
           -9.74,     2.26683]

penta_correction = [380, 358, 38.6]

hexa = []
hepta = []
octa = []
ennea = []
deca = []

def lines_points(poly, poly_correction):
    """Retourne la liste des points pour dessiner le polygone.
    poly=liste des points avec coordonnées blender
    poly_correction=[offset_x, offset_y, size_x, size_y]
    """

    pc = poly_correction
    points_list = []

    for i in range(len(poly)):
        # size
        pt =  poly[i] * poly_correction[2]

        # Offset
        if i % 2 == 0:
            pt += poly_correction[0]
        if i % 2 != 0:
            pt += poly_correction[1]

        points_list.append(int(pt))

    return points_list

def datagram_to_dict(data):
    """Decode le message.
    Retourne un dict ou None
    """

    try:
        dec = data.decode("utf-8")
    except:
        print("Décodage UTF-8 impossible")
        dec = data

    try:
        msg = ast.literal_eval(dec)
    except:
        print("ast.literal_eval impossible")
        msg = dec

    if isinstance(msg, dict):
        return msg
    else:
        print("Message reçu: None")
        return None


class Screen5(Screen):
    """Ecran pour 5 joueurs"""

    p = lines_points(penta, penta_correction)
    points = ListProperty(p)

    def __init__(self, **kwargs):

        super(Screen5, self).__init__(**kwargs)


class Screen4(Screen):
    """Ecran pour 4 joueurs"""

    p = lines_points(carre, carre_correction)
    points = ListProperty(p)

    def __init__(self, **kwargs):

        super(Screen4, self).__init__(**kwargs)


class Screen3(Screen):
    """Ecran pour 3 joueurs"""

    p = lines_points(triangle, triangle_correction)
    points = ListProperty(p)

    def __init__(self, **kwargs):

        super(Screen3, self).__init__(**kwargs)


class Screen2(Screen):
    """Ecran pour 2 joueurs"""

    p = lines_points(carre, carre_correction)
    points = ListProperty(p)

    def __init__(self, **kwargs):

        super(Screen2, self).__init__(**kwargs)


class PongBall(Widget):
    center_x = NumericProperty(0)
    center_y = NumericProperty(0)
    center = ReferenceListProperty(center_x, center_y)

    def move(self):
        pass


class Screen1(Screen):

    # Ce sont des attibuts de classe
    # Accessible avec root.points dans kv
    ball = ObjectProperty(None)
    points = ListProperty(lines_points(carre, carre_correction))
    paddle = ListProperty((15, 320, 700, 320))

    def __init__(self, **kwargs):

        super(Screen1, self).__init__(**kwargs)
        print(dir(self))

    def update(self, dt):
        """Recupere le message du seveur tous les dt lance par Clock:
        {'svr_msg': {'dictat': {'transit': 0, 'reset': 0, 'level': 1,
        'ball': [10, 10]}, 'ip': '192.168.1.17'}}
        TODO cette fonction doit etre commune a tous les screen
        """

        svr_data = self.get_svr_data()
        self.apply_svr_data(svr_data)

    def get_svr_data(self):
        # Acces a screen manager dans MultiPongApp
        screen_manager = MultiPongApp.get_running_app().screen_manager
        # Acces a l'ecran Menu
        self.menu = screen_manager.get_screen("Menu")
        # Acces a Network
        svr_data = self.menu.network.server_data

        return svr_data

    def apply_svr_data(self, svr_data):
        """Recupere la position de la balle dans le message du serveeur,
        puis applique cette position a la balle.
        """
        ball_pos = self.get_ball_position(svr_data)
        self.apply_ball_position(ball_pos)

    def get_ball_position(self, svr_data):
        """Recupere la position de la balle dans le message du serveur
        """

        try:
            svr_msg = svr_data["svr_msg"]
            dictat = svr_msg["dictat"]
            # Position de la balle dans le repere de blender
            ball_pos = dictat["ball"]
        except:
            ball_pos = 100, 100

        return ball_pos

    def apply_ball_position(self, ball_pos):
        """Positionne la balle avec position du serveur"""

        cc = carre_correction

        self.ball.center[0] = int((self.ball.center[0]*cc[2]) + cc[0])
        self.ball.center[1] = int((self.ball.center[1]*cc[2]) + cc[1])

    def on_touch_move(self, touch):
        ##Screen1.paddle[1] = touch.y
        pass


class MainScreen(Screen):
    """Ecran principal"""

    def __init__(self, **kwargs):

        super(MainScreen, self).__init__(**kwargs)


class Network:
    """."""

    def __init__(self):

        # config, obtenu par hasard
        MultiPongApp.load_config(self)
        config = MultiPongApp.get_running_app().config

        # TCP
        self.tcp_ip = None
        self.tcp_port = self.get_tcp_port(config)
        self.tcp_clt = None

        # Multi
        self.multi_ip, self.multi_port = self.get_multicast_addr(config)
        self.my_multi = Multicast(  self.multi_ip,
                                    self.multi_port,
                                    1024)
        self.server_msg = None

        # Verif freq
        self.t = time()
        self.v_freq = 0

    def verif_freq(self):
        self.v_freq += 1
        a = time()
        if a - self.t > 1:
            print("FPS:", self.v_freq)
            self.v_freq = 0
            self.t = a

    def network_update(self, dt):
        """A chaque Clock, maj de reception, maj des datas, envoi
        level
        ball
        paddles
        scores
        """

        self.verif_freq()

        # Recup du message su serveur en multicast
        server_msg = self.get_multicast_msg()

        # Recup ip serveur si pas deffinie
        self.set_server_addr(server_msg)

        # Création du socket TCP si none
        self.create_tcp_socket()

        # Recup des datas dans le message


        # Maj du jeu


        # Envoi au serveur
        self.send_TCP_msg()

    def get_multicast_addr(self, config):
        """Retourne l'adresse multicast"""

        multi_ip = config.get('network', 'multi_ip')
        multi_port = int(config.get('network', 'multi_port'))

        return multi_ip, multi_port

    def get_multicast_msg(self):
        try:
            data = my_multi.receive()
            server_msg = datagram_to_dict(data)
        except:
            #print("Pas de réception multicast")
            server_msg = None
        return server_msg

    def get_tcp_port(self, config):
        """Retourne le port TCP"""

        return int(config.get('network', 'tcp_port'))

    def set_server_addr(self, msg):
        """Récupère l'ip du serveur, et defini l'adresse serveur."""

        if msg and "svr_msg" in msg:
            if "ip" in msg["svr_msg"] and not self.tcp_addr:
                self.tcp_ip = msg["svr_msg"]["ip"]

    def create_tcp_socket(self):
        if self.tcp_ip and not self.tcp_clt:
            try:
                self.tcp_clt = LabTcpClient(self.tcp_addr[0],
                                            self.tcp_addr[1])
            except:
                self.tcp_clt = None
                print("Pas d'ip dans le message du serveur")

    def send_TCP_msg(self):
        msg = {"joueur": {  "name": "toto",
                    "ball": [10, 10],
                    "paddle":  [-9.5, 3] }}
        env = json.dumps(msg).encode("utf-8")
        if self.tcp_clt:
            self.tcp_clt.send(env)


SCREENS = { 0: (MainScreen, "Menu"),
            1: (Screen1,    "1"),
            2: (Screen2,    "2"),
            3: (Screen3,    "3"),
            4: (Screen4,    "4"),
            5: (Screen5,    "5")}


class MultiPongApp(App, Network):
    """Construction de l'application. Exécuté par __main__,
    app est le parent de cette classe dans kv.
    """

    def __init__(self, **kwargs):
        super(MultiPongApp, self).__init__(**kwargs)

    def build(self):
        """Exécuté en premier apres run()"""

        # Creation des ecrans
        self.screen_manager = ScreenManager()
        for i in range(len(SCREENS)):
            self.screen_manager.add_widget(SCREENS[i][0](name=SCREENS[i][1]))

        return self.screen_manager

    def on_start(self, **kwargs):
        """Exécuté apres build()"""

        #super(MultiPongApp, self).__init__(**kwargs)

        # Nom du joueur: name est déjà attribut de self
        self.my_name = self.get_user_id()

        # Construit le réseau, tourne tout le temps
        #self.network = Network()

        # Rafraichissement du jeu
        tempo = self.get_tempo()
        self.event = Clock.schedule_interval(self.network_update, tempo)

    def get_tempo(self):
        """Retourne la tempo de la boucle de Clock."""

        freq = int(self.config.get('network', 'freq'))

        if freq > 60:
            freq = 60
        if freq < 1:
            freq = 1
        print("Fréquence d'envoi en TCP =", freq)

        return 1/freq

    def get_user_id(self):
        user = os.getlogin()
        print("User login:", user)
        return  user

    def build_config(self, config):
        """Si le fichier *.ini n'existe pas,
        il est créé avec ces valeurs par défaut.
        Si il manque seulement des lignes, il ne fait rien !
        """

        config.setdefaults('network',
                            { 'multi_ip': '228.0.0.5',
                              'multi_port': '18888',
                              'tcp_port': '8000',
                              'freq': '60'})

        config.setdefaults('kivy',
                            { 'log_level': 'debug',
                              'log_name': 'multipong_%y-%m-%d_%_.txt',
                              'log_dir': '/sdcard',
                              'log_enable': '1'})

        config.setdefaults('postproc',
                            { 'double_tap_time': 250,
                              'double_tap_distance': 20})

    def build_settings(self, settings):
        """Construit l'interface de l'écran Options,
        pour multipong seul,
        Kivy est par défaut,
        appelé par app.open_settings() dans .kv
        """

        data = """[{"type": "title", "title": "Configuration du reseau"},

                      {"type": "numeric",
                      "title": "Frequence d'envoi",
                      "desc": "Frequence entre 1 et 60 Hz",
                      "section": "network", "key": "freq"}
                   ]"""

        # self.config est le config de build_config
        settings.add_json_panel('MultiPong', self.config, data=data)

    def on_config_change(self, config, section, key, value):
        """Si modification des options, fonction appelee automatiquement."""

        freq = int(self.config.get('network', 'freq'))
        menu = self.screen_manager.get_screen("Menu")

        if config is self.config:
            token = (section, key)

            # If frequency change
            if token == ('network', 'freq'):
                # Restart the server with new address
                #self.screen_manager.get_screen("Menu").restart_server()
                print("Nouvelle frequence", freq)

    def go_mainscreen(self):
        """Retour au menu principal depuis les autres ecrans."""

        #if touch.is_double_tap:
        self.screen_manager.current = ("Menu")

    def do_quit(self):
        """Quitter proprement."""

        print("Quitter proprement")

        # Stop propre de Clock
        self.event.cancel()

        # Kivy
        MultiPongApp.get_running_app().stop()

        # Extinction de tout
        os._exit(0)


if __name__ == '__main__':
    MultiPongApp().run()

"""


['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__events__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__le__', '__lt__', '__metaclass__', '__module__', '__ne__', '__new__', '__proxy_getter', '__proxy_setter', '__pyx_vtable__', '__reduce__', '__reduce_ex__', '__repr__', '__self__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '_apply_transform', '_context', '_kwargs_applied_init', '_proxy_ref', '_walk', '_walk_reverse', 'add_widget', 'apply_property', 'bind', 'canvas', 'center', 'center_x', 'center_y', 'children', 'clear_widgets', 'cls', 'collide_point', 'collide_widget', 'create_property', 'disabled', 'dispatch', 'dispatch_children', 'dispatch_generic', 'events', 'export_to_png', 'fbind', 'funbind', 'get_center_x', 'get_center_y', 'get_parent_window', 'get_property_observers', 'get_right', 'get_root_window', 'get_top', 'get_window_matrix', 'getter', 'height', 'id', 'ids', 'is_event_type', 'move', 'on_disabled', 'on_opacity', 'on_touch_down', 'on_touch_move', 'on_touch_up', 'opacity', 'parent', 'pos', 'pos_hint', 'pos_x', 'pos_y', 'properties', 'property', 'proxy_ref', 'register_event_type', 'remove_widget', 'right', 'set_center_x', 'set_center_y', 'set_right', 'set_top', 'setter', 'size', 'size_hint', 'size_hint_max', 'size_hint_max_x', 'size_hint_max_y', 'size_hint_min', 'size_hint_min_x', 'size_hint_min_y', 'size_hint_x', 'size_hint_y', 'to_local', 'to_parent', 'to_widget', 'to_window', 'top', 'uid', 'unbind', 'unbind_uid', 'unregister_event_types', 'walk', 'walk_reverse', 'width', 'x', 'y']
"""
