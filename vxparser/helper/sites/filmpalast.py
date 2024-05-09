# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!
# Sprachauswahl für Filme
# HTML LangzeitCache hinzugefügt
    #showValue:     24 Stunden
    #showEntries:    6 Stunden
    #showEpisodes:   4 Stunden

from helper.requestHandler import cRequestHandler
from helper.tools import cParser


SITE_IDENTIFIER = 'filmpalast'
SITE_NAME = 'FilmPalast'
SITE_ICON = 'filmpalast.png'
SITE_DOMAIN = 'filmpalast.to'

URL_MAIN = 'https://filmpalast.to'
URL_MOVIES = URL_MAIN + '/movies/%s'
URL_SERIES = URL_MAIN + '/serien/view'
URL_ENGLISH = URL_MAIN + '/search/genre/Englisch'
URL_SEARCH = URL_MAIN + '/search/title/%s'


def load():
    ret = []
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MAIN, "typ": 1, "key": "showEntries", "title": "New"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MOVIES % 'new', "typ": 1, "key": "showEntries", "title": "New Movies"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MOVIES % 'top', "typ": 1, "key": "showEntries", "title": "Top Movies"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MOVIES % 'imdb', "typ": 1, "key": "showEntries", "title": "IMDB rating"})
    return ret


def showValue(entryUrl=False, value=False):
    folder = []
    sUrl = entryUrl
    oRequest = cRequestHandler(sUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24 # HTML Cache Zeit 1 Tag
    sHtmlContent = oRequest.request()
    pattern = '<section[^>]id="%s">(.*?)</section>' % value # Suche in der Section Einträge
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        isMatch, aResult = cParser.parse(sContainer, 'href="([^"]+)">([^<]+)')
    if not isMatch: return

    for sUrl, sName in aResult:
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showEntries'
        oGuiElement["url"] = sUrl
        folder.append(oGuiElement)
    return folder


def showEntries(entryUrl=False, sSearchText=False):
    folder = []
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # 6 Stunden
    sHtmlContent = oRequest.request()
    # Durchsuche Einträge auf (filmpalast.to)
    pattern = '<article[^>]*>\s*' # container start
    pattern += '<a href="([^"]+)' # url
    pattern += '" title="([^"]+)">\s*' # name
    pattern += '<img src=["\']([^"\']+)["\'][^>]*>' # thumb
    pattern += '(.*?)</article>' # dummy
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        # Durchsuche Einträge auf (filmpalast.to/movies/new)
        pattern = '<a[^>]*href="([^"]*)"[^>]*'  # url
        pattern += 'title="([^"]*)"'  # name
        pattern += '[^>]*>[^<]*<img[^>]*src=["\']([^"\']*)["\'][^>]*>\s*</a>'  # thumb
        pattern += '(\s*)</article>'  # dummy
        isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch: return

    total = len(aResult)
    for sUrl, sName, sThumbnail, sDummy in aResult:
        isTvshow, aResult = cParser.parse(sName, 'S\d\dE\d\d')
        # seriesname should not be crippled here!
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        if sThumbnail.startswith('/'):
            sThumbnail = URL_MAIN + sThumbnail
        isYear, sYear = cParser.parseSingleResult(sDummy, 'Jahr:[^>]([\d]+)')
        isDuration, sDuration = cParser.parseSingleResult(sDummy, '[Laufzeit][Spielzeit]:[^>]([\d]+)')
        isRating, sRating = cParser.parseSingleResult(sDummy, 'Imdb:[^>]([^<]+)')
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showSeasons' if isTvshow else 'showHosters'
        oGuiElement["thumb"] = sThumbnail
        oGuiElement["mediatype"] = 'tvshow' if isTvshow else 'movie'
        oGuiElement["total"] = total
        if isYear: oGuiElement["year"] = sYear
        if isDuration: oGuiElement["duration"] = sDuration
        if isRating: oGuiElement["rating"] = 'rating', sRating.replace(',', '.')
        # Parameter übergeben
        if sUrl.startswith('//'): oGuiElement["url"] = 'https:' + sUrl
        else: oGuiElement["url"] = sUrl
        folder.append(oGuiElement)
    return folder


def showSeasons(entryUrl=False, sThumbnail=False, sName=False):
    folder = []
    sUrl = entryUrl
    oRequest = cRequestHandler(sUrl)
    oRequest.cacheTime = 60 * 60 * 24  # HTML Cache Zeit 24 Stunden
    sHtmlContent = oRequest.request()
    pattern = '<a[^>]*class="staffTab"[^>]*data-sid="(\d+)"[^>]*>'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch: return

    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, '"description">([^<]+)')
    total = len(aResult)
    for sSeason in aResult:
        oGuiElement = {}
        if isDesc: oGuiElement["desc"] = sDesc
        oGuiElement["name"] = 'Staffel ' + str(sSeason)
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showEpisodes'
        oGuiElement["url"] = sUrl
        oGuiElement["mediatype"] = 'season'
        oGuiElement["p2"] = sSeason
        oGuiElement["s"] = sSeason
        oGuiElement["total"] = total
        folder.append(oGuiElement)
    return folder


def showEpisodes(entryUrl=False, sSeason=False, sThumbnail=False, sShowName=False):
    folder = []
    # Parameter laden
    sUrl = entryUrl
    oRequest = cRequestHandler(sUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # HTML Cache Zeit 24 Stunden
    sHtmlContent = oRequest.request()
    pattern = '<div[^>]*class="staffelWrapperLoop[^"]*"[^>]*data-sid="%s">(.*?)</ul></div>' % sSeason
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if not isMatch: return

    pattern = 'href="([^"]+)'
    isMatch, aResult = cParser.parse(sContainer, pattern)
    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, '"description">([^<]+)')
    total = len(aResult)
    for sUrl in aResult:
        isMatch, sName = cParser.parseSingleResult(sUrl, 'e(\d+)')
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showHosters'
        oGuiElement["mediatype"] = 'episode'
        oGuiElement["e"] = sName
        if sUrl.startswith('//'): oGuiElement["url"] = 'https:' + sUrl
        else: oGuiElement["url"] = sUrl
        if isDesc: oGuiElement["desc"] = sDesc
        folder.append(oGuiElement)
    return folder


def showHosters(entryUrl=False):
    sUrl = entryUrl
    sHtmlContent = cRequestHandler(sUrl, ignoreErrors=True).request()
    pattern = 'hostName">([^<]+).*?(http[^"]+)' # Hoster Link
    releaseQuality = 'class="rb">.*?(\d\d\d+)p\.' # Release Qualität
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    isQuality, sQuality = cParser.parseSingleResult(sHtmlContent, releaseQuality)  # sReleaseQuality auslesen z.B. 1080
    if not isQuality: sQuality = '720'
    hosters = []
    if isMatch:
        for sName, sUrl in aResult:
            sName = sName.strip(' HD')
            hoster = {'link': sUrl, 'name': sName, 'displayedName': '%s [I][%sp][/I]' % (sName.replace('HD', ''), sQuality), 'quality': sQuality} # Qualität Anzeige aus Release Eintrag
            hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    return [{'streamUrl': sUrl, 'resolved': False}]


def search(sSearchText):
    find = showEntries(URL_SEARCH % cParser().quotePlus(sSearchText), sSearchText)
    if find:
        if len(find) > 0:
            return find
    return None

