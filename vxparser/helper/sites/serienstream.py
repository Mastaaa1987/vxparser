# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!
# Sprachauswahl für Hoster enthalten.
# Ajax Suchfunktion enthalten.
# HTML LangzeitCache hinzugefügt
    #showValue:     24 Stunden
    #showAllSeries: 24 Stunden
    #showEpisodes:   4 Stunden
    #SSsearch:      24 Stunden
    
# 2022-12-06 Heptamer - Suchfunktion überarbeitet

from helper.requestHandler import cRequestHandler
from helper.tools import cParser
import resolveurl as resolver
from urllib.parse import urlparse
import utils.common as common

SITE_IDENTIFIER = 'serienstream'
SITE_NAME = 'SerienStream'
SITE_ICON = 'serienstream.png'
SITE_DOMAIN = 's.to (186.2.175.5)'

URL_MAIN = 'http://186.2.175.5'
proxy = 'false'

URL_SERIES = URL_MAIN + '/serien'
URL_NEW_SERIES = URL_MAIN + '/neu'
URL_NEW_EPISODES = URL_MAIN + '/neue-episoden'
URL_POPULAR = URL_MAIN + '/beliebte-serien'
URL_LOGIN = URL_MAIN + '/login'


def load():
    username = common.get_setting('serienstream_username')
    password = common.get_setting('serienstream_password')
    if username == '' or password == '': return
    ret = []
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_NEW_SERIES, "typ": 2, "key": "showEntries", "title": "New Series"})
    ret.append({"site": SITE_IDENTIFIER, "domain": SITE_DOMAIN, "url": URL_POPULAR, "typ": 2, "key": "showEntries", "title": "Popular Series"})
    return ret


def showValue(entryUrl=False):
    folder = []
    sUrl = entryUrl
    #sHtmlContent = cRequestHandler(sUrl).request()
    oRequest = cRequestHandler(sUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24 # HTML Cache Zeit 1 Tag
    sHtmlContent = oRequest.request()
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, '<ul[^>]*class="%s"[^>]*>(.*?)<\\/ul>' % params.getValue('sCont'))
    if isMatch:
        isMatch, aResult = cParser.parse(sContainer, '<li>\s*<a[^>]*href="([^"]*)"[^>]*>(.*?)<\\/a>\s*<\\/li>')
    if not isMatch: return

    for sUrl, sName in aResult:
        sUrl = sUrl if sUrl.startswith('http') else URL_MAIN + sUrl
        params.setParam('sUrl', sUrl)
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showEntries'
        oGuiElement["title"] = sMovieTitle
        oGuiElement["url"] = sUrl
        oGuiElement["mediatype"] = 'tvshow'
        oGuiElement["total"] = total
        folder.append(oGuiElement)
    return folder


def showAllSeries(entryUrl=False, sGui=False, sSearchText=False):
    folder = []
    if not entryUrl: return
    #sHtmlContent = cRequestHandler(entryUrl, ignoreErrors=(sGui is not False)).request()
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24 # HTML Cache Zeit 1 Tag
    sHtmlContent = oRequest.request()
    pattern = '<a[^>]*href="(\\/serie\\/[^"]*)"[^>]*>(.*?)</a>'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch: return

    total = len(aResult)
    for sUrl, sName in aResult:
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showSeasons'
        oGuiElement["url"] = URL_MAIN + sUrl
        oGuiElement["mediatype"] = 'tvshow'
        oGuiElement["total"] = total
        folder.append(oGuiElement)
    return folder


def showNewEpisodes(entryUrl=False, sGui=False):
    folder = []
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    sHtmlContent = oRequest.request()
    pattern = '<div[^>]*class="col-md-[^"]*"[^>]*>\s*<a[^>]*href="([^"]*)"[^>]*>\s*<strong>([^<]+)</strong>\s*<span[^>]*>([^<]+)</span>'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch: return

    total = len(aResult)
    for sUrl, sName, sInfo in aResult:
        sMovieTitle = sName + ' ' + sInfo
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showSeasons'
        oGuiElement["title"] = sMovieTitle
        oGuiElement["url"] = URL_MAIN + sUrl
        oGuiElement["mediatype"] = 'tvshow'
        oGuiElement["total"] = total
        folder.append(oGuiElement)
    return folder


def showEntries(entryUrl=False, sGui=False):
    folder = []
    if not entryUrl: return
    oRequest = cRequestHandler(entryUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # 6 Stunden
    sHtmlContent = oRequest.request()
    pattern = '<div[^>]*class="col-md-[^"]*"[^>]*>.*?'  # start element
    pattern += '<a[^>]*href="([^"]*)"[^>]*>.*?'  # url
    pattern += 'data-src="([^"]*).*?'  # thumbnail
    pattern += '<h3>(.*?)<span[^>]*class="paragraph-end">.*?'  # title
    pattern += '<\\/div>'  # end element
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch: return

    total = len(aResult)
    for sUrl, sThumbnail, sName in aResult:
        #sThumbnail = URL_MAIN + sThumbnail
        oGuiElement = {}
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showSeasons'
        oGuiElement["thumb"] = URL_MAIN + sThumbnail
        oGuiElement["url"] = URL_MAIN + sUrl
        oGuiElement["mediatype"] = 'tvshow'
        oGuiElement["total"] = total
        folder.append(oGuiElement)
    return folder


def showSeasons(entryUrl=False):
    folder = []
    sUrl = entryUrl
    oRequest = cRequestHandler(sUrl, ignoreErrors=True)
    sHtmlContent = oRequest.request()
    pattern = '<div[^>]*class="hosterSiteDirectNav"[^>]*>.*?<ul>(.*?)<\\/ul>'
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        pattern = '<a[^>]*href="([^"]*)"[^>]*title="([^"]*)"[^>]*>(.*?)<\\/a>.*?'
        isMatch, aResult = cParser.parse(sContainer, pattern)
    if not isMatch: return

    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, '<p[^>]*data-full-description="(.*?)"[^>]*>')
    isThumbnail, sThumbnail = cParser.parseSingleResult(sHtmlContent, '<div[^>]*class="seriesCoverBox"[^>]*>.*?data-src="([^"]*)"[^>]*>')
    if isThumbnail:
        if sThumbnail.startswith('/'):
            sThumbnail = URL_MAIN + sThumbnail

    total = len(aResult)
    for sUrl, sName, sNr in aResult:
        isMovie = sUrl.endswith('filme')
        oGuiElement = {}
        if isThumbnail: oGuiElement["thumb"] = sThumbnail
        if isDesc: oGuiElement["desc"] = sDesc
        if not isMovie: oGuiElement["s"] = sNr
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showEpisodes'
        oGuiElement["url"] = URL_MAIN + sUrl
        oGuiElement["mediatype"] = 'season'
        oGuiElement["total"] = total
        folder.append(oGuiElement)
    return folder


def showEpisodes(entryUrl=False, sSeason=False, sTVShowTitle=False, sThumbnail=False):
    folder = []
    sUrl = entryUrl
    if not sSeason: sSeason = '0'
    isMovieList = sUrl.endswith('filme')
    oRequest = cRequestHandler(sUrl, ignoreErrors=True)
    oRequest.cacheTime = 60 * 60 * 24  # HTML Cache Zeit 4 Stunden
    sHtmlContent = oRequest.request()
    pattern = '<table[^>]*class="seasonEpisodesList"[^>]*>(.*?)<\\/table>'
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        pattern = '<tr[^>]*data-episode-season-id="(\d+).*?<a href="([^"]+).*?(?:<strong>(.*?)</strong>.*?)?(?:<span>(.*?)</span>.*?)?<'
        isMatch, aResult = cParser.parse(sContainer, pattern)
    if not isMatch: return

    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, '<p[^>]*data-full-description="(.*?)"[^>]*>')
    total = len(aResult)
    for sID, sUrl2, sNameGer, sNameEng in aResult:
        sName = '%d - ' % int(sID)
        sName += sNameGer if sNameGer else sNameEng
        oGuiElement = {}
        if sThumbnail: oGuiElement["thumb"] = sThumbnail
        if isDesc: oGuiElement["desc"] = sDesc
        if not isMovieList:
            oGuiElement["s"] = sSeason
            oGuiElement["e"] = int(sID)
            oGuiElement["show"] = sTVShowTitle
        oGuiElement["name"] = sName
        oGuiElement["site"] = SITE_IDENTIFIER
        oGuiElement["domain"] = SITE_DOMAIN
        oGuiElement["key"] = 'showHosters'
        oGuiElement["surl"] = sUrl
        oGuiElement["url"] = URL_MAIN + sUrl2
        oGuiElement["mediatype"] = 'tvshow' if not isMovieList else 'movie'
        oGuiElement["total"] = total
        folder.append(oGuiElement)
    return folder


def showHosters(entryUrl=False, sUrl=False):
    hosters = []
    if not sUrl: sUrl = entryUrl
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = '<li[^>]*data-lang-key="([^"]+).*?data-link-target="([^"]+).*?<h4>([^<]+)<([^>]+)'
    pattern2 = 'itemprop="keywords".content=".*?Season...([^"]+).S.*?' # HD Kennzeichen
    # data-lang-key="1" Deutsch
    # data-lang-key="2" Englisch
    # data-lang-key="3" Englisch mit deutschen Untertitel
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    aResult2 = cParser.parse(sHtmlContent, pattern2) # pattern 2 auslesen
    if isMatch:
        for sLangCode, sUrl, sName, sQualy in aResult:
            sLanguage = '1'
            if sLanguage == '1':        # Voreingestellte Sprache Deutsch in settings.xml
                if '2' in sLangCode:    # data-lang-key="2"
                    continue
                if '3' in sLangCode:    # data-lang-key="3"
                    continue
                if sLangCode == '1':    # data-lang-key="1"
                    sLang = 'Deutsch'   # Anzeige der Sprache
            if sLanguage == '2':        # Voreingestellte Sprache Englisch in settings.xml
                if '1' in sLangCode:    # data-lang-key="1"
                    continue
                if '3' in sLangCode:    # data-lang-key="3"
                    continue
                if sLangCode == '2':    # data-lang-key="2"
                    sLang = 'Englisch'   # Anzeige der Sprache    
            if sLanguage == '3':        # Voreingestellte Sprache Japanisch in settings.xml
                continue        
            if sLanguage == '0':        # Alle Sprachen 
                if sLangCode == '1':    # data-lang-key="1"
                    sLang = 'Deutsch'   # Anzeige der Sprache
                if sLangCode == '2':    # data-lang-key="2"
                    sLang = 'Englisch'  # Anzeige der Sprache   
                elif sLangCode == '3':  # data-lang-key="3"
                    sLang = 'Englisch mit deutschen Untertitel'    # Anzeige der Sprache
            if 'HD' in aResult2[1]: sQualy = 'HD'
            else: sQualy = 'SD'
                # Ab hier wird der sName mit abgefragt z.B:
                # aus dem Log [serienstream]: ['/redirect/12286260', 'VOE']
                # hier ist die sUrl = '/redirect/12286260' und der sName 'VOE'
                # hoster.py 194
            hoster = {'link': [sUrl, sName], 'name': sName, 'displayedName': '%s %s %s' % (sName, sQualy, sLang), 'languageCode': sLangCode}    # Language Code für hoster.py Sprache Prio
            hosters.append(hoster)
        if hosters:
            hosters.append('getHosterUrl')
        if not hosters: return
        return hosters


def isBlockedHoster(domain, checkResolver=True ):
    domain = urlparse(domain).path if urlparse(domain).hostname == None else urlparse(domain).hostname
    hostblockDict = ['flashx','streamlare','evoload']  # permanenter Block
    for i in hostblockDict:
        if i in domain.lower() or i.split('.')[0] in domain.lower(): return True, domain
    if checkResolver:   # Überprüfung in resolveUrl
        if resolver.relevant_resolvers(domain=domain) == []:
            print('[xStream] -> [isblockedHoster]: In resolveUrl no domain for url: %s' % domain)
            return True, domain    # Domain nicht in resolveUrl gefunden
    return False, domain


def getHosterUrl(hUrl, entryUrl=False):
    if type(hUrl) == str: hUrl = eval(hUrl)
    username = common.get_setting('serienstream_username')
    password = common.get_setting('serienstream_password')
    if username == '' or password == '': return
    if not entryUrl: entryUrl = hUrl[0]
    Handler = cRequestHandler(URL_LOGIN, caching=False)
    Handler.addHeaderEntry('Upgrade-Insecure-Requests', '1')
    Handler.addHeaderEntry('Referer', entryUrl)
    Handler.addParameters('email', username)
    Handler.addParameters('password', password)
    Handler.request()
    Request = cRequestHandler(URL_MAIN + hUrl[0], caching=False)
    Request.addHeaderEntry('Referer', entryUrl)
    Request.addHeaderEntry('Upgrade-Insecure-Requests', '1')
    Request.request()
    sUrl = Request.getRealUrl()

    if 'voe' in hUrl[1].lower():
        isBlocked, sDomain = isBlockedHoster(sUrl)  # Die funktion gibt 2 werte zurück!
        if isBlocked:  # Voe Pseudo sDomain nicht bekannt in resolveUrl
            sUrl = sUrl.replace(sDomain, 'voe.sx')
        return [{'streamUrl': sUrl, 'resolved': False}]

    return [{'streamUrl': sUrl, 'resolved': False}]


def search(sSearchText):
    username = common.get_setting('serienstream_username')
    password = common.get_setting('serienstream_password')
    if username == '' or password == '': return
    find = SSsearch(sSearchText)
    if find:
        if len(find) > 0:
            return find
    return None


def SSsearch(sSearchText=False):
    folder = []

    from json import loads

    oRequest = cRequestHandler(URL_SERIES, caching=True, ignoreErrors=True)
    oRequest.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
    oRequest.addHeaderEntry('Referer', 'https://s.to/serien')
    oRequest.addHeaderEntry('Origin', 'https://s.to')
    oRequest.addHeaderEntry('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    oRequest.addHeaderEntry('Upgrade-Insecure-Requests', '1')
    oRequest.cacheTime = 60 * 60 * 24  # HTML Cache Zeit 1 Tag
    sHtmlContent = oRequest.request()
    if not sHtmlContent: return

    sst = sSearchText.lower()

    pattern = '<li><a data.+?href="([^"]+)".+?">(.*?)\<\/a><\/l' #link - title

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, pattern)

    if not aResult[0]: return

    total = len(aResult[1])
    for link, title in aResult[1]:
        if not sst in title.lower():
            continue
        else:
            #get images thumb / descr pro call. (optional)
            try:
                sThumbnail, sDescription = getMetaInfo(link, title)
                oGuiElement = {}
                oGuiElement["name"] = title
                oGuiElement["site"] = SITE_IDENTIFIER
                oGuiElement["domain"] = SITE_DOMAIN
                oGuiElement["key"] = 'showSeasons'
                oGuiElement["url"] = URL_MAIN + link
                oGuiElement["mediatype"] = 'tvshow'
                oGuiElement["thumb"] = URL_MAIN + sThumbnail
                oGuiElement["desc"] = sDescription
                oGuiElement["total"] = total
                folder.append(oGuiElement)
            except Exception:
                oGuiElement = {}
                oGuiElement["name"] = title
                oGuiElement["site"] = SITE_IDENTIFIER
                oGuiElement["domain"] = SITE_DOMAIN
                oGuiElement["key"] = 'showSeasons'
                oGuiElement["url"] = URL_MAIN + link
                oGuiElement["mediatype"] = 'tvshow'
                oGuiElement["total"] = total
                folder.append(oGuiElement)
    return folder


def getMetaInfo(link, title):   # Setzen von Metadata in Suche:
    oRequest = cRequestHandler(URL_MAIN + link, caching=False)
    oRequest.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
    oRequest.addHeaderEntry('Referer', 'https://s.to/serien')
    oRequest.addHeaderEntry('Origin', 'https://s.to')

    #GET CONTENT OF HTML
    sHtmlContent = oRequest.request()
    if not sHtmlContent: return

    pattern = 'seriesCoverBox">.*?data-src="([^"]+).*?data-full-description="([^"]+)"' #img , descr

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, pattern)

    if not aResult[0]: return

    for sImg, sDescr in aResult[1]:
        return sImg, sDescr
