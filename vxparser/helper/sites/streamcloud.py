# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!
# HTML LangzeitCache hinzugefÃ¼gt
    #showGenre:     48 Stunden
    #showYears:     48 Stunden
    #showEpisodes:   4 Stunden
# 2023-03-20 Hep

from helper.requestHandler import cRequestHandler
from helper.tools import cParser


SITE_IDENTIFIER = 'streamcloud'
SITE_NAME = 'Streamcloud'
SITE_ICON = 'streamcloud.png'

URL_MAIN = 'https://streamcloud.my/'
URL_MAINPAGE = URL_MAIN + 'streamcloud/'
URL_MOVIES = URL_MAIN + 'filme-stream/'
URL_KINO = URL_MAIN + 'kinofilme/'
URL_FAVOURITE_MOVIE_PAGE = URL_MAIN + 'beliebte-filme/'
URL_SERIES = URL_MAIN + 'serien/'
URL_NEW = URL_MAIN + 'neue-filme/'
URL_SEARCH = URL_MAIN + 'index.php?story=%s&do=search&subaction=search'


def load():
    ret = []
    ret.append({"site": SITE_IDENTIFIER, "url": URL_NEW, "typ": 1, "key": "showEntries", "title": "New Movies"})
    ret.append({"site": SITE_IDENTIFIER, "url": URL_KINO, "typ": 1, "key": "showEntries", "title": "Current films in the cinema"})
    ret.append({"site": SITE_IDENTIFIER, "url": URL_SERIES, "typ": 2, "key": "showSeries", "title": "Series"})
    return ret


def showEntries(entryUrl=False, sGui=False, sSearchText=False):
    folder = []
    isTvshow = False
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 6  # HTML Cache Zeit 6 Stunden
    sHtmlContent = oRequest.request()
    pattern = 'class="thumb".*?title="([^"]+).*?href="([^"]+).*?src="([^"]+).*?_year">([^<]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch: return

    total = len(aResult)
    for sName, sUrl, sThumbnail, sYear in aResult:
        if sSearchText and not cParser.search(sSearchText, sName):
            continue
        if sThumbnail[0] == '/':
            sThumbnail = sThumbnail[1:]

        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["key"] = 'showHosters'
        oGuiElement["thumb"] = sThumbnail
        oGuiElement["mediatype"] = 'movie'
        oGuiElement["total"] = total
        oGuiElement["url"] = sUrl
        oGuiElement["year"] = sYear
        #if isDuration: oGuiElement["duration"] = sDuration
        folder.append(oGuiElement)
    return folder


def showEntries(entryUrl=False, sSearchText=False):
    folder = []
    isTvshow = False
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 6  # HTML Cache Zeit 6 Stunden
    sHtmlContent = oRequest.request()
    pattern = 'class="thumb".*?title="([^"]+).*?href="([^"]+).*?src="([^"]+).*?_year">([^<]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch: return

    total = len(aResult)
    for sName, sUrl, sThumbnail, sYear in aResult:
        if sSearchText and not cParser.search(sSearchText, sName):
            continue
        if sThumbnail[0] == '/':
            sThumbnail = sThumbnail[1:]

        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["key"] = 'showHosters'
        oGuiElement["thumb"] = sThumbnail
        oGuiElement["mediatype"] = 'movie'
        oGuiElement["total"] = total
        oGuiElement["url"] = sUrl
        oGuiElement["year"] = sYear
        #if isDuration: oGuiElement["duration"] = sDuration
        folder.append(oGuiElement)
    return folder


def showSeries(entryUrl=False, sSearchText=False): # Neu eingebaut da auf der Webseite nicht erkennbar ist was Serien sind und was nicht
    folder = []
    isTvshow = True
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 6  # HTML Cache Zeit 6 Stunden
    sHtmlContent = oRequest.request()
    pattern = 'class="thumb".*?title="([^"]+).*?href="([^"]+).*?src="([^"]+).*?_year">([^<]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch: return

    total = len(aResult)
    for sName, sUrl, sThumbnail, sYear in aResult:
        if sSearchText and not cParser.search(sSearchText, sName):
            continue
        if sThumbnail[0] == '/':
            sThumbnail = sThumbnail[1:]

        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["key"] = 'showEpisodes'
        oGuiElement["thumb"] = sThumbnail
        oGuiElement["mediatype"] = 'tvshow'
        oGuiElement["total"] = total
        oGuiElement["url"] = sUrl
        oGuiElement["year"] = sYear
        folder.append(oGuiElement)
    return folder


def showSeries(entryUrl=False, sSearchText=False): # Neu eingebaut da auf der Webseite nicht erkennbar ist was Serien sind und was nicht
    folder = []
    isTvshow = True
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 6  # HTML Cache Zeit 6 Stunden
    sHtmlContent = oRequest.request()
    pattern = 'class="thumb".*?title="([^"]+).*?href="([^"]+).*?src="([^"]+).*?_year">([^<]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch: return

    total = len(aResult)
    for sName, sUrl, sThumbnail, sYear in aResult:
        if sSearchText and not cParser.search(sSearchText, sName):
            continue
        if sThumbnail[0] == '/':
            sThumbnail = sThumbnail[1:]

        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["key"] = 'showEpisodes'
        oGuiElement["thumb"] = sThumbnail
        oGuiElement["mediatype"] = 'tvshow'
        oGuiElement["total"] = total
        oGuiElement["url"] = sUrl
        oGuiElement["year"] = sYear
        folder.append(oGuiElement)
    return folder


def showEpisodes(entryUrl=False, sThumbnail=False):
    folder = []
    sHtmlContent = cRequestHandler(entryUrl).request()
    isMatch, aResult = cParser.parse(sHtmlContent, 'data-num="([^"]+)')
    if not isMatch: return

    total = len(aResult)
    for sName in aResult:
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setMediaType('episode')
        params.setParam('entryUrl', entryUrl)
        params.setParam('episode', sName)
        cGui().addFolder(oGuiElement, params, False, total)

        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["key"] = 'showHosters'
        oGuiElement["thumb"] = sThumbnail
        oGuiElement["mediatype"] = 'episode'
        oGuiElement["total"] = total
        oGuiElement["url"] = entryUrl
        folder.append(oGuiElement)
    return folder


def showEpisodes(entryUrl=False, sThumbnail=False):
    folder = []
    sHtmlContent = cRequestHandler(entryUrl).request()
    isMatch, aResult = cParser.parse(sHtmlContent, 'data-num="([^"]+)')
    if not isMatch: return

    total = len(aResult)
    for sName in aResult:
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["key"] = 'showHosters'
        oGuiElement["thumb"] = sThumbnail
        oGuiElement["mediatype"] = 'episode'
        oGuiElement["total"] = total
        oGuiElement["url"] = entryUrl
        oGuiElement["episode"] = sName
        folder.append(oGuiElement)
    return folder


def showHosters(entryUrl=False, episode=False):
    hosters = []
    if not entryUrl: return
    sUrl = entryUrl
    sHtmlContent = cRequestHandler(sUrl).request()
    if ParameterHandler().exist('episode'): #kommt aus showSeries
        pattern = 'data-num="{0}".*?allowfull'.format(episode)
        isMatch, sHtmlContent = cParser.parseSingleResult(sHtmlContent, pattern)
    else:
        pattern = '<iframe.*?allowfull'
        isMatch, sHtmlContainer = cParser.parseSingleResult(sHtmlContent, pattern)
        if isMatch:
            isMatch, aResult = cParser.parse(sHtmlContainer, 'src="([^"]+)')
            try: sUrl = aResult[0]
            except: pass
        if not isMatch: return
        sHtmlContent = cRequestHandler(sUrl).request()

    isMatch, aResult = cParser().parse(sHtmlContent, 'data-link="([^"]+)')
    if isMatch:
        for sUrl in aResult:
            sName = cParser.urlparse(sUrl)
            if 'youtube' in sUrl: continue
            elif sUrl.startswith('//'): sUrl = 'https:' + sUrl
            hoster = {'link': sUrl, 'name': cParser.urlparse(sUrl)}
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

