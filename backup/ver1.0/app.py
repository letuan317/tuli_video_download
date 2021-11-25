
from __future__ import unicode_literals
import sys
import youtube_dl
import eel
from termcolor import cprint
import functions
import json
import os
import subprocess


import yt_dlp
from yt_dlp.postprocessor.common import PostProcessor


# Set web files folder and optionally specify which file types to check for eel.expose()
#   *Default allowed_extensions are: ['.js', '.html', '.txt', '.htm', '.xhtml']
eel.init('web', allowed_extensions=['.js', '.html'])


# init data
DEFAULT_PATH_CONFIG = "./config.json"
DEFAULT_PATH_STORAGE = "./videos"
DEFAULT_PATH_DOWNLOADED = "./downloaded.txt"
DEFAULT_PATH_DATABASE = "./database.json"
DEFAULT_PATH_VIDEO_ERROR_LOG = "./error_video.log"
VIDEO_SOURCES = ["youtube.com", "ok.ru"]

# Load config from config.js
if os.path.exists(DEFAULT_PATH_CONFIG):
    with open(DEFAULT_PATH_CONFIG) as json_file:
        data_config = json.load(json_file)
    DEFAULT_PATH_STORAGE = data_config["path_storage"]+"/"
    DEFAULT_PATH_DOWNLOADED = data_config["path_downloaded"] + \
        "/downloaded.txt"
else:
    with open(DEFAULT_PATH_CONFIG, 'w') as outfile:
        json.dump({
            "path_storage": DEFAULT_PATH_STORAGE,
            "path_downloaded": DEFAULT_PATH_DOWNLOADED
        }, outfile
        )

# Send the setup to js
eel.setup_config_js({
    "path_storage": DEFAULT_PATH_STORAGE[:len(DEFAULT_PATH_STORAGE)-1],
    "path_downloaded": DEFAULT_PATH_DOWNLOADED[:len(DEFAULT_PATH_DOWNLOADED)-len("/downloaded.txt")]
}
)

if not os.path.exists(DEFAULT_PATH_STORAGE):
    os.mkdir(DEFAULT_PATH_STORAGE)


cprint("[INFO] {} {}".format(DEFAULT_PATH_STORAGE,
                             DEFAULT_PATH_DOWNLOADED), 'green')

global GLOBAL_THREAD
# Load database
if os.path.exists(DEFAULT_PATH_DATABASE):
    with open(DEFAULT_PATH_DATABASE) as json_file:
        listOfLinks = json.load(json_file)
    for idx, video in enumerate(listOfLinks["data"]):
        if(video["status"] in ["Downloading", "Error"]):
            video["status"] = "Wait"
    with open(DEFAULT_PATH_DATABASE, 'w') as outfile:
        json.dump(listOfLinks, outfile)
else:
    listOfLinks = {"data": []}

# Load downloaded video ids
listOfLinksDownloaded = []
if os.path.exists(DEFAULT_PATH_DOWNLOADED):
    with open(DEFAULT_PATH_DOWNLOADED, "r") as fr:
        for line in fr:
            temp_id = line.split(" ")[1]
            listOfLinksDownloaded.append(temp_id.rstrip("\n"))
cprint("[INFO] Length of downloaded.txt: " +
       str(len(listOfLinksDownloaded)), 'green')


@eel.expose
def get_info_py(linkData):
    cprint("getInfo: "+linkData, "blue")
    if not any(source in linkData for source in VIDEO_SOURCES):
        message = "[!] Link can NOT be downloaded: " + linkData
        eel.error_message_js(message)
        cprint(message, "red")
    else:
        if("youtube.com" in linkData and not any(item in linkData for item in ["list=", "/videos"])):
            cprint("getInfo: Single youtube video", "yellow")
            # Single youtube video
            single_video_link(linkData, linkData.split(
                'watch?v=')[1].split("&")[0])
        elif("ok.ru" in linkData):
            cprint("getInfo: ok.ru video", "yellow")
            # ok.ru video
            single_video_link(linkData, linkData.split('video/')[1])
        elif("youtube.com" in linkData and "list=" in linkData):
            cprint("getInfo: Youtube playlist", "yellow")
            # Youtube playlist
            answer = functions.DialogYesNo(
                "Comfirmation", linkData+" is a playlist. Do you want download them?")
            if answer:
                playlist_videos_link(linkData)
        elif "youtube.com" in linkData and any(temp in linkData for temp in ["/channel/", "/c/"]):
            cprint("getInfo: Youtube channel", "yellow")
            # Youtube channel
            answer = functions.DialogYesNo(
                "Comfirmation", linkData+" is a channel. Do you want download all videos?")
            if answer:
                playlist_videos_link(linkData)
        else:
            message = "[!] get_info_py: " + linkData
            eel.error_message_js(message)
            cprint(message, "red")


def single_video_link(linkData, temp_id):
    cprint("[INFO] single_video_link", "green")
    if(temp_id in listOfLinksDownloaded):
        message = "[!] Link is already downloaded: " + temp_id
        eel.error_message_js(message)
        cprint(message, "yellow")
    else:
        checkAdded = False
        if(listOfLinks["data"]):
            if any(temp_id == item["id"] for item in listOfLinks["data"]):
                checkAdded = True
        if not checkAdded:
            cprint("[+] It a link that can be downloaded", "green")
            check, data_video = functions.GetYoutubeInfo(
                linkData, listOfLinksDownloaded)
            if(check == False and data_video == None):
                message = "[!] Link is already downloaded: " + temp_id
                eel.error_message_js(message)
                cprint(message, "yellow")
            elif(check == True):
                data_video = functions.ExtractInfoData(
                    data_video)
                listOfLinks["data"].append(data_video)
                with open(DEFAULT_PATH_DATABASE, 'w') as outfile:
                    json.dump(listOfLinks, outfile)
                eel.update_listOfLinks_js(listOfLinks["data"])
                eel.notify_message_js("[INFO] Success")
            else:   # link cant be get info by age, ...
                message = "[!] get_info_py: " + data_video
                eel.error_message_js(message)
                cprint(message, "red")

                temp_list = []
                with open(DEFAULT_PATH_VIDEO_ERROR_LOG, "r") as fr:
                    for line in fr:
                        temp_list.append(line.strip("\r\n"))
                if not any(linkData == x for x in temp_list):
                    with open(DEFAULT_PATH_VIDEO_ERROR_LOG, "a") as fa:
                        fa.write(linkData+"\n")

        else:
            message = "[!] Link is already added: " + temp_id
            eel.error_message_js(message)
            cprint(message, "yellow")


def playlist_videos_link(linkData):
    cprint("[INFO] playlist_videos_link", "green")
    check, list_videos_data = functions.GetYoutubePlaylistInfo(linkData)
    if(check):
        for data_video in list_videos_data:
            temp_id = data_video["id"]
            if any(temp_id == item["id"] for item in listOfLinks["data"]):
                message = "[!] Link is already added: " + temp_id
                eel.error_message_js(message)
                cprint(message, "yellow")
            elif(temp_id in listOfLinksDownloaded):
                message = "[!] Link is already downloaded: " + temp_id
                eel.error_message_js(message)
                cprint(message, "yellow")
            else:
                data_video = functions.ExtractInfoData(
                    data_video)
                listOfLinks["data"].append(data_video)
                with open(DEFAULT_PATH_DATABASE, 'w') as outfile:
                    json.dump(listOfLinks, outfile)
                eel.update_listOfLinks_js(listOfLinks["data"])
                message = "[+] Add new video: " + temp_id
                eel.notify_message_js(message)
                cprint(message, "yellow")

    else:
        message = "[!] playlist_videos_link: " + linkData
        eel.error_message_js(message)
        cprint(message, "red")

        temp_list = []
        with open(DEFAULT_PATH_VIDEO_ERROR_LOG, "r") as fr:
            for line in fr:
                temp_list.append(line.strip("\r\n"))
        if not any(linkData == x for x in temp_list):
            with open(DEFAULT_PATH_VIDEO_ERROR_LOG, "a") as fa:
                fa.write(linkData+"\n")


@eel.expose
def update_listOfLinks_py(temp_data):
    global listOfLinks
    cprint("[INFO] Update select_format", "green")
    listOfLinks["data"] = temp_data.copy()
    with open(DEFAULT_PATH_DATABASE, 'w') as outfile:
        json.dump(listOfLinks, outfile)


@eel.expose
def delete_item_action_py(item_id):
    cprint("[INFO] Delete video id "+item_id, "green")
    for idx, video in enumerate(listOfLinks["data"]):
        if(video["id"] == item_id):
            listOfLinks["data"].remove(video)
            break
    with open(DEFAULT_PATH_DATABASE, 'w') as outfile:
        json.dump(listOfLinks, outfile)
    eel.update_listOfLinks_js(listOfLinks["data"])
    eel.notify_message_js("Deleted video id "+item_id)


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
    try:
        if (d['status'] == 'finished'):
            status = 'Finished'
            temp_check = False
            for idx, video in enumerate(listOfLinks["data"]):
                if (video["status"] == ["Downloading", "Error"]):
                    video["status"] = "Wait"
                    temp_check = True
            if (temp_check):
                with open(DEFAULT_PATH_DATABASE, 'w') as outfile:
                    json.dump(listOfLinks, outfile)
            eel.update_listOfLinks_js(listOfLinks["data"])
        else:
            status = d['_percent_str'] + " of " + d['_total_bytes_str'] + \
                " at " + d['_speed_str'] + " ETA " + d['_eta_str']
        eel.download_process_js(status)
    except Exception as e:
        cprint("[!] my_hook: Error downloading", 'red')
        print(e)
        status = "Downloaded" if (
            "already been recorded in archive" in str(d)) else "Error"
        eel.download_process_js(status)


def run_downloaded_script():
    if(listOfLinks["data"]):
        for idx, video in enumerate(listOfLinks["data"]):
            if(video["status"] in ["Wait", "Paused", "Error"]):
                video["status"] = "Downloading"
                eel.update_listOfLinks_js(listOfLinks["data"])
                ydl_opts = {
                    'format': video["select_format"]+'+bestaudio',
                    'download_archive': DEFAULT_PATH_DOWNLOADED,
                    'outtmpl': DEFAULT_PATH_STORAGE+video["channel"]+'-'+video['id']+'-'+video["title"]+".%(ext)s",
                    'noplaylist': True,
                    'progress_hooks': [my_hook],
                    # extra for yt_dlp
                    'logger': MyLogger(),
                }
                try:

                    """with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video["webpage_url"]])"""
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.add_post_processor(MyCustomPP())
                        ydl.extract_info(video["webpage_url"])
                    video["status"] = "Downloaded"
                    with open(DEFAULT_PATH_DATABASE, 'w') as outfile:
                        json.dump(listOfLinks, outfile)
                    eel.update_listOfLinks_js(listOfLinks["data"])
                except Exception as e:
                    cprint("[!] run_downloaded_script: Error downloading", 'red')
                    print(e)
                    eel.error_message_js(
                        "[!] run_downloaded_script: Error downloading" + video["id"])
                    video["status"] = "Error"
                    eel.update_listOfLinks_js(listOfLinks["data"])
                    continue
    eel.download_process_js("DONE")


@eel.expose
def paste_link_action_py(cliptext):
    eel.notify_message_js("Get link INFO")
    get_info_py(cliptext)
    eel.paste_link_response_js()
    eel.update_listOfLinks_js(listOfLinks["data"])
    eel.notify_message_js("DONE")


@eel.expose
def add_file_action_py():
    cprint("[INFO] Add file action", "green")
    path_filename = functions.DialogSelectFile()
    if os.path.exists(path_filename) and path_filename[len(path_filename)-4:len(path_filename)] == ".txt":
        eel.add_file_response_js()
        eel.notify_message_js("Reading "+path_filename)
        try:
            with open(path_filename, 'r') as fr:
                for line in fr:
                    if(len(line) > 10):
                        eel.notify_message_js("Processing...")
                        get_info_py(line[:len(line)-1])
        except Exception as e:
            cprint("[] add_file_action_py: "+str(e).strip("\n"))
            eel.error_message_js(e)
        eel.notify_message_js("DONE.")
    else:
        eel.error_message_js("File is not exist")
    cprint("[INFO] DONE - Add file action", "green")


@eel.expose
def start_download_py():
    cprint("[INFO] Start download videos", "green")

    global GLOBAL_THREAD
    GLOBAL_THREAD = functions.KThread(target=run_downloaded_script)
    GLOBAL_THREAD.start()


@eel.expose
def pause_download_py():
    cprint("\n[!] Pausing download", "red")
    # GLOBAL_THREAD.terminate()
    GLOBAL_THREAD.kill()
    for idx, video in enumerate(listOfLinks["data"]):
        if(video["status"] == "Downloading"):
            video["status"] = "Paused"
            eel.update_listOfLinks_js(listOfLinks["data"])
            eel.download_process_js("Paused")
            break


@eel.expose
def sort_action_py():
    cprint("[INFO] Sorting list", "green")
    eel.notify_message_js("[INFO] Sorting list")
    temp_list = []
    temp_list_downloaded = []
    for idx, video in enumerate(listOfLinks["data"]):
        temp_list_downloaded.append(video) if(
            video["status"] == "Downloaded") else temp_list.append(video)
    listOfLinks["data"] = temp_list+temp_list_downloaded
    with open(DEFAULT_PATH_DATABASE, 'w') as outfile:
        json.dump(listOfLinks, outfile)
    eel.update_listOfLinks_js(listOfLinks["data"])
    eel.notify_message_js("DONE.")


@eel.expose
def clear_action_py():
    cprint("[INFO] Cleaning list", "green")
    temp_list = []
    for idx, video in enumerate(listOfLinks["data"]):
        if video["status"] != "Downloaded":
            temp_list.append(video)
    listOfLinks["data"] = temp_list.copy()
    with open(DEFAULT_PATH_DATABASE, 'w') as outfile:
        json.dump(listOfLinks, outfile)
    eel.update_listOfLinks_js(listOfLinks["data"])


@eel.expose
def setting_change_default_path_py(item):
    global DEFAULT_PATH_STORAGE
    global DEFAULT_PATH_DOWNLOADED
    directory = functions.DialogSelectDirectory()
    if item == "path_storage":
        DEFAULT_PATH_STORAGE = directory
        DEFAULT_PATH_DOWNLOADED = DEFAULT_PATH_DOWNLOADED[:len(
            DEFAULT_PATH_DOWNLOADED)-len("/downloaded.txt")]
    else:
        DEFAULT_PATH_STORAGE = DEFAULT_PATH_STORAGE[:len(
            DEFAULT_PATH_STORAGE)-1]
        DEFAULT_PATH_DOWNLOADED = directory
    print(DEFAULT_PATH_STORAGE, DEFAULT_PATH_DOWNLOADED)

    data_config = {
        "path_storage": DEFAULT_PATH_STORAGE,
        "path_downloaded": DEFAULT_PATH_DOWNLOADED
    }
    with open(DEFAULT_PATH_CONFIG, 'w') as outfile:
        json.dump(data_config, outfile)
    eel.setup_config_js(data_config)
    DEFAULT_PATH_STORAGE = data_config["path_storage"]+"/"
    DEFAULT_PATH_DOWNLOADED = data_config["path_downloaded"] + \
        "/downloaded.txt"


@eel.expose
def open_folder_storage_py():
    cprint("[INFO] open_folder_storage_py", 'green')
    if(sys.platform == "win32"):
        os.startfile(DEFAULT_PATH_STORAGE)
    elif(sys.platform == "darwin"):
        os.system('open "%s"' % DEFAULT_PATH_STORAGE)
    elif(sys.platform == "linux"):
        os.system('xdg-open "%s"' % DEFAULT_PATH_STORAGE)


@eel.expose
def say_hello_py(x):
    print('Hello from %s' % x)


say_hello_py('Python World!')
eel.say_hello_js('Python World!')
eel.update_listOfLinks_js(listOfLinks["data"])
eel.start('main.html')
