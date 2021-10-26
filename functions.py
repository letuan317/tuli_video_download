from __future__ import unicode_literals
import youtube_dl
import requests
from termcolor import cprint


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


def GetYoutubeInfo(yt_link, data_last_links):
    yt_link = yt_link.split("&")[0]
    if(yt_link not in data_last_links):
        ydl_opts = {
            'logger': MyLogger(),
            'progress_hooks': [MyHook],
        }

        ydl = youtube_dl.YoutubeDL()
        with ydl:
            result = ydl.extract_info(yt_link,
                                      download=False
                                      )
        if 'entries' in result:
            video_data = result['entries'][0]
        else:
            video_data = result
        return True, video_data
    else:
        return False, None


def ExtractInfoData(video_data):
    for i in range(len(video_data["formats"])-1, 0, -1):
        if(video_data["formats"][i]["width"] == 1920 and
           video_data["formats"][i]["ext"] == "mp4"):
            video_data["formats"].insert(
                0, video_data["formats"][i])
            break
    data = {
        "id": video_data["id"],
        "channel": video_data["channel"].replace(" ", ""),
        "webpage_url": video_data["webpage_url"],
        "title": video_data["title"][:50],
        "thumbnail": video_data["thumbnail"],
        "select_format": video_data["formats"][0]["format_id"],
        "formats": video_data["formats"],
        "status": "Wait",
        # Wait, Dowloaded, Error
    }
    return data
