from __future__ import unicode_literals
import youtube_dl
import json


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def MyHook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


yt_link = "https://www.youtube.com/watch?v=WDsALdPl2nU"

ydl_opts = {
    'logger': MyLogger(),
    'progress_hooks': [MyHook],
}

ydl = youtube_dl.YoutubeDL()

with ydl:
    result = ydl.extract_info(yt_link,
                              download=False
                              )
with open("test.json", 'w') as outfile:
    json.dump(result, outfile)
