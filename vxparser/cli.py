import inquirer, re, time, os, json
from datetime import timedelta

import utils.common as common
from utils.common import Logger as Logger
import utils.xstream as xstream
import services

con = common.con0
cache = common.cp


def mainMenu():
    c = []
    c.append((" ","0"))
    c.append(("Settings =>","settings"))
    c.append(("Vavoo (LiveTV) =>","submenu_vavoo"))
    c.append(("Xstream (VoD's & Series) =>", "submenu_xstream"))
    c.append(("Stop Services", "stop_service"))
    c.append(("Restart Services", "restart_service"))
    c.append(("- Clean Database (Settings)","clean_db"))
    c.append(("- Clear Cache Path","clear_cache"))
    c.append(("<= Shutdown","shutdown"))
    q = [ inquirer.List("item", message="Main Menu", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    return quest['item']


def mainSettings():
    cur = con.cursor()
    c = []
    rows = []
    x = 0
    l = 0
    c.append(("<= Back","-1"))
    for row in cur.execute('SELECT * FROM settings WHERE grp="' + str('Main') + '"'):
        if row['type'] == 'text':
            val = row['value']
        if row['type'] == 'bool' or row['type'] == 'select':
            values = json.loads(row['values'])
            val = values[row['value']]
        if len(val) > l:
            l = len(val)
    for row in cur.execute('SELECT * FROM settings WHERE grp="' + str('Main') + '"'):
        rows.append(row)
        if row['type'] == 'text':
            val = row['value']
        if row['type'] == 'bool' or row['type'] == 'select':
            values = json.loads(row['values'])
            val = values[row['value']]
        t = '] '
        if not l - len(val) == 0:
            for i in range(0, l-len(val)):
                t += ' '
        c.append(('['+val+t+row['info'], str(x)))
        x += 1
    q = [ inquirer.List("item", message="Main Settings", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    if not quest["item"] == '-1':
        row = rows[int(quest["item"])]
        if row['type'] == 'text':
            q2 = [ inquirer.Text("input", message="edit: "+row["name"], default=row["value"]) ]
            quest2 = inquirer.prompt(q2)
            common.set_setting(row["name"], quest2["input"], 'Main')
        if row['type'] == 'bool':
            values = json.loads(row['values'])
            for v in values:
                if not v == row['value']:
                    new = v
                    break
            common.set_setting(row["name"], new, 'Main')
        if row['type'] == 'select':
            c2 = []
            values = json.loads(row['values'])
            for v in values:
                c2.append(('['+values[v]+']', v))
            q2 = [ inquirer.List("item", message="select: "+row['name'], choices=c2, carousel=True) ]
            quest2 = inquirer.prompt(q2)
            common.set_setting(row["name"], quest2["item"], 'Main')
    else: return 'back'
    return True


def xstreamMenu():
    c = []
    c.append((" ","0"))
    c.append(("Settings =>","settings"))
    c.append(("Global Search","search"))
    c.append(("Get New VoD & Series","get_new"))
    c.append(("ReCreate vod+series.m3u8","gen_lists"))
    c.append(("Refresh VideoOnDemand Lists", "get_vod"))
    c.append(("- Clean Database (Streams)","clean_db"))
    c.append(("<= Main Menu","back"))
    q = [ inquirer.List("item", message="VoD & Series", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    return quest['item']


def xstreamSettings():
    cur = con.cursor()
    c = []
    d = []
    keys = []
    vals = []
    x = 0
    for row in cur.execute('SELECT * FROM settings WHERE grp="' + str('Xstream') + '"'):
        site = re.sub('_auto|_search', '', row['name'])
        if "_auto" in row['name']: name = site+': auto list creation?'
        else: name = site+': global search?'
        c.append((name, str(x)))
        if int(row['value']) == 1: d.append(str(x))
        keys.append(row['name'])
        vals.append(row['value'])
        x += 1
    q = [ inquirer.Checkbox("check", message="Site Settings", choices=c, default=d, carousel=True) ]
    quest = inquirer.prompt(q)
    for y in range(0, x):
        if str(y) in quest["check"] and not str(y) in d:
            common.set_setting(keys[y], str(1), 'Xstream')
        if not str(y) in quest["check"] and str(y) in d:
            common.set_setting(keys[y], str(0), 'Xstream')
    return True


def vavooMenu():
    c = []
    c.append((" ","0"))
    c.append(("Settings =>","settings"))
    c.append(("Get LiveTV Lists","get_list"))
    c.append(("Get epg.xml.gz", "get_epg"))
    c.append(("- Clean Database (LiveTV)","clean_db"))
    c.append(("<= Main Menu","back"))
    q = [ inquirer.List("item", message="Sky Live TV", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    return quest['item']


def vavooSettings():
    cur = con.cursor()
    c = []
    rows = []
    x = 0
    l = 0
    c.append(("<= Back","-1"))
    for row in cur.execute('SELECT * FROM settings WHERE grp="' + str('Vavoo') + '"'):
        if row['type'] == 'text':
            val = row['value']
        if row['type'] == 'bool' or row['type'] == 'select':
            values = json.loads(row['values'])
            val = values[row['value']]
        if len(val) > l:
            l = len(val)
    for row in cur.execute('SELECT * FROM settings WHERE grp="' + str('Vavoo') + '"'):
        rows.append(row)
        if row['type'] == 'text':
            val = row['value']
        if row['type'] == 'bool' or row['type'] == 'select':
            values = json.loads(row['values'])
            val = values[row['value']]
        t = '] '
        if not l - len(val) == 0:
            for i in range(0, l-len(val)):
                t += ' '
        c.append(('['+val+t+row['info'], str(x)))
        x += 1
    q = [ inquirer.List("item", message="EPG Settings", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    if not quest["item"] == '-1':
        row = rows[int(quest["item"])]
        if row['type'] == 'text':
            q2 = [ inquirer.Text("input", message="edit: "+row["name"], default=row["value"]) ]
            quest2 = inquirer.prompt(q2)
            common.set_setting(row["name"], quest2["input"], 'Vavoo')
        if row['type'] == 'bool':
            values = json.loads(row['values'])
            for v in values:
                if not v == row['value']:
                    new = v
                    break
            common.set_setting(row["name"], new, 'Vavoo')
        if row['type'] == 'select':
            c2 = []
            values = json.loads(row['values'])
            for v in values:
                c2.append(('['+values[v]+']', v))
            q2 = [ inquirer.List("item", message="select: "+row['name'], choices=c2, carousel=True) ]
            quest2 = inquirer.prompt(q2)
            common.set_setting(row["name"], quest2["item"], 'Vavoo')
    else: return 'back'
    return True


def menu():
    menu = 'main'
    try:
        while True:
            if menu == 'msettings':
                quest = mainSettings()
                if not quest: Logger(3, 'Error!', 'main', 'settings')
                elif quest == 'back': menu = 'main'
            if menu == 'main':
                time.sleep(0.2)
                item = mainMenu()
                if item == 'submenu_vavoo': menu = 'vavoo'
                if item == 'submenu_xstream': menu = 'xstream'
                if item == 'settings':
                    menu = 'msettings'
                    quest = mainSettings()
                    if not quest: Logger(3, 'Error!', 'main', 'settings')
                    elif quest == 'back': menu = 'main'
                if item == 'shutdown':
                    Logger(0, "Quitting Now...")
                    services.handler('kill')
                    con.close()
                    break
                if item == 'stop_service': services.handler('service_stop')
                if item == 'restart_service': services.handler('service_restart')
                if item == 'clean_db':
                    c = []
                    c.append((" ","0"))
                    c.append(("Yes","yes"))
                    c.append(("No", "no"))
                    c.append(("<= Back","back"))
                    q = [ inquirer.List("item", message="Really Clean settings Database?", choices=c, carousel=True) ]
                    quest = inquirer.prompt(q)
                    if quest['item'] == 'yes':
                        clean = common.clean_tables('settings')
                        if not clean: Logger(3, 'Error!', 'db', 'clean')
                        else: Logger(0, 'Successful ...', 'db', 'clean')
                if item == 'clear_cache':
                    c = []
                    c.append((" ","0"))
                    c.append(("Yes","yes"))
                    c.append(("No", "no"))
                    c.append(("<= Back","back"))
                    q = [ inquirer.List("item", message="Really Clear Cache?", choices=c, carousel=True) ]
                    quest = inquirer.prompt(q)
                    if quest['item'] == 'yes':
                        services.handler('kill')
                        clear = common.clear_cache()
                        if not clear: Logger(3, 'Error!', 'data', 'clear')
                        else: 
                            Logger(0, 'Successful ...', 'data', 'clear')
                            services.handler('init')
            if menu == 'vsettings':
                quest = vavooSettings()
                if not quest: Logger(3, 'Error!', 'vavoo', 'settings')
                elif quest == 'back': menu = 'vavoo'
            if menu == 'vavoo':
                item = vavooMenu()
                if item == 'back': menu = 'main'
                if item == 'get_list': services.handler('m3u8_start')
                if item == 'get_epg': services.handler('epg_start')
                if item == 'settings':
                    menu = 'vsettings'
                    quest = vavooSettings()
                    if not quest: Logger(3, 'Error!', 'vavoo', 'settings')
                    elif quest == 'back': menu = 'vavoo'
                if item == 'clean_db':
                    c = []
                    c.append((" ","0"))
                    c.append(("Yes","yes"))
                    c.append(("No", "no"))
                    c.append(("<= Back","back"))
                    q = [ inquirer.List("item", message="Really clean LiveTV Database?", choices=c, carousel=True) ]
                    quest = inquirer.prompt(q)
                    if quest['item'] == 'yes':
                        clean = common.clean_tables('live')
                        if not clean: Logger(3, 'Error!', 'db', 'clean')
                        else: Logger(0, 'Successful ...', 'db', 'clean')
            if menu == 'xstream':
                item = xstreamMenu()
                if item == 'settings':
                    quest = xstreamSettings()
                    if not quest: Logger(3, 'Error!', 'vod', 'settings')
                    else: Logger(1, 'Successful ...', 'vod', 'settings')
                if item == 'back': menu = 'main'
                if item == 'clean_db':
                    c = []
                    c.append((" ","0"))
                    c.append(("Yes","yes"))
                    c.append(("No", "no"))
                    c.append(("<= Back","back"))
                    q = [ inquirer.List("item", message="Really clean Stream Database?", choices=c, carousel=True) ]
                    quest = inquirer.prompt(q)
                    if quest['item'] == 'yes':
                        clean = common.clean_tables('streams')
                        if not clean: Logger(3, 'Error!', 'db', 'clean')
                        else: Logger(0, 'Successful ...', 'db', 'clean')
                if item == 'get_new':
                    st = int(time.time())
                    movies = xstream.getMovies()
                    if not movies: Logger(3, 'Error!', 'vod', 'get')
                    else: Logger(0, 'Successful ...', 'vod', 'get')
                    Logger(1, 'Completed in %s' % timedelta(seconds=int(time.time())-st), 'vod', 'get')
                if item == 'gen_lists':
                    lists = xstream.genLists()
                    if not lists: Logger(3, 'Error!', 'vod', 'gen')
                    else: Logger(0, 'Successful ...', 'vod', 'gen')
                if item == 'get_vod':
                    services.handler('xstream_start')
                if item == 'search':
                    quest = inquirer.prompt([inquirer.Text("item", message="Search for?")])
                    ser = xstream.search(quest['item'])
    except TypeError:
        Logger(0, "Quitting Now...")
        services.handler('kill')
        con.close()
