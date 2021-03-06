auto-tatort
===========

Kleines Script um die aktuellen Tatort Folgen automatisiert (cron) aus der ARD Mediathek zu laden.

Wer ein weniger automatisiertes Script benoetigt und einfach nur eine Folge (bzw beliebige Sendung aus der Mediathek) runterladen moechte, schaut am besten bei Leo Gaggl vorbei: https://github.com/leogaggl/media/

Einsatz
=======

Bitte editieren und den Pfad anpassen in dem die Dateien abgelegt werden sollen. Die Vergabe des Names erfolgt automatisch und basiert auf dem Titel des RSS Feed Eintrags.

Dann Script jeden Abend um 23:50 via cron automatisiert ausfuehren lassen:

50 23 * * * python ~/bin/auto-tatort/autoTatort.py

Das Script laed nur Folgen aus dem RSS Feed, die auch das Datum des aktuellen Tages haben. Das hat den Vorteil, dass die ganzen Dokumentationen und Vorschauen etc nicht geladen werden. Diese werden naemlich meistens mit einem vergangenen Datum eingestellt. Die Filme werden irgendwann kurz nach der Sendung in den Feed eingebaut. Daher sollte es eigentlich immer mit 23:50 klappen.

Untertitel
==========

Die meisten oder alle Tatortfolgen scheinen auch Untertitel zu enthalten. Diese werden automatisch mit runter geladen und im gleichen Verzeichnis abgelegt. Bisher sind das rohe XML Dateien, mit denen man noch nicht viel anfangen kann. Es wird spaeter mal einen Konverter geben, der diese in gebraeuchliche Formate umwandeln kann.
Wenn keine Untertitel gewuenscht sind, kann man das entsprechend im Script anpassen.

Abhaengigkeiten
===============

import sys  
import feedparser (apt-get install python-feedparser)  
import datetime  
import urlparse  
from urllib import urlopen, urlretrieve  
import json  

Wurde nicht mit Python3 getestet, sollte aber vorher mit dem 2to3 Tool konvertiert werden!

Credits
=======
Author: Felix Knecht  
Die Idee hierzu ist aus den Scripten von Robin Gareus entstanden: http://www.rg42.org/wiki/tatort-dl
