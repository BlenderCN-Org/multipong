# Multi Pong


## Jeu de pong sur android jusqu'à 10 joueurs

### Licence

~~~text

Copyright (C) Labomedia November 2017

Multi Pong is licensed under the
    Creative Commons Attribution-ShareAlike 3.0 Unported License.

To view a copy of this license, visit
    http://creativecommons.org/licenses/by-sa/3.0/

or send a letter to
    Creative Commons
    444 Castro Street
    Suite 900, Mountain View
    California, 94041
    USA

~~~

### Kivy, buildozer, python 3.5

Construit sur Debian Stretch 9.2

Voir [Kivy Buildozer pour créer une application Android avec un script python](https://wiki.labomedia.org/index.php/Kivy_Buildozer_pour_cr%C3%A9er_une_application_Android_avec_un_script_python)


### Installation sur android
Récupérer le apk sur android, l'installer après avoir autorisé les sources inconnues puisque la source est connue !!


### Réception sur Android en Multicast

Dans buildozer.spec,

~~~text
android.permissions = INTERNET,CHANGE_WIFI_MULTICAST_STATE,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE
~~~


### Merci à La Labomedia
