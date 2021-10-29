from __future__ import unicode_literals
import youtube_dl
from termcolor import cprint
import sys
import threading
from tkinter import *
from tkinter import filedialog as fd
from tkinter.messagebox import askyesno


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


def GetYoutubeInfo(yt_link, listOfLinksDownloaded):
    if("youtube.com" in yt_link and "list=" not in yt_link):
        # Single youtube video
        temp_id = yt_link.split('watch?v=')[1].split("&")[0]
        yt_link = yt_link.split("&")[0]
    elif("ok.ru" in yt_link):
        # ok.ru video
        temp_id = yt_link.split('video/')[1]
    else:
        # Youtube playlist
        None

    # check single youtube video
    if(temp_id not in listOfLinksDownloaded):
        ydl_opts = {
            'logger': MyLogger(),
            'progress_hooks': [MyHook],
        }

        ydl = youtube_dl.YoutubeDL()

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

    ydl = youtube_dl.YoutubeDL()

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


def ExtractInfoData(video_data):
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

    if(video_data.get("channel") == None):
        video_data.setdefault("channel", video_data["uploader"])

    data = {
        "id": video_data["id"],
        "channel": video_data["channel"].replace(" ", ""),
        "webpage_url": video_data["webpage_url"],
        "title": video_data["id"]+' - '+video_data["title"][:50].replace("/", ""),
        "thumbnail": video_data["thumbnail"],
        "select_format": video_data["formats"][0]["format_id"],
        "formats": video_data["formats"],
        "status": "Wait",
        # Wait, Dowloaded, Error
    }
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


default_logo = './web/img/logo.ico'


def DialogSelectFile():
    filetypes = (
        ('text files', '*.txt'),
        ('All files', '*.*')
    )
    root = Tk()
    root.wm_iconbitmap(default_logo)
    root.withdraw()
    filename = fd.askopenfilename(title='Open a file',
                                  # initialdir='/',
                                  filetypes=filetypes)
    root.destroy()
    print(filename)
    return filename


def DialogSelectDirectory():
    root = Tk()
    root.wm_iconbitmap(default_logo)
    root.withdraw()
    directory = fd.askdirectory()
    root.destroy()
    print(directory)
    return directory


def DialogYesNo(title, message):
    root = Tk()
    root.wm_iconbitmap(default_logo)
    root.geometry('0x0')
    answer = askyesno(title=title,
                      message=message)
    if answer:
        root.destroy()
    return answer
