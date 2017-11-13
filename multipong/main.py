#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = '0.021'

"""
pas d'accent dans les fichiers !!!!!!!!!!!!!!!

version
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

Window.size = (int(640*2), int(360*2))

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

def test_old_new_xy(xy_old, xy_new):
    """xy = liste de 2
    arrondi a 0.01
    retourne True si different, False sinon
    La frequence d'envoi des xy peut monter a 73 Hz = beaucoup trop,
    a 0.01 c'est suffisamment precis.
    """

    ret = False

    if xy_new[0] != None and xy_new[1] != None:
        if isinstance(xy_old, list) and len(xy_old) == 2:
            if isinstance(xy_new, list) and len(xy_new) == 2:
                # Arrondi a 0.01
                a_old = [int(100 * xy_old[0]), int(100 * xy_old[1])]
                a_new = [int(100 * xy_new[0]), int(100 * xy_new[1])]
                if a_old != a_new:
                    ret = True

    return ret

def xy_correction(x, y):
    """Retourne x, y recalcule au dessus du bouton, de 0 a 1."""

    a1 = 0.015
    a2 = 0.50
    b1 = 0.09
    b2 = 0.97

    if x <= a1:
        x = 0.0
    elif x >= a2:
        x = 1.0
        y = None
    elif a1 < x < a2:
        x = (x / (a2 - a1)) - a1 / (a2- a1)

    if y:
        if y <= b1:
            y = 0.0
        elif y >= b2:
            y = 1.0
        elif b1 < y < b2:
            y = (y / (b2 - b1)) - b1 / (b2- b1)

    return x, y


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
    pos_x = NumericProperty(0)
    pos_y = NumericProperty(0)
    pos = ReferenceListProperty(pos_x, pos_y)

    def move(self):
        self.pos = self.pos + 1


class Screen1(Screen):

    ball = ObjectProperty(None)
    ##bat_0 = ObjectProperty(None)
    ##bat_1 = ObjectProperty(None)

    # Ce sont des attibuts de classe
    # Accessible avec root.points dans kv
    points = ListProperty(lines_points(carre, carre_correction))

    # Les 2 raquettes
    bat = ListProperty((15, 320, 700, 320))

    def __init__(self, **kwargs):

        super(Screen1, self).__init__(**kwargs)

        # Pour déplacement raquette
        self.xy_old = [0, 0]

        Clock.schedule_interval(self.update, 0.016)

    def update(self, dt):
        """{'svr_msg': {'dictat': {'transit': 0, 'reset': 0, 'level': 1,
        'ball': [10, 10]}, 'ip': '192.168.1.17'}}
        """

        # Acces a screen manager dans MultiPongApp
        screen_manager = MultiPongApp.get_running_app().screen_manager
        # Acces a l'ecran Menu
        self.menu = screen_manager.get_screen("Menu")
        # Acces a Network
        svr_data = self.menu.network.server_data
        self.apply_svr_data(svr_data)

    def apply_svr_data(self, svr_data):
        ball_pos = self.get_ball_position(svr_data)
        self.apply_ball_position(ball_pos)

    def get_ball_position(self, svr_data):
        try:
            svr_msg = svr_data["svr_msg"]
            dictat = svr_msg["dictat"]
            # Position de la balle dans le repere de blender
            ball_pos = dictat["ball"]
        except:
            ball_pos = 100, 100
        return ball_pos

    def apply_ball_position(self, ball_pos):

        cc = carre_correction

        self.ball.pos[0] = int((ball_pos[0]*cc[2]) + cc[0])
        self.ball.pos[1] = int((ball_pos[1]*cc[2]) + cc[1])

    ##def on_touch_move(self, touch):

        ##Screen1.bat[1] = touch.y


class MainScreen(Screen):
    """Ecran principal"""

    def __init__(self, **kwargs):

        super(MainScreen, self).__init__(**kwargs)

        # Nom du joueur
        #self.my_name = "j" + str(int(time()))[-6:]
        # name est déjà attribut de self
        self.my_name = self.get_user_id()

        # Construit le réseau, tourne tout le temps
        self.network = Network()
        self.network.network_start()

    def get_user_id(self):
        user = os.getlogin()
        print("User login:", user)
        return  user


class Network:
    """Tout le réseau, tourne toujours."""

    def __init__(self):

        # Adresse
        self.tcp_addr = None
        # True si ip serveur reçu
        self.tcp = None
        # Pour les loop
        self.loop = "Pour toujours"

        config = MultiPongApp.get_running_app().config
        self.tcp_port = self.get_tcp_port(config)
        self.tempo = self.get_tempo(config)
        self.multi_addr = self.get_multicast_addr(config)
        self.server_data = None

    def network_start(self):
        """La réception de l'ip lancera l'envoi"""

        self.receive_thread()

    def get_tcp_port(self, config):
        """Retourne le port TCP"""

        return int(config.get('network', 'tcp_port'))

    def get_multicast_addr(self, config):
        """Retourne l'adresse multicast"""

        multi_ip = config.get('network', 'multi_ip')
        multi_port = int(config.get('network', 'multi_port'))

        return (multi_ip, multi_port)

    def get_tempo(self, config):
        """pour sleep dans la boucle TCP"""

        freq = int(config.get('network', 'freq'))

        if freq > 60:
            freq = 60
        if freq < 1:
            freq = 1
        print("Fréquence d'envoi en TCP =", freq)

        return 1/freq

    def receive_thread(self):
        """Thread de réception"""

        # Thread de reception
        self.thread_multicast = Thread(target=self.my_multicast_loop)
        self.thread_multicast.start()

    def my_multicast_loop(self):
        """Boucle infine de réception du serveur

        # TODO: diviser en plusieurs méthodes, ip port de config
        """

        my_multi = Multicast(   self.multi_addr[0],
                                self.multi_addr[1],
                                1024)
        while self.loop:
            sleep(self.tempo)
            try:
                data = my_multi.receive()
                self.server_data = datagram_to_dict(data)
                # Si ip serveur recu, lancera le thread une fois
                self.run_tcp_thread(resp)
            except:
                #print("Pas de réception multicast")
                pass

    def run_tcp_thread(self, resp):
        """"""

        if resp:
            self.ip_server = self.get_server_ip(resp)

        self.tcp_addr = self.ip_server, self.tcp_port

        # Lance le thread si ip_server
        self.run_send_thread()

    def get_server_ip(self, resp):
        """Récupère l'ip du serveur, et lance le thread"""

        ip = None
        if "svr_msg" in resp:
            if "ip" in resp["svr_msg"]:
                ip = resp["svr_msg"]["ip"]
        return ip

    def my_tcp_sender_loop(self, addr):
        """Envoi en TCP au serveur, lorsque l'ip serveur a été reçue
        en multicast"""

        clt = LabTcpClient(addr[0], addr[1])

        while self.loop:
            msg = {"joueur": {  "name": "toto",
                                "ball": [10, 10],
                                "bat":  [-9.5, 3] }}

            env = json.dumps(msg).encode("utf-8")
            clt.send(env)
            sleep(self.tempo)

    def run_send_thread(self):
        if not self.tcp:
            if self.tcp_addr:
                self.tcp = "tcp tourne"
                self.send_thread()
                sleep(0.1)

    def send_thread(self):
        """Thread d'envoi: ne doit être lancé qu'une seule fois,
        les reconnexions sont faites par le client.
        """

        a = "Un thread d'envoi en TCP est lancé ip = {} port {}"
        print(a.format(self.ip_server, self.tcp_port))

        self.thread_tcp = Thread(target=self.my_tcp_sender_loop,
                                        args=(self.tcp_addr,))
        self.thread_tcp.start()


# Liste des écrans, cette variable appelle les classes ci-dessus
# et doit être placée après ces classes
SCREENS = { 0: (MainScreen, "Menu"),
            1: (Screen1,    "1"),
            2: (Screen2,    "2"),
            3: (Screen3,    "3"),
            4: (Screen4,    "4"),
            5: (Screen5,    "5")}


class MultiPongApp(App):
    """Construction de l'application. Exécuté par __main__,
    app est le parent de cette classe dans kv.
    """

    def build(self):
        """Exécuté en premier apres run()"""

        # Creation des ecrans
        self.screen_manager = ScreenManager()
        for i in range(len(SCREENS)):
            self.screen_manager.add_widget(SCREENS[i][0](name=SCREENS[i][1]))

        ##un = self.screen_manager.get_screen("1")
        ##Clock.schedule_interval(un.update, 0.0166)

        return self.screen_manager

    def on_start(self):
        """Exécuté apres build()"""
        pass

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

        if section == 'graphics' and key == 'rotation':
            Config.set('graphics', 'rotation', int(value))
            print("Screen rotation = {}".format(value))

    def go_mainscreen(self):
        """Retour au menu principal depuis les autres ecrans."""

        #if touch.is_double_tap:
        self.screen_manager.current = ("Menu")

    def do_quit(self):
        """Quitter proprement."""

        print("Quitter proprement")

        # Acces a screen manager dans MultiPongApp
        screen_manager = MultiPongApp.get_running_app().screen_manager

        # Acces a l'ecran Menu
        menu = screen_manager.get_screen("Menu")

        # Stop propre des threads reseaux
        menu.network.loop = None

        # Kivy
        MultiPongApp.get_running_app().stop()

        # Extinction de tout
        os._exit(0)


if __name__ == '__main__':
    MultiPongApp().run()

"""


['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__events__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__le__', '__lt__', '__metaclass__', '__module__', '__ne__', '__new__', '__proxy_getter', '__proxy_setter', '__pyx_vtable__', '__reduce__', '__reduce_ex__', '__repr__', '__self__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '_apply_transform', '_context', '_kwargs_applied_init', '_proxy_ref', '_walk', '_walk_reverse', 'add_widget', 'apply_property', 'bind', 'canvas', 'center', 'center_x', 'center_y', 'children', 'clear_widgets', 'cls', 'collide_point', 'collide_widget', 'create_property', 'disabled', 'dispatch', 'dispatch_children', 'dispatch_generic', 'events', 'export_to_png', 'fbind', 'funbind', 'get_center_x', 'get_center_y', 'get_parent_window', 'get_property_observers', 'get_right', 'get_root_window', 'get_top', 'get_window_matrix', 'getter', 'height', 'id', 'ids', 'is_event_type', 'move', 'on_disabled', 'on_opacity', 'on_touch_down', 'on_touch_move', 'on_touch_up', 'opacity', 'parent', 'pos', 'pos_hint', 'pos_x', 'pos_y', 'properties', 'property', 'proxy_ref', 'register_event_type', 'remove_widget', 'right', 'set_center_x', 'set_center_y', 'set_right', 'set_top', 'setter', 'size', 'size_hint', 'size_hint_max', 'size_hint_max_x', 'size_hint_max_y', 'size_hint_min', 'size_hint_min_x', 'size_hint_min_y', 'size_hint_x', 'size_hint_y', 'to_local', 'to_parent', 'to_widget', 'to_window', 'top', 'uid', 'unbind', 'unbind_uid', 'unregister_event_types', 'walk', 'walk_reverse', 'width', 'x', 'y']
"""
