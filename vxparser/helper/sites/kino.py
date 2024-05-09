# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!
# HTML LangzeitCache hinzugefügt
    #showGenre:     48 Stunden
    #showEntries:    6 Stunden
    #showEpisodes:   4 Stunden
    
from helper.requestHandler import cRequestHandler
from helper.tools import cParser


SITE_IDENTIFIER = 'kino'
SITE_NAME = 'Kino'
SITE_ICON = 'kino_ws.png'
SITE_DOMAIN = 'kino.ws'

URL_MAIN = 'https://kino.ws/'
URL_MOVIES = URL_MAIN + 'filme-kostenlos.html'
URL_SERIES = URL_MAIN + 'serien-kostenlos.html'
URL_SEARCH = URL_MAIN + 'recherche?_token=kZDYEMkRbBXOKMQbZZOnGOaR9JMeGAjXpzKtj0s3&q=%s'


def load():
    ret = []
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MOVIES, "typ": 1, "key": "showEntries", "title": "Movies"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_SERIES, "typ": 2, "key": "showEntries", "title": "Series"})
    return ret


def showEntries(entryUrl=False, sSearchText=False):
    folder = []
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # 6 Stunden
    sHtmlContent = oRequest.request()
    pattern = 'class="short-in.*?'  # container start
    pattern += 'nl">(.*?)a\s+class.*?'  # dummy
    pattern += 'href="(http[^"]+).*?'  # url
    pattern += 'src="([^"]+).*?'  # thumbnail
    pattern += 'alt(.*?)' # info dummy
    pattern += 'short-title">([^<]+)'  # name
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch: return
    total = len(aResult)
    isTvshow = None
    for sDummy, sUrl, sThumbnail, sInfo, sName in aResult:
        if sSearchText and not cParser.search(sSearchText, sName):
            continue
        isQuality, sQuality = cParser.parseSingleResult(sDummy, 'film-ripz.*?#">([^<]+)')  # Qualität
        isInfoEpisode, sInfoEpisode = cParser.parseSingleResult(sInfo, 'mli-eps">.*?<i>([\d]+)')  # Episodenanzahl
        isTvshow, aResult = cParser.parse(sName, '\s+-\s+Staffel\s+\d+')
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showEpisodes' if isTvshow else 'showHosters'
        oGuiElement["thumb"] = URL_MAIN + sThumbnail
        oGuiElement["url"] = sUrl
        oGuiElement["mediatype"] = 'tvshow' if isTvshow else 'movie'
        oGuiElement["total"] = total
        if isQuality:
            oGuiElement["quality"] = sQuality
        if isInfoEpisode:
            oGuiElement["info"] = sInfoEpisode + ' Episoden'
        folder.append(oGuiElement)
    return folder


def showEpisodes(entryUrl=False):
    folder = []
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # 4 Stunden
    sHtmlContent = oRequest.request()
    pattern = 'id="episode(\d+)' # d fügt Anzahl der Episoden hinzu
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch: return
    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, 's-desc">([^<]+)')  # Beschreibung
    total = len(aResult)
    for sName in aResult:
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showHosters'
        oGuiElement["thumb"] = URL_MAIN + sThumbnail
        oGuiElement["url"] = entryUrl
        oGuiElement["p2"] = sName
        oGuiElement["e"] = sName
        oGuiElement["mediatype"] = 'episode'
        oGuiElement["desc"] = sDesc
        oGuiElement["total"] = total
        oGuiElement["episode"] = 'Episode ' + sName
        folder.append(oGuiElement)
    return folder


def showHosters(entryUrl=False, sEpisode= False, sMediaType='Filme'):
    hosters = []
    sUrl = entryUrl
    sHtmlContent = cRequestHandler(sUrl).request()
    if sMediaType == 'episode':
        sEpisode = params.getValue('sEpisode')
        pattern = 'id="episode%s.*?style' % sEpisode        # Episoden Bereich
        isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    else:
        pattern = '<div class="tabs-sel">.*?</div>'         # Filme
        isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    pattern = 'href="([^"]+).*?seriePlayer.*?</i>([^<]+)'
    releaseQuality = 'Qualität:.*?\d{3,4}.*?(\d\d\d+)P'  # Hoster Release Quality Kennzeichen
    isMatch, aResult = cParser.parse(aResult[0], pattern)   # Nimmt nur das 1.Result
    if not isMatch: return
    isQuality, sQuality = cParser.parseSingleResult(sHtmlContent, releaseQuality)  # sReleaseQuality auslesen z.B. 1080
    if not isQuality: sQuality = '720'
    for sUrl, sName in aResult:
        hoster = {'link': sUrl, 'name': sName, 'displayedName': '%s [I][%sp][/I]' % (sName, sQuality), 'quality': sQuality, 'resolveable': True}
        hosters.append(hoster)    
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    return [{'streamUrl': sUrl, 'resolved': False}] 


def search(sSearchText):
    find = showEntries(URL_SEARCH % cParser.quotePlus(sSearchText), sSearchText)
    if find:
        if len(find) > 0:
            return find
    return None

