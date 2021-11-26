
from __future__ import unicode_literals
import yt_dlp
from yt_dlp.postprocessor.common import PostProcessor
import sys
from termcolor import cprint
import json
import os
import functions


class VideoDonwloadObject():
    def __init__(self):
        # init data
        self.DEFAULT_PATH_CONFIG = "./config.json"
        self.DEFAULT_PATH_STORAGE = "./videos"
        self.DEFAULT_PATH_DOWNLOADED = "./downloaded.txt"
        self.DEFAULT_PATH_DATABASE = "./database.json"
        self.DEFAULT_PATH_VIDEO_ERROR_LOG = "./error_video.log"
        self.VIDEO_SOURCES = ["youtube.com", "ok.ru"]

        self.GLOBAL_THREAD

        self.listOfLinks = []
        self.listOfLinksDownloaded = []

        self.Settings()

    def Settings(self):
        # Load config from config.js
        if os.path.exists(self.DEFAULT_PATH_CONFIG):
            with open(self.DEFAULT_PATH_CONFIG) as json_file:
                data_config = json.load(json_file)
            self.DEFAULT_PATH_STORAGE = data_config["path_storage"]+"/"
            self.DEFAULT_PATH_DOWNLOADED = data_config["path_downloaded"] + \
                "/downloaded.txt"
        else:
            with open(self.DEFAULT_PATH_CONFIG, 'w') as outfile:
                json.dump({
                    "path_storage": self.DEFAULT_PATH_STORAGE,
                    "path_downloaded": self.DEFAULT_PATH_DOWNLOADED
                }, outfile
                )

        if not os.path.exists(self.DEFAULT_PATH_STORAGE):
            os.mkdir(self.DEFAULT_PATH_STORAGE)

        cprint("[INFO] {} {}".format(self.DEFAULT_PATH_STORAGE,
                                     self.DEFAULT_PATH_DOWNLOADED), 'green')

        # Load database
        if os.path.exists(self.DEFAULT_PATH_DATABASE):
            with open(self.DEFAULT_PATH_DATABASE) as json_file:
                self.listOfLinks = json.load(json_file)
            for idx, video in enumerate(self.listOfLinks["data"]):
                if(video["status"] in ["Downloading", "Error"]):
                    video["status"] = "Wait"
            with open(self.DEFAULT_PATH_DATABASE, 'w') as outfile:
                json.dump(self.listOfLinks, outfile)
        else:
            self.listOfLinks = {"data": []}

        # Load downloaded video ids
        if os.path.exists(self.DEFAULT_PATH_DOWNLOADED):
            with open(self.DEFAULT_PATH_DOWNLOADED, "r") as fr:
                for line in fr:
                    temp_id = line.split(" ")[1]
                    self.listOfLinksDownloaded.append(temp_id.rstrip("\n"))
        cprint("[INFO] Length of downloaded.txt: " +
               str(len(self.listOfLinksDownloaded)), 'green')

    def GetInfo(self, url_link):
        cprint("getInfo: "+url_link, "blue")
        if not any(source in url_link for source in self.VIDEO_SOURCES):
            message = "[!] Link can NOT be downloaded: " + url_link
            cprint(message, "red")
        else:
            if("youtube.com" in url_link and not any(item in url_link for item in ["list=", "/videos"])):
                cprint("getInfo: Single youtube video", "yellow")
                # Single youtube video
                self.single_video_link(url_link, url_link.split(
                    'watch?v=')[1].split("&")[0])
            elif("ok.ru" in url_link):
                cprint("getInfo: ok.ru video", "yellow")
                # ok.ru video
                self.single_video_link(url_link, url_link.split('video/')[1])
            elif("youtube.com" in url_link and "list=" in url_link):
                cprint("getInfo: Youtube playlist", "yellow")
                # Youtube playlist
                answer = functions.DialogYesNo(
                    "Comfirmation", url_link+" is a playlist. Do you want download them?")
                if answer:
                    self.playlist_videos_link(url_link)
            elif "youtube.com" in url_link and any(temp in url_link for temp in ["/channel/", "/c/"]):
                cprint("getInfo: Youtube channel", "yellow")
                # Youtube channel
                answer = functions.DialogYesNo(
                    "Comfirmation", url_link+" is a channel. Do you want download all videos?")
                if answer:
                    self.playlist_videos_link(url_link)
            else:
                message = "[!] get_info_py: " + url_link
                cprint(message, "red")
        return message

    def single_video_link(self, url_link, temp_id):
        cprint("[INFO] single_video_link", "green")
        if(temp_id in self.listOfLinksDownloaded):
            message = "[!] Link is already downloaded: " + temp_id
            cprint(message, "yellow")
        else:
            checkAdded = False
            if(self.listOfLinks["data"]):
                if any(temp_id == item["id"] for item in self.listOfLinks["data"]):
                    checkAdded = True
            if not checkAdded:
                cprint("[+] It a link that can be downloaded", "green")
                check, data_video = functions.GetYoutubeInfo(
                    url_link, self.listOfLinksDownloaded)
                if(check == False and data_video == None):
                    message = "[!] Link is already downloaded: " + temp_id
                    cprint(message, "yellow")
                elif(check == True):
                    data_video = functions.ExtractInfoData(
                        data_video)
                    self.listOfLinks["data"].append(data_video)
                    with open(self.DEFAULT_PATH_DATABASE, 'w') as outfile:
                        json.dump(self.listOfLinks, outfile)
                else:   # link cant be get info by age, ...
                    message = "[!] get_info_py: " + data_video
                    cprint(message, "red")

                    temp_list = []
                    with open(self.DEFAULT_PATH_VIDEO_ERROR_LOG, "r") as fr:
                        for line in fr:
                            temp_list.append(line.strip("\r\n"))
                    if not any(url_link == x for x in temp_list):
                        with open(self.DEFAULT_PATH_VIDEO_ERROR_LOG, "a") as fa:
                            fa.write(url_link+"\n")
            else:
                message = "[!] Link is already added: " + temp_id
                cprint(message, "yellow")

    def playlist_videos_link(self, url_link):
        cprint("[INFO] playlist_videos_link", "green")
        check, list_videos_data = functions.GetYoutubePlaylistInfo(url_link)
        if(check):
            for data_video in list_videos_data:
                temp_id = data_video["id"]
                if any(temp_id == item["id"] for item in self.listOfLinks["data"]):
                    message = "[!] Link is already added: " + temp_id
                    cprint(message, "yellow")
                elif(temp_id in self.listOfLinksDownloaded):
                    message = "[!] Link is already downloaded: " + temp_id
                    cprint(message, "yellow")
                else:
                    data_video = functions.ExtractInfoData(
                        data_video)
                    self.listOfLinks["data"].append(data_video)
                    with open(self.DEFAULT_PATH_DATABASE, 'w') as outfile:
                        json.dump(self.listOfLinks, outfile)
                    message = "[+] Add new video: " + temp_id
                    cprint(message, "yellow")

        else:
            message = "[!] playlist_videos_link: " + url_link
            cprint(message, "red")

            temp_list = []
            with open(self.DEFAULT_PATH_VIDEO_ERROR_LOG, "r") as fr:
                for line in fr:
                    temp_list.append(line.strip("\r\n"))
            if not any(url_link == x for x in temp_list):
                with open(self.DEFAULT_PATH_VIDEO_ERROR_LOG, "a") as fa:
                    fa.write(url_link+"\n")
