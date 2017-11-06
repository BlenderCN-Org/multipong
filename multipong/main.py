#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = '0.008'

"""
version
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
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.core.window import Window
from kivy.config import Config
from kivy.core.window import Window

import os
from time import sleep
import socket
import json
import ast
from threading import Thread

# Les fichiers de ces modules sont dans le dossier courrant
# Réception en multicast
from labmulticast import Multicast
# Envoi en TCP
from labtcpclient import LabTcpClient


#Window.size = (640*2, 360*2)


def datagram_to_dict(data):
    '''Decode le message.
    Retourne un dict ou None
    '''

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


class Screen1(Screen):
    def __init__(self, **kwargs):

        super(Screen1, self).__init__(**kwargs)


class MainScreen(Screen):
    """Ecran principal"""

    def __init__(self, **kwargs):

        super(MainScreen, self).__init__(**kwargs)

        self.addr = None
        self.tcp = None
        self.get_tcp_port()
        self.get_tempo()
        self.receive_thread()

    def get_tcp_port(self):
        config = MultiPongApp.get_running_app().config
        self.tcp_port = int(config.get('network', 'tcp_port'))

    def get_tempo(self):
        config = MultiPongApp.get_running_app().config
        freq = int(config.get('network', 'freq'))
        if freq > 30:
            freq = 30
        if freq < 1:
            freq = 1
        self.tempo = 1 / freq

    def my_multicast(self):
        """Boucle infine de réception du serveur

        # TODO: diviser en plusieurs méthodes
        """

        my_multi = Multicast("228.0.0.5", 18888, 1024)

        a = 0
        while "Pour toujours":
            sleep(0.016)

            try:
                data = my_multi.receive()
                resp = datagram_to_dict(data)

                if resp:
                    if "paradis" in resp:
                        if "ip" in resp["paradis"]:
                            ip_server = resp["paradis"]["ip"]
                            self.addr = ip_server, self.tcp_port
                            self.run_send_thread()
            except:
                pass

    def my_tcp_sender(self, addr):
        """Envoi en TCP au serveur, lorsque l'ip serveur a été reçue
        en multicast"""


        clt = LabTcpClient(addr[0], addr[1])
        clt.connect_sock()
        a = 0

        while "Pour toujours":
            msg = {"Envoi": a}
            a += 1
            env = json.dumps(msg).encode("utf-8")
            clt.send(env)
            sleep(self.tempo)

    def receive_thread(self):
        # Thread de reception
        self.thread_multicast = Thread(target=self.my_multicast)
        self.thread_multicast.start()

    def run_send_thread(self):
        if self.addr:
            if not self.tcp:
                self.tcp = "tcp tourne"
                self.send_thread()
                sleep(0.1)

    def send_thread(self):
        """Thread d'envoi
        Ne doit être lancé qu'une seule fois,
        TODO: et être relancé si déconnexion
        """

        print("Un thread d'envoi est lancé")
        self.thread_tcp = Thread(target=self.my_tcp_sender,
                                        args=(self.addr,))
        self.thread_tcp.start()


# Liste des écrans, cette variable appelle les classes ci-dessus
# et doit être placée après ces classes
SCREENS = { 0: (MainScreen, "Menu"),
            1: (Screen1, "Jouer")}


class MultiPongApp(App):
    """Construction de l'application"""

    #TODO vérifier à quoi ça sert
    title = 'multipong'
    icon = '/data/multipong.png'

    """Exécuté par __main__,
    app est le parent de cette classe dans kv."""

    def build(self):
        """Exécuté en premier apres run()"""

        # Creation des ecrans
        self.screen_manager = ScreenManager()
        for i in range(len(SCREENS)):
            self.screen_manager.add_widget(SCREENS[i][0](name=SCREENS[i][1]))
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
                            { 'host': '228.0.0.5',
                              'multi_port': '18888',
                              'tcp_port': '8000',
                              'freq': '30'})

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
                      "desc": "Frequence entre 1 et 30 Hz",
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

        # Kivy
        MultiPongApp.get_running_app().stop()

        # Extinction de tout
        os._exit(0)


if __name__ == '__main__':
    MultiPongApp().run()
