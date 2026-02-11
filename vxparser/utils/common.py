import random, os, string, time, socket, sys, sqlite3, json, time
from unidecode import unidecode

VERSION = '1.4.9'
unicode = str
rp = os.path.normpath(os.path.dirname(os.path.abspath(__file__))+'/../')

sys.path.append(rp)
sys.path.append(os.path.join(rp, 'helper', 'resolveurl', 'lib'))
sys.path.append(os.path.join(rp, 'helper', 'sites'))
sys.path.append(os.path.join(rp, 'helper'))
sys.path.append(os.path.join(rp, 'utils'))

from helper import sql, sites

dp = os.path.join(rp, 'data')
cp = os.path.join(dp, 'cache')
lp = os.path.join(dp, 'lists')
db0 = os.path.join(dp, 'common.db')
db1 = os.path.join(dp, 'live.db')
db2 = os.path.join(dp, 'vod.db')
db3 = os.path.join(dp, 'epg.db')
if not os.path.exists(dp):
    os.makedirs(dp)
if not os.path.exists(cp):
    os.makedirs(cp)
if not os.path.exists(lp):
    os.makedirs(lp)

con0 = sqlite3.connect(db0)
con0.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])
con0.text_factory = lambda x: unicode(x, errors='ignore')
con1 = sqlite3.connect(db1)
con1.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])
con1.text_factory = lambda x: unicode(x, errors='ignore')
con2 = sqlite3.connect(db2)
con2.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])
con2.text_factory = lambda x: unicode(x, errors='ignore')
con3 = sqlite3.connect(db3)
con3.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])
con3.text_factory = lambda x: unicode(x, errors='ignore')


def Logger(lvl, msg, name=None, typ=None):
    if int(lvl) >= int(get_setting('log_lvl')) or int(lvl) == 0:
        if name or typ:
            if name and typ:
                print('[%s][%s]:: %s' %(str(typ).upper(), str(name).upper(), str(msg)))
            elif name:
                print('[%s]:: %s' %(str(name).upper(), str(msg)))
            elif typ:
                print('[%s]:: %s' %(str(typ).upper(), str(msg)))
            return
        print(msg)
    #CLIENT.send_message(b'/echo', [msg.encode('utf8'), ])


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return '127.0.0.1'


def get_public_ip():
    import urllib.request
    try:
        external_ip = urllib.request.urlopen('https://v4.ident.me').read().decode('utf8')
        return external_ip
    except:
        return None


def set_cache(key, value, path=None):
    #data={"timestamp": int(time.time()), "value": value}
    data={"value": value}
    if path:
        if not os.path.exists(os.path.join(cp, path)):
            os.makedirs(os.path.join(cp, path))
        file = os.path.join(cp, path, key)
    else: file = os.path.join(cp, key)
    if os.path.exists(file+".json"):
        os.remove(file+".json")
    with open(file+".json", "w") as k:
        json.dump(data, k, indent=4)


def get_cache(key, path=None):
    try:
        if path: file = os.path.join(cp, path, key)
        else: file = os.path.join(cp, key)
        with open(file+".json") as k:
            r = json.load(k)
        if None:
            timestamp = r.get('timestamp', 0)
            if int(timestamp + 86400*5) < int(time.time()):
                os.remove(file)
                return
        value = r.get('value')
        return value
    except:
        return None


def clear_cache():
    if os.path.exists(dp):
        import shutil
        con0.close()
        con1.close()
        con2.close()
        con3.close()
        shutil.rmtree(dp)
    return True



def clean_tables(item=None):
    if item:
        if item == 'live':
            cur = con1.cursor()
            cur.execute('DROP TABLE IF EXISTS channel')
            con1.commit()
        if item == 'streams':
            cur = con2.cursor()
            cur.execute('DROP TABLE IF EXISTS streams')
            cur.execute('DROP TABLE IF EXISTS info')
            con2.commit()
        if item == 'settings':
            cur = con0.cursor()
            cur.execute('DROP TABLE IF EXISTS settings')
            con0.commit()
        check()
        return True
    return False


def check_new_version():
    sett = ('VERSION', 'Hidden', VERSION, '', '', '', '')
    cur0 = con0.cursor()
    cur0.execute('SELECT * FROM settings')
    test = cur0.fetchall()
    if test:
        cur0.execute('SELECT * FROM settings WHERE name="VERSION"')
        test2 = cur0.fetchone()
        if test2:
            if test2['value'] == VERSION: return True
        lang = get_setting('lang')
        if lang == None: lang = 0
        else: lang = int(lang)
        Logger(0, 'Drop Database after Version update ...' if lang == 1 else 'Leere Datenbank nach Programm update ...')
        cur0.execute('DROP TABLE IF EXISTS settings')
        cur0.execute('DROP TABLE IF EXISTS lists')
        cur0.execute('DROP TABLE IF EXISTS categories')
        cur0.execute('DROP TABLE IF EXISTS epgs')
        con0.commit()
        cur1 = con1.cursor()
        cur1.execute('DROP TABLE IF EXISTS channel')
        con1.commit()
        cur2 = con2.cursor()
        cur2.execute('DROP TABLE IF EXISTS streams')
        cur2.execute('DROP TABLE IF EXISTS info')
        con2.commit()
        cur3 = con3.cursor()
        cur3.execute('DROP TABLE IF EXISTS epg')
        con3.commit()
        if os.path.exists(cp):
            import shutil
            shutil.rmtree(cp)
            time.sleep(0.1)
            os.makedirs(cp)
        time.sleep(0.1)
        add_tables()
    time.sleep(0.1)
    cur0.execute('INSERT INTO settings VALUES (?,?,?,?,?,?,?)', sett)
    con0.commit()
    return True


def add_tables():
    cur = con0.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS settings ("name" TEXT, "grp" TEXT, "value" TEXT, "info" TEXT, "default" TEXT, "type" TEXT, "values" TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS lists ("id" INTEGER PRIMARY KEY AUTOINCREMENT, "name" TEXT, "custom" INTEGER)')
    cur.execute('CREATE TABLE IF NOT EXISTS categories ("category_id" INTEGER PRIMARY KEY AUTOINCREMENT, "media_type" TEXT, "category_name" TEXT, "lid" INTEGER, "custom" TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS epgs ( "id" INTEGER PRIMARY KEY AUTOINCREMENT, "rid" TEXT, "mid" TEXT, "mn" TEXT, "tid" TEXT, "tn" TEXT, "display" TEXT, "ol" TEXT, "ml" TEXT, "tl" TEXT, "name" TEXT, "name1" TEXT, "name2" TEXT, "name3" TEXT, "name4" TEXT, "name5" TEXT)')
    con0.commit()
    cur = con1.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS channel ("id" INTEGER PRIMARY KEY AUTOINCREMENT, "name" TEXT, "grp" TEXT, "logo" TEXT, "tid" TEXT, "url" TEXT, "display" TEXT, "country" TEXT, "cid" INTEGER, "hls" TEXT)')
    con1.commit()
    cur = con2.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS streams ("id" INTEGER PRIMARY KEY AUTOINCREMENT, "sid" INTEGER, "site" TEXT, "key" TEXT, "p2" TEXT, "media_type" TEXT, "season" TEXT, "episode" TEXT, "name" TEXT, "url" TEXT, "thumb" TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS info ("id" INTEGER PRIMARY KEY AUTOINCREMENT, "site" TEXT, "category_id" INTEGER, "tmdb_id" INTEGER, "media_type" TEXT, "name" TEXT, "originalName" TEXT, "releaseDate" TEXT, "genres" TEXT, "description" TEXT, "countries" TEXT, "rating" TEXT, "votes" TEXT, "duration" TEXT, "poster" TEXT, "backdrop" TEXT, "quality" TEXT)')
    con2.commit()
    cur = con3.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS epg ( "id" INTEGER PRIMARY KEY AUTOINCREMENT, "cid" TEXT, "start" INTEGER, "end" INTEGER, "title" TEXT, "desc" TEXT, "lang" TEXT)')
    con3.commit()
    return True


def check_epg_tables():
    epg = sql.epg
    cur = con0.cursor()
    for row in epg:
        cur.execute('SELECT * FROM epgs WHERE rid="' + row[1] + '"')
        data = cur.fetchone()
        if not data:
            cur.execute('INSERT INTO epgs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', row)
    con0.commit()


def check_category_tables():
    cur = con0.cursor()
    groups = ['Sky','Sport','Cine','Germany']
    cur.execute('SELECT * FROM lists WHERE name="Germany"')
    test = cur.fetchone()
    if not test:
        cur.execute('INSERT INTO lists VALUES (NULL,"' + str('Germany') + '","' + str('0') + '")')
    cur.execute('SELECT * FROM lists WHERE name="Germany"')
    data = cur.fetchone()
    lid = data['id']
    for g in groups:
        cur.execute('SELECT * FROM categories WHERE category_name="' + g + '" AND media_type="' + str('live') + '"')
        test = cur.fetchone()
        if not test:
            if g == 'Germany':
                cur.execute('INSERT INTO categories VALUES (NULL,"' + str('live') + '","' + str(g) + '","' + str(lid) + '","0")')
            else:
                cur.execute('INSERT INTO categories VALUES (NULL,"' + str('live') + '","' + str(g) + '","' + str(lid) + '","1")')
    for site in sites.sites:
        name = site.SITE_IDENTIFIER
        cur.execute('SELECT * FROM categories WHERE category_name="' + name + '" AND media_type="' + str('movie') + '"')
        test = cur.fetchone()
        if not test:
            cur.execute('INSERT INTO categories VALUES (NULL,"' + str('movie') + '","' + str(name) + '","' + str('0') + '","' + str('0') + '")')
        cur.execute('SELECT * FROM categories WHERE category_name="' + name + '" AND media_type="' + str('tvshow') + '"')
        test = cur.fetchone()
        if not test:
            cur.execute('INSERT INTO categories VALUES (NULL,"' + str('tvshow') + '","' + str(name) + '","' + str('0') + '","' + str('0') + '")')
    cur.execute('SELECT * FROM categories WHERE category_name="' + str('vavoo') + '" AND media_type="' + str('movie') + '"')
    test = cur.fetchone()
    if not test:
        cur.execute('INSERT INTO categories VALUES (NULL,"' + str('movie') + '","' + str('vavoo') + '","' + str('0') + '","0")')
    cur.execute('SELECT * FROM categories WHERE category_name="' + str('vavoo') + '" AND media_type="' + str('tvshow') + '"')
    test = cur.fetchone()
    if not test:
        cur.execute('INSERT INTO categories VALUES (NULL,"' + str('tvshow') + '","' + str('vavoo') + '","' + str('0') + '","0")')
    con0.commit()


def check_settings_tables():
    sett = [
        ('server_host', 'Main', '0.0.0.0', '["FastAPI Server IP (0.0.0.0 = alle ips)", "FastAPI Server IP (0.0.0.0 = listen on all ips)"]', '0.0.0.0', 'text', ''),
        ('server_ip', 'Main', '', '["Genutze Server IP in den M3U8 Listen", "Server IP for M3U8 List Creation"]', '', 'text', ''),
        ('server_port', 'Main', '8080', '["Server Port", "Server Port"]', '8080', 'text', ''),
        ('server_service', 'Main', '1', '["Setze Server IP automatisch auf Netzwerk IP", "Set Automatic Network IP to Server IP Setting"]', '1', 'bool', '{"1": "On", "0": "Off"}'),
        ('m3u8_service', 'Main', '1', '["LiveTV Listen Erstellung als Service starten", "Start LiveTV List Creation as Service"]', '1', 'bool', '{"1": "On", "0": "Off"}'),
        ('m3u8_sleep', 'Main', '5', '["Zeit in Tagen zwischen LiveTV Listen Erstellung", "Sleep Time for Auto LiveTV List Creation Service in Hours"]', '5', 'text', ''),
        ('vod_service', 'Main', '1', '["VoD & Serien Listen Erstellung als Service starten", "Start VoD & Series List Creation as Service"]', '1', 'bool', '{"1": "On", "0": "Off"}'),
        ('vod_sleep', 'Main', '5', '["Zeit in Tagen zwischen automatischer VoD & Serien Listen erstellung", "Sleep Time for Auto List Creation Service for VoD & Series in Hours"]', '5', 'text', ''),
        ('epg_service', 'Main', '1', '["Starte epg.xml.gz Erstellung als Service", "Start epg.xml.gz Creation for LiveTV as Service"]', '1', 'bool', '{"1": "On", "0": "Off"}'),
        ('epg_sleep', 'Main', '5', '["Zeit in Tagen zwischen epg.xml.gz Erstellung", "Sleep Time for epg.xml.gz Creation Service in Days"]', '5', 'text', ''),
        ('log_lvl', 'Main', '1', '["LogLevel", "LogLevel"]', '1', 'select', '{"1": "Info", "3": "Error"}'),
        ('get_tmdb', 'Main', '0', '["Durchsuche TMDB für zusätzliche Informationen", "Search in TMDB after VoD & Series Infos"]', '0', 'bool', '{"1": "On", "0": "Off"}'),
        ('serienstream_username', 'Hidden', 'michael.zauner@live.at', '["Benutzername vom serienstream Account (s.to)", "Username of S.to User Accound"]', '', 'text', ''),
        ('serienstream_password', 'Hidden', 'michaz2455', '["Passwort für serienstream Account (s.to)", "Password for S.to User Accound"]', '', 'text', ''),
        ('xtream_codec', 'Main', 'h', '["Bevorzugter codec für Xtream Codes api", "Preferred codec for xtream codes api"]', 'h', 'select', '{"t": "ts", "h": "hls"}'),
        ('m3u8_hls', 'Vavoo', '1', '["Erstelle HLS m3u8 Listen", "Generate HLS m3u8 lists"]', '1', 'bool', '{"1": "On", "0": "Off"}'),
        ('m3u8_name', 'Vavoo', '1', '["Vavoo Channel Namen ersetzen", "Replace Vavoo Channel Name"]', '1', 'bool', '{"1": "On", "0": "Off"}'),
        ('epg_provider', 'Vavoo', 'm', '["Provider für EPG Informationen", "Provider for get EPG Infos"]', 'm', 'select', '{"m": "Magenta", "t": "TvSpielfilme"}'),
        ('epg_grab', 'Vavoo', '7', '["Anzahl an Tagen für epg.xml.gz Erstellung", "Count of Days for epg.xml.gz creation"]', '7', 'text', ''),
        ('epg_rytec', 'Vavoo', '1', '["Ersetze Provider IDs mit Rytec", "Replace Provider IDs with Rytec"]', '1', 'bool', '{"1": "On", "0": "Off"}'),
        ('epg_logos', 'Vavoo', 'p', '["Bevorzugte Logos", "Prefer Logos"]', 'p', 'select', '{"o": "Original", "p": "Provider"}'),
        ('init', 'Hidden', '0', '', '', '', ''),
        ('lang', 'Hidden', '0', '', '', '', ''),
        ('m3u8', 'Loop', '0', '', '', '', ''),
        ('epg', 'Loop', '0', '', '', '', ''),
        ('vod', 'Loop', '0', '', '', '', '')
    ]
    for site in sites.sites:
        name = site.SITE_IDENTIFIER
        sett.append((name+'_auto', 'Xstream', '1', '["Benutze %s Site in Automatic Modus", "Use %s Site in Auto Mode"]' % (name, name), '1', 'bool', '{"1": "On", "0": "Off"}'))
        sett.append((name+'_search', 'Xstream', '1', '["Suche auf %s Seite", "Search on %s Site"]' % (name, name), '1', 'bool', '{"1": "On", "0": "Off"}'))
    cur = con0.cursor()
    for row in sett:
        cur.execute('SELECT * FROM settings WHERE name="' + row[0] + '"')
        data = cur.fetchone()
        if not data:
            cur.execute('INSERT INTO settings VALUES (?,?,?,?,?,?,?)', row)
    con0.commit()


def check():
    if add_tables():
        check_new_version()
        check_category_tables()
        check_settings_tables()
        check_epg_tables()
    if int(get_setting('server_service')) == 1:
        set_setting('server_ip', str(get_ip_address()))


def server_info():
    server_info = {
        "url": str(get_ip_address()),
        "port": str(get_setting('server_port')),
        "https_port": "8443",
        "rtmp_port": "8880",
        "server_protocol": "http",
        "timestamp_now": int(time.time()),
    }
    server_info["time_now"] = time.strftime("%Y-%m-%d, %H:%M:%S", time.localtime())
    server_info["timezone"] = "Europe/London"
    return server_info


def gen_hash(length=32):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


def get_setting(name, group=None):
    cur = con0.cursor()
    if name:
        cur.execute('SELECT * FROM settings WHERE name="' + name + '"')
        data = cur.fetchone()
        if data: return data['value']
    return None


def set_setting(name, value, group=None):
    cur = con0.cursor()
    cur.execute('SELECT * FROM settings WHERE name="' + name + '"')
    test = cur.fetchone()
    if test:
        cur.execute('UPDATE settings SET value="' + value + '" WHERE name="' + name + '"')
    else:
        if group: g = group
        else: g = 'Hidden'
        row = ( name, g, value, '', '', '', '' )
        cur.execute('INSERT INTO settings VALUES (?,?,?,?,?,?,?)', row)
    con0.commit()
    return True


def random_user_agent():
    user_agent_pool = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; Tablet PC 2.0; .NET4.0E)",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.33 Safari/534.3 SE 2.X MetaSr 1.0",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E) QQBrowser/6.9.11079.201",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    ]
    return random.choice(user_agent_pool)

