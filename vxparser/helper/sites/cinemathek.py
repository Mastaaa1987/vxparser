# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!
# HTML LangzeitCache hinzugefügt
    #showGenre:     48 Stunden
    #showEntries:    6 Stunden
    #showSeasons:    6 Stunden
    #showEpisodes:   4 Stunden
    
import json

from helper.requestHandler import cRequestHandler
from helper.tools import cParser

SITE_IDENTIFIER = 'cinemathek'
SITE_NAME = 'Cinemathek'
SITE_ICON = 'cinemathek.png'
SITE_DOMAIN = 'cinemathek.net'

URL_MAIN = 'https://cinemathek.net/'
URL_MOVIES = URL_MAIN + 'filme/'
URL_SERIES = URL_MAIN + 'serien/'
URL_NEW_EPISODES = URL_MAIN + 'episoden/'
URL_SEARCH = URL_MAIN + '?s=%s'


def load():
    ret = []
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MOVIES, "typ": 1, "key": "showEntries", "title": "Movies"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_SERIES, "typ": 2, "key": "showEntries", "title": "Series"})
    return ret


def showRegs(entryUrl=False):
    folder = []
    sUrl = entryUrl
    oRequest = cRequestHandler(sUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 48  # 48 Stunden
    sHtmlContent = oRequest.request()
    pattern = '<ul class="sub-menu"><li id="menu-item-26052".*?</ul>' # Alle Einträge in dem Bereich suchen
    isMatch, sHtmlContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        isMatch, aResult = cParser.parse(sHtmlContainer, 'href="([^"]+).*?>([^<]+)') # sUrl + sName
    if not isMatch: return
    for sUrl, sName in aResult:
        if sUrl.startswith('/'):
            sUrl = URL_MAIN + sUrl
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["url"] = sUrl
        folder.append(oGuiElement)
    return folder


def showEntries(entryUrl=False, sSearchText=False):
    folder = []
    isTvshow = False    
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # HTML Cache Zeit 6 Stunden
    sHtmlContent = oRequest.request()
    if not sHtmlContent: return
    # Für Filme und Serien Content
    pattern = '<article id=.*?'  # container start
    pattern += 'src="([^"]+).*?'  # sThumbnail
    pattern += 'href="([^"]+).*?'  # url  
    pattern += '>([^<]+).*?'  # name 
    pattern += '(.*?)</article>'  # dummy
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        # Für die Suche von Filmen und Serien
        pattern = '<article.*?'  # container start
        pattern += '<img src="([^"]+).*?'  # sThumbnail alt
        pattern += 'href="([^"]+).*?'  # url
        pattern += '>([^<]+).*?'  # name
        pattern += '(.*?)</article>'  # dummy
        isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch: return
    total = len(aResult)
    for sThumbnail, sUrl, sName, sDummy in aResult:
        if sSearchText and not cParser.search(sSearchText, sName):
            continue
        isTvshow, aResult = cParser.parse(sUrl, 'serien') # Muss nur im Serien Content auffindbar sein
        isDesc, sDesc = cParser.parseSingleResult(sDummy, '<div class="texto">([^<]+)') # Beschreibung
        if not isDesc:
            isDesc, sDesc = cParser.parseSingleResult(sDummy, 'class="contenido"><p>([^<]+)\s') # Beschreibung in der Suche
        isYear, sYear = cParser.parseSingleResult(sDummy, 'class="imdb">\S+.*?\S+.*?<span>([\d]+)') # Release Jahr
        if not isYear:
            isYear, sYear = cParser.parseSingleResult(sDummy, 'class="year">([\d]+)') # Release Jahr in der Suche
        if not isYear:
            isYear, sYear = cParser.parseSingleResult(sDummy, 'metadata"> <span>([\d]+)') # Release Jahr
        isDuration, sDuration = cParser.parseSingleResult(sDummy, '<span>([\d]+)\smin')  # Laufzeit
        isRating, sRating = cParser.parseSingleResult(sDummy, 'IMDb:([^<]+)') # IMDb Bewertung
        if not isRating:
            isRating, sRating = cParser.parseSingleResult(sDummy, 'IMDb\s([^<]+)')# IMDb Bewertung in der Suche
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showSeasons' if isTvshow else 'showHosters'
        oGuiElement["thumb"] = sThumbnail
        oGuiElement["url"] = sUrl
        oGuiElement["mediatype"] = 'tvshow' if isTvshow else 'movie'
        oGuiElement["total"] = total
        if isDesc: oGuiElement["desc"] = sDesc
        if isYear: oGuiElement["year"] = sYear
        if isTvshow is False: # Laufzeit bei Serie ausblenden
            if isDuration: oGuiElement["duration"] = sDuration
        if isRating: oGuiElement["rating"] = sRating
        # Parameter übergeben
        folder.append(oGuiElement)
    return folder


def showNewEpisodes(entryUrl=False, sSearchText=False):
    folder = []
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # HTML Cache Zeit 6 Stunden
    sHtmlContent = oRequest.request()
    if not sHtmlContent: return
    # Für die Suche von Neuen Episoden
    pattern = '<article.*?'  # container start
    pattern += '<img src="([^"]+).*?'  # sThumbnail alt
    pattern += 'href="([^"]+).*?'  # url
    pattern += '>([^<]+).*?'  # name
    pattern += '</h3><span>S([\d]+)'  # Staffel Nummer
    pattern += '\sE([\d]+)'  # Episoden Nummer
    pattern += '(.*?)</article>'  # dummy
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)  # neue Episoden
    if not isMatch: return
    total = len(aResult)
    for sThumbnail, sUrl, sName, sSeason, sEpisode, sDummy in aResult:
        oGuiElement = {}
        isEpisode, aResult = cParser.parse(sUrl, 'episoden') # Im Episoden Content auffindbar
        isTVShowTitle, sTVShowTitle = cParser.parseSingleResult(sDummy, 'class="serie">([^<]+)')  # Serien Titel
        isYear, sYear = cParser.parseSingleResult(sDummy, '([\d]+)</span>\s<span class="serie') # Release Jahr
        if isTVShowTitle: oGuiElement["show"] = sTVShowTitle
        if isYear: oGuiElement["year"] = sYear
        # Parameter übergeben
        oGuiElement["name"] = sName
        oGuiElement["title"] = 'Staffel ' + sSeason + ' Episode '+ sEpisode + ' - ' + sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showHosters'
        oGuiElement["thumb"] = sThumbnail
        oGuiElement["url"] = sUrl
        oGuiElement["mediatype"] = 'episode'
        oGuiElement["e"] = sEpisode
        oGuiElement["s"] = sSeason
        oGuiElement["total"] = total
        folder.append(oGuiElement)
    return folder


def showSeasons(entryUrl=False, sThumbnail=False, sDesc=False):
    folder = []
    oRequest = cRequestHandler(entryUrl)
    oRequest.cacheTime = 60 * 60 * 24  # HTML Cache Zeit 6 Stunden
    sHtmlContent = oRequest.request()
    isMatch, aResult = cParser.parse(sHtmlContent, 'Season ([\d]+)') # Sucht den Staffel Eintrag und d fügt die Anzahl hinzu
    if not isMatch: return
    total = len(aResult)
    for sSeason in aResult:
        oGuiElement = {}
        oGuiElement["name"] = 'Staffel ' + sSeason
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showEpisodes'
        oGuiElement["thumb"] = sThumbnail
        oGuiElement["url"] = entryUrl
        oGuiElement["mediatype"] = 'seasons'
        oGuiElement["total"] = total
        oGuiElement["p2"] = sSeason
        oGuiElement["s"] = sSeason
        oGuiElement["desc"] = sDesc
        folder.append(oGuiElement)
    return folder


def showEpisodes(entryUrl=False, sSeason=False):
    folder = []
    oRequest = cRequestHandler(entryUrl)
    oRequest.cacheTime = 60 * 60 * 24  # HTML Cache Zeit 4 Stunden
    sHtmlContent = oRequest.request()
    pattern = '>Season %s <i>.*?</ul>' % sSeason # Suche alles in diesem Bereich
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        pattern = "mark-([\d]+).*?'" # Episoden Eintrag
        pattern += "img src='([^']+).*?" # sThumbnail
        pattern += "<a href='([^']+).*?" # sUrl
        pattern += ">([^<]+)</a>" # sName
        isMatch, aResult = cParser.parse(sContainer, pattern)
    if not isMatch:
        pattern = 'mark-([\d]+).*?' # Episoden Eintrag
        pattern += 'img src="([^"]+).*?' # sThumbnail
        pattern += '<a href="([^"]+).*?' # sUrl
        pattern += '>([^<]+)</a>' # sName
        isMatch, aResult = cParser.parse(sContainer, pattern)
    if not isMatch: return
    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, 'class="wp-content">(.*?)</p>')  # Beschreibung
    total = len(aResult)
    for sEpisode, sThumbnail, sUrl, sName in aResult:
        oGuiElement = {}
        if isDesc: oGuiElement["desc"] = sDesc
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showHosters'
        oGuiElement["thumb"] = sThumbnail
        oGuiElement["s"] = sSeason
        oGuiElement["e"] = sEpisode
        oGuiElement["url"] = sUrl
        oGuiElement["mediatype"] = 'episode'
        oGuiElement["total"] = total
        folder.append(oGuiElement)
    return folder


def showHosters(entryUrl=False):
    hosters = []
    sUrl = entryUrl # ParameterHandler().getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    # <li id="player-option-1" class="dooplay_player_option" data-type="movie" data-post="29224" data-nume="1">
    pattern = "player-option-\d.*?" # Player Option Nr. z.B 1 für Link 1
    pattern += "type='([^']+).*?" # Eintrag [0] movie oder tv
    pattern += "post='(\d+).*?" # Eintrag [1] ist die Film oder Serien Nr.29224
    pattern += "nume='(\d).*?" # Eintrag [2] ist die Link Nr.1
    pattern += "starten!\s([^<]+)" # Eintrag [3] = sName des Link Eintrag
    releaseQuality = ">Release:.*?\s*(\d\d\d+)p"  # Hoster Release Quality Kennzeichen
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    if not isMatch:
        pattern = 'player-option-\d.*?'  # Player Option Nr. z.B 1 für Link 1
        pattern += 'type="([^"]+).*?'  # Eintrag [0] movie oder tv
        pattern += 'post="(\d+).*?'  # Eintrag [1] ist die Film oder Serien Nr.29224
        pattern += 'nume="(\d).*?'  # Eintrag [2] ist die Link Nr.1
        pattern += 'starten!\s([^<]+)'  # Eintrag [3] = sName des Link Eintrag
        releaseQuality = '>Release:.*?\s*(\d\d\d+)p'  # Hoster Release Quality Kennzeichen
        isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    if not isMatch: return
    isQuality, sQuality = cParser.parseSingleResult(sHtmlContent, releaseQuality)  # sReleaseQuality auslesen z.B. 1080
    if not isQuality: sQuality = '720'
    if isMatch:
        for sType, sID, sLink, sName in aResult:
            sUrl = 'https://cinemathek.net/wp-json/dooplayer/v2/%s/%s/%s' % (sID, sType, sLink)
            if 'StreamSB' in sName: continue  # StreamSB Offline
            hoster = {'link': sUrl, 'name': sName, 'displayedName': '%s [I][%sp][/I]' % (sName, sQuality), 'quality': sQuality, 'resolveable': True}
            hosters.append(hoster)
    if not isMatch: return
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    sUrl = json.loads(cRequestHandler(sUrl).request()).get("embed_url")
    # Überprüfe sUrl auf korrekte Domain
    Request = cRequestHandler(sUrl, caching=False)
    Request.request()
    sUrl = Request.getRealUrl() # hole reale sURL
    return [{'streamUrl': sUrl, 'resolved': False}]


def search(sSearchText):
    find = showEntries(URL_SEARCH % cParser().quotePlus(sSearchText), sSearchText)
    if find:
        if len(find) > 0:
            return find
    return None

