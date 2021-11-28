from __future__ import unicode_literals
import youtube_dl
import yt_dlp
from yt_dlp.postprocessor.common import PostProcessor

from termcolor import cprint
import sys
import threading
import json


class MyLogger:
    def debug(self, msg):
        # For compatability with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        if msg.startswith('[download] '):
            pass
        else:
            cprint("MyLogger: " + msg, "green")

    def warning(self, msg):
        cprint("MyLogger: " + msg, "yellow")

    def error(self, msg):
        cprint("MyLogger: " + msg, "red")


def MyHook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def GetYoutubeInfo(yt_link, listOfLinksDownloaded, restricted=False):
    if("youtube.com" in yt_link and "list=" not in yt_link):
        # Single youtube video
        temp_id = yt_link.split('watch?v=')[1].split("&")[0]
        yt_link = yt_link.split("&")[0]
    elif("ok.ru" in yt_link):
        # ok.ru video
        temp_id = yt_link.split('video/')[1]
    elif("youtu.be" in yt_link):
        temp_id = yt_link.split('/')[-1]

    # check single youtube video
    if(temp_id not in listOfLinksDownloaded):
        ydl_opts = {
            'logger': MyLogger(),
            'progress_hooks': [MyHook],
        }

        ydl = yt_dlp.YoutubeDL(
            ydl_opts) if restricted else youtube_dl.YoutubeDL(ydl_opts)

        try:
            with ydl:
                result = ydl.extract_info(yt_link,
                                          download=False
                                          )
            if 'entries' in result:
                video_data = result['entries'][0]
            else:
                video_data = result
            return True, video_data
        except Exception as e:
            cprint("[] GetYoutubeInfo: "+str(e).strip("\r\n"), 'red')
            return False, str(e).strip("\r\n")
    else:
        return False, None


def GetYoutubePlaylistInfo(yt_link):
    ydl_opts = {
        'logger': MyLogger(),
        'progress_hooks': [MyHook],
    }

    ydl = yt_dlp.YoutubeDL(ydl_opts)

    try:
        with ydl:
            result = ydl.extract_info(yt_link,
                                      download=False
                                      )

        list_videos_data = result['entries']
        return True, list_videos_data
    except Exception as e:
        cprint("[] GetYoutubePlaylistInfo: "+str(e).strip("\r\n"), 'red')
        return False, str(e).strip("\r\n")


def ExtractInfoData(video_data, restricted=False):
    # BUG when try on a ok.ru video
    for i in range(len(video_data["formats"])-1, 0, -1):
        if((video_data["formats"][i]["width"] == 1920 or video_data["formats"][i]["height"] == 1920) and
           video_data["formats"][i]["ext"] == "mp4"):
            video_data["formats"].insert(
                0, video_data["formats"][i])
            temp_list = []
            for idx, frmat in enumerate(video_data["formats"]):
                if(frmat not in temp_list):
                    temp_list.append(frmat)
            video_data["formats"] = temp_list.copy()
            break

    # delete formats contain audio
    temp_list = list()
    for idx, formatt in enumerate(video_data["formats"]):
        if "audio" not in formatt["format"]:
            if formatt["filesize"] != 0:
                temp_list.append(formatt)
    video_data["formats"] = temp_list
    video_data["formats"].insert(1, "bestaudio")

    if(video_data.get("channel") == None):
        video_data.setdefault("channel", video_data["uploader"])

    data = {
        "id": video_data["id"],
        "channel": video_data["channel"].replace(" ", ""),
        "channel_id": video_data["channel_id"],
        "webpage_url": video_data["webpage_url"],
        "title": video_data["id"]+'-'+video_data["title"].replace("/", "").replace(" ", ""),
        "thumbnail": video_data["thumbnail"],
        "select_format": video_data["formats"][0]["format_id"],
        "formats": video_data["formats"],
        "status": "Wait",
        "restricted": False
    }
    data["restricted"] = True if restricted else False

    return data


class KThread(threading.Thread):
    """A subclass of threading.Thread, with a kill() method."""

    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        """Hacked run function, which installs the trace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True


def ConvertVideoSize(video_size):
    if video_size == None:
        return str(0)
    else:
        toMB = video_size / pow(1024, 2)
        toGB = video_size / pow(1024, 3)
        if toGB > 1:
            return str(round(toGB, 2)) + " GB"
        else:
            return str(round(toMB, 2)) + " MB"
