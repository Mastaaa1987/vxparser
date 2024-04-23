import requests, random, sys, os, json, time, re, base64, codecs, threading, gzip, ssl, signal, sqlite3
from base64 import b64encode, b64decode
from time import sleep
from datetime import date, datetime
from unidecode import unidecode

from utils.common import get_ip_address as ip
from utils.common import Logger as Logger
import utils.common as com
import resolveurl as resolver

unicode = str

session = requests.session()
BASEURL = "https://www2.vavoo.to/ccapi/"

cachepath = com.cp
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
        veclist=requests.get("https://raw.githubusercontent.com/michaz1988/michaz1988.github.io/master/data.json").json()
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
    xlist=[
        "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"]
    while not sig:
        _data={"x":random.choice(xlist)}
        _headers={"user-agent": "Rokkr/1.8.3 (android)", "accept": "application/json", "content-type": "application/json; charset=utf-8", "content-length": "2408", "accept-encoding": "gzip", "cookie": "lng=en"}
        req = requests.post('https://www.rokkr.net/api/box/ping', json=_data, headers=_headers).json()
        if req.get('signed'):
            sig = req['signed']
        elif req.get('data', {}).get('signed'):
            sig = req['data']['signed']
        elif req.get('response', {}).get('signed'):
            sig = req['response']['signed']
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
    _data='{"token":"26fY7-FIvyz_UA5t9T_ndXB02KgaCT-jDx0uA9CE7iRAO_V2lCSGkAzzTXOpjHZHBvOoKcuq1OVCnbYX035d8698U0OYDaLo-7p8BJJIJNj7d1z-7byaQDuDFdEHPbnZAKAxG_fskVIrE0XkBV7_HbBnlIBDQ_EgxA","reason":"app-focus","locale":"de","theme":"light","metadata":{"device":{"type":"Handset","brand":"Xiaomi","model":"21081111RG","name":"21081111RG","uniqueId":"33267ca74bec24c7"},"os":{"name":"android","version":"7.1.2","abis":["arm64-v8a","armeabi-v7a","armeabi"],"host":"non-pangu-pod-sbcp6"},"app":{"platform":"android","version":"1.1.2","buildId":"97245000","engine":"jsc","signatures":["7c8c6b5030a8fa447078231e0f2c0d9ee4f24bb91f1bf9599790a1fafbeef7e0"],"installer":"com.android.secex"},"version":{"package":"net.dezor.browser","binary":"1.1.2","js":"1.2.9"}},"appFocusTime":1589,"playerActive":false,"playDuration":0,"devMode":false,"hasMhub":false,"castConnected":false,"package":"net.dezor.browser","version":"1.2.9","process":"app","firstAppStart":1681125328576,"lastAppStart":1681125328576,"ipLocation":null,"adblockEnabled":true,"proxy":{"supported":true,"enabled":true}}'
    signed = requests.post("https://www.dezor.net/api/app/ping", data=_data).json()["mhub"]
    _headers={"user-agent": "MediaHubMX/2", "accept": "application/json", "content-type": "application/json; charset=utf-8", "content-length": "158", "accept-encoding": "gzip", "Host": "www.kool.to", "mediahubmx-signature":signed}
    _data={"language":"de","region":"AT","url":link.replace("oha.to/oha-tv", "kool.to/kool-tv").replace("huhu.to/huhu-tv", "kool.to/kool-tv"),"clientVersion":"1.1.3"}
    url = "https://www.kool.to/kool-cluster/mediahubmx-resolve.json"
    resp = requests.post(url, data=json.dumps(_data), headers=_headers)
    if resp.status_code == 200: return resp.json()[0]["url"]
    return None


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


def sky_m3u8():
    hurl = 'http://'+str(com.get_setting('server_ip', 'Main'))+':'+str(com.get_setting('server_port', 'Main'))
    Logger(1, 'Starting with URL: %s ...' % str(hurl), 'm3u8', 'process')
    #url = 'https://www2.vavoo.to/live2/index'
    matches1 = ["13TH", "AXN", "A&E", "INVESTIGATION", "TNT", "DISNEY", "SKY", "WARNER"]
    matches2 = ["BUNDESLIGA", "SPORT", "TELEKOM"]
    matches3 = ["CINE", "EAGLE", "KINO", "FILMAX", "POPCORN"]
    groups = []
    epg_logos = com.get_setting('epg_logos')
    epg_rytec = com.get_setting('epg_rytec')
    m3u8_name = com.get_setting('m3u8_name')
    epg_provider = com.get_setting('epg_provider')

    con0 = sqlite3.connect(com.db0)
    con0.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])
    con0.text_factory = lambda x: unicode(x, errors='ignore')
    con1 = sqlite3.connect(com.db1)
    con1.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])
    con1.text_factory = lambda x: unicode(x, errors='ignore')
    con3 = sqlite3.connect(com.db3)
    con3.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])
    con3.text_factory = lambda x: unicode(x, errors='ignore')
    cur0 = con0.cursor()
    cur1 = con1.cursor()
    cur3 = con3.cursor()

    ssl._create_default_https_context = ssl._create_unverified_context
    _headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36', 'Content-Type': 'application/json; charset=utf-8'}
    channel = requests.get('https://www2.vavoo.to/live2/index?output=json', headers=_headers).json()
    #print(channel)
    #req = Request('https://www2.vavoo.to/live2/index?output=json', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36'})
    #req.add_header('Content-Type', 'application/json; charset=utf-8')
    #response = urlopen(req)
    #content = response.read().decode('utf8')
    #channel = json.loads(content)

    for c in channel:
        url = c['url']
        country = c['group']
        group = country
        if group not in groups:
            groups.append(group)
            cur0.execute('SELECT * FROM categories WHERE category_name="' + group + '" AND media_type="' + str('live') + '"')
            test = cur0.fetchone()
            if not test:
                cur0.execute('INSERT INTO categories VALUES (NULL,"' + str('live') + '","' + str(group) + '",NULL)')
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
                cur3.execute('SELECT * FROM epgs WHERE name="' + name + '" OR name1="' + name + '" OR name2="' + name + '" OR name3="' + name + '" OR name4="' + name + '" OR name5="' + name + '"')
                test = cur3.fetchone()
                if test:
                    tid = str(test['id'])
            cur1.execute('INSERT INTO channel VALUES(NULL,"' + c['name'].encode('ascii', 'ignore').decode('ascii') + '","' + group + '","' + logo + '","' + tid + '","' + c['url'] + '","' + name + '","' + str(country) + '","' + str(cid) + '","' + str(ti) + '")')
        else:
            cur1.execute('UPDATE channel SET url="' + c['url'] + '" WHERE name="' + c['name'].encode('ascii', 'ignore').decode('ascii') + '" AND grp="' + group + '"')
    con0.commit()
    con1.commit()
    con3.commit()

    for group in groups:
        if os.path.exists("%s/%s.m3u8" % (_path, re.sub(' ', '_', group))):
            os.remove("%s/%s.m3u8" % (_path, re.sub(' ', '_', group)))
        Logger(1, 'creating %s.m3u8 ...' % str(re.sub(' ', '_', group)))
        tf = open("%s/%s.m3u8" % (_path, re.sub(' ', '_', group)), "w")
        tf.write("#EXTM3U")
        tf.close()

    for c in channel:
        group = c['group']
        if c['group'] not in groups:
            groups.append(c['group'])
        if c['group'] == 'Germany':
            if any(x in c['name'] for x in matches1):
                group = 'Sky'
            if any(x in c['name'] for x in matches2):
                group = 'Sport'
            if any(x in c['name'] for x in matches3):
                group = 'Cine'

        cur1.execute('SELECT * FROM channel WHERE name="' + c['name'].encode('ascii', 'ignore').decode('ascii') + '" AND grp="' + group + '"')
        row = cur1.fetchone()
        if row:
            tid = None
            name = None
            logo = None
            if not str(row['tid']) == '':
                cur3.execute('SELECT * FROM epgs WHERE id="' + row['tid'] + '"')
                dat = cur3.fetchone()
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

            tf = open("%s/%s.m3u8" % (_path, re.sub(' ', '_', c['group'])), "a")
            if not logo == None and not tid == None:
                tf.write('\n#EXTINF:-1 tvg-name="%s" group-title="%s" tvg-logo="%s" tvg-id="%s",%s' % (row['name'], row['grp'], logo, tid, name))
            elif not logo == None and tid == None:
                tf.write('\n#EXTINF:-1 tvg-name="%s" group-title="%s" tvg-logo="%s",%s' % (row['name'], row['grp'], logo, name))
            elif not tid == None and logo == None:
                tf.write('\n#EXTINF:-1 tvg-name="%s" group-title="%s" tvg-id="%s",%s' % (row['name'], row['grp'], tid, name))
            else:
                tf.write('\n#EXTINF:-1 tvg-name="%s" group-title="%s",%s' % (row['name'], row['grp'], name))
            tf.write('\n#EXTVLCOPT:http-user-agent=VAVOO/2.6')
            tf.write('\n%s/channel/%s' % (hurl, row['id']))
            tf.close()
        else:
            Logger(3, 'Error!', 'm3u8', 'process')

    if int(com.get_setting('m3u8_hls')) == 1:
        global channels
        channels = []
        def _getchannels(group, cursor=0):
            global channels
            _headers={"user-agent":"WATCHED/1.8.3 (android)", "accept": "application/json", "content-type": "application/json; charset=utf-8", "cookie": "lng=", "watched-sig": getWatchedSig()}
            _data={"adult": True,"cursor": cursor,"filter": {"group": group},"sort": "name"}
            r = requests.post("https://www.oha.to/oha-tv-index/directory.watched", data=json.dumps(_data), headers=_headers).json()
            nextCursor = r.get("nextCursor")
            items = r.get("items")
            for item in items:
                channels.append(item)
            if nextCursor: _getchannels(group, nextCursor)

        for group in groups:
            _getchannels(group)

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
                    cur0.execute('SELECT * FROM categories WHERE category_name="' + group + '" AND media_type="' + str('live') + '"')
                    test = cur0.fetchone()
                    if not test:
                        cur0.execute('INSERT INTO categories VALUES (NULL,"' + str('live') + '","' + str(group) + '",NULL)')
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
                name = re.sub('( (\\|.*|AUSTRIA|AT|HEVC|RAW|SD|HD|FHD|UHD|H265|GERMANY|DEUTSCHLAND|1080|DE|S-ANHALT|SACHSEN|MATCH TIME))|(\\+)|( \\(BACKUP\\))|\\(BACKUP\\)|( \\([\\w ]+\\))|\\([\\d+]\\)', '', c['name'].encode('ascii', 'ignore').decode('ascii'))
                logo = c['logo']
                tid = ''
                ti = ''
                if c['group'] == 'Germany':
                    cur3.execute('SELECT * FROM epgs WHERE name="' + name + '" OR name1="' + name + '" OR name2="' + name + '" OR name3="' + name + '" OR name4="' + name + '" OR name5="' + name + '"')
                    test = cur3.fetchone()
                    if test:
                        tid = str(test['id'])
                cur1.execute('INSERT INTO channel VALUES(NULL,"' + c['name'].encode('ascii', 'ignore').decode('ascii') + '","' + group + '","' + logo + '","' + tid + '","' + str(ti) + '","' + name + '","' + str(country) + '","' + str(cid) + '","' + c['url'] + '")')
            else:
                cur1.execute('UPDATE channel SET hls="' + c['url'] + '" WHERE id="' + str(test['id']) + '"')
        con0.commit()
        con1.commit()
        con3.commit()

        for group in groups:
            if os.path.exists("%s/%s_hls.m3u8" % (_path, re.sub(' ', '_', group))):
                os.remove("%s/%s_hls.m3u8" % (_path, re.sub(' ', '_', group)))
            Logger(1, 'creating %s_hls.m3u8 ...' % str(re.sub(' ', '_', group)))
            tf = open("%s/%s_hls.m3u8" % (_path, re.sub(' ', '_', group)), "w")
            tf.write("#EXTM3U")
            tf.close()

        for c in channels:
            cur1.execute('SELECT * FROM channel WHERE hls="' + c['url'] + '"')
            row = cur1.fetchone()
            if row:
                tid = None
                name = None
                logo = None
                if not str(row['tid']) == '':
                    cur3.execute('SELECT * FROM epgs WHERE id="' + row['tid'] + '"')
                    dat = cur3.fetchone()
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

                tf = open("%s/%s_hls.m3u8" % (_path, re.sub(' ', '_', c['group'])), "a")
                if not logo == None and not tid == None:
                    tf.write('\n#EXTINF:-1 tvg-name="%s" group-title="%s" tvg-logo="%s" tvg-id="%s",%s' % (row['name'], row['grp'], logo, tid, name))
                elif not logo == None and tid == None:
                    tf.write('\n#EXTINF:-1 tvg-name="%s" group-title="%s" tvg-logo="%s",%s' % (row['name'], row['grp'], logo, name))
                elif not tid == None and logo == None:
                    tf.write('\n#EXTINF:-1 tvg-name="%s" group-title="%s" tvg-id="%s",%s' % (row['name'], row['grp'], tid, name))
                else:
                    tf.write('\n#EXTINF:-1 tvg-name="%s" group-title="%s",%s' % (row['name'], row['grp'], name))
                tf.write('\n%s/hls/%s' % (hurl, row['id']))
                tf.close()
            else:
                Logger(2, 'Warning!', 'm3u8', 'process')

    Logger(0, 'Done!', 'm3u8', 'process')
    Logger(9, 'done', 'm3u8', 'process')
    con0.close()
    con1.close()
    con3.close()
    return True
