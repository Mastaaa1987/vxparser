[app]
title = VX-Parser
package.name = vxparser
package.domain = org.mastaaa
source.dir = .
source.include_exts = py, db, json, png, kv
source.exclude_dirs = data, bilder, bakk
version = 1.4.8
requirements = android, hostpython3==3.9.6, python3==3.9.6, werkzeug==2.2.2, kivy, https://github.com/kivymd/KivyMD/archive/master.zip, gestures4kivy, camera4kivy, aiohttp==3.8.5, fastapi==0.95.0, uvicorn==0.13.3, plyer, unidecode, click, kvdroid, pyjnius, typing_extensions, starlette, pydantic, anyio, sniffio, exceptiongroup, notifications_android_tv, python-multipart, six, certifi>=2018.4.16, pillow, sqlite3, requests==2.31.0, charset-normalizer==3.0.1, idna==3.4, chardet, pytz, oscpy, aiosqlite, notifications-android-tv, httpx, httpcore, h11
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, FOREGROUND_SERVICE
orientation = portrait, landscape
fullscreen = 0
services = Task:services.py:foreground:sticky
#          archs = armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = armeabi-v7a
android.allow_backup = True
presplash.filename = %(source.dir)s/resources/presplash.png
icon.filename = %(source.dir)s/resources/icon.png
#p4a.bootstrap = sdl2
#p4a.branch = master
#android.accept_sdk_license = True

[buildozer]
log_level = 1
warn_on_root = 0

