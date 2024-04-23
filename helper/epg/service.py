# -*- coding: utf-8 -*-
import time, os, json, re, socket, sys, importlib
from datetime import datetime
from collections import Counter
import utils.common as com
from helper.epg.lib import xml_structure
from helper.epg.providers import magenta_DE, tvspielfilm_DE


datapath = com.cp
temppath = os.path.join(datapath, "temp")
thread_temppath = os.path.join(temppath, "multithread")

## Read Global Settings
enable_rating_mapper = True
use_local_sock = False
tvh_local_sock = None
download_threads = int(10)
enable_multithread = True

## Get Enabled Grabbers
enabled_grabber = True

## Make a debug logger
def log(message, loglevel=None):
    print(message)


def check_channel_dupes():
    with open(guide_temp, encoding='utf-8') as f:
        c = Counter(c.strip() for c in f if c.strip())  # for case-insensitive search
        dupe = []
        for line in c:
            if c[line] > 1:
                if ('display-name' in line or 'icon src' in line or '</channel' in line):
                    pass
                else:
                    dupe.append(line + '\n')
        dupes = ''.join(dupe)

        if (not dupes == ''):
            log(dupes)
            return False
        else:
            return True


def run_grabber():
    if check_startup():
        importlib.reload(magenta_DE)
        importlib.reload(tvspielfilm_DE)
        xml_structure.xml_start()
        ## Check Provider , Create XML Channels
        print("epg_provider: " + str(com.get_setting('epg_provider', 'Vavoo')))
        if str(com.get_setting('epg_provider', 'Vavoo')) == 'm':
            if magenta_DE.startup():
                magenta_DE.create_xml_channels()
                magenta_DE.create_xml_broadcast(enable_rating_mapper, thread_temppath, download_threads)
        if str(com.get_setting('epg_provider', 'Vavoo')) == 't':
            if tvspielfilm_DE.startup():
                tvspielfilm_DE.create_xml_channels()
                tvspielfilm_DE.create_xml_broadcast(enable_rating_mapper, thread_temppath, download_threads)
        ## Finish XML
        xml_structure.xml_end()
        xml_structure.write_gz()
        return True
    return False


def check_startup():
    #Create Tempfolder if not exist
    if not os.path.exists(temppath):
        os.makedirs(temppath)
    if not os.path.exists(thread_temppath):
        os.makedirs(thread_temppath)
    return True


#if __name__ == '__main__':
