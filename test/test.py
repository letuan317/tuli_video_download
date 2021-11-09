from __future__ import unicode_literals
import youtube_dl
import json

import yt_dlp
from yt_dlp.postprocessor.common import PostProcessor

yt_link = ""

'''
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
'''


class MyLogger:
    def debug(self, msg):
        # For compatability with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


class MyCustomPP(PostProcessor):
    def run(self, info):
        self.to_screen('Doing stuff')
        return [], info


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')
    else:
        status = d['_percent_str'] + " of " + d['_total_bytes_str'] + \
            " at " + d['_speed_str'] + " ETA " + d['_eta_str']
        print(status)


ydl_opts = {
    'format': '313' + "+bestaudio",
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.add_post_processor(MyCustomPP())
    info = ydl.extract_info(yt_link)
    """
    with open("output.json", 'w') as outfile:
        json.dump(info, outfile)
    """
