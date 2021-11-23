from __future__ import unicode_literals
import yt_dlp
from yt_dlp.postprocessor.common import PostProcessor

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


from urllib import request
from termcolor import cprint
import json
import os
import sys
import random

import functions

program_name = "Youtube Video Download"


def MessageBox(self, title, text):
    dlg = QMessageBox(self)
    dlg.setWindowTitle(title)
    dlg.setText(text)
    dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    dlg.setIcon(QMessageBox.Question)
    button = dlg.exec()

    if button == QMessageBox.Yes:
        return True
    else:
        return False


class UIApp(QWidget):
    def __init__(self):
        super().__init__()
        self.window_width = 900
        self.window_height = 500

        self.setGeometry(80, 50, self.window_width, self.window_height)
        self.setMinimumSize(self.window_width, self.window_height)
        self.setWindowTitle(program_name)

        self.colorDarkGreen = "#264653"
        self.colorGreen = "#2a9d8f"
        self.colorGreenArmy = "#6b705c"
        self.colorYellow = "#e9c46a"
        self.colorOrange = "#f4a261"
        self.colorRed = "#e76f51"

        self.InitData()

        self.sizeMenuContainer = 100
        self.sizeMenuIcon = 48
        self.posXMenuIcon = 20
        self.posYMenuIcon = 20
        self.sizeFooterContainer = 20

        self.sizeVideoContainer = 100

        self.videosContainer = list()

        self.scroll = QScrollArea(self)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setGeometry(
            0, 100, self.window_width, self.window_height - 120)

        self.MenuContainer()
        self.ContentContainer()
        self.Footer("Ready")

        self.ReloadWindows()

        self.temp_select_format = None

    def MenuContainer(self):
        margin = 20

        self.menuBackground = QFrame(self)
        self.menuBackground.setStyleSheet(
            "QWidget { background-color: %s}" % self.colorDarkGreen)
        self.AddMenuButton("Paste", 10, 'img/icons8-plus-48.png',
                           self.posXMenuIcon, self.posYMenuIcon, self.ActionPasteLink)
        self.AddMenuButton("Add", 13, 'img/icons8-add-file-48.png', self.posXMenuIcon +
                           self.sizeMenuIcon+margin, self.posYMenuIcon, self.ActionAddFile)
        self.AddMenuButton("Download", 0, 'img/icons8-download-48.png', self.posXMenuIcon +
                           2*(self.sizeMenuIcon+margin), self.posYMenuIcon, self.ActionDownload)
        self.AddMenuButton("Pause", 8, 'img/icons8-pause-48.png', self.posXMenuIcon +
                           3*(self.sizeMenuIcon+margin), self.posYMenuIcon, self.ActionPause)
        self.AddMenuButton("Open", 8, 'img/icons8-folder-48.png', self.posXMenuIcon+4*(
            self.sizeMenuIcon+margin), self.posYMenuIcon, self.ActionOpenFolder)
        self.AddMenuButton("Sort", 12, 'img/icons8-sort-48.png', self.posXMenuIcon +
                           5*(self.sizeMenuIcon+margin), self.posYMenuIcon, self.ActionSort)
        self.AddMenuButton("Clear", 10, 'img/icons8-clear-48.png', self.posXMenuIcon +
                           6*(self.sizeMenuIcon+margin), self.posYMenuIcon, self.ActionClear)

        self.btnSetting = QLabel(self)
        self.btnSetting.setPixmap(QPixmap("img/icons8-setting-48.png"))
        self.btnSetting.mousePressEvent = self.ActionSetting

        self.textSetting = QLabel("Settings", self)
        self.textSetting.setStyleSheet("QWidget { color: white}")

    def ReloadWindows(self):
        self.timer = QTimer()
        self.timer.start(0)
        self.timer.timeout.connect(self.UpdateScrollContent)

    def ContentContainer(self):
        self.videosContainer = []
        self.scroll_widget = QWidget()
        self.scroll_vbox = QVBoxLayout()

        for idx, video in enumerate(self.listOfLinks["data"]):
            videoBackground, thumbnail, title, channel, combo_box, status = self.VideoContainer(
                y=110*(idx), video_id=video["id"], url_image=video["thumbnail"], title=video["title"], channel=video["channel"], formats=video["formats"], status=video["status"])
            self.videosContainer.append({"videoBackground": videoBackground, "thumbnail": thumbnail,
                                        "title": title, "channel": channel, "combo_box": combo_box, "status": status})

            self.scroll_vbox.addWidget(videoBackground)
            self.scroll_vbox.addWidget(thumbnail)
            self.scroll_vbox.addWidget(title)
            self.scroll_vbox.addWidget(channel)
            self.scroll_vbox.addWidget(combo_box)
            self.scroll_vbox.addWidget(status)

        self.scroll_widget.setLayout(self.scroll_vbox)
        self.scroll.setWidget(self.scroll_widget)

        self.ReloadWindows()

    def resizeEvent(self, event):
        window_size = self.geometry()
        self.window_width = window_size.width()
        self.window_height = window_size.height()

        self.menuBackground.setGeometry(
            0, 0, self.window_width, self.sizeMenuContainer)
        self.btnSetting.move(
            self.window_width - self.sizeMenuIcon - self.posXMenuIcon, self.posYMenuIcon)
        self.textSetting.move(
            self.window_width - self.sizeMenuIcon-17, self.posYMenuIcon+self.sizeMenuIcon+5)
        self.scroll.setGeometry(
            0, 100, self.window_width, self.window_height - 120)

        self.footerBackground.setGeometry(
            0, self.window_height-self.sizeFooterContainer, self.window_width, self.sizeFooterContainer)
        self.footerMessage.setGeometry(
            5, self.window_height-self.sizeFooterContainer, self.window_width, self.sizeFooterContainer)

        self.UpdateScrollContent()

    def UpdateScrollContent(self):
        for i in range(0, len(self.videosContainer)):
            self.videosContainer[i]["videoBackground"].setGeometry(
                5, 110*(i)+10, self.window_width-30, 100)
            self.videosContainer[i]["thumbnail"].move(10, 110*(i)+15)
            self.videosContainer[i]["title"].setGeometry(
                175, 110*(i)+10, self.window_width-250, 50)
            self.videosContainer[i]["channel"].setGeometry(
                175, 110*(i)+60, (self.window_width-180)*2/10, 50)
            self.videosContainer[i]["combo_box"].setGeometry(
                175+(self.window_width-180)*2/10+5, 110*(i)+72, (self.window_width-180)*5/10, 25)
            self.videosContainer[i]["status"].setGeometry(
                175+(self.window_width-180)*7.5/10+10, 110*(i)+60, (self.window_width-180)*3/10-10, 50)

    def VideoContainer(self, y, video_id, url_image, title, channel, formats, status):
        videoBackground = QFrame()
        videoBackground.setStyleSheet(
            "QWidget { border-radius: 5px; background-color: %s}" % self.colorGreenArmy)

        data = request.urlopen(url_image).read()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        pixmap = pixmap.scaled(200, 90, Qt.KeepAspectRatio)
        thumbnail = QLabel()
        thumbnail.setPixmap(pixmap)

        title = QLabel(title)
        title.setStyleSheet(
            "QWidget { color: white; font-size: 15px; font-weight: bold}")

        channel = QLabel(channel)
        channel.setStyleSheet("QWidget { color: white;}")

        combo_box = QComboBox()
        for ft in formats:
            combo_box.addItem(", ".join((ft["format"], ft["ext"], ft["format_note"], str(
                ft["fps"])+" fps", functions.ConvertVideoSize(ft["filesize"]))))
        combo_box.activated.connect(
            lambda: self.UpdateSelectFormat(video_id, combo_box.currentText()))

        if status == "Wait":
            colorStatus = "white"
        elif status == "Downloading":
            colorStatus = self.colorYellow
        elif status == "Downloaded":
            colorStatus = self.colorGreen
        else:
            print(status)
            colorStatus = self.colorRed
        status = QLabel(status)
        status.setStyleSheet(
            "QWidget { color: "+colorStatus+"; font-size: 15px; font-weight: bold;}")

        '''
        videoBackground.setGeometry(5, y+10, 800, 100)
        thumbnail.move(10, y+5)
        title.setGeometry(175, y+10, 600, 50)
        channel.setGeometry(175, y+60, 160, 50)
        combo_box.setGeometry(175, y+72, 150, 50)
        status.setGeometry(175, y+60, 100, 50)
        '''

        return videoBackground, thumbnail, title, channel, combo_box, status

    def AddMenuButton(self, name, text_adjust, path_img, x, y, action):
        btnIconAddfile = QLabel(self)
        btnIconAddfile.setPixmap(QPixmap(path_img))
        btnIconAddfile.move(x, y)
        btnIconAddfile.mousePressEvent = action
        text = QLabel(name, self)
        text.move(x+text_adjust, y + self.sizeMenuIcon + 5)
        text.setStyleSheet("QWidget { color: white}")

    def ActionPasteLink(self, event):
        # TODO ActiocPasteLink: Paste a link from clipboard
        cprint('[INFO] ActionPasteLink', "green")
        text_clipborad = QApplication.clipboard().text()
        message = "Clipboard: " + text_clipborad
        self.FooterUpdate(message)
        self.GetInfo(text_clipborad)

    def ActionAddFile(self, event):
        # TODO ActionAddFile: Read a file with youtube links and paste
        print('ActionAddFile')

    def ActionDownload(self, event):
        # TODO ActionDownload: Downloading
        print('ActionDownload')

    def ActionPause(self, event):
        # TODO ActionPause: Pause to download
        print('ActionPause')

    def ActionOpenFolder(self, event):
        # TODO ActionOpenFolder: Open video folder
        print('ActionOpenFolder')

    def ActionSort(self, event):
        # TODO ActionSort: Sort wait and downloaded
        print('ActionSort')

    def ActionClear(self, event):
        # TODO ActionClear: Delete video downloaded
        print('ActionClear')

    def ActionSetting(self, event):
        # TODO ActionSetting: Open Setting Panel
        print('ActionSetting')

    def Footer(self, text):
        self.footerBackground = QFrame(self)
        self.footerBackground.setStyleSheet(
            "QWidget { background-color: %s}" % self.colorDarkGreen)
        self.footerMessage = QLabel(text, self)
        self.footerMessage.setStyleSheet("QWidget { color: white}")

    def FooterUpdate(self, message, color="white"):
        cprint(message, color)
        self.footerMessage.setText(message)
        self.footerMessage.setStyleSheet("QWidget { color: "+color+"}")

    def InitData(self):
        # init data
        self.DEFAULT_PATH_CONFIG = "./config.json"
        self.DEFAULT_PATH_STORAGE = "./videos"
        self.DEFAULT_PATH_DOWNLOADED = "./downloaded.txt"
        self.DEFAULT_PATH_DATABASE = "./database.json"
        self.DEFAULT_PATH_VIDEO_ERROR_LOG = "./error_video.log"
        self.VIDEO_SOURCES = ["youtube.com", "ok.ru"]

        self.GLOBAL_THREAD = None

        self.listOfLinks = {"data": []}
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
                }, outfile, indent=2
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
                json.dump(self.listOfLinks, outfile, indent=2)
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

        if not os.path.exists(self.DEFAULT_PATH_VIDEO_ERROR_LOG):
            with open(self.DEFAULT_PATH_VIDEO_ERROR_LOG, 'w') as fw:
                pass

    def GetInfo(self, url_link):
        cprint("getInfo: "+url_link, "blue")
        if not any(source in url_link for source in self.VIDEO_SOURCES):
            message = "[!] Link can NOT be downloaded: " + url_link
            self.FooterUpdate(message, 'red')
        else:
            if("youtube.com" in url_link and not any(item in url_link for item in ["list=", "/videos"])):
                # Single youtube video
                self.FooterUpdate(url_link + " is a youtube link", "green")
                self.SingleVideoLink(url_link, url_link.split(
                    'watch?v=')[1].split("&")[0])
            elif("ok.ru" in url_link):
                self.FooterUpdate(url_link + " is a ok.ru link", "green")
                # ok.ru video
                self.SingleVideoLink(url_link, url_link.split('video/')[1])
            elif("youtube.com" in url_link and "list=" in url_link):
                self.FooterUpdate(url_link + " is a youtube playlist", "green")
                # Youtube playlist
                answer = MessageBox(
                    "Comfirmation", url_link+" is a playlist. Do you want download them?")
                if answer:
                    self.PlaylistVideosLink(url_link)
            elif "youtube.com" in url_link and any(temp in url_link for temp in ["/channel/", "/c/"]):
                self.FooterUpdate(url_link + " is a youtube channel", "green")
                # Youtube channel
                answer = MessageBox(
                    "Comfirmation", url_link+" is a channel. Do you want download all videos?")
                if answer:
                    self.PlaylistVideosLink(url_link)
            else:
                message = "[!] get_info_py: " + url_link
                self.FooterUpdate(message, "red")

    def SingleVideoLink(self, url_link, temp_id):
        cprint("[INFO] SingleVideoLink", "green")
        if(temp_id in self.listOfLinksDownloaded):
            message = "[!] Link is already downloaded: " + temp_id
            self.Footer(message, "yellow")
        else:
            checkAdded = False
            if(self.listOfLinks["data"]):
                if any(temp_id == item["id"] for item in self.listOfLinks["data"]):
                    checkAdded = True
            if not checkAdded:
                message = "[+] It a link that can be downloaded"
                self.FooterUpdate(message, "green")
                check, data_video = functions.GetYoutubeInfo(
                    url_link, self.listOfLinksDownloaded)
                if(check == False and data_video == None):
                    message = "[!] Link is already downloaded: " + temp_id
                    self.FooterUpdate(message, "red")
                elif(check == True):
                    self.FooterUpdate(
                        "[*] Trying to extract info video", "green")

                    data_video = functions.ExtractInfoData(
                        data_video)

                    self.FooterUpdate(
                        "[*] Extract info video SUCCESSFUL", "green")
                    self.listOfLinks["data"].append(data_video)
                    with open(self.DEFAULT_PATH_DATABASE, 'w') as outfile:
                        json.dump(self.listOfLinks, outfile, indent=2)

                    self.ContentContainer()

                else:   # link cant be get info by age, ...
                    # TODO restrict by age, login to download
                    message = "[!] Link cant be get info by age: " + data_video
                    self.FooterUpdate(message, "red")
                    temp_list = []
                    with open(self.DEFAULT_PATH_VIDEO_ERROR_LOG, "r") as fr:
                        for line in fr:
                            temp_list.append(line.strip("\r\n"))
                    if not any(url_link == x for x in temp_list):
                        with open(self.DEFAULT_PATH_VIDEO_ERROR_LOG, "a") as fa:
                            fa.write(url_link+"\n")
            else:
                message = "[!] Link is already added: " + temp_id
                self.FooterUpdate(message, "red")

    def PlaylistVideosLink(self, url_link):
        cprint("[INFO] PlaylistVideosLink", "green")

        '''
        TODO Add videos from playlist, but some videos may be restrict by age,
        so it can get list of videos, and call SingVideoLink
      '''
        check, list_videos_data = functions.GetYoutubePlaylistInfo(url_link)
        if(check):
            for data_video in list_videos_data:
                temp_id = data_video["id"]
                if any(temp_id == item["id"] for item in self.listOfLinks["data"]):
                    message = "[!] Link is already added: " + temp_id
                    self.FooterUpdate(message, "red")
                elif(temp_id in self.listOfLinksDownloaded):
                    message = "[!] Link is already downloaded: " + temp_id
                    self.FooterUpdate(message, "red")
                else:
                    data_video = functions.ExtractInfoData(
                        data_video)
                    self.listOfLinks["data"].append(data_video)
                    with open(self.DEFAULT_PATH_DATABASE, 'w') as outfile:
                        json.dump(self.listOfLinks, outfile, indent=2)
                    message = "[+] Add new video: " + temp_id
                    self.FooterUpdate(message, "yellow")

        else:
            message = "[!] PlaylistVideosLink: " + url_link
            self.FooterUpdate(message, "red")

            temp_list = []
            with open(self.DEFAULT_PATH_VIDEO_ERROR_LOG, "r") as fr:
                for line in fr:
                    temp_list.append(line.strip("\r\n"))
            if not any(url_link == x for x in temp_list):
                with open(self.DEFAULT_PATH_VIDEO_ERROR_LOG, "a") as fa:
                    fa.write(url_link+"\n")

    def UpdateSelectFormat(self, video_id, video_format):
        print(video_id, video_format)


def Main():
    app = QApplication(sys.argv)
    w = UIApp()
    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    Main()
