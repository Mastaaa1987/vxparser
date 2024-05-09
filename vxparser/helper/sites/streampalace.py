# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!
# HTML LangzeitCache hinzugefügt
# showGenre:     48 Stunden
# showEntries:    6 Stunden
# showSeasons:    6 Stunden
# showEpisodes:   4 Stunden

import json

from helper.requestHandler import cRequestHandler
from helper.tools import cParser

SITE_IDENTIFIER = 'streampalace'
SITE_NAME = 'StreamPalace'
SITE_ICON = 'streampalace.png'
SITE_DOMAIN = 'streampalace.org'

URL_MAIN = 'https://streampalace.org/'
URL_MOVIES = URL_MAIN + 'filme/'
URL_SERIES = URL_MAIN + 'serien/'
URL_SEARCH = URL_MAIN + '?s=%s'


def load():
    ret = []
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MOVIES, "typ": 1, "key": "showEntries", "title": "Movies"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_SERIES, "typ": 2, "key": "showEntries", "title": "Series"})
    return ret


def showEntries(entryUrl=False, sSearchText=False):
    folder = []
    isTvshow = False
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # HTML Cache Zeit 6 Stunden
    sHtmlContent = oRequest.request()
    pattern = '<div id="archive-content".*?</article>\</div>'
    isMatch, sHtmlContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        # Für Filme und Serien Content
        pattern = '<article id=".*?'  # container start
        pattern += 'src="([^"]+).*?'  # sThumbnail
        pattern += 'href="([^"]+).*?'  # url
        pattern += '>([^<]+).*?'  # name
        pattern += '(.*?)</article>'  # dummy
        isMatch, aResult = cParser.parse(sHtmlContainer, pattern)
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
        if sSearchText and not cParser.search(sSearchText, sName): continue
        isTvshow, aResult = cParser.parse(sUrl, 'serien')  # Muss nur im Serien Content auffindbar sein
        isDesc, sDesc = cParser.parseSingleResult(sDummy, '<div class="texto">([^<]+)')  # Beschreibung
        if not isDesc:
            isDesc, sDesc = cParser.parseSingleResult(sDummy, 'class="contenido"><p>([^<]+)\s')  # Beschreibung in der Suche
        isYear, sYear = cParser.parseSingleResult(sDummy, 'class="imdb">\S+.*?\S+.*?<span>([\d]+)')  # Release Jahr
        if not isYear:
            isYear, sYear = cParser.parseSingleResult(sDummy, 'class="year">([\d]+)')  # Release Jahr in der Suche
        if not isYear:
            isYear, sYear = cParser.parseSingleResult(sDummy, 'metadata"> <span>([\d]+)')  # Release Jahr

        isDuration, sDuration = cParser.parseSingleResult(sDummy, '<span>([\d]+)\smin')  # Laufzeit
        isRating, sRating = cParser.parseSingleResult(sDummy, 'IMDb:([^<]+)')  # IMDb Bewertung
        if not isRating:
            isRating, sRating = cParser.parseSingleResult(sDummy, 'IMDb\s([^<]+)')  # IMDb Bewertung in der Suche
        
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showSeasons' if isTvshow else 'showHosters'
        oGuiElement["mediatype"] = 'tvshow' if isTvshow else 'movie'
        oGuiElement["thumb"] = sThumbnail
        if isDesc:
            oGuiElement["desc"] = sDesc
        if isYear:
            oGuiElement["year"] = sYear
        if isTvshow is False:  # Laufzeit bei Serie ausblenden
            if isDuration:
                oGuiElement["duration"] = sDuration
        if isRating:
            oGuiElement["rating"] = sRating
        oGuiElement["url"] = sUrl
        oGuiElement["total"] = total
        folder.append(oGuiElement)
    return folder


def showSeasons(entryUrl=False):
    folder = []
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # HTML Cache Zeit 6 Stunden
    sHtmlContent = oRequest.request()
    isMatch, aResult = cParser.parse(sHtmlContent, 'Staffel ([\d]+)')  # Sucht den Staffel Eintrag und d fügt die Anzahl hinzu
    if not isMatch: return
    total = len(aResult)
    for sSeason in aResult:
        oGuiElement = {}
        oGuiElement["name"] = 'Staffel ' + sSeason
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showEpisodes'
        oGuiElement["s"] = sSeason
        oGuiElement["url"] = entryUrl
        oGuiElement["p2"] = sSeason
        oGuiElement["mediatype"] = 'season'
        oGuiElement["total"] = total
        folder.append(oGuiElement)
    return folder


def showEpisodes(entryUrl=False, sSeason=False):
    folder = []
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # HTML Cache Zeit 4 Stunden
    sHtmlContent = oRequest.request()
    pattern = '>Staffel %s <i>.*?</ul>' % sSeason  # Suche alles in diesem Bereich
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        pattern = "mark-([\d]+).*?"  # Episoden Eintrag
        pattern += "img src='([^']+).*?"  # sThumbnail
        pattern += "<a href='([^']+).*?"  # sUrl
        pattern += ">([^<]+)</a>"  # sName
        isMatch, aResult = cParser.parse(sContainer, pattern)
    if not isMatch:
        pattern = 'mark-([\d]+).*?'  # Episoden Eintrag
        pattern += 'img src="([^"]+).*?'  # sThumbnail
        pattern += '<a href="([^"]+).*?'  # sUrl
        pattern += '>([^<]+)</a>'  # sName
        isMatch, aResult = cParser.parse(sContainer, pattern)
    if not isMatch: return
    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, 'class="wp-content">(.*?)</p>')  # Beschreibung
    total = len(aResult)
    for sEpisode, sThumbnail, sUrl, sName in aResult:
        oGuiElement = {}
        if isDesc: oGuiElement["desc"] = sDesc
        oGuiElement["e"] = sEpisode
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showHosters'
        oGuiElement["thumb"] = sThumbnail
        oGuiElement["s"] = sSeason
        oGuiElement["url"] = sUrl
        oGuiElement["mediatype"] = 'episode'
        oGuiElement["total"] = total
        folder.append(oGuiElement)
    return folder


def showHosters(entryUrl=False):
    hosters = []
    sUrl = entryUrl
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = '<tbody>.*?</tbody>'  # Alle Einträge in dem Bereich suchen
    isMatch, sHtmlContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        isMatch, aResult = cParser.parse(sHtmlContainer, "href='([^']+).*?>([^<]+)")  # sUrl + sName
    if not isMatch:
        isMatch, aResult = cParser.parse(sHtmlContainer, 'href="([^"]+).*?>([^<]+)')  # sUrl + sName
    if not isMatch: return
    sQuality = '720p'
    for sUrl, sName in aResult:
        hoster = {'link': sUrl, 'name': sName, 'displayedName': '%s [I][%s][/I]' % (sName, sQuality), 'quality': sQuality, 'resolveable': True}
        hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    Request = cRequestHandler(sUrl, caching=False)
    Request.request()
    sUrl = Request.getRealUrl()  # hole reale sURL
    return [{'streamUrl': sUrl, 'resolved': False}]


def search(sSearchText):
    oGui = False
    find = showEntries(URL_SEARCH % cParser().quotePlus(sSearchText), sSearchText)
    if find:
        if len(find) > 0:
            return find
    return None

