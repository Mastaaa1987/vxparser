# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!
# HTML LangzeitCache hinzugefügt
    #showGenre:     48 Stunden
    #showEntries     6 Stunden
    #showSeasons:   24 Stunden
    #showEpisodes:   4 Stunden

from helper.requestHandler import cRequestHandler
from helper.tools import cParser, cUtil

SITE_IDENTIFIER = 'streamen'
SITE_NAME = 'Streamen'
SITE_ICON = 'streamen.png'
SITE_DOMAIN = 'streamen.cx'

URL_MAIN = 'https://wwv.streamen.cx' # + DOMAIN
URL_MOVIES = URL_MAIN + '/filme.html'
URL_SERIES = URL_MAIN + '/serien.html'
URL_SEARCH = URL_MAIN + '/recherche?q=%s'


def load():
    ret = []
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MOVIES, "typ": 1, "key": "showEntries", "title": "Movies"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_SERIES, "typ": 2, "key": "showEntries", "title": "Series"})
    return ret


def showEntries(entryUrl=False, sGui=False, sSearchText=False):
    folder = []
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # HTML Cache Zeit 6 Stunden
    sHtmlContent = oRequest.request()
    pattern = '<div[^>]*class="short-images[^"]*"[^>]*>.*?'  # start element
    pattern += '<a[^>]*href="([^"]*)"[^>]*>.*?'  # url
    pattern += '<img[^>]*src="([^"]*)".*?'  # thumbnail
    pattern += 'alt="([^"]*).*?'  # name
    pattern += '<\/div>'  # end element
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch: return

    total = len(aResult)
    for sUrl, sThumbnail, sName in aResult:
        if sSearchText and not cParser.search(sSearchText, sName): continue
        isTvshow = True if 'serien' in sUrl else False # Wenn Serie dann True
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showSeasons' if isTvshow else 'showHosters'
        oGuiElement["thumb"] = sThumbnail
        oGuiElement["url"] = sUrl
        oGuiElement["mediatype"] = 'tvshow' if isTvshow else 'movie'
        oGuiElement["total"] = total
        folder.append(oGuiElement)
    return folder


def showSeasons(entryUrl=False):
    folder = []
    sUrl = entryUrl
    oRequest = cRequestHandler(sUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24 # HTML Cache Zeit 1 Tag
    sHtmlContent = oRequest.request()
    isMatch, aResult = cParser.parse(sHtmlContent, '<div[^>]*class="short-images[^"]*"[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>.*?<img[^>]*src="([^"]*)".*?<figcaption>Staffel\s([\d]+)') # Sucht den Staffel Eintrag und d fügt die Anzahl hinzu
    if not isMatch: return
    
    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, 'fsynopsis">\s<p>\s([^"]*)</p>') # Staffel Beschreibung
    total = len(aResult)
    for sUrl, sThumbnail, sSeason in aResult:
        oGuiElement = {}
        if isDesc:
            sDesc = sDesc.replace('&quot;', '"')
            oGuiElement["desc"] = sDesc
        oGuiElement["name"] = 'Staffel ' + sSeason
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showEpisodes'
        oGuiElement["thumb"] = sThumbnail
        oGuiElement["s"] = sSeason
        oGuiElement["p2"] = sSeason
        oGuiElement["url"] = sUrl
        oGuiElement["mediatype"] = 'season'
        oGuiElement["total"] = total
        folder.append(oGuiElement)
    return folder


def showEpisodes(entryUrl=False, sSeason=False):
    folder = []
    sUrl = entryUrl
    oRequest = cRequestHandler(sUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # HTML Cache Zeit 4 Stunden
    sHtmlContent = oRequest.request()
    isMatch, aResult = cParser.parse(sHtmlContent, '_LI2">.*?href="([^"]+).*?Folge\s([\d]+)</span>')
    if not isMatch: return

    total = len(aResult)
    for sUrl, sEpisode in aResult:
        oGuiElement = {}
        oGuiElement["e"] = sEpisode
        oGuiElement["name"] = 'Episode ' + sEpisode
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showHosters'
        oGuiElement["s"] = sSeason
        oGuiElement["url"] = sUrl
        oGuiElement["mediatype"] = 'episode'
        oGuiElement["total"] = total
        folder.append(oGuiElement)
    return folder


def showHosters(entryUrl=False):
    hosters = []
    sUrl = entryUrl # ParameterHandler().getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = '<div data-url="([^"]+).*?player_v_DIV_5">([^<]*)\s' # sUrl, sName
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    if isMatch:
        for sUrl, sName in aResult:
            if 'ayer' in sName:
                continue
            #if cConfig().isBlockedHoster(sName)[0]: continue # Hoster aus settings.xml oder deaktivierten Resolver ausschließen
            elif sUrl.startswith('/'):
                sUrl = URL_MAIN + sUrl # URL_MAIN + übergebener Link
            hoster = {'link': sUrl, 'name': sName}
            hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    if not hosters: return

    return hosters


def getHosterUrl(sUrl=False):
    Request = cRequestHandler(sUrl, caching=False)
    Request.request()
    sUrl = Request.getRealUrl() # hole reale URL von der Umleitung
    return [{'streamUrl': sUrl, 'resolved': False}]


def search(sSearchText):
    find = showEntries(URL_SEARCH % cParser.quotePlus(sSearchText), sSearchText)
    if find:
        if len(find) > 0:
            return find
    return None

