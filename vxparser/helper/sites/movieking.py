# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!
# HTML LangzeitCache hinzugefügt
    #showGenre:     48 Stunden
    #showEntries:    6 Stunden

from helper.requestHandler import cRequestHandler
from helper.tools import cParser

SITE_IDENTIFIER = 'movieking'
SITE_NAME = 'MovieKing'
SITE_ICON = 'movieking.png'
SITE_DOMAIN = 'movieking.io'

URL_MAIN = 'https://movieking.io/'
URL_KINO = URL_MAIN + 'cinema'
URL_MOVIES = URL_MAIN + 'movies.html'
URL_YEAR = URL_MAIN + 'year.html'
URL_SEARCH = URL_MAIN + 'search?q=%s'

def load():
    ret = []
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_KINO, "typ": 1, "key": "showEntries", "title": "Current films in the cinema"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MOVIES, "typ": 1, "key": "showEntries", "title": "Movies"})
    return ret


def showEntries(entryUrl=False, sSearchText=False):
    folder = []
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # 6 Stunden
    sHtmlContent = oRequest.request()
    pattern = '<div class="latest-.*?'  # container start
    pattern += 'data-src="([^"]+).*?' # Thumb
    pattern += 'class="video_quality">(.*?)<h3>.*?'  # dummy
    pattern += 'href="([^"]+)">([^<]+).*?'  # url + name

    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    if not isMatch: return

    total = len(aResult)
    for sThumbnail, sDummy, sUrl, sName in aResult:
        if sSearchText and not cParser().search(sSearchText, sName): continue
        isQuality, sQuality = cParser.parseSingleResult(sDummy, 'label-primary">([^"]+)\s</span>')  # Qualität

        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showHosters'
        oGuiElement["thumb"] = sThumbnail
        oGuiElement["url"] = sUrl
        oGuiElement["mediatype"] = 'movie'
        oGuiElement["total"] = total
        if isQuality:
            if 'PISODES' in sQuality: continue
            oGuiElement["quality"] = sQuality
        folder.append(oGuiElement)
    return folder


def showHosters(entryUrl=False):
    hosters = []
    sUrl = entryUrl # ParameterHandler().getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = '<a href="([^"]+)"\sclass="btn movie-player.*?>([^<]+)'
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    if isMatch:
        for sUrl, sName in aResult:
            #if cConfig().isBlockedHoster(sName)[0]: continue # Hoster aus settings.xml oder deaktivierten Resolver ausschließen
            hoster = {'link': sUrl, 'name': sName }
            hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    Request = cRequestHandler(sUrl, caching=False)
    sHtmlContent = Request.request()
    pattern = 'embed-item".*?src="(http[^"]+)'
    isMatch, sUrl = cParser.parseSingleResult(sHtmlContent, pattern)
    return [{'streamUrl': sUrl, 'resolved': False}]


def search(sSearchText):
    find = showEntries(URL_SEARCH % cParser().quotePlus(sSearchText), sSearchText)
    if find:
        if len(find) > 0:
            return find
    return None

