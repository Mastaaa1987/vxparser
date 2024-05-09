# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!
# HTML LangzeitCache hinzugefügt
    #showValue:     24 Stunden
    #showEntries:    6 Stunden
    #showEpisodes:   4 Stunden
    
from helper.requestHandler import cRequestHandler
from helper.tools import cParser, cUtil


SITE_IDENTIFIER = 'kinokiste'
SITE_NAME = 'Kinokiste'
SITE_ICON = 'kinokistetech.png'
SITE_DOMAIN = 'kinokiste.cloud'

URL_MAIN = 'https://kinokiste.cloud/'
URL_NEW = URL_MAIN + 'kinofilme-online/'
URL_KINO = URL_MAIN + 'aktuelle-kinofilme-im-kino/'
URL_ANIMATION = URL_MAIN + 'animation/'
URL_SERIES = URL_MAIN + 'serienstream-deutsch/'
URL_SEARCH = URL_MAIN + '?do=search&subaction=search&story=%s'

def load():
    ret = []
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_NEW, "typ": 1, "key": "showEntries", "title": "New"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_KINO, "typ": 1, "key": "showEntries", "title": "Current films in the cinema"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_SERIES, "typ": 2, "key": "showEntries", "title": "Series"})
    return ret


def showEntries(entryUrl=False, sSearchText=False):
    folder = []
    isTvshow = False
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # 6 Stunden
    sHtmlContent = oRequest.request()    
    pattern = '<section class="fl-item.*?' # start container
    pattern += 'href="([^"]+).*?' # url
    pattern += 'alt="([^"]+).*?' # name
    pattern += 'src="([^"]+).*?' # thumb
    pattern += '(.*?)</section>' # dummy
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)

    if not isMatch: return

    total = len(aResult)
    for sUrl, sName, sThumbnail, sDummy in aResult:
        # Abfrage der voreingestellten Sprache
        sLanguage = '1'
        if (sLanguage == '1' and 'English*' in sName):   # Deutsch
            continue
        if (sLanguage == '2' and not 'English*' in sName):   # English
            continue
        if sSearchText and not cParser.search(sSearchText, sName):
            continue
        if sThumbnail[0] == '/': sThumbnail = sThumbnail[1:]
        isQuality, sQuality = cParser.parseSingleResult(sDummy, 'fl-quality[^"]+">([^<]+)')  # Qualität
        isInfoEpisode, sInfoEpisode = cParser.parseSingleResult(sDummy, 'mli-ep">ep.([\d]+)')  # Episodenanzahl
        isTvshow, aResult = cParser.parse(sName, '\s+-\s+Staffel\s+\d+')
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showEpisodes' if isTvshow else 'showHosters'
        oGuiElement["thumb"] = URL_MAIN + sThumbnail
        oGuiElement["url"] = sUrl
        oGuiElement["p2"] = sName
        oGuiElement["mediatype"] = 'tvshow' if isTvshow else 'movie'
        oGuiElement["total"] = total
        if isQuality: oGuiElement["quality"] = sQuality
        if isInfoEpisode: oGuiElement["info"] = sInfoEpisode + ' Episoden'
        folder.append(oGuiElement)
    return folder


def showEpisodes(entryUrl=False, sName=False, sThumbnail=False):
    folder = []
    sUrl = entryUrl
    isMatch, sShowName = cParser.parseSingleResult(sName, '(.*?)\s+-\s+Staffel\s+\d+')
    if not isMatch: return
    isMatch, sSeason = cParser.parseSingleResult(sName, '\s+-\s+Staffel\s+(\d+)')
    if not isMatch: return

    oRequest = cRequestHandler(sUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # HTML Cache Zeit 4 Stunden
    sHtmlContent = oRequest.request()
    pattern = '<li\s+id="serie-([^"]+)">\s*<a\s+href="#">([^<]+)</a>'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)

    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, '"description"[^>]content="([^"]+)')
    total = len(aResult)
    for episode, episodeName in aResult:
        oGuiElement = {}
        if isDesc: oGuiElement["desc"] = sDesc
        if '_' in episode: 
            oGuiElement["episode"] = episode.partition('_')[2]
            oGuiElement["p2"] = episode.partition('_')[2]
            oGuiElement["e"] = episode.partition('_')[2]
        else: 
            oGuiElement["episode"] = episode
            oGuiElement["p2"] = episode
            oGuiElement["e"] = episode
        oGuiElement["name"] = str(episodeName)
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showEpisodeHosters'
        oGuiElement["thumb"] = URL_MAIN + sThumbnail
        oGuiElement["show"] = sShowName
        oGuiElement["season"] = sSeason
        oGuiElement["url"] = sUrl
        oGuiElement["mediatype"] = 'episode'
        oGuiElement["total"] = total
        folder.append(oGuiElement)
    return folder


def showHosters(entryUrl=False, sName=False):
    hosters = []
    sUrl = entryUrl
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = '<li>\s*<a\s+href="#"\s+data-link="([^"]+)">\s*<i>\s*</i>\s*([^<]+)</a>\s*</li>'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if isMatch:
        for sUrl, sHoster in aResult:
            sName = cParser.urlparse(sUrl)
            hoster = {'link': sUrl, 'name': sHoster}
            hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def showEpisodeHosters(entryUrl=False, episodeId=False):
    hosters = []
    sUrl = entryUrl
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = '<li>\s*<a\s+href="#"\s+id="[^"]+-%s"\s+data-link="([^"]+)">\s*([^<]+)</a>\s*</li>' % episodeId
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if isMatch:
        for sUrl, sHoster in aResult:
            sName = cParser.urlparse(sUrl)
            hoster = {'link': sUrl, 'name': sHoster}
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

