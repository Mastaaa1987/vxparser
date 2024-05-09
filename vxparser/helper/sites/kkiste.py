# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!
# HTML LangzeitCache hinzugefügt
    #showValue:     48 Stunden
    #showEntries:    6 Stunden
    #showEpisodes:   4 Stunden
    
from helper.requestHandler import cRequestHandler
from helper.tools import cParser

SITE_IDENTIFIER = 'kkiste'
SITE_NAME = 'KKiste'
SITE_ICON = 'kkiste.png'
SITE_DOMAIN = 'kkiste.house'

URL_MAIN = 'https://kkiste.house/'
URL_NEW = URL_MAIN + 'kinofilme-online/'
URL_KINO = URL_MAIN + 'aktuelle-kinofilme-im-kino/'
URL_SERIES = URL_MAIN + 'serienstream-deutsch/'
URL_ANIMATION = URL_MAIN + 'animation/'
URL_SEARCH = URL_MAIN + 'index.php?do=search&subaction=search&story=%s'


def load():
    ret = []
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_NEW, "typ": 1, "key": "showEntries", "title": "New"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_KINO, "typ": 1, "key": "showEntries", "title": "Cinema"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_ANIMATION, "typ": 3, "key": "showEntries", "title": "Animated Films"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_SERIES, "typ": 2, "key": "showEntries", "title": "Series"})
    return ret


def showValue():
    folder = []
    oRequest = cRequestHandler(URL_MAIN)
    oRequest.cacheTime = 60 * 60 * 48  # 48 Stunden
    sHtmlContent = oRequest.request()    
    pattern = '>{0}<.*?</ul>'.format(params.getValue('Value'))
    isMatch, sHtmlContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        isMatch, aResult = cParser.parse(sHtmlContainer, 'href="([^"]+).*?>([^<]+)')
    if not isMatch: return

    for sUrl, sName in aResult:
        if sUrl.startswith('/'):
            sUrl = URL_MAIN + sUrl
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showEntries'
        oGuiElement["thumb"] = sThumbnail
        oGuiElement["url"] = sUrl
        folder.append(oGuiElement)
    return folder


def showEntries(entryUrl=False, sSearchText=False):
    folder = []
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # 6 Stunden
    sHtmlContent = oRequest.request()
    pattern = 'class="short">.*?' # container start
    pattern += 'href="([^"]+)' # url
    pattern += '">([^<]+).*?' # name
    pattern += '(.*?)</article>' # dummy

    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    if not isMatch: return

    total = len(aResult)
    for sUrl, sName, sDummy in aResult:
        if sSearchText and not cParser.search(sSearchText, sName): continue
        sLanguage = '1'
        if (sLanguage == '1' and 'English*' in sName):   # Deutsch
            continue
        if (sLanguage == '2' and not 'English*' in sName):   # English
            continue
        isThumbnail, sThumbnail = cParser.parseSingleResult(sDummy, 'img src="([^"]+)')  # Thumbnail
        isQuality, sQuality = cParser.parseSingleResult(sDummy, 'label-1">([^<]+)')  # Qualität
        isInfoEpisode, sInfoEpisode = cParser.parseSingleResult(sDummy, 'serie-num.*?</span>([\d]+)')  # Episodenanzahl
        isDesc, sDesc = cParser.parseSingleResult(sDummy, 'desc">([^<]+)')  # Beschreibung
        isYear, sYear = cParser.parseSingleResult(sDummy, 'Jahr.*?([\d]+)')  # Release Jahr
        isDuration, sDuration = cParser.parseSingleResult(sDummy, 's-red">([\d]+)')  # Laufzeit
        isTvshow = True if 'taffel' in sName or 'serie' in sUrl else False
        if isThumbnail: sThumbnail = URL_MAIN + sThumbnail
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showEpisodes' if isTvshow else 'showHosters'
        oGuiElement["thumb"] = sThumbnail
        oGuiElement["url"] = sUrl
        oGuiElement["mediatype"] = 'tvshow' if isTvshow else 'movie'
        oGuiElement["total"] = total
        if isQuality: oGuiElement["quality"] = sQuality
        if isInfoEpisode: oGuiElement["info"] = sInfoEpisode + ' Episoden'
        if isDesc: oGuiElement["desc"] = sDesc
        if isYear: oGuiElement["year"] = sYear
        if isDuration: oGuiElement["duration"] = sDuration
        folder.append(oGuiElement)
    return folder


def showEpisodes(entryUrl=False):
    folder = []
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # HTML Cache Zeit 4 Stunden
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
        oGuiElement["url"] = entryUrl
        oGuiElement["p2"] = sName
        oGuiElement["e"] = sName
        oGuiElement["mediatype"] = 'episode'
        oGuiElement["total"] = total
        if isDesc: oGuiElement["desc"] = sDesc
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
            if 'vod' in sUrl:
                continue
            if 'youtube' in sUrl:
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
    find = showEntries(URL_SEARCH % cParser.quotePlus(sSearchText), sSearchText)
    if find:
        if len(find) > 0:
            return find
    return None

