# -*- coding: utf-8 -*-
import sys, os, json, requests, time, aiohttp, asyncio, re, random
from base64 import b64encode, b64decode 
from unidecode import unidecode
from re import search
from urllib.parse import urlencode, urlparse, parse_qsl, quote_plus
import utils.common as com
import utils.vavoo as vavoo

unicode = str

BASEURL = "https://www2.vavoo.to/ccapi/"
cachepath = os.path.join(com.dp, 'vavoo')
cp = com.cp
con0 = com.con0
con1 = com.con1
con2 = com.con2
con3 = com.con3

if not os.path.exists(cachepath):
    os.makedirs(cachepath)
if not os.path.exists(os.path.join(cachepath, "list")):
    os.makedirs(os.path.join(cachepath, "list"))
if not os.path.exists(os.path.join(cachepath, "series")):
    os.makedirs(os.path.join(cachepath, "series"))
if not os.path.exists(os.path.join(cachepath, "movie")):
    os.makedirs(os.path.join(cachepath, "movie"))

def set_cache(key, value, timeout=1200):
    if "signfile" in key:
        data={"sigValidUntil": int(time.time()) +timeout,"value": value}
    else:
        data={"value": value}
    if "signfile" in key or "veclist" in key: file = os.path.join(cp, key)
    else: file = os.path.join(cachepath, key)
    with open(file+".json", "w") as k:
        json.dump(data, k, indent=4)


def get_cache(key):
    try:
        if "signfile" in key or "veclist" in key: file = os.path.join(cp, key)
        else: file = os.path.join(cachepath, key)
        with open(file+".json") as k:
            r = json.load(k)
        if "signfile" in key:
            sigValidUntil = r.get('sigValidUntil', 0)
            if sigValidUntil < int(time.time()):
                os.remove(file)
                return
        value = r.get('value')
        return value
    except:
        return


def getAuthSignature():
    signfile = get_cache('signfile')
    if signfile: return signfile
    veclist = get_cache('veclist')
    import requests, random
    if not veclist:
        veclist=requests.get("https://raw.githubusercontent.com/michaz1988/michaz1988.github.io/master/data.json").json()
        set_cache('veclist', veclist)
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
    set_cache('signfile', sig)
    return sig


async def cachedcall(sem, session, action, params):
    #cacheKey = action + "?" + ("&").join([ str(key) + "=" + str(value) for key, value in sorted(list(params.items())) ])
    if action == "list":
        cacheKey = os.path.join(action, params["id"])
    elif "movie" in params["id"]:
        cacheKey = os.path.join("movie", params["id"])
    elif "series" in params["id"]:
        cacheKey = os.path.join("series", params["id"])
    content = get_cache(cacheKey)
    if content:
        return content
    else:
        async with sem:
            content = await callApi2(session, action, params)
            set_cache(cacheKey, content, timeout=1800)
            return content


async def callApi(session, action, params, method="GET", headers=None, **kwargs):
    if not headers: headers = dict()
    headers["auth-token"] = getAuthSignature()
    async with session.request(method, (BASEURL + action), params=params, headers=headers, **kwargs) as resp:
        resp.raise_for_status()
        #data = resp.json()
        return await resp.json()


async def callApi2(session, action, params):
    res = await callApi(session, action, params)
    if type(res) is not dict or "id" not in res or "data" not in res:
        return res
    return res["data"]


async def main():
    import re
    start_time = int(time.time())
    print('\nstarting database update ...')
    print('this might be serveral minutes...')
    params = {}
    ids = [ "movie.popular", "movie.trending", "series.trending", "series.popular" ]
    sem = asyncio.Semaphore(1000)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in ids:
            params["id"] = i
            while True:
                data = await cachedcall(sem, session, "list", params)
                for e in data["data"]:
                    task = asyncio.ensure_future(cachedcall(sem, session, "info", {"id": e["id"], "language": "de"}))
                    tasks.append(task)
                if data["next"]:
                    null = i + ".null.null"
                    if params["id"] == null or data["next"] == null or data["next"] == "series.popular.null.501" or data["next"] == "series.popular.null.500":
                        break
                    params["id"] = data["next"]
                else:
                    break
        responses = await asyncio.gather(*tasks)
        return
        con.text_factory = lambda x: unicode(x, errors='ignore')
        cur = con.cursor()
        for row in cur.execute('SELECT * FROM categories WHERE category_name="' + str('vavoo') + '"'):
            if row[1] == 'movie': cidM = row[0]
            elif row[1] == 'tvshow': cidS = row[0]
        print('\ncache files collecting, Done!')
        print('now flush the database ...')
        add = []
        V = S = I = 0
        for resp in responses:
            vid = resp["id"]
            if not vid in add:
                if "releaseDate" in resp: releaseDate = resp["releaseDate"]
                else: releaseDate = ''
                if "description" in resp: description = resp["description"].replace("\u201e", "").replace("\u201c", "").replace("\\\"", "").replace("'", "").replace("\"", "")
                else: description = ''
                if "backdrop" in resp: backdrop = resp["backdrop"]
                else: backdrop = ''
                if "poster" in resp: poster = resp["poster"]
                else: poster = ''
                if "name" in resp: name = resp["name"].replace("\\\"", "").replace("'", "").replace("\"", "")
                else: name = ''
                if "originalName" in resp: originalName = resp["originalName"].replace("\\\"", "").replace("'", "").replace("\"", "")
                else: originalName = ''
                cid = 0
                if "genres" in resp:
                    genres = str(resp["genres"]).replace("['", "").replace("']", "").replace("', '", ", ")
                else: genres = ''
                if "countries" in resp: 
                    if len(resp["countries"]) > 1: countries = str(resp["countries"]).replace("['", "").replace("']", "").replace("', '", ", ")
                    elif len(resp["countries"]) > 0: countries = str(resp["countries"]).replace("['", "").replace("']", "")
                    else: countries = ''
                else: countries = ''
                if "videos" in resp:
                    if "url" in resp["videos"][0]: 
                        if re.search("watch\?v=", resp["videos"][0]["url"]):
                            youtube = re.sub(".*?=", "", resp["videos"][0]["url"])
                        else: youtube = resp["videos"][0]["url"]
                    else: youtube = ''
                else: youtube = ''
                tmdb = re.sub("movie.|series.|\..*", "", vid)
                cur.execute('INSERT INTO info VALUES (NULL,"'+str(vid)+'","'+str(cid)+'","'+str(name)+'","'+str(originalName)+'","'+str(releaseDate)+'","'+str(genres)+'","'+str(description)+'","'+str(production)+'","'+str(countries)+'","'+str(poster)+'","'+str(writer)+'","'+str(director)+'","'+str(backdrop)+'","'+str(tmdb)+'","'+str(youtube)+'")')
                #"info" ("id","sites","category_id","tmdb_id","media_type","name","originalName","releaseDate","genres","description","countries","rating","votes","duration","poster","backdrop","youtube");
                #"streams" ("id","sid","sites","season","episode","name","urls","duration");
                if "movie" in vid:
                    cur.execute('INSERT INTO streams VALUES (NULL,"'+str(vid)+'","","","","")')
                    V += 1
                    I += 1
                    #qb.insert("streams", {"sid": str(vid), "custom_sid": "", "season": "", "episode": "", "name": ""}).go()
                elif "series" in vid:
                    S += 1
                    ##cur.execute('INSERT INTO streams VALUES (NULL,"'+str(vid)+'","","0","0","")')
                    if "seasons" in resp:
                        for season in resp["seasons"]:
                            for episode in resp["seasons"][season]:
                                sid = episode["id"]
                                snum = str(season)
                                enum = str(episode["episode"])
                                ename = episode["name"].replace("\u201e", "").replace("\u201e", "").replace("\u201c", "").replace("\\\"", "").replace("'", "").replace("\"", "")
                                if "Episode" in ename or "Folge" in ename or "PAGE" in ename:
                                    import re
                                    ename = re.sub('Episode ([0-9]+): |Episode ([0-9]+)|Folge ([0-9]+)|Folge ([0-9]+): |Episode: |Folge: |PAGE ([0-9]+)|PAGE', '', ename)
                                cur.execute('INSERT INTO streams VALUES (NULL,"'+str(vid)+'","'+str(sid)+'","'+str(snum)+'","'+str(enum)+'","'+str(ename)+'")')
                                I += 1
                add.append(vid)
                
        for gen in genM:
            cur.execute('INSERT INTO categories VALUES ("'+str(genM[gen])+'","1","'+str(gen)+'","0")')
        for gen in genS:
            cur.execute('INSERT INTO categories VALUES ("'+str(genS[gen])+'","2","'+str(gen)+'","0")')
        con.commit()
        con.close()
    print('\nDatabase update complete in %s seconds' % (int(time.time()) - start_time))
    print("%s VOD's & %s Serie's, %s Item's" % (str(V), str(S), str(I)))


def init_db():
    cur.execute('DROP TABLE IF EXISTS "streams";')
    cur.execute('CREATE TABLE "streams" ("id" INTEGER PRIMARY KEY AUTOINCREMENT, "sid" TEXT, "custom_sid" TEXT, "season" TEXT, "episode" TEXT, "name" TEXT)')
    cur.execute('DROP TABLE IF EXISTS "info";')
    cur.execute('CREATE TABLE "info" ("id" INTEGER PRIMARY KEY AUTOINCREMENT, "custom_sid" TEXT, "category_id" INTEGER, "name" TEXT, "originalName" TEXT, "releaseDate" TEXT, "genres" TEXT, "description" TEXT, "production" TEXT, "countries" TEXT, "poster" TEXT, "writer" TEXT, "director" TEXT, "backdrop" TEXT, "tmdb" TEXT, "youtube" TEXT)')
    cur.execute('DROP TABLE IF EXISTS "categories";')
    cur.execute('CREATE TABLE "categories" ("category_id" INTEGER PRIMARY KEY AUTOINCREMENT, "media_type" INTEGER, "category_name" TEXT, "parent_id" INTEGER)')
    con.commit()
    print("Database clear...")


def resolve():
    #init_db()
    asyncio.run(main())

