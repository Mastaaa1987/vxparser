import time, os, json, re, sys
from multiprocessing import Process
from datetime import timedelta
#from threading import Thread as Process
from uvicorn import Server, Config

from utils.common import Logger as Log

import utils.common as com
import utils.vavoo as vavoo
import utils.xstream as xstream
from helper.epg import service as epg
from api import UvicornServer
from kivy.utils import platform
from kivy.logger import Logger
from oscpy.server import OSCThreadServer
#if None:
if platform == 'android':
    from jnius import autoclass
    PythonService = autoclass('org.kivy.android.PythonService')
    PythonService.mService.setAutoRestartService(True)

cachepath = com.cp
jobs = xstream.jobs
proc = {}
proc['api'] = proc['m3u8'] = proc['epg'] = proc['m3u8_p'] = proc['epg_p'] = proc['search'] = proc['xstream_p'] = None
procs = [ 'm3u8', 'epg', 'm3u8_p', 'epg_p', 'search' ]

sPort = int(com.get_setting('osc_port'))
CLIENT = com.get_osc_client('localhost', sPort)
stopped = False


def Logger2(lvl, msg, name=None, typ=None):
    if int(lvl) == 0:
        if name and typ:
            Send(b'/echo', msg, name, typ)
        elif name:
            Send(b'/echo', msg, name)
        elif typ:
            Send(b'/echo', msg, typ)
        else:
            Send(b'/echo', msg)
        return
    if name and typ:
        Send(b'/log', str(lvl), msg, name, typ)
    elif name:
        Send(b'/log', str(lvl), msg, name)
    elif typ:
        Send(b'/log', str(lvl), msg, typ)
    else:
        Send(b'/log', str(lvl), msg)


def handler(typ, name=None):
    if typ == 'init':
        if not proc['api']:
            ip = str(com.get_setting('server_host', 'Main'))
            port = int(com.get_setting('server_port', 'Main'))
            proc['api'] = UvicornServer(config=Config("api:app", host=ip, port=port, log_level="info", reload=True))
            proc['api'].start()
            Log(1, 'Successful started ...', 'api', 'service')
        elif proc['api']: Log(1, 'Service allready running ...', 'api', 'service')
        if not proc['m3u8'] and bool(int(com.get_setting('m3u8_service', 'Main'))) == True:
            proc['m3u8'] = Process(target=loop_m3u8)
            proc['m3u8'].start()
            Log(1, 'Successful started ...', 'm3u8', 'service')
        elif proc['m3u8']: Log(1, 'Service allready running ...', 'm3u8', 'service')
        elif bool(int(com.get_setting('m3u8_service', 'Main'))) == False: Log(1, 'Service disabled ...', 'm3u8', 'service')
        if not proc['epg'] and bool(int(com.get_setting('epg_service', 'Main'))) == True:
            proc['epg'] = Process(target=loop_epg)
            proc['epg'].start()
            Log(1, 'Successful started ...', 'epg', 'service')
        elif proc['epg']: Log(1, 'Service allready running ...', 'epg', 'service')
        elif bool(int(com.get_setting('epg_service', 'Main'))) == False: Log(1, 'Service disabled ...', 'epg', 'service')
    if typ == 'kill':
        for p in procs:
            if proc[p]:
                proc[p].join(timeout=0)
                if proc[p].is_alive():
                    if '_p' in p: Log(1, 'terminate ...', re.sub('_p', '', p), 'process')
                    else: Log(1, 'terminate ...', p, 'service')
                    proc[p].terminate()
                    proc[p] = None
        if len(jobs) > 0:
            for job in jobs:
                job.join(timeout=0)
                if job.is_alive():
                    Log(1, 'terminate ...', 'process', 'jobs')
                    job.terminate()
                    job = None
        if proc['api']:
            Log(1, 'terminate ...', 'api', 'service')
            proc['api'].stop()
            proc['api'] = None
    if typ == 'service_stop':
        if proc['m3u8']:
            proc['m3u8'].join(timeout=0)
            if proc['m3u8'].is_alive():
                Log(1, 'terminate ...', 'm3u8', 'service')
                proc['m3u8'].terminate()
                proc['m3u8'] = None
            else: Log(1, 'not running ...', 'm3u8', 'service')
        else: Log(1, 'not running ...', 'm3u8', 'service')
        if proc['epg']:
            proc['epg'].join(timeout=0)
            if proc['epg'].is_alive():
                Log(1, 'terminate ...', 'epg', 'service')
                proc['epg'].terminate()
                proc['epg'] = None
            else: Log(1, 'not running ...', 'epg', 'service')
        else: Log(1, 'not running ...', 'epg', 'service')
    if typ == 'service_restart':
        if bool(int(com.get_setting('m3u8_service', 'Main'))) == True:
            if proc['m3u8']:
                proc['m3u8'].join(timeout=0)
                if proc['m3u8'].is_alive():
                    Log(1, 'terminate ...', 'm3u8', 'service')
                    proc['m3u8'].terminate()
                    proc['m3u8'] = None
            proc['m3u8'] = Process(target=loop_m3u8)
            proc['m3u8'].start()
            Log(1, 'Successful started ...', 'm3u8', 'service')
        else: Log(1, 'Service disabled ...', 'm3u8', 'service')
        if bool(int(com.get_setting('epg_service', 'Main'))) == True:
            if proc['epg']:
                proc['epg'].join(timeout=0)
                if proc['epg'].is_alive():
                    Log(1, 'terminate ...', 'epg', 'service')
                    proc['epg'].terminate()
                    proc['epg'] = None
            proc['epg'] = Process(target=loop_epg)
            proc['epg'].start()
            Log(1, 'Successful started ...', 'epg', 'service')
        else: Log(1, 'Service disabled ...', 'epg', 'service')
    if typ == 'epg_start':
        if proc['epg_p']:
            proc['epg_p'].join(timeout=0)
            if proc['epg_p'].is_alive():
                Log(1, 'terminate ...', 'epg', 'process')
                proc['epg_p'].terminate()
                proc['epg_p'] = None
        proc['epg_p'] = Process(target=epg.run_grabber)
        proc['epg_p'].start()
        Log(1, 'Successful started ...', 'epg', 'process')
    if typ == 'm3u8_start':
        if proc['m3u8_p']:
            proc['m3u8_p'].join(timeout=0)
            if proc['m3u8_p'].is_alive():
                Log(1, 'terminate ...', 'm3u8', 'process')
                proc['m3u8_p'].terminate()
                proc['m3u8_p'] = None
        proc['m3u8_p'] = Process(target=vavoo.sky_m3u8)
        proc['m3u8_p'].start()
        Log(1, 'Successful started ...', 'm3u8', 'process')
    if typ == 'api_start':
        if proc['api']:
            proc['api'].join(timeout=0)
            if proc['api'].is_alive():
                Log(1, 'Allready running ...', 'api', 'service')
            else:
                ip = str(com.get_setting('server_host', 'Main'))
                port = int(com.get_setting('server_port', 'Main'))
                proc['api'] = UvicornServer(config=Config("api:app", host=ip, port=port, log_level="info", reload=True))
                proc['api'].start()
                Log(1, 'Successful started ...', 'api', 'service')
        else:
            ip = str(com.get_setting('server_host', 'Main'))
            port = int(com.get_setting('server_port', 'Main'))
            proc['api'] = UvicornServer(config=Config("api:app", host=ip, port=port, log_level="info", reload=True))
            proc['api'].start()
            Log(1, 'Successful started ...', 'api', 'service')
    if typ == 'xstream_start':
        if proc['xstream_p']:
            proc['xstream_p'].join(timeout=0)
            if proc['xstream_p'].is_alive():
                Log(1, 'terminate ...', 'vods', 'process')
                proc['xstream_p'].terminate()
                proc['xstream_p'] = None
        proc['xstream_p'] = Process(target=xstream.vod_m3u8)
        proc['xstream_p'].start()
        Log(1, 'Successful started ...', 'vods', 'process')
    if typ == 'epg_stop':
        if proc['epg_p']:
            proc['epg_p'].join(timeout=0)
            if proc['epg_p'].is_alive():
                Log(1, 'terminate ...', 'epg', 'process')
                proc['epg_p'].terminate()
                proc['epg_p'] = None
        else: Log(1, 'Allready stopped ...', 'epg', 'process')
    if typ == 'm3u8_stop':
        if proc['m3u8_p']:
            proc['m3u8_p'].join(timeout=0)
            if proc['m3u8_p'].is_alive():
                Log(1, 'terminate ...', 'm3u8', 'process')
                proc['m3u8_p'].terminate()
                proc['m3u8_p'] = None
        else: Log(1, 'Allready stopped ...', 'm3u8', 'process')
    if typ == 'xstream_stop':
        if proc['xstream_p']:
            proc['xstream_p'].join(timeout=0)
            if proc['xstream_p'].is_alive():
                Log(1, 'terminate ...', 'vods', 'process')
                proc['xstream_p'].terminate()
                proc['xstream_p'] = None
        else: Log(1, 'Allready stopped ...', 'vods', 'process')
    if typ == 'api_stop':
        if proc['api']:
            proc['api'].join(timeout=0)
            if proc['api'].is_alive():
                Log(1, 'stopping ...', 'api', 'service')
                proc['api'].stop()
                proc['api'] = None
                Log(1, 'Stopped ...', 'api', 'service')
        else: Log(1, 'Allready stopped ...', 'api', 'service')
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
            Log(1, 'sleeping for %s ...' % timedelta(seconds=int(last + sleep * 60 * 60 - now)), 'm3u8', 'service')
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
            Log(1, 'sleeping for %s ...' % timedelta(seconds=int(last + sleep * 24 * 60 * 60 - now)), 'epg', 'service')
            time.sleep(int(last + sleep * 24 * 60 * 60 - now))
    pass


def set_auto_restart_service(restart=True,restart2=False):
    from jnius import autoclass
    Service = autoclass('org.kivy.android.PythonService').mService
    Service.setAutoRestartService(restart)
    Service.stopForeground(restart2)


def Send(type, *values):
    val = []
    for v in values:
        val.append(v.encode('utf8'))
    CLIENT.send_message(type, val)


def reg(key, val=None):
    handler(key.decode('utf8'))


def recieve_kill(*values):
    global stopped
    handler('kill')
    stopped = True


def recieve_search(val=None, *args):
    if val:
        proc['search'] = Process(target=xstream.search, args=(val.decode('utf8'),))
        proc['search'].start()


def service():
    global stopped
    SERVER = OSCThreadServer()
    SERVER.listen('localhost', default=True)
    SERVER.bind(b'/kill', recieve_kill)
    SERVER.bind(b'/search', recieve_search)
    SERVER.bind(b'/reg', reg)
    handler('init')
    Send(b'/reg', str(SERVER.getaddress()[1]))
    #if None:
    if platform == 'android':
        set_auto_restart_service()
    while True:
        time.sleep(1)
        if stopped:
            break
    Logger.info('terminate_service_layer ...')
    #if None:
    if platform == 'android':
        set_auto_restart_service(False, True)
    SERVER.terminate_server()
    time.sleep(0.1)
    SERVER.close()

if __name__ == '__main__':
    service()
