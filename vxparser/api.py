import time, os, sys, signal, asyncio, uvicorn, re
from concurrent.futures import ProcessPoolExecutor
from typing import Union
from typing_extensions import Annotated
from notifications_android_tv import Notifications

from uvicorn import Server, Config
from fastapi import FastAPI, HTTPException, Request, Response, Body, Form
from fastapi.responses import JSONResponse, StreamingResponse, RedirectResponse, FileResponse, HTMLResponse, PlainTextResponse
from contextlib import asynccontextmanager
from typing import AsyncIterator
from pydantic import BaseModel
from multiprocessing import Process
#from threading import Thread as Process

import utils.common as common
from utils.common import Logger as Logger
import utils.xstream as xstream
import utils.vavoo as vavoo
import utils.video as video
import utils.user as user

import resolveurl as resolver
from helper import sites
from helper.proxy import ForwardHttpProxy

cachepath = common.cp
listpath = common.lp
rootpath = common.rp
con0 = common.con0
con1 = common.con1
con2 = common.con2
con3 = common.con3

common.check()

class UvicornServer(Process):
    def __init__(self, config: Config):
        super().__init__()

        self.config = config

    def stop(self):
        self.terminate()

    def run(self, *args, **kwargs):
        server = Server(config=self.config)
        server.run()

proxy = ForwardHttpProxy()

@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    # Init
    application.state.aGlobaVar = "request.app.state.aGlobaVar"
    yield # Run
    # Stop
    await proxy.aclose()

app = FastAPI(lifespan=lifespan)
links = {}
linked = {}


#def handleServices():
    #global p3, p4
    #time.sleep(2)
    #if bool(int(cfg.get('Main', 'm3u8_service'))) == True:
        #if not p3:
            #p3 = Process(target=services.loop_m3u8)
            #p3.start()
            #Logger('[LOOP][M3U8::] Successful started...')
        #else: Logger('[LOOP][M3U8::] not started, because service allready running ...')
    #else: Logger('[LOOP][M3U8::] not started, because service are disabled ...')
    #if bool(int(cfg.get('Main', 'epg_service'))) == True:
        #if not p4:
            #p4 = Process(target=services.loop_epg)
            #p4.start()
            #Logger('[LOOP][EPG::] Successful started...')
        #else: Logger('[LOOP][EPG::] not started, because service allready running ...')
    #else: Logger('[LOOP][EPG::] not started, because service are disabled ...')
    #return


#@app.on_event("startup")
#async def on_startup():
    #app.state.executor = ProcessPoolExecutor()
    #app.state.loop = asyncio.get_event_loop()
    #app.state.loop.run_in_executor(app.state.executor, handleServices)


#@app.on_event("shutdown")
#async def on_shutdown():
    #app.state.executor.shutdown()


# API XTREAM-CODES
############################################################################################################
@app.head("/get.php")
@app.options("/get.php", status_code=204)
@app.get("/get.php")
async def get_get(username: Union[str, None] = None, password: Union[str, None] = None, type: Union[str, None] = None, output: Union[str, None] = None):
    if username is None: username = "nobody"
    if password is None: password = "pass"
    typ = "m3u_plus"
    if type is not None:
        if type == "m3u": typ = "m3u"
    out = "mp4"
    if output is not None:
        if output == "ts" or output == "mpegts": out = "ts"
        elif output == "hls": out = "m3u8"
    of = os.path.join(cachepath, 'streams.m3u')
    if os.path.exists(of):
        os.remove(of)
    vid = video.get_m3u8(username, password, out, typ, of)
    if os.path.exists(of):
        file = open(of, "rb")
        if typ == 'm3u8_plus': headers = {'Content-Disposition': 'attachment; filename="tv_channels_%s_plus.m3u"' % username, 'Content-Description': 'File Transfer'}
        else: headers = {'Content-Disposition': 'attachment; filename="tv_channels_%s.m3u"' % username, 'Content-Description': 'File Transfer'}
        return StreamingResponse(file, headers=headers, media_type="application/vnd.apple.mpegurl; charset=utf-8")
    else:
        raise HTTPException(status_code=404, detail="File not found")


@app.post("/get.php")
async def get_post(username: Annotated[str, Form()] = None, password: Annotated[str, Form()] = None, type: Annotated[str, Form()] = None, output: Annotated[str, Form()] = None):
    return
    if username is None: username = "nobody"
    if password is None: password = "pass"
    typ = "m3u_plus"
    if type is not None:
        if type == "m3u": typ = "m3u"
    out = "mp4"
    if output is not None:
        if output == "ts" or output == "mpegts": out = "ts"
        elif output == "hls": out = "m3u8"
    of = os.path.join(cachepath, 'streams.m3u')
    if os.path.exists(of):
        os.remove(of)
    vid = video.get_m3u8(username, password, out, typ, of)
    if os.path.exists(of):
        file = open(of, "rb")
        if typ == 'm3u8': headers = {'Content-Disposition': 'attachment; filename="tv_channels_%s_plus.m3u"' % username, 'Content-Description': 'File Transfer'}
        else: headers = {'Content-Disposition': 'attachment; filename="tv_channels_%s.m3u"' % username, 'Content-Description': 'File Transfer'}
        return StreamingResponse(file, headers=headers, media_type="application/vnd.apple.mpegurl; charset=utf-8")
    else:
        raise HTTPException(status_code=404, detail="File not found")


@app.head("/player_api.php")
@app.options("/player_api.php", status_code=204)
@app.get("/player_api.php")
async def player_get(username: Union[str, None] = None, password: Union[str, None] = None, action: Union[str, None] = None, vod_id: Union[str, None] = None, series_id: Union[str, None] = None, stream_id: Union[str, None] = None, limit: Union[str, None] = None, category_id: Union[str, None] = None, params: Union[str, None] = None):
    if username is None: username = "nobody"
    if password is None: password = "pass"

    user_data = user.auth(username, password)
    if action is None:
        return {
            "user_info": user.user_info_xtream(user_data, username, password),
            "server_info": common.server_info(),
        }
    if action is not None:
        if action == "get_live_categories":
            return video.get_live_categories()
        elif action == "get_live_streams":
            return video.get_live_streams(category_id)
        elif action == "get_vod_categories":
            return video.get_vod_categories()
        elif action == "get_vod_streams":
            return video.get_vod_streams(category_id)
        elif action == "get_vod_info":
            return video.get_vod_info(vod_id)
        elif action == "get_series_categories":
            return video.get_series_categories()
        elif action == "get_series_info":
            return video.get_series_info(series_id)
        elif action == "get_series":
            return video.get_series(category_id)
        elif action == "get_simple_data_table":
            return video.get_simple_data_table(stream_id)
        elif action == "get_short_epg":
            return video.get_short_epg(stream_id, limit)


@app.post("/player_api.php")
async def player_post(username: Annotated[str, Form()] = None, password: Annotated[str, Form()] = None, action: Annotated[str, Form()] = None, vod_id: Annotated[str, Form()] = None, series_id: Annotated[str, Form()] = None, stream_id: Annotated[str, Form()] = None, limit: Annotated[str, Form()] = None, category_id: Annotated[str, Form()] = None, params: Annotated[str, Form()] = None):
    if username is None: username = "nobody"
    if password is None: password = "pass"

    user_data = user.auth(username, password)
    if action is None:
        return {
            "user_info": user.user_info_xtream(user_data, username, password),
            "server_info": common.server_info(),
        }
    if action is not None:
        if action == "get_live_categories":
            return video.get_live_categories()
        elif action == "get_live_streams":
            return video.get_live_streams(category_id)
        elif action == "get_vod_categories":
            return video.get_vod_categories()
        elif action == "get_vod_streams":
            return video.get_vod_streams(category_id)
        elif action == "get_vod_info":
            return video.get_vod_info(vod_id)
        elif action == "get_series_categories":
            return video.get_series_categories()
        elif action == "get_series_info":
            return video.get_series_info(series_id)
        elif action == "get_series":
            return video.get_series(category_id)
        elif action == "get_simple_data_table":
            return video.get_simple_data_table(stream_id)
        elif action == "get_short_epg":
            return video.get_short_epg(stream_id, limit)


@app.head("/panel_api.php")
@app.options("/panel_api.php", status_code=204)
@app.get("/panel_api.php")
async def panel_get(username: Union[str, None] = None, password: Union[str, None] = None, action: Union[str, None] = None):
    if username is None: username = "nobody"
    if password is None: password = "pass"

    user_data = user.auth(username, password)
    return {
        "user_info": user.user_info_xtream(user_data, username, password),
        "server_info": common.server_info(),
        "categories": { "live": video.get_live_categories(), "movie": video.get_vod_categories(), "series": video.get_series_categories() },
        "available_channels": video.get_all_channels(),
    }


@app.post("/panel_api.php")
async def panel_post(username: Annotated[str, Form()] = None, password: Annotated[str, Form()] = None, action: Annotated[str, Form()] = None):
    if username is None: username = "nobody"
    if password is None: password = "pass"

    user_data = user.auth(username, password)
    return {
        "user_info": user.user_info_xtream(user_data, username, password),
        "server_info": common.server_info(),
        "categories": { "live": video.get_live_categories(), "movie": video.get_vod_categories(), "series": video.get_series_categories() },
        "available_channels": video.get_all_channels(),
    }


@app.head("/live/{any_path:path}")
@app.options("/live/{any_path:path}", status_code=204)
@app.get("/live/{username}/{password}/{sid}.{ext}", response_class=RedirectResponse, status_code=302)
async def live(request: Request, username: str, password: str, sid: str, ext: str):
    if username is None: username = "nobody"
    if password is None: password = "pass"

    user_data = user.auth(username, password)
    cur = con1.cursor()
    cur.execute('SELECT * FROM channel WHERE id="' + sid + '"')
    data = cur.fetchone()
    if str(common.get_setting('xtream_codec')) == 't':
        sig = vavoo.getAuthSignature()
        if data and sig:
            url = str(data['url'])
            link = url + '?n=1&b=5&vavoo_auth=' + sig
            return await proxy.stream(request=request, stream_url=link)
        else: raise HTTPException(status_code=404, detail="Stream not found")
    else:
        if data:
            link = vavoo.resolve_link(data['hls'])
            if link:
                #return await proxy.stream(request=request, stream_url=link)
                return link
            else: raise HTTPException(status_code=404, detail="Stream not found")
        else: raise HTTPException(status_code=404, detail="Stream not found")


@app.head("/{typ}/{any_path:path}")
@app.options("/{typ}/{any_path:path}", status_code=204)
@app.get("/{typ}/{username}/{password}/{sid}.{ext}", response_class=StreamingResponse, status_code=200)
async def vod(request: Request, typ: str, username: str, password: str, sid: str, ext: str):
    if username is None: username = "nobody"
    if password is None: password = "pass"

    user_data = user.auth(username, password)
    cur = con2.cursor()
    cur.execute('SELECT * FROM streams WHERE id="' + sid + '"')
    data = cur.fetchone()
    if not data:
        raise HTTPException(status_code=404, detail="No Data")
    if sid not in links:
        urls = xstream.getHoster(data)
        if urls:
            links[sid] = urls
            if sid not in linked: linked[sid] = {}
            if username not in linked[sid]: linked[sid][username] = 0
    if sid in links:
        if len(links[sid]) > linked[sid][username]:
            url = links[sid][linked[sid][username]]
            if not "streamUrl" in url:
                try:
                    shost = xstream.getHosterUrl(url["link"], data['site'])
                    if shost:
                        url["streamUrl"] = shost[0]["streamUrl"]
                except Exception:
                    link = None
            if "streamUrl" in url:
                try:
                    link = xstream.getStream(url["streamUrl"])
                except Exception:
                    link = None
            linked[sid][username] += 1
            if link is None:
                notify = Notifications("0.0.0.0")
                try:
                    await notify.async_connect()
                    await notify.async_send("Link (%s/%s) not found" %(str(linked[sid][username]), str(len(links[sid]))), title="Mastaaa's VX Parser")
                except Exception:
                    Logger(1, "Link (%s/%s) not found" %(str(linked[sid][username]), str(len(links[sid]))))
                raise HTTPException(status_code=404, detail="Link (%s/%s) not found" %(str(linked[sid][username]), str(len(links[sid]))))
            elif "voe" in link.lower():
                link = re.sub('\|User-Agent=.*', '', link)
            return await proxy.stream(request=request, stream_url=link)
        elif len(links[sid]) > 1:
            linked[sid][username] = 0
            return
    else: raise HTTPException(status_code=404, detail="Stream not found")


@app.head("/xmltv.php")
@app.options("/xmltv.php", status_code=204)
@app.get("/xmltv.php")
async def epg(username: str, password: str):
    if username is None: username = "nobody"
    if password is None: password = "pass"

    user_data = user.auth(username, password)
    f = os.path.join(cachepath, 'xmltv.xml')
    if os.path.exists(f):
        file = open(f, "rb")
        headers = {'Content-Disposition': 'attachment; filename="xmltv.xml"', 'Connection': 'close'}
        return StreamingResponse(file, headers=headers, media_type="application/xml; charset=utf-8")
    else:
        raise HTTPException(status_code=404, detail="File not found")


# VAVOO API
############################################################################################################
@app.head("/epg.xml.gz")
@app.options("/epg.xml.gz", status_code=204)
@app.get("/epg.xml.gz", response_class=StreamingResponse, status_code=200)
def gz():
    f = os.path.join(listpath, 'epg.xml.gz')
    if os.path.exists(f):
        def iterfile():
            with open(f, mode="rb") as file_like:
                yield from file_like
        return StreamingResponse(iterfile(), media_type="application/gzip")
    else:
        raise HTTPException(status_code=404, detail="File not found")


@app.head("/{m3u8}.m3u8")
@app.options("/{m3u8}.m3u8", status_code=204)
@app.get("/{m3u8}.m3u8", response_class=StreamingResponse, status_code=200)
def m3u8(m3u8: str):
    f = os.path.join(listpath, m3u8+'.m3u8')
    if os.path.exists(f):
        playlisttyp = "application/vnd.apple.mpegurl; charset=utf-8" if m3u8.endswith("_hls") else "application/octet-stream"
        def iterfile():
            with open(f, mode="rb") as file_like:
                yield from file_like
        return StreamingResponse(iterfile(), media_type=playlisttyp)
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.head("/channel/{sid}")
@app.options("/channel/{sid}", status_code=204)
@app.get("/channel/{sid}", response_class=StreamingResponse, status_code=200)
async def channel(request: Request, sid: str):
    cur = con1.cursor()
    cur.execute('SELECT * FROM channel WHERE id="' + sid + '"')
    data = cur.fetchone()
    sig = vavoo.getAuthSignature()
    if data and sig:
        url = str(data['url'])
        link = url + '?n=1&b=5&vavoo_auth=' + sig
        return await proxy.stream(request=request, stream_url=link)
    else: raise HTTPException(status_code=404, detail="Stream not found")


@app.head("/hls/{sid}")
@app.options("/hls/{sid}", status_code=204)
@app.get("/hls/{sid}", response_class=RedirectResponse, status_code=302)
async def channel(request: Request, sid: str):
    cur = con1.cursor()
    cur.execute('SELECT * FROM channel WHERE id="' + sid + '"')
    data = cur.fetchone()
    if data:
        link = vavoo.resolve_link(data['hls'])
        if link:
            # return await proxy.stream(request=request, stream_url=link)
            return link
        else: raise HTTPException(status_code=404, detail="Stream not found")
    else: raise HTTPException(status_code=404, detail="Stream not found")


@app.head("/stream/{sid}")
@app.options("/stream/{sid}", status_code=204)
@app.get("/stream/{sid}", response_class=StreamingResponse, status_code=200)
async def stream(request: Request, sid: str):
    cur = con2.cursor()
    cur.execute('SELECT * FROM streams WHERE id="' + sid + '"')
    data = cur.fetchone()
    if not data:
        raise HTTPException(status_code=404, detail="No Data")
    if sid not in links:
        urls = xstream.getHoster(data)
        if urls:
            links[sid] = urls
            if sid not in linked: linked[sid] = 0
    if sid in links:
        if len(links[sid]) > linked[sid]:
            url = links[sid][linked[sid]]
            if not "streamUrl" in url:
                try:
                    shost = xstream.getHosterUrl(url["link"], data['site'])
                    if shost:
                        url["streamUrl"] = shost[0]["streamUrl"]
                except Exception:
                    link = None
            if "streamUrl" in url:
                try:
                    link = xstream.getStream(url["streamUrl"])
                except Exception:
                    link = None
            linked[sid] += 1
            if link is None:
                notify = Notifications("0.0.0.0")
                try:
                    await notify.async_connect()
                    await notify.async_send("Link (%s/%s) not found" %(str(linked[sid]), str(len(links[sid]))), title="Mastaaa's VX Parser")
                except Exception:
                    Logger(1, "Link (%s/%s) not found" %(str(linked[sid]), str(len(links[sid]))))
                raise HTTPException(status_code=404, detail="Link (%s/%s) not found" %(str(linked[sid]), str(len(links[sid]))))
            return await proxy.stream(request=request, stream_url=link)
        elif len(links[sid]) > 1:
            linked[sid] = 0
            return
    else: raise HTTPException(status_code=404, detail="Stream not found")


@app.head("/{name}.{ext}")
@app.options("/{name}.{ext}", status_code=204)
@app.get("/{name}.{ext}", response_class=FileResponse, status_code=200)
def main(name: str, ext: str):
    # https://fastapi.tiangolo.com/tutorial/static-files/
    if os.path.exists(os.path.join(rootpath, name+'.'+ext)):
        f = os.path.join(rootpath, name+'.'+ext)
    elif os.path.exists(os.path.join(rootpath, 'html', name+'.'+ext)):
        f = os.path.join(rootpath, 'html', name+'.'+ext)
    else: raise HTTPException(status_code=404, detail="File not found")
    return f


@app.head("/")
@app.options("/", status_code=204)
@app.get("/", response_class=HTMLResponse, status_code=200)
def root():
    data = ''
    listdir = os.listdir(listpath)
    for l in listdir:
        data += '<a href="'+l+'">'+l+'</a><br>'
    return data


@app.head("/video/{sid}")
@app.options("/video/{sid}", status_code=204)
@app.get("/video/{sid}", response_class=HTMLResponse, status_code=200)
async def videoplayer(sid: str):
    # TODO streaming requires video.js hls-player and dynamic proxy-routing capabilities
    content = f"""
<body>
<video controls width="1280px" height="720px" preload="none" src="/hls/{sid}" />
</body>
    """
    return content
