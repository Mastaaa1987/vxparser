# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!
# HTML LangzeitCache hinzugefügt
    #showValue:     48 Stunden
    #showEntries:    6 Stunden
    #showEpisodes:   4 Stunden
    
from helper.requestHandler import cRequestHandler
from helper.tools import cParser


SITE_IDENTIFIER = 'megakino'
SITE_NAME = 'Megakino'
SITE_ICON = 'megakino.png'
SITE_DOMAIN = 'megakino.co'

URL_MAIN = 'https://megakino.co/'
URL_KINO = URL_MAIN + 'kinofilme/'
URL_MOVIES = URL_MAIN + 'films/'
URL_SERIES = URL_MAIN + 'serials/'
URL_ANIMATION = URL_MAIN + 'multfilm/'
URL_DOKU = URL_MAIN + 'documentary/'
URL_SEARCH = URL_MAIN + '?do=search&subaction=search&story=%s'


def load():
    ret = []
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MAIN, "typ": 1, "key": "showEntries", "title": "New"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_KINO, "typ": 1, "key": "showEntries", "title": "Current films in the cinema"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MOVIES, "typ": 1, "key": "showEntries", "title": "Movies"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_SERIES, "typ": 2, "key": "showEntries", "title": "Series"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_DOKU, "typ": 3, "key": "showEntries", "title": "Documentations"})
    return ret


def showEntries(entryUrl=False, sSearchText=False):
    folder = []
    isTvshow = False
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # 6 Stunden
    sHtmlContent = oRequest.request()
    #pattern = '<a[^>]*class="poster grid-item.*?href="([^"]+).*?<img data-src="([^"]+).*?alt="([^"]+)".*?class="poster__label">([^<]+).*?class="poster__text[^"]+">([^<]+)'
    pattern = '<a[^>]*class="poster grid-item.*?' # container start
    pattern += 'href="([^"]+).*?' # url
    pattern += '<img data-src="([^"]+).*?' # thumb
    pattern += 'alt="([^"]+)".*?' # name
    pattern += '(.*?)</a>' # dummy
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)

    if not isMatch: return

    total = len(aResult)
    for sUrl, sThumbnail, sName, sDummy in aResult:
        if sSearchText and not cParser.search(sSearchText, sName):
            continue
        isQuality, sQuality = cParser.parseSingleResult(sDummy, 'poster__label">\+([\d]+)')  # Episoden Info mit +
        if not isQuality:
            isQuality, sQuality = cParser.parseSingleResult(sDummy, 'poster__label">\+\s([\d]+)') # Episoden Info mit + und Leerzeichen
        if not isQuality:
            isQuality, sQuality = cParser.parseSingleResult(sDummy, 'poster__label">([^<]+)') # Qualität bei Filmen
        isYear, sYear = cParser.parseSingleResult(sDummy, '([\d]+)</li>\s+<li>')  # Release Jahr
        isDesc, sDesc = cParser.parseSingleResult(sDummy, 'class="poster__text[^"]+">([^<]+)')  # Beschreibung
        isTvshow, aResult = cParser.parse(sName, '\s+-\s+Staffel\s+\d+')
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showEpisodes' if isTvshow else 'showHosters'
        oGuiElement["thumb"] = URL_MAIN + sThumbnail
        oGuiElement["url"] = sUrl
        if isTvshow: oGuiElement["p2"] = sName
        oGuiElement["mediatype"] = 'tvshow' if isTvshow else 'movie'
        oGuiElement["total"] = total
        if isQuality:
            if isTvshow is True:
                if sQuality == 'Komplett':
                    oGuiElement["quality"] = 'Komplette Staffel'
                else:
                    oGuiElement["quality"] = sQuality + ' Episoden'
            else:
                oGuiElement["quality"] = sQuality
        if isYear:
            oGuiElement["year"] = sYear
        if isDesc:
            if sDesc[-1] != '.':
                sDesc += '...'
            oGuiElement["desc"] = sDesc
        folder.append(oGuiElement)
    return folder


def showEpisodes(entryUrl=False, sName=False, sThumbnail=False, sDesc=False):
    folder = []
    sUrl = entryUrl
    isMatch, sShowName = cParser.parseSingleResult(sName, '(.*?)\s+-\s+Staffel\s+\d+')
    if not isMatch: return
    isMatch, sSeason = cParser.parseSingleResult(sName, '\s+-\s+Staffel\s+(\d+)')
    if not isMatch: return

    oRequest = cRequestHandler(sUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # HTML Cache Zeit 4 Stunden
    sHtmlContent = oRequest.request()     
    pattern = '<option\s+value="ep([^"]+)">([^<]+)</option>'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    total = len(aResult)
    for episode, episodeName in aResult:
        oGuiElement = {}
        oGuiElement["name"] = str(episodeName)
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showEpisodeHosters'
        oGuiElement["thumb"] = URL_MAIN + sThumbnail
        oGuiElement["show"] = sShowName
        oGuiElement["season"] = sSeason
        oGuiElement["url"] = sUrl
        oGuiElement["p2"] = episode
        oGuiElement["e"] = episode
        oGuiElement["mediatype"] = 'episode'
        oGuiElement["desc"] = sDesc
        oGuiElement["total"] = total
        folder.append(oGuiElement)
    return folder


def showHosters(entryUrl=False):
    hosters = []
    sUrl = entryUrl
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = '<iframe\s+id="film_main"\s+data-src="([^"]+)"'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if isMatch:
        for sUrl in aResult:
            sName =cParser.urlparse(sUrl)
            hoster = {'link': sUrl, 'name': sName}
            hosters.append(hoster)
    pattern = '<iframe\s+src=([^\s]+).*?width'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if isMatch:
        for sUrl in aResult:
            sName = cParser.urlparse(sUrl)
            hoster = {'link': sUrl, 'name': sName}
            hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def showEpisodeHosters(entryUrl=False, episode=False):
    hosters = []
    if not entryUrl: return
    if not episode: return
    sUrl = entryUrl
    episodeId = 'ep' + episode
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = '<select\s+name="pmovie__select-items"\s+class="[^"]+"\s+style="[^"]+"\s+id="%s">\s*(.*?)\s*</select>' % episodeId
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        pattern = '<option\s+value="([^"]+)">'
        isMatch, aResult = cParser.parse(sContainer, pattern)
        if isMatch:
            for sUrl in aResult:
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

