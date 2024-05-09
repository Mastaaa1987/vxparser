# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!
# HTML LangzeitCache hinzugefügt
    #showValue:     48 Stunden
    #showEntries:    6 Stunden
    #showEpisodes:   4 Stunden
    
from helper.requestHandler import cRequestHandler
from helper.tools import cParser


SITE_IDENTIFIER = 'movie4k'
SITE_NAME = 'Movie4k'
SITE_ICON = 'movie4k.png'
SITE_DOMAIN = 'movie4k.buzz'

URL_MAIN = 'https://movie4k.buzz/'
URL_KINO = URL_MAIN + 'aktuelle-kinofilme-im-kino'
URL_MOVIES = URL_MAIN + 'kinofilme-online'
URL_SERIES = URL_MAIN + 'serienstream-deutsch'
URL_SEARCH = URL_MAIN + 'index.php?do=search&subaction=search&search_start=0&full_search=0&result_from=1&story=%s'

def load():
    ret = []
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_KINO, "typ": 1, "key": "showEntries", "title": "Current films in the cinema"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MOVIES, "typ": 1, "key": "showEntries", "title": "Movies"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_SERIES, "typ": 2, "key": "showEntries", "title": "Series"})
    return ret


def showEntries(entryUrl=False, sSearchText=False):
    folder = []
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # 6 Stunden
    sHtmlContent = oRequest.request()
    pattern = '<article.*?' # Container Start
    pattern += '(.*?)<a.*?'  # info dummy
    pattern += 'href="([^"]+).*?' # URL
    pattern += '<h3>([^<]+).*?' # Name
    pattern += '(.*?)</article>' # dummy
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch: return
    total = len(aResult)
    for sInfo, sUrl, sName, sDummy in aResult:
        if sSearchText and not cParser().search(sSearchText, sName): continue
        # Abfrage der voreingestellten Sprache
        sLanguage = '1' # cConfig().getSetting('prefLanguage')
        if (sLanguage == '1' and 'English*' in sName):   # Deutsch
            continue
        if (sLanguage == '2' and not 'English*' in sName):   # English
            continue
        isInfoEpisode, sInfo = cParser.parseSingleResult(sInfo, '</span>([\d]+)')  # Episodenanzahl
        isThumbnail, sThumbnail = cParser.parseSingleResult(sDummy, 'data-src="([^"]+)')  # Thumbnail
        isQuality, sQuality = cParser.parseSingleResult(sDummy, '<li>([^<]+)')  # Qualität
        isYear, sYear = cParser.parseSingleResult(sDummy, 'class="white">([\d]+)')  # Release Jahr
        isTvshow = True if 'taffel' in sName else False
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showEpisodes' if isTvshow else 'showHosters'
        oGuiElement["url"] = sUrl
        oGuiElement["mediatype"] = 'tvshow' if isTvshow else 'movie'
        oGuiElement["total"] = total
        if isThumbnail: oGuiElement["thumb"] = URL_MAIN + sThumbnail
        if isYear: oGuiElement["year"] = sYear
        if isQuality: oGuiElement["quality"] = sQuality
        if isInfoEpisode: oGuiElement["info"] = sInfo + ' Episoden'
        folder.append(oGuiElement)
    return folder


def showEpisodes(entryUrl=False, sThumbnail=False):
    folder = []
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # HTML Cache Zeit 4 Stunden
    sHtmlContent = oRequest.request()    
    pattern = 'id="serie-(\d+)[^>](\d+).*?href="#">([^<]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch: return
    isTvshow, sTVShowTitle = cParser.parseSingleResult(sHtmlContent, '<title>([^-]+)')
    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, 'name="description" content="([^"]+)')
    total = len(aResult)
    for sSeasonNr, sEpisodeNr, sName in aResult:
        oGuiElement = {}
        if isTvshow: oGuiElement["show"] = sTVShowTitle.strip()
        if isDesc: oGuiElement["desc"] = sDesc
        oGuiElement["name"] = 'Episode ' + sEpisodeNr
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showHosters'
        oGuiElement["thumb"] = sThumbnail
        oGuiElement["e"] = sEpisodeNr
        oGuiElement["season"] = sSeasonNr
        oGuiElement["url"] = entryUrl
        oGuiElement["p2"] = sEpisodeNr
        oGuiElement["mediatype"] = 'episode'
        oGuiElement["total"] = total
        folder.append(oGuiElement)
    return folder


def showHosters(entryUrl=False, sEpisodeNr=False):
    hosters = []
    sHtmlContent = cRequestHandler(entryUrl).request()
    if sEpisodeNr:
        pattern = '%s<.*?</ul>' % sEpisodeNr
        isMatch, sHtmlContent = cParser.parseSingleResult(sHtmlContent, pattern)
    isMatch, aResult = cParser().parse(sHtmlContent, 'link="([^"]+)">([^<]+)')
    if isMatch:
        sQuality = '720p'
        for sUrl, sName in aResult:
            if 'railer' in sName: continue # Youtube Trailer
            elif 'vod' in sUrl: continue # VOD Link
            if sUrl.startswith('//'):
                sUrl = 'https:' + sUrl
            hoster = {'link': sUrl, 'name': sName, 'displayedName': '%s [I][%s][/I]' % (sName, sQuality), 'quality': sQuality, 'resolveable': True}
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

