# vavoo-parser (für LiveTV) + xstream-addon (für VoD's & Series) ...

## Next Gen fork - (Beta!) CLI Version

# Update Verlauf:

### Update v.1.3.8:
- Immer diese fu_ki_g mini fixxes nervt total ^^
### Update v1.3.7:
- Datenbank auf gesplittet um database locks zu vermeiden ...
- api.py added: Http HEAD & OPTIONS function ...
- Settings changed: m3u8+epg service function set to ON & m3u8 sleep time to 96 & codec set to hls ...
### Update v.1.3.5:
- neuer Menüeintrag im cli zum Ausführen der XStream scraper und anschließendem re-generieren der Listen
### Update v.1.3.2:
- epg.xml.gz export bug fixx ... Jetzt läuft's wieder gut ;-)
### Update v1.3.0:
- Xtream Code Api letzte Funktion komplementiert. (get.php m3u/m3u_plus ...)
- added custom_sid: '' to return json, nun laufen alle gängigen Xtream Code App's wie IPTV Smarters, IPTV Extream, IPTV Pro usw.
### Update to v1.2.5:
- Xtream Code Api gefixxt, sodass jetzt xtream code api, livetv + serien + filme mit epg läuft ...
### Update to v1.2.1:
- HLS/TS Stream Source Settings wahl für Xtream api code Live TV ...
- Einstellung für epg Provider, Icon & Rytec ID's xml.gz generation ...
- Automatische erfassung der Internet IP für den Vavoo key, ggf automatische neu generierung dessen ...
- Vavoo Live TV hls Streams hinzugefügt, sodass via SmartIPTV auf Samsung Smart TV's gestreamt werden kann...
- Global Search, Fixxed sodass jetzt auch Filme gesucht und geaddet werden konnen ...
- Signatur Key check integriert, sodass wenn sich internet ip ändert bzw. key sigvalitUntil ausläuft, automatisch ein neuer Key angefordert wird ...
- Main Settings wurden neu gestaltet, jetzt gibts ne kleine Info zur Setting ;-)
- Xtream Code zu 100% integriert. Ab jetzt kann insofern Xtream Code api vom clienten unterstützt wird, den gesamten Kontent darüber bekommen könnt! (Info hier drunter ^^)

# Installation / Start:

```shell
python3 -m pip install vxparser
```

```shell
vxparser
```

# Xtream Codes API Readme:

Xtream ist nun soweit verbaut dass die panel_api.php, player_api.php & xmltv.php zu 100% via GET+POST Callable sind ...

Wie gehabt spielt der username & password keine Rolle, aber um auch Items angezeigt zu bekommen muss zuvor (wie für die m3u8 listen) Get LiveTV Lists (für LiveTV) oder

Get New VoD & Series (für Filme & Serien) zumindest 1x ausgeführt worden sein. Genauer gesagt es sollten auch Datensätze in der Database vorhanden sein ;-)

Aber dann läuft der LiveTV teil komplett ohne das auf die Server IP in den m3u8 Listen geachtet werden muss, zwecks dynamischer Übergabe dessen (und automatischer SigKey

überprüfung, funktioniert selbst Intetnet IP change nahtlos ohne das was eingestellt werden muss! (Solange die Server API von mir local auf dem Client Gerät gestartet ist!)

Z.b. über Android -> Termux -> locale Ausführung meiner API ...

So das erstmal dazu, jetzt gibts noch ne api callable Übersicht (Beispiel Anhand GET Requests, für POST Request müssen die Parameter in body form übertragen werden ...):

(* = kann man eingeben was man will! X = int(id) ... (also eine Zahl ^^))


- GET ACCOUND Info:
```shell
panel_api.php?username=*&password=*
```
- GET VOD Stream Categories:
```shell
player_api.php?username=*&password=*&action=get_vod_categories
```
- GET VOD Streams:
```shell
player_api.php?username=*&password=*&action=get_vod_streams
player_api.php?username=*&password=*&action=get_vod_streams&category_id=X
```
- GET VOD Info:
```shell
player_api.php?username=*&password=*&action=get_vod_info&vod_id=X
```
- GET SERIES Categories:
```shell
player_api.php?username=*&password=*&action=get_series_categories
```
- GET SERIES Streams:
```shell
player_api.php?username=*&password=*&action=get_series
player_api.php?username=*&password=*&action=get_series&category_id=X
```
- GET SERIES Info:
```shell
player_api.php?username=*&password=*&action=get_series_info&series_id=X
```
- GET LIVE Categories:
```shell
player_api.php?username=*&password=*&action=get_live_categories
```
- GET LIVE Streams:
```shell
player_api.php?username=*&password=*&action=get_live_streams
player_api.php?username=*&password=*&action=get_live_streams&category_id=X
```
- GET XMLTV:
```shell
xmltv.php?username=*&password=*
```
- GET EPG:
```shell
player_api.php?username=*&password=*&action=get_simple_data_table&steam_id=X
```
- GET SHORT EPG:
```shell
player_api.php?username=*&password=*&action=get_short_epg&steam_id=X&limit=X
```
- GET m3u:
```shell
get.php?username=*&password=*&type=[m3u|m3u_plus]&output=[hls|ts|mpegts|rtmp]
```

### Verbesserungen in dieser Version:

- API komplett mit Python 3 verwendbar. Alle benötigten Packages via pip installierbar. Keine zusätzlichen Binaries benötigt! (wie lighttpd, php in termux Version z.b...)
- Auf jedem System startbar. Android (via Termux ab Android version 5), Linux, Raspberry Pi, Windows ...
- Effizienz Steigerung im Allgemein verfahren durch multiprocessing bzw. async requests ...

### Erneuerungen in dieser Version:

- CLI Menü
- Settings
- Service Option (LiveTV m3u8 lists & epg.xml.gz)
- Xstream Addon integration (voll automatische Kontent abfrage der aktuell beliebtesten Stream Sites für Filme und Serien ...)
Momentan verfügbare Plugins:
- cinemathek
- dokus4
- filmpalast
- hdfilme
- kinokiste
- kino
- kkiste
- megakino
- movie2k
- movie4k
- movieking
- serienstream (accound benötigt!)
- streamcloud
- streamen
- streampalace
- xcine

### Hintergrund Infos:

1. Menü Information:

Allgemeine Menüpunkt Auswahl (bestätigung) via
- [ENTER]

Im Selection Menü Menüpunkt Auswahl (select) via
- [Leertaste] (an oder abwählen)
- [Rechts] (anwählen eines Menüpunktes)
- [Links] (abwählen eines Menüpunktes)

Bestätigung der getroffenen Auswahl im Selection Menü via
- [ENTER]

Falls das Menü mal nicht Sichtbar sein sollte (zwecks output etc.), bekommt man es wieder Sichtbar indem man [Hoch] oder [Runter] geht.


2. Menü Aufbau:

- Main Menü:

```shell
   Settings =>                       #Submenü
   Vavoo (LiveTV) =>                 #Submenü
   Xstream (VoDs & Series) =>        #Submenü
   Stop Services                     #Services einschaltbar via Settings
   Restart Services                  #epg_service / m3u8_service:
   - Clean Database (Settings)       #Löscht aktuelle einstellungen aus der Sqlite Datenbank
   - Clear Cache Path                #Löscht den aktuellen cache Ordner
   <= Shutdown                       #Exit Programm
```

- Main Settings:

```shell
   <= Back                           #Zurück zum Hauptmenü
   [0.0.0.0]                         #FastAPI Server IP (0.0.0.0 = listen on all ips)
   [192.168.2.67]                    #Server IP for M3U8 List Creation
   [8080]                            #Server Port
   [On]                              #Set Automatic Network IP to Server IP Setting
   [Off]                             #LiveTV m3u8 Listen erstellung Background Service (0=Aus,1=Ein)
   [12]                              #Warte Zeit für m3u8 Listen erstellung in Stunden.
   [Info]                            #Log Level (1=Info,3=Error)
   [Off]                             #Search in TMDB after VoD & Series Infos
   []                                #Username of S.to User Accound
   []                                #Password for S.to User Accound
   [ts]                              #Bevorzugter codec für Xtream Codes
```

- Vavoo Menü:

```shell
Get LiveTV Lists                     #Erstellt Sky LiveTV m3u8 Lists (alle Länder...)
Get epg.xml.gz                       #Erstellt epg.xml.gz für Germany LiveTV
Delete Signatur Key                  #Löscht aktuellen Vavoo Signatur Key
Clean Database (LiveTV)              #Löscht alle LiveTV Einträge aus der Datenbank.
<= Main Menu                         #Zurück zum Hauptmenü
```

- Vavoo Settings:

```shell
   <= Back
   [On]                              #Generate HLS m3u8
   [On]                              #Vavoo Channel Namen ersetzen
   [Magenta]                         #Provider to get EPG Infos
   [Off]                             #Start epg.xml.gz Creation for LiveTV als Service
   [5]                               #Sleep Time for epg.xml.gz Creation Service in Tagen
   [7]                               #Anzahl an Tagen für epg.xml.gz Erstellung
   [On]                              #Provider IDs mit Rytec ersetzen
   [Provider]                        #Logos bevorzugen
```

- Info:
Wenn sich die Server Ip ändert 1x "Get LiveTV Lists" ausgewählen, damit die aktuelle Netzwerk IP in den LiveTV Listen ersetzt wird.
ggf. "Delete Signatur Key" falls momentaner Signatur Key noch nicht ausgelaufen ist. (neuer key wird automatisch erstellt...)

- Xstream Menü:

```shell
   Settings =>                       #Site Einstellungen, an/abschaltung einzelner Sites für Suche/Auto Generation.
   Global Search                     #Site Suche um Movies und/oder Serien zur Datenbank hinzu zu fügen.
   Get New VoD & Series              #Automatische Suche nach Inhalten in allen Sites (Sites unter Settings ein/abschaltbar)
   ReCreate vod+series.m3u8          #Erstellt vod.m3u8 (für Filme) + series.m3u8 (für Serien) aus der Datenbank.
   Clean Database (Streams)          #Löscht alle Stream's aus der Datenbank.
   <= Main Menu                      #Zurück zum Hauptmenü
```

- Info:
Genereller Ablauf ist wie folgt:
1. "Get New VoD & Series" oder "Global Search" zum befüllen der Datenbank.
2. Gefolgt von "ReCreate vod+series.m3u8" um die neuen Datenbank einträge in die Listen zu schreiben.
- ggf. Wenn sich die Server Ip ändert 1x"ReCreate vod+series.m3u8" ausgewählen, damit die aktuelle Netzwerk IP in den LiveTV Listen ersetzt wird.

- Xstream Settings:

```shell
[X] cinemathek: auto list creation?  # Aktiviert Site für die Automatische Suche (Xstream Menü: Get New VoD & Series)
[X] cinemathek: global search?       # Aktiviert SIte für die Site Suche (Xstream Menü: Global Search)
...
...
```

### Allgemeiner Ablauf:

Die meisten Programm Daten leiten sich von dem Kodi Plugin Xstream (Special thanks to Xstream Team!) & resolverurl (Special thanks to gujal!) ab.

Das Autoscript durchsucht die Sites bis zu dem link "showHosters" und trägt alle Items inklusive aller relevanten Infos in die Datenbank.

Wenn dann ein Stream vom Clienten angefordert wird, holt der Server alle aktuellen Hoster zu dem Item ein und leitet den 1. Stream an den Clienten weiter. (insofern Online ...)

Fragt man den selben Item nocheinmal an, mekt sich der Server die Position in der Hoster Liste und versucht dann den 2. Stream der List an den Clienten weiter. (insofern mehr als 1 Hoster vorhanden ...)

Dabei spielt es momentan noch keine Rolle ob der vorige Stream Erfolgreich weitergeleitet wurde oder nicht. Das bedeutet will man wieder zur 1. Hoster Url muss das Item so lange angefragt werden bis der Server wieder bei der 1. Url zurück springt ... (Output Infos im Server Terminal ...)


<del>Hidden Features:</del>

- Xtream Codes API faker für VoD's & Series weitesgehend Integriert. Das bedeutet, wenn der Client Xtream Codes API unterstützt, kann man den Server über den selben port wie normal eintragen und alle LiveTV + VoD & Series Inhalte mit allen Infos (wie beschreibung, länge usw.) genießen.

Dabei spielt es keine Rolle was als username & password eingetragen wird, der Server akzeptiert euch immer. Hierfür wird automatisch die tmdb infos zu jedem Item (falls vorhanden) mit in die Datenbank eingetragen.

<del>Dennoch ist momentan noch von der Xtream Codes API ab zu raten! </del>

<del>Weil der Xtream Codes API Client hat scheinbar keine Timeout Zeiten, was schnell zu einer dauer wieder Anfrage des clienten führt, was wiederrum den Server schnell zum überschlagen bringt. </del>

<del>Da dieser bei jeder neuen Anfrage automatisch den nächsten Hoster in der Liste erfragt. Dies führt ganz schnell zum Stau im Client -> Server stream anfrage, bis hin zum Server Absturz! </del>

<del>Die Zeit wird zeigen ob und wie Ich dieses grundlegende Problem in den Griff bekomme ;-) </del>


# Copyright 2023 @Mastaaa1987

