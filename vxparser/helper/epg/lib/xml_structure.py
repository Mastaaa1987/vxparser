# -*- coding: utf-8 -*-
import os, gzip, shutil, base64, time, sqlite3
from datetime import datetime, timedelta
from helper.epg.lib import mapper
from utils.common import Logger as Logger
import utils.common as com

datapath = com.cp
listpath = com.lp
temppath = os.path.join(com.cp, "temp")
con = com.con3

unicode = str

now = datetime.now()
guide_temp = os.path.join(datapath, 'epg.xml')
xmltv_temp = os.path.join(datapath, 'xmltv.xml')
guide_dest = os.path.join(listpath, 'epg.xml.gz')


def epg_start():
    cur = con.cursor()
    cur.execute('DELETE FROM epg')
    con.commit()


def epg_broadcast(cid, item_title, item_date, item_start, item_end, item_description, lang, item_country, item_season, item_episode, item_agerating):
    cur = con.cursor()
    desc = ''
    if not item_country == '':
        desc = desc + '(%s) ' % item_country
    if not item_date == '':
        desc = desc + '%s ' % item_date
    if not item_season == '':
        desc = desc + '• S%s ' % item_season
    if not item_episode == '':
        desc = desc + 'E%s ' % item_episode
    if not item_agerating == '':
        desc = desc + '• FSK %s' % item_agerating
    if not item_description == '':
        desc = desc + '\n        %s' % item_description
        desc = base64.b64encode(str(desc).encode('utf-8')).decode('utf-8')
    else: desc = ''
    if not item_title == '': title = base64.b64encode(str(item_title).encode('utf-8')).decode('utf-8')
    else: title = ''

    if not item_title == '' and not desc == '':
        cur.execute('INSERT INTO epg VALUES (NULL,"'+str(cid)+'","'+str(item_start)+'","'+str(item_end)+'","'+str(title)+'","'+str(desc)+'","'+str(lang)+'")')


def epg_end():
    con.commit()


def xmltv_start():
    if os.path.exists(xmltv_temp):
        os.remove(xmltv_temp)
    ret = []
    ret.append('<?xml version="1.0" encoding="utf-8" ?>')
    ret.append('<!DOCTYPE tv SYSTEM "http://www.example.org/xmltv.dtd">')
    ret.append('<tv generator-info-name="Xtream Codes" generator-info-url="http://www.example.org">')
    start = ''.join(ret)
    with open(xmltv_temp, 'w', encoding='utf-8') as f:
        f.write(start)


def xmltv_channels(channel_name, channel_id, channel_icon, lang):
    ret = []
    ret.append('<channel id="%s">' % channel_id)
    ret.append('<display-name>%s</display-name>' % channel_name)
    ret.append('<icon src="%s" />' % channel_icon)
    ret.append('</channel>')
    s = ''.join(ret).replace('&', '&amp;')
    with open(xmltv_temp, 'a', encoding='utf-8') as f:
        f.write(s)


def xmltv_broadcast(channel_id, item_title, item_starttime, item_endtime, item_description, lang, item_date, item_country, item_season, item_episode, item_agerating):
    ret = []
    desc = ''
    if not item_country == '':
        desc = desc + '%s ' % item_country
    if not item_date == '':
        desc = desc + '%s ' % item_date
    if not item_season == '':
        desc = desc + 'S%s ' % item_season
    if not item_episode == '':
        desc = desc + 'E%s ' % item_episode
    if not item_agerating == '':
        desc = desc + 'FSK %s' % item_agerating
    if not item_description == '':
        desc = desc + '\n        %s' % item_description.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    else: desc = ''

    if not item_title == '': item_title = item_title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    ret.append('<programme start="{} +0000" stop="{} +0000" channel="{}">'.format(item_starttime, item_endtime, channel_id))
    ret.append('<title lang="de">{}</title>'.format(item_title))
    ret.append('<desc  lang="de">{}</desc>'.format(desc))
    ret.append('</programme>')
    s = ''.join(ret)
    with open(xmltv_temp, 'a', encoding='utf-8') as f:
        f.write(s)


def xmltv_end():
    ret = []
    ret.append('</tv>')
    s = ''.join(ret)
    with open(xmltv_temp, 'a', encoding='utf-8') as f:
        f.write(s)


def write_gz():
    if os.path.exists(guide_temp):
        if os.path.exists(guide_dest):
            os.remove(guide_dest)
        with open(guide_temp, 'rb') as f_in:
            with gzip.open(guide_dest, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        if os.path.exists(guide_dest):
            Logger(0, 'epg.xml.gz successful created!', 'epg')
        return True
    return False


def xml_start():
    copyright = '<?xml version="1.0" encoding="UTF-8" ?>\n<tv>\n'
    with open(guide_temp, 'w', encoding='utf-8') as f:
        f.write(copyright)


def xml_channels_start(provider):
    start = '\n<!--  {}  CHANNEL LIST -->\n'.format(provider)
    with open(guide_temp, 'a', encoding='utf-8') as f:
        f.write(start)


def xml_channels(channel_name, channel_id, channel_icon, lang):
    channels = []
    channels.append('    <channel id="{}">\n'.format(channel_id))
    channels.append('        <display-name lang="{}">{}</display-name>\n'.format(lang, channel_name))
    channels.append('        <icon src="{}" />\n'.format(channel_icon))
    channels.append('    </channel>\n')
    s = ''.join(channels).replace('&', '&amp;')
    with open(guide_temp, 'a', encoding='utf-8') as f:
        f.write(s)


def xml_broadcast_start(provider):
    start = '\n<!--  {}  PROGRAMME LIST -->'.format(provider)
    with open(guide_temp, 'a', encoding='utf-8') as f:
        f.write(start)


def xml_broadcast(episode_format, channel_id, item_title, item_starttime, item_endtime, item_description, item_country, item_picture, item_subtitle, items_genre, item_date, item_season, item_episode, item_agerating, item_starrating, items_director, items_producer, items_actor, enable_rating_mapper, lang):
    guide = []
    guide.append('\n')

    if (not item_starttime == '' and not item_endtime == '' and not item_title == ''):
        ## Programme Condition
        if (not item_starttime == '' and not item_endtime == ''):
            channel_id = channel_id.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            guide.append('    <programme start="{} +0000" stop="{} +0000" channel="{}">\n'.format(item_starttime, item_endtime, channel_id))

        ## Map Imdb Stars
        if not item_starrating == '':
            stars = mapper.map_stars(item_starrating)
        else:
            stars = ''

        ## TITLE Condition
        if not item_title == '':
            item_title = item_title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            guide.append('        <title lang="{}">{}</title>\n'.format(lang, item_title))

        ## SUBTITLE Condition
        if not item_subtitle == '':
            item_subtitle = item_subtitle.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            guide.append('        <sub-title lang="{}">{}</sub-title>\n'.format(lang, item_subtitle))

        ## DESCRIPTION Condition
        if not item_description == '':
            item_description = item_description.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '\n        ')
            if enable_rating_mapper == False:
                guide.append('        <desc lang="{}">{}</desc>\n'.format(lang, item_description))

            ## Rating Mapper
            elif enable_rating_mapper == True:
                country = '' if item_country == '' else '({})'.format(item_country)
                date = '' if item_date == '' else '{}'.format(item_date)
                season = '' if item_season == '' else '• S{}'.format(item_season)
                episode = '' if item_episode == '' else 'E{}'.format(item_episode)
                fsk = '' if item_agerating == '' else '• FSK {}'.format(item_agerating)
                imdbstars = '' if stars == '' else '{}'.format(stars)
                desc = '<desc lang="{}">{} {} {} {} {} {}'.format(lang, country, date, season, episode, fsk, imdbstars)
                guide.append('        {}\n        {}</desc>\n'.format(' '.join(desc.split()), item_description))

        ## CAST Condition
        if not items_producer == '':
            items_producer = items_producer.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        producerlist = items_producer.split(',')
        if not items_director == '':
            items_director = items_director.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        directorlist = items_director.split(',')
        if not items_actor == '':
            items_actor = items_actor.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        actorlist = items_actor.split(',')
        # Complete
        if (not items_director == '' and not items_producer == '' and not items_actor == ''):
            guide.append('        <credits>\n')
            for director in directorlist:
                guide.append('            <director>{}</director>\n'.format(director))
            for actor in actorlist:
                guide.append('            <actor>{}</actor>\n'.format(actor))
            for producer in producerlist:
                guide.append('            <producer>{}</producer>\n'.format(producer))
            guide.append('        </credits>\n')
        # Producer + Director
        elif (not items_director == '' and not items_producer == '' and items_actor == ''):
            guide.append('        <credits>' + '\n')
            for director in directorlist:
                guide.append('            <director>{}</director>\n'.format(director))
            for producer in producerlist:
                guide.append('            <producer>{}</producer>\n'.format(producer))
            guide.append('       </credits>\n')
        # Director + Actor
        elif (not items_director == '' and items_producer == '' and not items_actor == ''):
            guide.append('        <credits>\n')
            for director in directorlist:
                guide.append('            <director>{}</director>\n'.format(director))
            for actor in actorlist:
                guide.append('            <actor>{}</actor>\n'.format(actor))
            guide.append('        </credits>\n')
        # Producer + Actor
        elif (items_director == '' and not items_producer == '' and not items_actor == ''):
            guide.append('        <credits>\n')
            for actor in actorlist:
                guide.append('            <actor>{}</actor>\n'.format(actor))
            for producer in producerlist:
                guide.append('            <producer>{}</producer>\n'.format(producer))
            guide.append('        </credits>\n')
        # Only Director
        elif (not items_director == '' and items_producer == '' and items_actor == ''):
            guide.append('        <credits>\n')
            for director in directorlist:
                guide.append('            <director>{}</director>\n'.format(director))
            guide.append('        </credits>\n')
        # Only Producer
        if (items_director == '' and not items_producer == '' and items_actor == ''):
            guide.append('        <credits>\n')
            for producer in producerlist:
                guide.append('            <producer>{}</producer>\n'.format(producer))
            guide.append('        </credits>\n')
        # Only Actor
        if (items_director == '' and items_producer == '' and not items_actor == ''):
            guide.append('        <credits>\n')
            for actor in actorlist:
                guide.append('            <actor>{}</actor>\n'.format(actor))
            guide.append('        </credits>\n')

        ## DATE Condition
        if not item_date == '':
            guide.append('        <date>{}</date>\n'.format(item_date))

        ## GENRE Condition
        if not items_genre == '':
            items_genre = items_genre.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            genrelist = items_genre.split(',')
            for genre in genrelist:
                guide.append('        <category lang="{}">{}</category>\n'.format(lang, genre))


        ## IMAGE Condition
        if not item_picture == '':
            guide.append('        <icon src="{}"/>\n'.format(item_picture))

        ## COUNTRY Condition
        if not item_country == '':
            item_country = item_country.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            guide.append('        <country>{}</country>\n'.format(item_country))

        ## EPISODE Condition
        # XMLTV_NS
        if episode_format == 'xmltv_ns':
            if (not item_season == '' and not item_episode == ''):
                item_season_ns = int(item_season) - int(1)
                item_episode_ns = int(item_episode) - int(1)
                guide.append('        <episode-num system="xmltv_ns">{} . {} . </episode-num>\n'.format(str(item_season_ns),str(item_episode_ns)))
            elif (not item_season == '' and item_episode == ''):
                item_season_ns = int(item_season) - int(1)
                guide.append('        <episode-num system="xmltv_ns">{} . 0 . </episode-num>\n'.format(str(item_season_ns)))
            elif (item_season == '' and not item_episode == ''):
                item_episode_ns = int(item_episode) - int(1)
                guide.append('        <episode-num system="xmltv_ns">0 . {} . </episode-num>\n'.format(str(item_episode_ns)))
        # ONSCREEN
        elif episode_format == 'onscreen':
            if (not item_season == '' and not item_episode == ''):
                guide.append('        <episode-num system="onscreen">S{} E{}</episode-num>\n'.format(item_season, item_episode))
            elif (not item_season == '' and item_episode == ''):
                guide.append('        <episode-num system="onscreen">S{}</episode-num>\n'.format(item_season))
            elif (item_season == '' and not item_episode == ''):
                guide.append('        <episode-num system="onscreen">E{}</episode-num>\n'.format(item_episode))

        ## AGE-RATING Condition
        if (not item_agerating == ''):
            guide.append('        <rating>\n')
            guide.append('            <value>{}</value>\n'.format(item_agerating))
            guide.append('        </rating>\n')

        ## STAR-RATING Condition
        if (not item_starrating == ''):
            item_starrating = int(item_starrating) / int(10)
            guide.append('        <star-rating system="IMDb">\n')
            guide.append('            <value>{}/10</value>\n'.format(item_starrating))
            guide.append('        </star-rating>\n')

        guide.append('    </programme>\n')
        s = ''.join(guide)
        with open(guide_temp, 'a', encoding='utf-8') as f:
            f.write(s)


def xml_end():
    end = '\n</tv>\n'
    with open(guide_temp, 'a', encoding='utf-8') as f:
        f.write(end)
