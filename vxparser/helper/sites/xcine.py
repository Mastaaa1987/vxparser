# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!
# HTML LangzeitCache hinzugefügt
    #showGenre:     48 Stunden
    #showYears:     48 Stunden
    #showEntries:    6 Stunden
    #showEpisodes:   4 Stunden
    
from helper.requestHandler import cRequestHandler
from helper.tools import cParser, cUtil

SITE_IDENTIFIER = 'xcine'
SITE_NAME = 'xCine'
SITE_ICON = 'xcinetop.png'
SITE_DOMAIN = 'xcine.click'

URL_MAIN = 'https://xcine.click/'
URL_NEW = URL_MAIN + 'kinofilme-online/'
URL_KINO = URL_MAIN + 'aktuelle-kinofilme-im-kino/'
URL_MOVIES = URL_MAIN + 'kinofilme-online'
URL_ANIMATION = URL_MAIN + 'animation/'
URL_SERIES = URL_MAIN + 'serienstream-deutsch/'
URL_SEARCH = URL_MAIN + 'index.php?do=search&subaction=search&story=%s'


def load():
    ret = []
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_NEW, "typ": 1, "key": "showEntries", "title": "New"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_KINO, "typ": 1, "key": "showEntries", "title": "Current films in the cinema"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MOVIES, "typ": 1, "key": "showEntries", "title": "Movies"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_SERIES, "typ": 2, "key": "showEntries", "title": "Series"})
    return ret


def showEntries(entryUrl=False, sSearchText=False):
    folder = []
    isTvshow = False
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # 6 Stunden
    iPage = 0
    oRequest = cRequestHandler(entryUrl + 'page/' + str(iPage) if iPage > 0 else entryUrl)
    sHtmlContent = oRequest.request()
    pattern = 'item__link.*?' # container start
    pattern += 'href="([^"]+).*?' # url
    pattern += '<img src="([^"]+).*?' # thumb
    pattern += 'alt="([^"]+).*?' # name
    pattern += '(.*?)</span>\s+<span>' # dummy
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)

    if not isMatch: return

    total = len(aResult)
    for sUrl, sThumbnail, sName, sDummy in aResult:
        if sSearchText and not cParser.search(sSearchText, sName):
            continue
        # Abfrage der voreingestellten Sprache
        sLanguage = '1'
        if (sLanguage == '1' and 'English*' in sName):   # Deutsch
            continue
        if (sLanguage == '2' and not 'English*' in sName):   # English
            continue
        isQuality, sQuality = cParser.parseSingleResult(sDummy, 'movie-item__label">([^<]+)')  # Qualität
        isInfoEpisode, sInfoEpisode = cParser.parseSingleResult(sDummy, 'ep-num">e.([\d]+)')  # Episodenanzahl
        isYear, sYear = cParser.parseSingleResult(sDummy, 'meta ws-nowrap">\s+<span>([\d]+)')  # Release Jahr
        isTvshow, aResult = cParser.parse(sName, '\s+-\s+Staffel\s+\d+')
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showEpisodes' if isTvshow else 'showHosters'
        if sThumbnail[0] == '/': sThumbnail = sThumbnail[1:]
        oGuiElement["thumb"] = URL_MAIN + sThumbnail
        if isQuality: oGuiElement["quality"] = sQuality
        if isInfoEpisode: oGuiElement["info"] = sInfoEpisode + ' Episoden'
        if isYear: oGuiElement["year"] = sYear
        oGuiElement["mediatype"] = 'tvshow' if isTvshow else 'movie'
        oGuiElement["url"] = sUrl
        oGuiElement["total"] = total

        folder.append(oGuiElement)
    return folder


def showEpisodes(entryUrl=False):
    folder = []
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # 6 Stunden
    sHtmlContent = oRequest.request()
    isMatch, aResult = cParser.parse(sHtmlContent, '"><a href="#">([^<]+)')
    if not isMatch: return

    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, '"description"[^>]content="([^"]+)')
    total = len(aResult)
    for sName in aResult:
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showHosters'
        oGuiElement["mediatype"] = 'episode'
        if isDesc: oGuiElement["desc"] = sDesc
        oGuiElement["url"] = entryUrl
        oGuiElement["p2"] = sName
        oGuiElement["e"] = sName
        folder.append(oGuiElement)
    return folder


def showHosters(entryUrl=False, episode=False):
    hosters = []
    sUrl = entryUrl
    sHtmlContent = cRequestHandler(sUrl).request()
    if episode:
        pattern = '>{0}<.*?</ul></li>'.format(episode)
        isMatch, sHtmlContent = cParser.parseSingleResult(sHtmlContent, pattern)
    isMatch, aResult = cParser().parse(sHtmlContent, 'link="([^"]+)')
    if isMatch:
        for sUrl in aResult:
            sName = cParser.urlparse(sUrl)
            if 'youtube' in sUrl:
                continue
            elif 'vod' in sUrl:
                continue
            elif sUrl.startswith('//'):
                 sUrl = 'https:' + sUrl
            hoster = {'link': sUrl, 'name': cParser.urlparse(sUrl)}
            hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    return [{'streamUrl': sUrl, 'resolved': False}]


def search(sSearchText):
    oGui = False
    find = showEntries(URL_SEARCH % cParser.quotePlus(sSearchText), sSearchText)
    if find:
        if len(find) > 0:
            return find
    return None

