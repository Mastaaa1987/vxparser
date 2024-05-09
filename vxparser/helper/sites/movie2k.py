# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!
# HTML LangzeitCache hinzugefügt
# showEntries:    6 Stunden
# showEpisodes:   4 Stunden

import re
import sys

from helper.requestHandler import cRequestHandler
from helper.tools import cParser

from json import loads


SITE_IDENTIFIER = 'movie2k'
SITE_NAME = 'Movie2K'
SITE_ICON = 'movie2k.png'
SITE_DOMAIN = 'movie2k.ch'

URL_MAIN = 'https://api.movie2k.ch/data/browse/?lang=%s&type=%s&order_by=%s&page=%s'  # lang=%s 2 = deutsch / 3 = englisch / all = Alles
URL_SEARCH = 'https://api.movie2k.ch/data/browse/?lang=%s&keyword=%s&page=%s'
URL_THUMBNAIL = 'https://image.tmdb.org/t/p/w300%s'
URL_WATCH = 'https://api.movie2k.ch/data/watch/?_id=%s'

ORIGIN = 'https://www2.movie2k.ch/'
# ORIGIN = 'https://movie2k.at/'
REFERER = ORIGIN + '/'

def load():
    sLanguage = '2'
    ret = []
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MAIN % (sLanguage, 'movies', 'featured', '1'), "typ": 1, "key": "showEntries", "title": "movies featured"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MAIN % (sLanguage, 'movies', 'releases', '1'), "typ": 1, "key": "showEntries", "title": "movies releases"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MAIN % (sLanguage, 'movies', 'trending', '1'), "typ": 1, "key": "showEntries", "title": "movies trending"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MAIN % (sLanguage, 'movies', 'updates', '1'), "typ": 1, "key": "showEntries", "title": "movies updates"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MAIN % (sLanguage, 'movies', 'requested', '1'), "typ": 1, "key": "showEntries", "title": "movies requested"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MAIN % (sLanguage, 'movies', 'rating', '1'), "typ": 1, "key": "showEntries", "title": "movies rating"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MAIN % (sLanguage, 'movies', 'votes', '1'), "typ": 1, "key": "showEntries", "title": "movies votes"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MAIN % (sLanguage, 'movies', 'views', '1'), "typ": 1, "key": "showEntries", "title": "movies views"})
    return ret


def _cleanTitle(sTitle):
    sTitle = re.sub("[\xE4]", 'ae', sTitle)
    sTitle = re.sub("[\xFC]", 'ue', sTitle)
    sTitle = re.sub("[\xF6]", 'oe', sTitle)
    sTitle = re.sub("[\xC4]", 'Ae', sTitle)
    sTitle = re.sub("[\xDC]", 'Ue', sTitle)
    sTitle = re.sub("[\xD6]", 'Oe', sTitle)
    sTitle = re.sub("[\x00-\x1F\x80-\xFF]", '', sTitle)
    return sTitle


def _getQuality(sQuality):
    isMatch, aResult = cParser.parse(sQuality, '(HDCAM|HD|WEB|BLUERAY|BRRIP|DVD|TS|SD|CAM)', 1, True)
    if isMatch:
        return aResult[0]
    else:
        return sQuality


def showEntries(entryUrl=False, sSearchText=False):
    folder = []
    isTvshow = False
    sThumbnail = ''
    sLanguage = '2'
    if not entryUrl: return
    try:
        oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
        oRequest.cacheTime = 60 * 60 * 24  # HTML Cache Zeit 6 Stunden
        oRequest.addHeaderEntry('Referer', REFERER)
        oRequest.addHeaderEntry('Origin', ORIGIN)
        sJson = oRequest.request()
        aJson = loads(sJson)
    except: return

    if 'movies' not in aJson or len(aJson['movies']) == 0: return

    total = 0
    # ignore movies which does not contain any streams
    for movie in aJson['movies']:
        if '_id' in movie:
            total += 1
    for movie in aJson['movies']:
        sTitle = movie['title']
        if sSearchText and not cParser().search(sSearchText, sTitle): continue
        if 'Staffel' in sTitle:
            isTvshow = True
        oGuiElement = {}
        oGuiElement["name"] = sTitle
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showEpisodes' if isTvshow else 'showHosters'
        
        oGuiElement["mediatype"] = 'tvshow' if isTvshow else 'movie'
        oGuiElement["total"] = total
        if 'poster_path_season' in movie: sThumbnail = URL_THUMBNAIL % movie['poster_path_season']
        elif 'poster_path' in movie: sThumbnail = URL_THUMBNAIL % movie['poster_path']
        elif 'backdrop_path' in movie: sThumbnail = URL_THUMBNAIL % movie['backdrop_path']
        oGuiElement["thumb"] = sThumbnail
        if 'storyline' in movie: oGuiElement["desc"] = movie['storyline']
        elif 'overview' in movie: oGuiElement["desc"] = movie['overview']
        if 'year' in movie: oGuiElement["year"] = movie['year']
        if 'quality' in movie: oGuiElement["quality"] = movie['quality']
        if 'rating' in movie: oGuiElement["rating"] = movie['rating']
        if 'lang' in movie:
            if (sLanguage != '1' and movie['lang'] == 2):  # Deutsch
                oGuiElement["lang"] = 'DE'
        if 'runtime' in movie:
            isMatch, sRuntime = cParser.parseSingleResult(movie['runtime'], '\d+')
            if isMatch: oGuiElement["duration"] = sRuntime
        oGuiElement["url"] = URL_WATCH % movie['_id']
        folder.append(oGuiElement)
    return folder


def showEpisodes(entryUrl=False, sThumbnail=False):
    folder = []
    aEpisodes = []
    sUrl = entryUrl
    try:
        oRequest = cRequestHandler(sUrl, ignoreErrors=True)
        oRequest.cacheTime = 60 * 60 * 4  # HTML Cache Zeit 4 Stunden
        oRequest.addHeaderEntry('Referer', REFERER)
        oRequest.addHeaderEntry('Origin', ORIGIN)
        sJson = oRequest.request()
        aJson = loads(sJson)
    except: return

    if 'streams' not in aJson or len(aJson['streams']) == 0: return

    for stream in aJson['streams']:
        if 'e' in stream:
            aEpisodes.append(int(stream['e']))
    if aEpisodes:
        aEpisodesSorted = set(aEpisodes)
        total = len(aEpisodesSorted)
        for sEpisode in aEpisodesSorted:
            oGuiElement = {}
            if 's' in aJson:  oGuiElement["s"] = aJson['s']
            oGuiElement["site"] = SITE_IDENTIFIER
            oGuiElement["domain"] = SITE_DOMAIN
            oGuiElement["key"] = 'showHosters'
            oGuiElement["thumb"] = sThumbnail
            oGuiElement["name"] = 'Episode ' + str(sEpisode)
            oGuiElement["e"] = sEpisode
            oGuiElement["p2"] = sEpisode
            oGuiElement["url"] = sUrl
            oGuiElement["mediatype"] = 'episode'
            oGuiElement["total"] = total
            folder.append(oGuiElement)
    return folder


def showHosters(entryUrl=False, sEpisode=False):
    hosters = []
    sUrl = entryUrl
    try:
        oRequest = cRequestHandler(sUrl, ignoreErrors=True)
        oRequest.addHeaderEntry('Referer', REFERER)
        oRequest.addHeaderEntry('Origin', ORIGIN)
        sJson = oRequest.request()
    except:
        return hosters
    if sJson:
        aJson = loads(sJson)
        if 'streams' in aJson:
            i = 0
            for stream in aJson['streams']:
                if (('e' not in stream) or (str(sEpisode) == str(stream['e']))):
                    sHoster = str(i) + ':'
                    isMatch, aName = cParser.parse(stream['stream'], '//([^/]+)/')
                    if isMatch:
                        sName = aName[0][:aName[0].rindex('.')]
                        #if cConfig().isBlockedHoster(sName)[0]: continue  # Hoster aus settings.xml oder deaktivierten Resolver ausschließen
                        sHoster = sHoster + ' ' + sName
                    if 'release' in stream:
                        sHoster = sHoster + ' [I][' + _getQuality(stream['release']) + '][/I]'
                    hoster = {'link': stream['stream'], 'name': sHoster}
                    hosters.append(hoster)
                    i += 1
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    return [{'streamUrl': sUrl, 'resolved': False}]


def search(sSearchText):
    sLang = '2'
    find = showEntries(URL_SEARCH % (sLang, cParser().quotePlus(sSearchText), '1'), sSearchText)
    if find:
        if len(find) > 0:
            return find
    return None

