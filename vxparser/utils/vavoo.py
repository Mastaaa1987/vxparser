import requests, random, sys, os, json, urllib3, time, re, urllib, base64, codecs, threading, gzip, ssl, signal
from base64 import b64encode, b64decode
from time import sleep
from datetime import date, datetime
from unidecode import unidecode
from urllib.parse import urlencode, urlparse, parse_qsl, quote_plus
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from multiprocessing import Process, Queue

from utils.common import get_ip_address as ip
from utils.common import Logger as Logger
import utils.common as com
import resolveurl as resolver


unicode = str
urllib3.disable_warnings()
session = requests.session()
BASEURL = "https://www2.vavoo.to/ccapi/"

cachepath = com.cp
con0 = com.con0
con1 = com.con1
_path = com.lp


def getAuthSignature():
    key = com.get_setting('signkey')
    if key:
        ip = com.get_public_ip()
        now = int(time.time())*1000
        jkey = json.loads(json.loads(base64.b64decode(key.encode('utf-8')).decode('utf-8'))['data'])
        if 'ips' in jkey:
            key_ip = jkey['ips'][0]
        if 'app' in jkey and 'ok' in jkey['app']:
            key_ok = jkey['app']['ok']
        if 'validUntil' in jkey:
            valid = int(jkey['validUntil'])
        if ip == key_ip and key_ok == True and valid > now: return key
    veclist = com.get_cache('veclist')
    if not veclist:
        vlist=requests.get("http://mastaaa1987.github.io/repo/veclist.json").json()
        veclist = vlist['value']
        com.set_cache('veclist', veclist)
    sig = None
    i = 0
    while (not sig and i < 50):
        i+=1
        vec = {"vec": random.choice(veclist)}
        req = requests.post('https://www.vavoo.tv/api/box/ping2', data=vec).json()
        if req.get('signed'):
            sig = req['signed']
        elif req.get('data', {}).get('signed'):
            sig = req['data']['signed']
        elif req.get('response', {}).get('signed'):
            sig = req['response']['signed']
    com.set_setting('signkey', sig)
    return sig


def getWatchedSig():
    key = com.get_setting('wsignkey')
    if key:
        ip = com.get_public_ip()
        now = int(time.time())*1000
        jkey = json.loads(json.loads(base64.b64decode(key.encode('utf-8')).decode('utf-8'))['data'])
        if 'ips' in jkey:
            key_ip = jkey['ips'][0]
        if 'app' in jkey and 'ok' in jkey['app']:
            key_ok = jkey['app']['ok']
        if 'validUntil' in jkey:
            valid = int(jkey['validUntil'])
        if ip == key_ip and key_ok == True and valid > now: return key
    sig = None
    _headers={"user-agent": "okhttp/4.11.0", "accept": "application/json", "content-type": "application/json; charset=utf-8", "content-length": "1106", "accept-encoding": "gzip"}
    _data = {"token":"","reason":"boot","locale":"de","theme":"dark","metadata":{"device":{"type":"desktop","uniqueId":""},"os":{"name":"win32","version":"Windows 10 Education","abis":["x64"],"host":"DESKTOP-JN65HTI"},"app":{"platform":"electron"},"version":{"package":"app.lokke.main","binary":"1.0.19","js":"1.0.19"}},"appFocusTime":173,"playerActive":False,"playDuration":0,"devMode":True,"hasAddon":True,"castConnected":False,"package":"app.lokke.main","version":"1.0.19","process":"app","firstAppStart":1770751158625,"lastAppStart":1770751158625,"ipLocation":0,"adblockEnabled":True,"proxy":{"supported":["ss"],"engine":"cu","enabled":False,"autoServer":True,"id":0},"iap":{"supported":False}}
    req = requests.post('https://www.lokke.app/api/app/ping', json=_data, headers=_headers).json()
    sig = req.get("addonSig")
    com.set_setting('wsignkey', sig)
    return sig


def callApi(action, params, method="GET", headers=None, **kwargs):
    if not headers: headers = dict()
    headers["auth-token"] = getAuthSignature()
    resp = session.request(method, (BASEURL + action), params=params, headers=headers, **kwargs)
    if resp:
        resp.raise_for_status()
        data = resp.json()
        return data
    else: return


def callApi2(action, params):
    res = callApi(action, params, verify=False)
    while True:
        if type(res) is not dict or "id" not in res or "data" not in res:
            return res
        data = res["data"]
        if type(data) is dict and data.get("type") == "fetch":
            params = data["params"]
            body = params.get("body")
            headers = params.get("headers")
            try: resp = session.request(params.get("method", "GET").upper(), data["url"], headers={k:v[0] if type(v) in (list, tuple) else v for k, v in headers.items()} if headers else None, data=body.decode("base64") if body else None, allow_redirects=params.get("redirect", "follow") == "follow")
            except: return
            headers = dict(resp.headers)
            resData = {"status": resp.status_code, "url": resp.url, "headers": headers, "data": b64encode(resp.content).decode("utf-8").replace("\n", "") if data["body"] else None}
            log(json.dumps(resData))
            log(resp.text)
            res = callApi("res", {"id": res["id"]}, method="POST", json=resData, verify=False)
        elif type(data) is dict and data.get("error"):
            log(data.get("error"))
            return
        else: return data


def getStream(url):
    link = None
    link = resolver.resolve(url)
    return link


def getGroups():
    _headers={"user-agent":"WATCHED/1.8.3 (android)", "accept": "application/json", "content-type": "application/json; charset=utf-8", "cookie": "lng=", "watched-sig": getWatchedSig()}
    _data={"adult": True,"cursor": 0,"sort": "name"}
    r = requests.post("https://www.oha.to/oha-tv-index/directory.watched", data=json.dumps(_data), headers=_headers).json()
    groups = r.get("features").get("filter")[0].get("values")
    if groups:
        return groups
    return None


def resolve_link(link):
    _headers={"user-agent": "MediaHubMX/2", "accept": "application/json", "content-type": "application/json; charset=utf-8", "content-length": "115", "accept-encoding": "gzip", "mediahubmx-signature":getWatchedSig()}
    _data={"language":"de","region":"AT","url":link,"clientVersion":"3.0.2"}
    url = "https://vavoo.to/mediahubmx-resolve.json"
    return requests.post(url, data=json.dumps(_data), headers=_headers).json()[0]["url"]


def getLinks(action, params):
    data = callApi2(action, params)
    if data:
        arr = {}
        arr["1"] = []
        arr["2"] = []
        arr["3"] = []
        for d in data:
            if d["language"] == "de":
                if "1080p" in d["name"]: arr["1"].append(d["url"])
                elif "720p" in d["name"]: arr["2"].append(d["url"])
                else: arr["3"].append(d["url"])
        urls = []
        if len(arr["1"]) > 0:
            for u in arr["1"]:
                urls.append(u)
        if len(arr["2"]) > 0:
            for u in arr["2"]:
                urls.append(u)
        if len(arr["3"]) > 0:
            for u in arr["3"]:
                urls.append(u)
        if len(urls) > 0:
            return urls
            #for url in urls:
                #try:
                    #sLink = resolver.resolve(url)
                    #return sLink
                #except:
                    #return


def sky_dbfill(m3u8_generation=True):
    lang = int(com.get_setting('lang'))
    hurl = 'http://'+str(com.get_setting('server_ip'))+':'+str(com.get_setting('server_port'))
    Logger(1, 'Filling Database with data ...' if lang == 1 else 'Fülle Datenbank mit Daten ...', 'db', 'process')
    matches1 = ["13TH", "AXN", "A&E", "INVESTIGATION", "TNT", "DISNEY", "SKY", "WARNER"]
    matches2 = ["BUNDESLIGA", "SPORT", "TELEKOM"]
    matches3 = ["CINE", "EAGLE", "KINO", "FILMAX", "POPCORN"]
    groups = []
    epg_logos = com.get_setting('epg_logos')
    epg_rytec = com.get_setting('epg_rytec')
    m3u8_name = com.get_setting('m3u8_name')
    epg_provider = com.get_setting('epg_provider')

    cur0 = con0.cursor()
    cur1 = con1.cursor()

    ssl._create_default_https_context = ssl._create_unverified_context
    req = Request('https://www.vavoo.to/live2/index?output=json', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36'})
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    response = urlopen(req)
    content = response.read().decode('utf8')
    channel = json.loads(content)

    for c in channel:
        url = c['url']
        country = c['group']
        group = country
        if group not in groups:
            groups.append(group)
            cur0.execute('SELECT * FROM lists WHERE name="' + group + '"')
            test = cur0.fetchone()
            if not test:
                cur0.execute('INSERT INTO lists VALUES (NULL,"' + str(group) + '","' + str('0') + '")')
            cur0.execute('SELECT * FROM categories WHERE category_name="' + group + '" AND media_type="' + str('live') + '"')
            test = cur0.fetchone()
            if not test:
                cur0.execute('SELECT * FROM lists WHERE name="' + group + '"')
                data = cur0.fetchone()
                lid = data['id']
                cur0.execute('INSERT INTO categories VALUES (NULL,"' + str('live') + '","' + str(group) + '","' + str(lid) + '","0")')
        if group == 'Germany':
            if any(x in c['name'] for x in matches1):
                group = 'Sky'
            if any(x in c['name'] for x in matches2):
                group = 'Sport'
            if any(x in c['name'] for x in matches3):
                group = 'Cine'
        cur0.execute('SELECT * FROM categories WHERE category_name="' + group + '" AND media_type="' + str('live') + '"')
        data = cur0.fetchone()
        cid = data['category_id']
        cur1.execute('SELECT * FROM channel WHERE name="' + c['name'].encode('ascii', 'ignore').decode('ascii') + '" AND grp="' + group + '"')
        test = cur1.fetchone()
        if not test:
            name = re.sub('( (AUSTRIA|AT|HEVC|RAW|SD|HD|FHD|UHD|H265|GERMANY|DEUTSCHLAND|1080|DE|S-ANHALT|SACHSEN|MATCH TIME))|(\\+)|( \\(BACKUP\\))|\\(BACKUP\\)|( \\([\\w ]+\\))|\\([\\d+]\\)', '', c['name'].encode('ascii', 'ignore').decode('ascii'))
            logo = c['logo']
            tid = ''
            ti = ''
            if c['group'] == 'Germany':
                cur0.execute('SELECT * FROM epgs WHERE name="' + name + '" OR name1="' + name + '" OR name2="' + name + '" OR name3="' + name + '" OR name4="' + name + '" OR name5="' + name + '"')
                test = cur0.fetchone()
                if test:
                    tid = str(test['id'])
            cur1.execute('INSERT INTO channel VALUES(NULL,"' + c['name'].encode('ascii', 'ignore').decode('ascii') + '","' + group + '","' + logo + '","' + tid + '","' + c['url'] + '","' + name + '","' + str(country) + '","[' + str(cid) + ']","' + str(ti) + '")')
        else:
            cur1.execute('UPDATE channel SET url="' + c['url'] + '" WHERE name="' + c['name'].encode('ascii', 'ignore').decode('ascii') + '" AND grp="' + group + '"')
    con0.commit()
    con1.commit()

    global channels
    channels = []
    def _getchannels(group, filter, cursor=0):
        global channels
        _headers={"accept-encoding": "gzip", "user-agent":"MediaHubMX/2", "accept": "application/json", "content-type": "application/json; charset=utf-8", "mediahubmx-signature": getWatchedSig()}
        _data={"language":"de","region":"AT","catalogId":"iptv","id":"iptv","adult":False,"search":"","sort":"name","filter":{"group":group},"cursor":cursor,"clientVersion":"3.0.2"}
        r = requests.post("https://vavoo.to/mediahubmx-catalog.json", data=json.dumps(_data), headers=_headers).json()
        nextCursor = r.get("nextCursor")
        items = r.get("items")
        for item in items:
            if filter !=0 and "LUXEMBOURG" in item["name"]: continue
            channels.append(item)
        if nextCursor: _getchannels(group, filter, nextCursor)

    for group in groups:
        if group == "Germany": _getchannels(group, filter=2)
        else: _getchannels(group, filter=0)

    for c in channels:
        u = re.sub('.*/', '', c['url'])
        uid = u[:len(u)-12]
        cur1.execute('SELECT * FROM channel WHERE url LIKE "%' + uid + '%" OR hls="' + c['url'] + '"')
        test = cur1.fetchone()
        if not test:
            country = c['group']
            group = country
            if group not in groups:
                groups.append(group)
                cur0.execute('SELECT * FROM lists WHERE name="' + group + '"')
                test = cur0.fetchone()
                if not test:
                    cur0.execute('INSERT INTO lists VALUES (NULL,"' + str(group) + '","' + str('0') + '")')
                cur0.execute('SELECT * FROM categories WHERE category_name="' + group + '" AND media_type="' + str('live') + '"')
                test = cur0.fetchone()
                if not test:
                    cur0.execute('SELECT * FROM lists WHERE name="' + group + '"')
                    data = cur0.fetchone()
                    lid = data['id']
                    cur0.execute('INSERT INTO categories VALUES (NULL,"' + str('live') + '","' + str(group) + '","' + str(lid) + '","0")')
            if group == 'Germany':
                if any(x in c['name'] for x in matches1):
                    group = 'Sky'
                if any(x in c['name'] for x in matches2):
                    group = 'Sport'
                if any(x in c['name'] for x in matches3):
                    group = 'Cine'
            cur0.execute('SELECT * FROM categories WHERE category_name="' + group + '" AND media_type="' + str('live') + '"')
            data = cur0.fetchone()
            cid = data['category_id']
            name = re.sub('( (4K|.b|.c|.s|\\[.*]|\\|.*|AUSTRIA|AT|HEVC|RAW|SD|HD|FHD|UHD|H265|GERMANY|DEUTSCHLAND|1080|DE|S-ANHALT|SACHSEN|MATCH TIME))|(\\+)|( \\(BACKUP\\))|\\(BACKUP\\)|( \\([\\w ]+\\))|\\([\\d+]\\)', '', c['name'].encode('ascii', 'ignore').decode('ascii'))
            logo = c['logo']
            tid = ''
            ti = ''
            if c['group'] == 'Germany':
                cur0.execute('SELECT * FROM epgs WHERE name="' + name + '" OR name1="' + name + '" OR name2="' + name + '" OR name3="' + name + '" OR name4="' + name + '" OR name5="' + name + '"')
                test = cur0.fetchone()
                if test:
                    tid = str(test['id'])
            cur1.execute('INSERT INTO channel VALUES(NULL,"' + c['name'].encode('ascii', 'ignore').decode('ascii') + '","' + group + '","' + logo + '","' + tid + '","' + str(ti) + '","' + name + '","' + str(country) + '","[' + str(cid) + ']","' + c['url'] + '")')
        else:
            cur1.execute('UPDATE channel SET hls="' + c['url'] + '" WHERE id="' + str(test['id']) + '"')
    con0.commit()
    con1.commit()

    if m3u8_generation:
        gen_m3u8()

    lang = int(com.get_setting('lang'))
    Logger(0, 'Done!' if lang == 1 else 'Fertig!', 'db', 'process')


def gen_m3u8():
    lang = int(com.get_setting('lang'))
    hurl = 'http://'+str(com.get_setting('server_ip'))+':'+str(com.get_setting('server_port'))
    Logger(1, 'Starting with URL: %s ...' % str(hurl) if lang == 1 else 'Starte mit URL: %s ...' % str(hurl), 'm3u8', 'process')
    epg_logos = com.get_setting('epg_logos')
    epg_rytec = com.get_setting('epg_rytec')
    m3u8_name = com.get_setting('m3u8_name')
    epg_provider = com.get_setting('epg_provider')

    cur0 = con0.cursor() # common.db
    cur1 = con1.cursor() # live.db

    cur0.execute('SELECT * FROM lists ORDER BY id ASC')
    dat1 = cur0.fetchall()
    for l in dat1:
        lid = l['id']
        lname = l['name']
        if os.path.exists("%s/%s.m3u8" % (_path, re.sub(' ', '_', lname))):
            os.remove("%s/%s.m3u8" % (_path, re.sub(' ', '_', lname)))
        if os.path.exists("%s/%s_hls.m3u8" % (_path, re.sub(' ', '_', lname))):
            os.remove("%s/%s_hls.m3u8" % (_path, re.sub(' ', '_', lname)))
        Logger(1, 'creating %s.m3u8 & %s_hls.m3u8 ...' % (str(re.sub(' ', '_', lname)), str(re.sub(' ', '_', lname))) if lang == 1 else 'erstelle %s.m3u8 & %s_hls.m3u8 ...' % (str(re.sub(' ', '_', lname)), str(re.sub(' ', '_', lname))))
        tf = open("%s/%s.m3u8" % (_path, re.sub(' ', '_', lname)), "w")
        tf.write("#EXTM3U")
        tf.close()
        tf = open("%s/%s_hls.m3u8" % (_path, re.sub(' ', '_', lname)), "w")
        tf.write("#EXTM3U")
        tf.close()
        tf1 = open("%s/%s.m3u8" % (_path, re.sub(' ', '_', lname)), "a")
        tf2 = open("%s/%s_hls.m3u8" % (_path, re.sub(' ', '_', lname)), "a")
        cur0.execute('SELECT * FROM categories WHERE lid="'+ str(lid) +'" ORDER BY category_name ASC')
        dat2 = cur0.fetchall()
        for r in dat2:
            cid = r['category_id']
            cname = r['category_name']
            cur1.execute('SELECT * FROM channel WHERE cid LIKE "%['+ str(cid) +',%" OR cid LIKE "% '+ str(cid) +',%" OR cid LIKE "% '+ str(cid) +']%" OR cid LIKE "%['+ str(cid) +']%"')
            dat3 = cur1.fetchall()
            for row in dat3:
                tid = None
                name = None
                logo = None
                if not str(row['tid']) == '':
                    cur0.execute('SELECT * FROM epgs WHERE id="' + row['tid'] + '"')
                    dat = cur0.fetchone()
                    if epg_rytec == '1': tid = dat['rid']
                    elif epg_provider == 'm':
                        if not dat['mn'] == None: tid = dat['mn']
                    elif epg_provider == 't':
                        if not dat['tn'] == None: tid = dat['tn']
                    if epg_logos == 'p':
                        if epg_provider == 'm':
                            if not dat['ml'] == None: logo = dat['ml']
                        elif epg_provider == 't':
                            if not dat['tl'] == None: logo = dat['tl']
                    elif epg_logos == 'o':
                        if not dat['ol'] == None: logo = dat['ol']
                    if m3u8_name == '1':
                        if not dat['display'] == None: name = dat['display']
                        else: name = row['display']
                    else: name = row['name']
                else:
                    if m3u8_name == '1': name = row['display']
                    else: name = row['name']
                    if not str(row['logo']) == '': logo = row['logo']
                if not row['url'] == '':
                    if not logo == None and not tid == None:
                        tf1.write('\n#EXTINF:-1 tvg-name="%s" group-title="%s" tvg-logo="%s" tvg-id="%s",%s' % (row['name'], cname, logo, tid, name))
                    elif not logo == None and tid == None:
                        tf1.write('\n#EXTINF:-1 tvg-name="%s" group-title="%s" tvg-logo="%s",%s' % (row['name'], cname, logo, name))
                    elif not tid == None and logo == None:
                        tf1.write('\n#EXTINF:-1 tvg-name="%s" group-title="%s" tvg-id="%s",%s' % (row['name'], cname, tid, name))
                    else:
                        tf1.write('\n#EXTINF:-1 tvg-name="%s" group-title="%s",%s' % (row['name'], cname, name))
                    tf1.write('\n#EXTVLCOPT:http-user-agent=VAVOO/2.6')
                    tf1.write('\n%s/channel/%s' % (hurl, row['id']))
                if not row['hls'] == '':
                    if not logo == None and not tid == None:
                        tf2.write('\n#EXTINF:-1 tvg-name="%s" group-title="%s" tvg-logo="%s" tvg-id="%s",%s' % (row['name'], cname, logo, tid, name))
                    elif not logo == None and tid == None:
                        tf2.write('\n#EXTINF:-1 tvg-name="%s" group-title="%s" tvg-logo="%s",%s' % (row['name'], cname, logo, name))
                    elif not tid == None and logo == None:
                        tf2.write('\n#EXTINF:-1 tvg-name="%s" group-title="%s" tvg-id="%s",%s' % (row['name'], cname, tid, name))
                    else:
                        tf2.write('\n#EXTINF:-1 tvg-name="%s" group-title="%s",%s' % (row['name'], cname, name))
                    tf2.write('\n%s/hls/%s' % (hurl, row['id']))
        tf1.close()
        tf2.close()
    lang = int(com.get_setting('lang'))
    Logger(0, 'Done!' if lang == 1 else 'Fertig!', 'm3u8', 'process')
    return True

