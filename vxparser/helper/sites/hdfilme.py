# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!
# HTML LangzeitCache hinzugefügt
    #showGenre:     48 Stunden
    #showYears:     48 Stunden
    #showEpisodes:   4 Stunden


from helper.requestHandler import cRequestHandler
from helper.tools import cParser

SITE_IDENTIFIER = 'hdfilme'
SITE_NAME = 'HD Filme'
SITE_ICON = 'hdfilme.png'
SITE_DOMAIN = 'hdfilme.mom'

URL_MAIN = 'https://hdfilme.mom'
URL_NEW = URL_MAIN + '/kinofilme-online/'
URL_KINO = URL_MAIN + '/aktuelle-kinofilme-im-kino/'
URL_MOVIES = URL_MAIN + '/kinofilme-online'
URL_SERIES = URL_MAIN + '/serienstream-deutsch/'
URL_SEARCH = URL_MAIN + '/index.php?do=search&subaction=search&story=%s'


def load():
    ret = []
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_NEW, "typ": 1, "key": "showEntries", "title": "New"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_KINO, "typ": 1, "key": "showEntries", "title": "Cinema"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MOVIES, "typ": 1, "key": "showEntries", "title": "Movies"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_SERIES, "typ": 2, "key": "showEntries", "title": "Series"})
    return ret


def showEntries(entryUrl=False, sSearchText=False):
    folder = []
    isTvshow = False
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # 24 Stunden
    iPage = 0
    oRequest = cRequestHandler(entryUrl + 'page/' + str(iPage) if iPage > 0 else entryUrl, ignoreErrors=True)
    sHtmlContent = oRequest.request()
    pattern = '<div class="box-product' # Container Start
    pattern += '(.*?)<h3.*?'  # info dummy
    pattern += 'href="([^"]+).*?' # URL
    pattern += '">([^<]+).*?' # Name
    pattern += '(.*?)</li>' # dummy
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)

    if not isMatch: return

    total = len(aResult)
    for sInfo, sUrl, sName, sDummy in aResult:
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        # Abfrage der voreingestellten Sprache
        sLanguage = '1'
        if (sLanguage == '1' and 'English*' in sName):   # Deutsch
            continue
        if (sLanguage == '2' and not 'English*' in sName):   # English
            continue
        isThumbnail, sThumbnail = cParser.parseSingleResult(sInfo, 'data-src="([^"]+)')  # Thumbnail
        isYear, sYear = cParser.parseSingleResult(sDummy, '([\d]+)\s</p>')  # Release Jahr
        isQuality, sQuality = cParser.parseSingleResult(sDummy, 'quality-product">([^<]+)')  # Qualität
        isTvshow = True if 'taffel' in sName else False
        oGuiElement = {}
        if isYear: oGuiElement["year"] = sYear
        if isQuality: oGuiElement["quality"] = sQuality
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showEpisodes' if isTvshow else 'showHosters'
        if sThumbnail.startswith('/'): oGuiElement["thumb"] = URL_MAIN + sThumbnail
        else: oGuiElement["thumb"] = sThumbnail
        oGuiElement["url"] = sUrl
        oGuiElement["mediatype"] = 'tvshow' if isTvshow else 'movie'
        oGuiElement["total"] = total
        folder.append(oGuiElement)
    return folder


def showEpisodes(entryUrl=False):
    folder = []
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # 4 Stunden
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
    sHtmlContent = cRequestHandler(entryUrl, ignoreErrors=True).request()
    if episode:
        pass
        pattern = '%s<.*?</ul>' % episode
        isMatch, sHtmlContent = cParser.parseSingleResult(sHtmlContent, pattern)
    isMatch, aResult = cParser().parse(sHtmlContent, 'link="([^"]+)')
    if isMatch:
        sQuality = '720p'
        for sUrl in aResult:
            sName = cParser.urlparse(sUrl)
            if 'youtube' in sUrl:
                continue
            elif 'vod' in sUrl:
                continue
            elif sUrl.startswith('//'):
                 sUrl = 'https:' + sUrl
            hoster = {'link': sUrl, 'name': cParser.urlparse(sUrl), 'displayedName': '%s [I][%s][/I]' % (sName, sQuality), 'quality': sQuality, 'resolveable': True}
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

