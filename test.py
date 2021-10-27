
import youtube_dl
from termcolor import cprint
yt_link = "https://www.youtube.com/watch?v=Y-IFroiOVWQ"


class MyLogger(object):
    def debug(self, msg):
        cprint(msg, 'blue')

    def warning(self, msg):
        cprint(msg, 'yellow')

    def error(self, msg):
        cprint(msg, 'red')


def MyHook(d):
    cprint(d, 'green')
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


ydl_opts = {
    'logger': MyLogger(),
    'progress_hooks': [MyHook],
}

ydl = youtube_dl.YoutubeDL()
with ydl:
    try:
        result = ydl.extract_info(yt_link,
                                  download=False
                                  )
    except Exception as e:
        cprint(e, 'red')
if 'entries' in result:
    video_data = result['entries'][0]
else:
    video_data = result
print(video_data)
