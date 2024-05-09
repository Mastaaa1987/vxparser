# -*- coding: utf-8 -*-
import json, os, sys, re, time, requests.cookies, requests.adapters, requests
from datetime import datetime, timedelta
from helper.epg.lib import xml_structure, channel_selector, mapper, filesplit
from utils.common import Logger as Logger
import utils.common as com

provider = 'TV SPIELFILM (DE)'
lang = 'de'

datapath = com.cp
temppath = os.path.join(datapath, "temp")
provider_temppath = os.path.join(temppath, "tvsDE")

## Enable Multithread
enable_multithread = True
if enable_multithread:
    try:
        from multiprocessing import Process
    except:
        pass

## MAPPING Variables Thx @ sunsettrack4
tvsDE_genres_url = 'https://raw.githubusercontent.com/sunsettrack4/config_files/master/tvs_genres.json'
tvsDE_genres_json = os.path.join(provider_temppath, 'tvs_genres.json')
tvsDE_channels_url = 'https://raw.githubusercontent.com/sunsettrack4/config_files/master/tvs_channels.json'
tvsDE_channels_json = os.path.join(provider_temppath, 'tvs_channels.json')

## Log Files
tvsDE_genres_warnings_tmp = os.path.join(provider_temppath, 'tvsDE_genres_warnings.txt')
tvsDE_genres_warnings = os.path.join(temppath, 'tvsDE_genres_warnings.txt')
tvsDE_channels_warnings_tmp = os.path.join(provider_temppath, 'tvsDE_channels_warnings.txt')
tvsDE_channels_warnings = os.path.join(temppath, 'tvsDE_channels_warnings.txt')

## Read tvsDE Settings
days_to_grab = int(com.get_setting('epg_grab', 'Main'))
episode_format = 'onscreen'
channel_format = 'provider' 
genre_format = 'provider'


# Make a debug logger
def log(message, loglevel=None):
    print(message)


# Calculate Date and Time
today = datetime.today()

## Channel Files
tvsDE_chlist_provider_tmp = os.path.join(provider_temppath, 'chlist_tvsDE_provider_tmp.json')
tvsDE_chlist_provider = os.path.join(provider_temppath, 'chlist_tvsDE_provider.json')
tvsDE_chlist_selected = os.path.join(datapath, 'chlist_tvsDE_selected.json')


tvsDE_header = {'Host': 'live.tvspielfilm.de',
                  'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0',
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                  'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
                  'Accept-Encoding': 'gzip, deflate, br',
                  'Connection': 'keep-alive',
                  'Upgrade-Insecure-Requests': '1'}

if not os.path.exists(provider_temppath):
    os.makedirs(provider_temppath)

def get_channellist():
    tvsDE_channellist_url = 'https://live.tvspielfilm.de/static/content/channel-list/livetv'
    tvsDE_chlist_url = requests.get(tvsDE_channellist_url, headers=tvsDE_header)
    tvsDE_chlist_url.raise_for_status()
    response = tvsDE_chlist_url.json()
    with open(tvsDE_chlist_provider_tmp, 'w', encoding='utf-8') as provider_list_tmp:
        json.dump(response, provider_list_tmp)

    #### Transform tvsDE_chlist_provider_tmp to Standard chlist Format as tvsDE_chlist_provider

    # Load Channellist from Provider
    with open(tvsDE_chlist_provider_tmp, 'r', encoding='utf-8') as provider_list_tmp:
        tvsDE_channels = json.load(provider_list_tmp)

    # Create empty new tvsDE_chlist_provider
    with open(tvsDE_chlist_provider, 'w', encoding='utf-8') as provider_list:
        provider_list.write(json.dumps({"channellist": []}))

    ch_title = ''

    # Load New Channellist from Provider
    with open(tvsDE_chlist_provider, encoding='utf-8') as provider_list:
        data = json.load(provider_list)

        temp = data['channellist']

        for channels in tvsDE_channels:
            ch_id = channels['id']
            ch_title = channels['name']
            try:
                hdimage = channels['image_large']['url']
            except:
                hdimage = ""
            # channel to be appended
            y = {"contentId": ch_id,
                 "name": ch_title,
                 "pictures": [{"href": hdimage}]}

            # appending channels to data['channellist']
            temp.append(y)

    #Save New Channellist from Provider
    with open(tvsDE_chlist_provider, 'w', encoding='utf-8') as provider_list:
        json.dump(data, provider_list, indent=4)
    #MyADD
    if not os.path.isfile(tvsDE_chlist_selected):
        with open((tvsDE_chlist_selected), 'w', encoding='utf-8') as selected_list:
            selected_list.write(json.dumps({"channellist": []}))
        
        ch_title = ''
        epg_channels = [] #"123.tv", "13th Street Universal", "3sat", "Animal Planet", "ANIXE", "ARD alpha", "ARTE", "Auto Motor Sport", "AXN", "Bibel TV", "Bloomberg Europe TV", "BR", "Cartoon Network", "Classica", "Comedy Central", "CRIME + INVESTIGATION", "Das Erste", "DAZN", "DELUXE MUSIC", "Deutsches Musik Fernsehen", "Discovery HD", "Disney Channel", "DMAX", "Eurosport 1", "Eurosport 2", "Fix &amp; Foxi", "Health TV", "Heimatkanal", "History HD", "HR", "HSE24", "Jukebox", "kabel eins", "kabel eins classics", "kabel eins Doku", "KiKA", "KinoweltTV", "K-TV", "MDR", "Motorvision TV", "MTV", "N24 Doku", "Nat Geo HD", "NAT GEO WILD", "NDR", "nick", "Nick Jr.", "Nicktoons", "NITRO", "n-tv", "ONE", "ORF 1", "ORF 2", "ORF III", "ORF SPORT +", "PHOENIX", "ProSieben", "ProSieben Fun", "ProSieben MAXX", "Romance TV", "RTL", "RTL Crime", "RTL II", "RTL Living", "RTL Passion", "RTLplus", "SAT.1", "SAT.1 emotions", "SAT.1 Gold", "ServusTV", "Silverline", "sixx", "Sky Action", "Sky Atlantic HD", "Sky Cinema Best Of", "Sky Cinema Classics", "Sky Cinema Fun", "Sky Cinema Premieren", "Sky Cinema Premieren +24", "Sky Cinema Special HD", "Sky Cinema Thriller", "Sky Family", "Sky Krimi", "Sky One", "Sony Channel", "Spiegel Geschichte", "Spiegel TV Wissen", "SUPER RTL", "SWR/SR", "Syfy", "tagesschau24", "Tele 5", "TLC", "TNT Comedy", "TNT Film", "TNT Serie", "TOGGO plus", "Universal Channel HD", "VOX", "VOXup", "WDR", "ZDF", "ZDFinfo", "ZDFneo" ]
        con = com.con3
        cur = con.cursor()
        for row in cur.execute('SELECT * FROM epgs ORDER BY id'):
            if not row["tid"] == None:
                epg_channels.append(row["tid"])

        with open(tvsDE_chlist_selected, encoding='utf-8') as selected_list:
            data = json.load(selected_list)

            temp = data['channellist']

            for channels in tvsDE_channels:
                if channels['id'] in epg_channels:
                    ch_id = channels['id']
                    ch_title = channels['name']
                    try:
                        hdimage = channels['image_large']['url']
                    except:
                        hdimage = ""
                    # channel to be appended
                    y = {"contentId": ch_id,
                        "name": ch_title,
                        "pictures": [{"href": hdimage}]}

                    # appending channels to data['channellist']
                    temp.append(y)

        with open(tvsDE_chlist_selected, 'w', encoding='utf-8') as selected_list:
            json.dump(data, selected_list, indent=4)


def select_channels():
    ## Create Provider Temppath if not exist
    if not os.path.exists(provider_temppath):
        os.makedirs(provider_temppath)

    ## Create empty (Selected) Channel List if not exist
    if not os.path.isfile(tvsDE_chlist_selected):
        with open((tvsDE_chlist_selected), 'w', encoding='utf-8') as selected_list:
            selected_list.write(json.dumps({"channellist": []}))

    ## Download chlist_tvsDE_provider.json
    get_channellist()
    dialog = xbmcgui.Dialog()

    with open(tvsDE_chlist_provider, 'r', encoding='utf-8') as o:
        provider_list = json.load(o)

    with open(tvsDE_chlist_selected, 'r', encoding='utf-8') as s:
        selected_list = json.load(s)

    ## Start Channel Selector
    user_select = channel_selector.select_channels(provider, provider_list, selected_list)

    if user_select is not None:
        with open(tvsDE_chlist_selected, 'w', encoding='utf-8') as f:
            json.dump(user_select, f, indent=4)
        if os.path.isfile(tvsDE_chlist_selected):
            valid = check_selected_list()
    else:
        valid = check_selected_list()


def check_selected_list():
    check = 'invalid'
    with open(tvsDE_chlist_selected, 'r', encoding='utf-8') as c:
        selected_list = json.load(c)
    for user_list in selected_list['channellist']:
        if 'contentId' in user_list:
            check = 'valid'
    if check == 'valid':
        return True
    else:
        return False

def download_multithread(thread_temppath, download_threads):
    # delete old broadcast files if exist
    for f in os.listdir(provider_temppath):
        if f.endswith('_broadcast.json'):
            os.remove(os.path.join(provider_temppath, f))

    list = os.path.join(provider_temppath, 'list.txt')
    splitname = os.path.join(thread_temppath, 'chlist_tvsDE_selected')

    with open(tvsDE_chlist_selected, 'r', encoding='utf-8') as s:
        selected_list = json.load(s)

    if filesplit.split_chlist_selected(thread_temppath, tvsDE_chlist_selected, splitname, download_threads, enable_multithread):
        multi = True
        needed_threads = sum([len(files) for r, d, files in os.walk(thread_temppath)])
        items_to_download = str(len(selected_list['channellist']))
        Logger(1, '%s Items to download ...' % items_to_download, 'epg')

        jobs = []
        for thread in range(0, int(needed_threads)):
            p = Process(target=download_thread, args=('{}_{}.json'.format(splitname, int(thread)), multi, list, ))
            jobs.append(p)
            p.start()
        for j in jobs:
            while j.is_alive():
                time.sleep(0.5)
                try:
                    last_line = ''
                    with open(list, 'r', encoding='utf-8') as f:
                        last_line = f.readlines()[-1]
                except:
                    pass
                items = sum(1 for f in os.listdir(provider_temppath) if f.endswith('_broadcast.json'))
                percent_remain = int(100) - int(items) * int(100) / int(items_to_download)
                percent_completed = int(100) * int(items) / int(items_to_download)
                if int(items) == int(items_to_download):
                    Logger(1, 'Download completed!', 'epg')
                    break
            j.join()
        for file in os.listdir(thread_temppath): os.remove(os.path.join(thread_temppath, file))

    else:
        multi = False
        download_thread(tvsDE_chlist_selected, multi, list)

def download_thread(tvsDE_chlist_selected, multi, list):
    requests.adapters.DEFAULT_RETRIES = 5

    with open(tvsDE_chlist_selected, 'r', encoding='utf-8') as s:
        selected_list = json.load(s)

    if not multi:
        items_to_download = str(len(selected_list['channellist']))

    for user_item in selected_list['channellist']:
        contentID = user_item['contentId']
        channel_name = user_item['name']
        broadcast_files = os.path.join(provider_temppath, '{}_broadcast.json'.format(contentID))

        ## Merge all selected Days in one Json file
        ## create empty broadcastfile
        with open(broadcast_files, 'w', encoding='utf-8') as playbill:
            playbill.write(json.dumps({"broadcasts": []}))

        ## Create a List with downloaded channels
        last_channel_name = '{}\n'.format(channel_name)
        with open(list, 'a', encoding='utf-8') as f:
            f.write(last_channel_name)

        ## open empty broadcastfile
        with open(broadcast_files, encoding='utf-8') as playbill:
            data = json.load(playbill)
            temp = data['broadcasts']

            day_to_start = datetime(today.year, today.month, today.day, hour=00, minute=00, second=1)

            for i in range(0, days_to_grab):
                day_to_grab = day_to_start.strftime("%Y-%m-%d")
                day_to_start += timedelta(days=1)
                tvs_data_url = 'https://live.tvspielfilm.de/static/broadcast/list/{}/{}'.format(contentID, day_to_grab)
                response = requests.get(tvs_data_url, headers=tvsDE_header)
                response.raise_for_status()
                tvs_data = response.json()
                temp.append(tvs_data)

        with open(broadcast_files, 'w', encoding='utf-8') as playbill:
            json.dump(data, playbill, indent=4)

        if not multi:
            items = sum(1 for f in os.listdir(provider_temppath) if f.endswith('_broadcast.json'))
            percent_remain = int(100) - int(items) * int(100) / int(items_to_download)
            percent_completed = int(100) * int(items) / int(items_to_download)
            pDialog.update(int(percent_completed), '{} {} '.format(loc(32500), channel_name), '{} {} {}'.format(int(percent_remain), loc(32501), provider))
            if int(items) == int(items_to_download):
                break
    if not multi:
        pDialog.close()

def create_xml_channels():
    if channel_format == 'rytec':
        ## Save tvsDE_channels.json to Disk
        tvsDE_channels_response = requests.get(tvsDE_channels_url).json()
        with open(tvsDE_channels_json, 'w', encoding='utf-8') as tvsDE_channels:
            json.dump(tvsDE_channels_response, tvsDE_channels)

    with open(tvsDE_chlist_selected, 'r', encoding='utf-8') as c:
        selected_list = json.load(c)

    items_to_download = str(len(selected_list['channellist']))
    items = 0
    ## Create XML Channels Provider information
    xml_structure.xml_channels_start(provider)
    xml_structure.xmltv_start()
    xml_structure.epg_start()

    #MyADD
    rytec = str(com.get_setting('epg_rytec', 'Vavoo'))
    if rytec == '1':
        epg_channels = {}
        con = com.con3
        cur = con.cursor()
        for row in cur.execute('SELECT * FROM epgs ORDER BY id'):
            if not row["tid"] == None and not row["tid"] == '':
                epg_channels[row["tid"]] = row["rid"]

    for user_item in selected_list['channellist']:
        items += 1
        percent_remain = int(100) - int(items) * int(100) / int(items_to_download)
        percent_completed = int(100) * int(items) / int(items_to_download)
        contentID = user_item['contentId']
        channel_name = user_item['name']
        channel_icon = user_item['pictures'][0]['href']
        channel_id = channel_name

        ## Map Channels
        if not channel_id == '':
            if rytec == '1':
                if contentID in epg_channels: 
                    channel_id = epg_channels[contentID]
                else: 
                    channel_id = mapper.map_channels(channel_id, channel_format, tvsDE_channels_json, tvsDE_channels_warnings_tmp, lang)
            else:
                channel_id = mapper.map_channels(channel_id, channel_format, tvsDE_channels_json, tvsDE_channels_warnings_tmp, lang)
        ## Create XML Channel Information with provided Variables
        xml_structure.xml_channels(channel_name, channel_id, channel_icon, lang)

        xml_structure.xmltv_channels(channel_name, channel_id, channel_icon, lang)


def create_xml_broadcast(enable_rating_mapper, thread_temppath, download_threads):
    download_multithread(thread_temppath, download_threads)

    if genre_format == 'eit':
        ## Save tvsDE_genres.json to Disk
        tvsDE_genres_response = requests.get(tvsDE_genres_url).json()
        with open(tvsDE_genres_json, 'w', encoding='utf-8') as tvsDE_genres:
            json.dump(tvsDE_genres_response, tvsDE_genres)

    with open(tvsDE_chlist_selected, 'r', encoding='utf-8') as c:
        selected_list = json.load(c)

    items_to_download = str(len(selected_list['channellist']))
    items = 0

    ## Create XML Broadcast Provider information
    xml_structure.xml_broadcast_start(provider)

    #MyADD
    rytec = str(com.get_setting('epg_rytec', 'Vavoo'))
    epg_channels = {}
    epg_ids = {}
    con = com.con3
    cur = con.cursor()
    for row in cur.execute('SELECT * FROM epgs ORDER BY id'):
        if not row["tid"] == None and not row["tid"] == '':
            epg_channels[row["tid"]] = row["rid"]
            epg_ids[row["tid"]] = row["id"]

    for user_item in selected_list['channellist']:
        items += 1
        percent_remain = int(100) - int(items) * int(100) / int(items_to_download)
        percent_completed = int(100) * int(items) / int(items_to_download)
        contentID = user_item['contentId']
        channel_name = user_item['name']
        channel_id = channel_name

        broadcast_files = os.path.join(provider_temppath, '{}_broadcast.json'.format(contentID))
        with open(broadcast_files, 'r', encoding='utf-8') as b:
            broadcastfiles = json.load(b)

        ### Map Channels
        if rytec == '1':
            if contentID in epg_channels:
                channel_id = epg_channels[contentID]
            elif not channel_id == '':
                channel_id = mapper.map_channels(channel_id, channel_format, tvsDE_channels_json, tvsDE_channels_warnings_tmp, lang)
        elif not channel_id == '':
            channel_id = mapper.map_channels(channel_id, channel_format, tvsDE_channels_json, tvsDE_channels_warnings_tmp, lang)

        if contentID in epg_ids: cid = epg_ids[contentID]
        else: cid = contentID

        try:
            for days in broadcastfiles['broadcasts']:
                for playbilllist in days:
                    try:
                        item_title = playbilllist['title']
                    except (KeyError, IndexError):
                        item_title = ''
                    try:
                        item_starttime = playbilllist['timestart']
                    except (KeyError, IndexError):
                        item_starttime = ''
                    try:
                        item_endtime = playbilllist['timeend']
                    except (KeyError, IndexError):
                        item_endtime = ''
                    try:
                        item_description = playbilllist['text']
                    except (KeyError, IndexError):
                        item_description = ''
                    try:
                        item_country = playbilllist['country']
                    except (KeyError, IndexError):
                        item_country = ''
                    try:
                        item_picture = playbilllist['images'][0]['size4']
                    except (KeyError, IndexError):
                        item_picture = ''
                    try:
                        item_subtitle = playbilllist['episodeTitle']
                    except (KeyError, IndexError):
                        item_subtitle = ''
                    try:
                        items_genre = playbilllist['genre']
                    except (KeyError, IndexError):
                        items_genre = ''
                    try:
                        item_date = playbilllist['year']
                    except (KeyError, IndexError):
                        item_date = ''
                    try:
                        item_season = playbilllist['seasonNumber']
                    except (KeyError, IndexError):
                        item_season = ''
                    try:
                        item_episode = playbilllist['episodeNumber']
                    except (KeyError, IndexError):
                        item_episode = ''
                    try:
                        item_agerating = playbilllist['fsk']
                    except (KeyError, IndexError):
                        item_agerating = ''
                    try:
                        items_director = playbilllist['director']
                    except (KeyError, IndexError):
                        items_director = ''
                    try:
                        actor_list = list()
                        keys_actor = playbilllist['actors']
                        for actor in keys_actor:
                            actor_list.append(list(actor.values())[0])
                        items_actor = ','.join(actor_list)
                    except (KeyError, IndexError):
                        items_actor = ''

                    # Transform items to Readable XML Format
                    item_starrating = ''
                    item_start = item_starttime
                    item_end = item_endtime
                    item_starttime = datetime.utcfromtimestamp(item_starttime).strftime('%Y%m%d%H%M%S')
                    item_endtime = datetime.utcfromtimestamp(item_endtime).strftime('%Y%m%d%H%M%S')

                    if not item_episode == '':
                        item_episode = re.sub(r"\D+", '#', item_episode).split('#')[0]
                    if not item_season == '':
                        item_season = re.sub(r"\D+", '#', item_season).split('#')[0]

                    items_producer = ''
                    if item_description == '':
                        item_description = 'No Program Information available'

                    # Map Genres
                    if not items_genre == '':
                        items_genre = mapper.map_genres(items_genre, genre_format, tvsDE_genres_json, tvsDE_genres_warnings_tmp, lang)

                    ## Create XML Broadcast Information with provided Variables
                    xml_structure.xml_broadcast(episode_format, channel_id, item_title, item_starttime, item_endtime,
                                                item_description, item_country, item_picture, item_subtitle,
                                                items_genre,
                                                item_date, item_season, item_episode, item_agerating, item_starrating, items_director,
                                                items_producer, items_actor, enable_rating_mapper, lang)

                    xml_structure.xmltv_broadcast(channel_id, item_title, item_starttime, item_endtime, item_description, lang, item_date, item_country, item_season, item_episode, item_agerating)

                    xml_structure.epg_broadcast(cid, item_title, item_date, item_start, item_end, item_description, lang, item_country, item_season, item_episode, item_agerating)
        except (KeyError, IndexError):
            print('Error!')

    
    xml_structure.xmltv_end()

    xml_structure.epg_end()
    
    ## Create Channel Warnings Textile
    channel_pull = '\nPlease Create an Pull Request for Missing Rytec Id´s to https://github.com/sunsettrack4/config_files/blob/master/tvs_channels.json\n'
    mapper.create_channel_warnings(tvsDE_channels_warnings_tmp, tvsDE_channels_warnings, provider, channel_pull)

    ## Create Genre Warnings Textfile
    genre_pull = '\nPlease Create an Pull Request for Missing EIT Genres to https://github.com/sunsettrack4/config_files/blob/master/tvs_genres.json\n'
    mapper.create_genre_warnings(tvsDE_genres_warnings_tmp, tvsDE_genres_warnings, provider, genre_pull)

    ## Delete old Tempfiles, not needed any more
    for file in os.listdir(provider_temppath): os.remove(os.path.join(provider_temppath, file))


def check_provider():
    ## Create Provider Temppath if not exist
    if not os.path.exists(provider_temppath):
        os.makedirs(provider_temppath)

    ## Create empty (Selected) Channel List if not exist
    if not os.path.isfile(tvsDE_chlist_selected):
        #with open((tvsDE_chlist_selected), 'w', encoding='utf-8') as selected_list:
            #selected_list.write(json.dumps({"channellist": []}))
        #return False
        get_channellist()

    ## If a Selected list exist, check valid
    valid = check_selected_list()
    if valid is False:
        return False
    return True

def startup():
    if check_provider():
        get_channellist()
        return True
    else:
        return False

# Channel Selector
try:
    if sys.argv[1] == 'select_channels_tvsDE':
        select_channels()
except IndexError:
    pass
