from __future__ import unicode_literals
import youtube_dl
import json

yt_link = ""


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
    'username': "test",
    'password': "test",
    'logger': MyLogger(),
    'progress_hooks': [MyHook],
}

ydl = youtube_dl.YoutubeDL()

try:
    with ydl:
        result = ydl.extract_info(yt_link,
                                  download=False
                                  )

    video_data = result
    with open("text.json", 'w') as outfile:
        json.dump(video_data, outfile)
except Exception as e:
    print(e)
