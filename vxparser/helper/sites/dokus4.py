# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!

from helper.requestHandler import cRequestHandler
from helper.tools import cParser


SITE_IDENTIFIER = 'dokus4'
SITE_NAME = 'Dokus4'
SITE_ICON = 'dokus4.png'
SITE_DOMAIN = 'dokus4.me'

# Domain Abfrage
URL_MAIN = 'http://www.dokus4.me/'
URL_SEARCH = URL_MAIN + '?s=%s'


def load():
    ret = []
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_MAIN, "typ": 3, "key": "showEntries", "title": "Documentations"})
    return ret


def showEntries(entryUrl=False, sSearchText=False):
    folder = []
    if not entryUrl: return
    sHtmlContent = cRequestHandler(entryUrl, ignoreErrors=True).request()
    if not sHtmlContent: return
    pattern = 'tbl_titel.*?title="([^"]+).*?href="([^"]+).*?src="([^"]+).*?vid_desc">([^<]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch: return

    total = len(aResult)
    for sName, sUrl, sThumbnail, sDesc in aResult:
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showHosters'
        oGuiElement["thumb"] = sThumbnail
        oGuiElement["url"] = sUrl
        oGuiElement["mediatype"] = 'movie'
        oGuiElement["total"] = total
        oGuiElement["desc"] = sDesc
        folder.append(oGuiElement)
    return folder


def showHosters(entryUrl=False):
    hosters = []
    sUrl = entryUrl # ParameterHandler().getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl, ignoreErrors=True).request()
    isMatch, aResult = cParser.parse(sHtmlContent, 'src="([^"]+)" f')
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
    find = showEntries(URL_SEARCH % cParser().quotePlus(sSearchText), sSearchText)
    if find:
        if len(find) > 0:
            return find
    return None

