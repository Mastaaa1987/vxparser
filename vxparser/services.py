import time, os, json, re
from multiprocessing import Process
from uvicorn import Server, Config

from utils.common import Logger as Logger
import utils.common as com
import utils.vavoo as vavoo
import utils.xstream as xstream
from helper.epg import service as epg
from api import UvicornServer

cachepath = com.cp
jobs = []
proc = {}
proc['api'] = proc['m3u8'] = proc['epg'] = proc['m3u8_p'] = proc['epg_p'] = proc['xstream_p'] = None
procs = [ 'm3u8', 'epg', 'm3u8_p', 'epg_p' ]


def handler(typ, name=None):
    if typ == 'init':
        if not proc['api']:
            ip = str(com.get_setting('server_host', 'Main'))
            port = int(com.get_setting('server_port', 'Main'))
            proc['api'] = UvicornServer(config=Config("api:app", host=ip, port=port, log_level="info", reload=True))
            proc['api'].start()
            Logger(1, 'Successful started ...', 'api', 'service')
        elif proc['api']: Logger(1, 'Service allready running ...', 'api', 'service')
        if not proc['m3u8'] and bool(int(com.get_setting('m3u8_service', 'Main'))) == True:
            proc['m3u8'] = Process(target=loop_m3u8)
            proc['m3u8'].start()
            Logger(1, 'Successful started ...', 'm3u8', 'service')
        elif proc['m3u8']: Logger(1, 'Service allready running ...', 'm3u8', 'service')
        elif bool(int(com.get_setting('m3u8_service', 'Main'))) == False: Logger(1, 'Service disabled ...', 'm3u8', 'service')
        if not proc['epg'] and bool(int(com.get_setting('epg_service', 'Main'))) == True:
            proc['epg'] = Process(target=loop_epg)
            proc['epg'].start()
            Logger(1, 'Successful started ...', 'epg', 'service')
        elif proc['epg']: Logger(1, 'Service allready running ...', 'epg', 'service')
        elif bool(int(com.get_setting('epg_service', 'Main'))) == False: Logger(1, 'Service disabled ...', 'epg', 'service')
    if typ == 'kill':
        for p in procs:
            if proc[p]:
                proc[p].join(timeout=0)
                if proc[p].is_alive():
                    if '_p' in p: Logger(1, 'terminate ...', re.sub('_p', '', p), 'process')
                    else: Logger(1, 'terminate ...', p, 'service')
                    proc[p].terminate()
                    proc[p] = None
        if len(jobs) > 0:
            for job in jobs:
                job.join(timeout=0)
                if job.is_alive():
                    Logger(1, 'terminate ...', 'process', 'jobs')
                    job.terminate()
                    job = None
        if proc['api']:
            Logger(1, 'terminate ...', 'api', 'service')
            proc['api'].stop()
            proc['api'] = None
    if typ == 'service_stop':
        if proc['m3u8']:
            proc['m3u8'].join(timeout=0)
            if proc['m3u8'].is_alive():
                Logger(1, 'terminate ...', 'm3u8', 'service')
                proc['m3u8'].terminate()
                proc['m3u8'] = None
            else: Logger(1, 'not running ...', 'm3u8', 'service')
        else: Logger(1, 'not running ...', 'm3u8', 'service')
        if proc['epg']:
            proc['epg'].join(timeout=0)
            if proc['epg'].is_alive():
                Logger(1, 'terminate ...', 'epg', 'service')
                proc['epg'].terminate()
                proc['epg'] = None
            else: Logger(1, 'not running ...', 'epg', 'service')
        else: Logger(1, 'not running ...', 'epg', 'service')
    if typ == 'service_restart':
        if bool(int(com.get_setting('m3u8_service', 'Main'))) == True:
            if proc['m3u8']:
                proc['m3u8'].join(timeout=0)
                if proc['m3u8'].is_alive():
                    Logger(1, 'terminate ...', 'm3u8', 'service')
                    proc['m3u8'].terminate()
                    proc['m3u8'] = None
            proc['m3u8'] = Process(target=loop_m3u8)
            proc['m3u8'].start()
            Logger(1, 'Successful started ...', 'm3u8', 'service')
        else: Logger(1, 'Service disabled ...', 'm3u8', 'service')
        if bool(int(com.get_setting('epg_service', 'Main'))) == True:
            if proc['epg']:
                proc['epg'].join(timeout=0)
                if proc['epg'].is_alive():
                    Logger(1, 'terminate ...', 'epg', 'service')
                    proc['epg'].terminate()
                    proc['epg'] = None
            proc['epg'] = Process(target=loop_epg)
            proc['epg'].start()
            Logger(1, 'Successful started ...', 'epg', 'service')
        else: Logger(1, 'Service disabled ...', 'epg', 'service')
    if typ == 'epg_start':
        if proc['epg_p']:
            proc['epg_p'].join(timeout=0)
            if proc['epg_p'].is_alive():
                Logger(1, 'terminate ...', 'epg', 'process')
                proc['epg_p'].terminate()
                proc['epg_p'] = None
        proc['epg_p'] = Process(target=epg.run_grabber)
        proc['epg_p'].start()
        Logger(1, 'Successful started ...', 'epg', 'process')
    if typ == 'm3u8_start':
        if proc['m3u8_p']:
            proc['m3u8_p'].join(timeout=0)
            if proc['m3u8_p'].is_alive():
                Logger(1, 'terminate ...', 'm3u8', 'process')
                proc['m3u8_p'].terminate()
                proc['m3u8_p'] = None
        proc['m3u8_p'] = Process(target=vavoo.sky_m3u8)
        proc['m3u8_p'].start()
        Logger(1, 'Successful started ...', 'm3u8', 'process')
    if typ == 'xstream_start':
        if proc['xstream_p']:
            proc['xstream_p'].join(timeout=0)
            if proc['xstream_p'].is_alive():
                Logger(1, 'terminate ...', 'vods', 'process')
                proc['xstream_p'].terminate()
                proc['xstream_p'] = None
        proc['xstream_p'] = Process(target=xstream.vod_m3u8)
        proc['xstream_p'].start()
        Logger(1, 'Successful started ...', 'vods', 'process')
    return


def loop_m3u8():
    while True:
        now = int(time.time())
        last = int(com.get_setting('m3u8', 'Loop'))
        sleep = int(com.get_setting('m3u8_sleep', 'Main'))
        if now > last + sleep * 60 * 60:
            vavoo.sky_m3u8()
            com.set_setting('m3u8', str(now), 'Loop')
        else:
            Logger(1, 'sleeping for %s sec...' % str(last + sleep * 60 * 60 - now), 'm3u8', 'service')
            time.sleep(int(last + sleep * 60 * 60 - now))
    pass


def loop_epg():
    while True:
        sleep = int(com.get_setting('epg_sleep', 'Main'))
        now = int(time.time())
        last = int(com.get_setting('epg', 'Loop'))
        if now > last + sleep * 24 * 60 * 60:
            epg.run_grabber()
            com.set_setting('epg', str(now), 'Loop')
        else:
            Logger(1, 'sleeping for %s sec...' % str(last + sleep * 24 * 60 * 60 - now), 'epg', 'service')
            time.sleep(int(last + sleep * 24 * 60 * 60 - now))
    pass

