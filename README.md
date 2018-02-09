# Multi Pong

## Jeu de pong sur android jusqu'à 6 joueurs


##### [Multi Pong sur le wiki de La Labomedia](https://wiki.labomedia.org/index.php/Kivy_Multi_Pong)

![3 joueurs](/images/Mpff_02.png | width=200)
![10joueurs](/images/10players.png | width=200)

### Licence

~~~text
Copyright (C) Labomedia November 2017

Multi Pong is licensed under the
    Creative Commons Attribution-ShareAlike 3.0 Unported License.

To view a copy of this license, visit
    [creativecommons.org](http://creativecommons.org/licenses/by-sa/3.0/)

or send a letter to
    Creative Commons
    444 Castro Street
    Suite 900, Mountain View
    California, 94041
    USA
~~~

### Installation sur android
Rechercher
~~~text
wiki labomedia multi pong
~~~

Vous devriez arriver sur https://wiki.labomedia.org/index.php/Multi_Pong

Télécharger MultiPong-0.506-debug.apk

Sur Android --> Navigateur de fichier --> Dowloads

Tap sur le apk, il devrait vous annoncer d'autoriser les sources inconnues,

--> autoriser les sources inconnues
--> installer

#### Se connecter sur le même wifi que le serveur
Au labo, c'est HELLGATE

#### Lancer
--> l'icône est **Multi Pong**

### Kivy, buildozer, python 3.5

Construit sur Debian Stretch 9.2

Voir [Kivy Buildozer pour créer une application Android avec un script python](https://wiki.labomedia.org/index.php/Kivy_Buildozer_pour_cr%C3%A9er_une_application_Android_avec_un_script_python)

pour l'installation de buildozer et son utilisation.

### Installation du serveur sur un PC

#### Principe du serveur

Le serveur envoie en multi-cast en permanence à tous les joueurs et blender toutes les datas nécessaires avec en plus l'IP du serveur pour que les joueurs envoient en TCP.

Le Blender Game Engine sert de moteur physique et de visualisation du jeu sur grand écran.

#### Installation de twisted

* [Installation de Twisted pour python 3.x](https://wiki.labomedia.org/index.php/Installation_de_Twisted_pour_python_3.x)

#### Installation de Blender

~~~text
sudo apt-get install blender
~~~

#### Installation de mylabotools

mylabotools comprend mes scripts pour mes tâches courantes.

Voir  [mylabotools](https://github.com/sergeLabo/mylabotools)

#### Lancement du serveur
Un script sh lance un script python qui est le serveur,
ce serveur lance le blend avec le blenderplayer.

Cliquer sur:

~~~text
run_server
~~~

ou

~~~text
run_server_optimus
~~~

### Jouer sur un PC pour tester

#### Installation de kivy

* [Installation de Kivy](https://wiki.labomedia.org/index.php/2_Kivy:_Installation)

#### Lancement
Cliquer sur:

~~~text
run_game
~~~

### Pour info: Réception sur Android en Multicast
Dans buildozer.spec, définir:

~~~text
android.permissions = INTERNET,CHANGE_WIFI_MULTICAST_STATE,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE
~~~

### Travail à faire

### Ce qui ne sera pas fait

* Construire les écrans pour aller jusqu'à 10 joueurs

### Merci à La Labomedia
