from __future__ import unicode_literals
import time
import youtube_dl
import yt_dlp
from yt_dlp.postprocessor.common import PostProcessor


from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import webbrowser
from urllib import request
from termcolor import cprint
import json
import os
import sys
import glob
from functools import partial

import functions
import essentials

program_name = "Youtube Video Download"

global_video_status = ["Wait", "Paused", "Downloading", "Downloaded", "Error"]

global_log = essentials.Logger()
global_log.info("Start new session")


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
        pass

    def error(self, msg):
        cprint("MyLogger: " + msg, "red")


class MyCustomPP(PostProcessor):
    def run(self, info):
        self.to_screen('Doing stuff')
        return [], info


class ThreadClass(QThread):
    any_signal = pyqtSignal(int)
    update_content_signal = pyqtSignal(list)
    update_database_signal = pyqtSignal(list)
    update_process_signal = pyqtSignal(str)
    # update_error_signal = pyqtSignal(str)
    update_done_signal = pyqtSignal(bool)

    def __init__(self, parent=None, force=False, listOfLinks=[], DEFAULT_PATH_DOWNLOADED=None, DEFAULT_PATH_STORAGE=None):
        super(ThreadClass, self).__init__(parent)
        self.is_running = True
        self.force = force
        self.listOfLinks = listOfLinks
        self.DEFAULT_PATH_DOWNLOADED = DEFAULT_PATH_DOWNLOADED
        self.DEFAULT_PATH_STORAGE = DEFAULT_PATH_STORAGE

    def HookGetStatus(self, d):
        try:
            if (d['status'] == 'finished'):
                status = 'Finished'
            else:
                status = d['_percent_str'] + " of " + d['_total_bytes_str'] + \
                    " at " + d['_speed_str'] + " ETA " + d['_eta_str']
            self.update_process_signal.emit(status)
        except Exception as e:
            cprint("[!] my_hook: Error downloading", 'red')
            print(e)
            status = "Downloaded" if (
                "already been recorded in archive" in str(d)) else "Error"
            self.update_process_signal.emit(status)

    def run(self):
        self.update_done_signal.emit(False)
        cprint("[+] Starting download ...", "yellow")
        if self.listOfLinks and self.DEFAULT_PATH_DOWNLOADED != None and self.DEFAULT_PATH_STORAGE != None:
            for idx, video in enumerate(self.listOfLinks):
                is_completed = False
                # FIXME error cant force download
                if(video["status"] in global_video_status) and (video["status"] != "Downloaded"):
                    video["status"] = "Downloading"
                    self.update_content_signal.emit(self.listOfLinks)
                    output_file_without_extension = self.DEFAULT_PATH_STORAGE + '/' + \
                        video["channel_id"]+"-" + video["channel"]+'-' + \
                        video["title"] + "-f" + video["select_format"]
                    output_file = output_file_without_extension + ".%(ext)s"
                    ydl_opts = {
                        'outtmpl': output_file,
                        'noplaylist': True,
                        'progress_hooks': [self.HookGetStatus],
                        'logger': MyLogger(),
                    }
                    if not self.force:
                        ydl_opts['download_archive'] = self.DEFAULT_PATH_DOWNLOADED
                    if video["select_format"] == "bestaudio":
                        ydl_opts['format'] = video["select_format"]
                        ydl_opts['postprocessors'] = [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }]

                    else:
                        ydl_opts['format'] = video["select_format"] + \
                            '+bestaudio'

                    message = "[*] Starting download video " + video["title"]
                    cprint(message, "yellow")
                    global_log.info(message)
                    try:
                        global_log.info("Trying yt_dlp post_processor...")
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.add_post_processor(MyCustomPP())
                            ydl.extract_info(video["webpage_url"])
                        is_completed = True
                    except Exception as e:
                        cprint("Download with yt_dlp: "+str(e), "red")
                        global_log.error(e)
                        try:
                            global_log.info("Trying youtube_dl...")
                            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                                ydl.download(video["webpage_url"])
                            is_completed = True
                        except Exception as e:
                            cprint("Download with youtube_dl: "+str(e), "red")
                            global_log.error(e)
                    if is_completed or glob.glob(output_file_without_extension+".*"):
                        video["status"] = "Downloaded"
                        self.update_content_signal.emit(self.listOfLinks)
                        self.update_database_signal.emit(self.listOfLinks)
                    else:
                        cprint("Video cant be downloaded", "red")
                        video["status"] = "Error"
                        self.update_content_signal.emit(self.listOfLinks)
                        self.update_database_signal.emit(self.listOfLinks)
                        # self.update_error_signal.emit(str(e))
        self.update_done_signal.emit(True)

    def stop(self):
        self.is_running = False
        cprint("[-] Stopping download ...", "yellow")
        self.terminate()


class UIApp(QWidget):
    def __init__(self):
        super().__init__()
        self.window_width = 900
        self.window_height = 500

        self.setGeometry(80, 50, self.window_width, self.window_height)
        self.setMinimumSize(self.window_width, self.window_height)
        self.setWindowTitle(program_name)
        self.setWindowIcon(QIcon('img/streaming.png'))

        self.colorDarkGreen = "#264653"
        self.colorGreen = "#2a9d8f"
        self.colorGreenArmy = "#6b705c"
        self.colorYellow = "#e9c46a"
        self.colorOrange = "#f4a261"
        self.colorRed = "#e76f51"

        self.InitData()
        self.IsProcessing = False
        self.IsProcessingSetting = False

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
        self.SettingsPanel()
        self.settingsPanelWidget.setHidden(True)

        self.ReloadWindows()

        self.temp_select_format = None

    def AddMenuButton(self, name, text_adjust, path_img, x, y, action):
        btnIconAddfile = QLabel(self)
        btnIconAddfile.setPixmap(QPixmap(path_img))
        btnIconAddfile.move(x, y)
        btnIconAddfile.mousePressEvent = action
        text = QLabel(name, self)
        text.move(x+text_adjust, y + self.sizeMenuIcon + 5)
        text.setStyleSheet("QWidget {color: white}")
        return btnIconAddfile

    def MenuShowButton(self, is_all_icons=False):
        self.btnPaste.setPixmap(QPixmap('img/icons8-plus-48.png'))
        self.btnAddFile.setPixmap(QPixmap('img/icons8-add-file-48.png'))
        self.btnDownload.setPixmap(QPixmap('img/icons8-download-48.png'))
        self.btnPause.setPixmap(QPixmap('img/icons8-pause-hide-48.png'))
        self.btnOpenFolder.setPixmap(QPixmap('img/icons8-folder-48.png'))
        self.btnSort.setPixmap(QPixmap('img/icons8-sort-48.png'))
        self.btnClear.setPixmap(QPixmap('img/icons8-clear-48.png'))
        self.btnSetting.setPixmap(QPixmap('img/icons8-setting-48.png'))
        self.forceDownload.setHidden(False)

    def MenuHideButton(self, is_all_icons=False):
        self.btnPaste.setPixmap(QPixmap('img/icons8-plus-hide-48.png'))
        # self.btnPaste.move(self.posXMenuIcon, self.posYMenuIcon)
        self.btnAddFile.setPixmap(QPixmap('img/icons8-add-file-hide-48.png'))
        self.btnDownload.setPixmap(QPixmap('img/icons8-download-hide-48.png'))
        if is_all_icons:
            self.btnPause.setPixmap(QPixmap('img/icons8-pause-hide-48.png'))
        else:
            self.btnPause.setPixmap(QPixmap('img/icons8-pause-48.png'))
        self.btnSetting.setPixmap(QPixmap('img/icons8-setting-hide-48.png'))
        self.btnOpenFolder.setPixmap(QPixmap('img/icons8-folder-48.png'))
        self.btnSort.setPixmap(QPixmap('img/icons8-sort-hide-48.png'))
        self.btnClear.setPixmap(QPixmap('img/icons8-clear-hide-48.png'))
        self.forceDownload.setHidden(True)

    def MenuContainer(self):
        margin = 20

        self.menuBackground = QFrame(self)
        self.menuBackground.setStyleSheet(
            "QWidget {background-color:%s}" % self.colorDarkGreen)
        self.btnPaste = self.AddMenuButton("Paste", 10, 'img/icons8-plus-48.png',
                                           self.posXMenuIcon, self.posYMenuIcon, self.ActionPasteLink)
        self.btnAddFile = self.AddMenuButton("Add", 13, 'img/icons8-add-file-48.png', self.posXMenuIcon +
                                             self.sizeMenuIcon+margin, self.posYMenuIcon, self.ActionAddFile)
        self.btnDownload = self.AddMenuButton("Download", 0, 'img/icons8-download-48.png', self.posXMenuIcon +
                                              2*(self.sizeMenuIcon+margin), self.posYMenuIcon, self.ActionDownload)
        self.btnPause = self.AddMenuButton("Pause", 8, 'img/icons8-pause-hide-48.png', self.posXMenuIcon +
                                           3*(self.sizeMenuIcon+margin), self.posYMenuIcon, self.ActionPause)
        self.btnOpenFolder = self.AddMenuButton("Open", 8, 'img/icons8-folder-48.png', self.posXMenuIcon+4*(
            self.sizeMenuIcon+margin), self.posYMenuIcon, self.ActionOpenFolder)
        self.btnSort = self.AddMenuButton("Sort", 12, 'img/icons8-sort-48.png', self.posXMenuIcon +
                                          5*(self.sizeMenuIcon+margin), self.posYMenuIcon, self.ActionSort)
        self.btnClear = self.AddMenuButton("Clear", 10, 'img/icons8-clear-48.png', self.posXMenuIcon +
                                           6*(self.sizeMenuIcon+margin), self.posYMenuIcon, self.ActionClear)

        self.btnSetting = QLabel(self)
        self.btnSetting.setPixmap(QPixmap("img/icons8-setting-48.png"))
        self.btnSetting.mousePressEvent = self.ActionSetting

        self.textSetting = QLabel("Settings", self)
        self.textSetting.setStyleSheet("QWidget {color: white}")

        self.forceDownload = QCheckBox("Force Download", self)
        self.forceDownload.setChecked(False)
        self.forceDownload.stateChanged.connect(
            lambda: self.ContentContainer())
        self.forceDownload.move(self.posXMenuIcon + 8 *
                                (self.sizeMenuIcon+margin), self.posYMenuIcon)
        self.forceDownload.setStyleSheet("QWidget {color: white}")

    def ReloadWindows(self):
        self.timer = QTimer()
        self.timer.start(0)
        self.timer.timeout.connect(self.UpdateScrollContent)

    def ContentContainer(self):
        # BUG not responding when reload, so need to make a thread
        self.videosContainer = []
        self.scroll_widget = QWidget()
        self.scroll_vbox = QVBoxLayout()
        start = time.time()
        for idx, video in enumerate(self.listOfLinks["data"]):
            temp = self.VideoContainer(video)
            self.videosContainer.append(temp)

            self.scroll_vbox.addWidget(temp["videoBackground"])
            self.scroll_vbox.addWidget(temp["thumbnail"])
            self.scroll_vbox.addWidget(temp["title"])
            self.scroll_vbox.addWidget(temp["channel"])
            self.scroll_vbox.addWidget(temp["combo_box"])
            self.scroll_vbox.addWidget(temp["status"])
            self.scroll_vbox.addWidget(temp["btn_link"])
            self.scroll_vbox.addWidget(temp["btn_delete"])
        end = time.time()
        global_log.critical("ContentContainer loop : " + str(end-start))

        start = time.time()
        self.scroll_widget.setLayout(self.scroll_vbox)
        self.scroll.setWidget(self.scroll_widget)
        end = time.time()
        global_log.critical("ContentContainer scroll set : " + str(end-start))
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
        if self.IsProcessing:
            self.footerMessage.setGeometry(
                310, self.window_height-self.sizeFooterContainer, self.window_width-310, self.sizeFooterContainer)
        else:
            self.footerMessage.setGeometry(
                5, self.window_height-self.sizeFooterContainer, self.window_width, self.sizeFooterContainer)
        self.footerProgress.setGeometry(
            5, self.window_height-self.sizeFooterContainer+round(self.sizeFooterContainer/4), 300, round(self.sizeFooterContainer/2))

        self.UpdateScrollContent()

    def UpdateScrollContent(self):
        for i in range(0, len(self.videosContainer)):
            self.videosContainer[i]["videoBackground"].setGeometry(
                5, 110*(i)+10, self.window_width-30, 100)
            self.videosContainer[i]["thumbnail"].setGeometry(
                10, 110*(i)+15, 200, 90)
            self.videosContainer[i]["title"].setGeometry(
                175, 110*(i)+10, self.window_width-280, 50)
            self.videosContainer[i]["channel"].setGeometry(
                175, 110*(i)+60, round((self.window_width-180)*2/10), 50)
            self.videosContainer[i]["combo_box"].setGeometry(
                175+round((self.window_width-180)*2/10)+5, 110*(i)+72, round((self.window_width-180)*6/10), 25)
            self.videosContainer[i]["status"].setGeometry(
                175+round((self.window_width-180)*8/10)+10, 110*(i)+60, round((self.window_width-180)*1.9/10)-10, 50)
            self.videosContainer[i]["btn_link"].setGeometry(
                self.window_width - 90, 110*(i)+15, 24, 24)
            self.videosContainer[i]["btn_delete"].setGeometry(
                self.window_width - 60, 110*(i)+15, 24, 24)

    def VideoContainer(self, video):
        videoBackground = QFrame()
        videoBackground.setStyleSheet(
            "QWidget {border-radius: 5px; background-color:%s}" % self.colorGreenArmy)

        data = request.urlopen(video["thumbnail"]).read()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        pixmap = pixmap.scaled(200, 90, Qt.KeepAspectRatio)
        thumbnail = QLabel()
        thumbnail.setPixmap(pixmap)

        title = QLabel(video["channel_id"]+"-"+video["title"])
        title.setStyleSheet(
            "QWidget {color: white; font-size: 15px; font-weight: bold}")

        channel = QLabel(video["channel"])
        channel.setStyleSheet("QWidget {color: white;}")

        combo_box = QComboBox()
        for ft in video["formats"]:
            combo_box.addItem("bestaudio") if ft == "bestaudio" else combo_box.addItem(", ".join((ft["format_id"], ft["format"], ft["ext"], ft["format_note"], str(
                ft["fps"])+" fps", functions.ConvertVideoSize(ft["filesize"]))))
        combo_box.activated.connect(
            lambda: self.UpdateSelectFormat(video["id"], combo_box.currentText()))

        if video["status"] == "Wait":
            colorStatus = "white"
        elif video["status"] == "Downloading":
            colorStatus = self.colorYellow
        elif video["status"] == "Downloaded":
            colorStatus = self.colorGreen
            if self.forceDownload.isChecked() == False:
                combo_box.setEnabled(False)
        else:
            print(video["status"])
            colorStatus = self.colorRed
        status = QLabel(video["status"])
        status.setStyleSheet(
            "QWidget {color: "+colorStatus+"; font-size: 15px; font-weight: bold;}")

        btn_link = QLabel()
        pixmap = QPixmap("img/icons8-link-48.png")
        pixmap = pixmap.scaled(24, 24, Qt.KeepAspectRatio)
        btn_link.setPixmap(pixmap)
        btn_link.mousePressEvent = partial(
            self.OpenVideoUrlLink, url_link=video["webpage_url"])

        btn_delete = QLabel()
        pixmap = QPixmap("img/icons8-delete-bin-48.png")
        pixmap = pixmap.scaled(24, 24, Qt.KeepAspectRatio)
        btn_delete.setPixmap(QPixmap(pixmap))
        btn_delete.mousePressEvent = partial(
            self.DeleteVideoInList, video_id=video["id"])

        if self.IsProcessing:
            combo_box.setEnabled(False)
            btn_link.setHidden(True)
            btn_delete.setHidden(True)
        '''
        videoBackground.setGeometry(5, y+10, 800, 100)
        thumbnail.move(10, y+5)
        title.setGeometry(175, y+10, 600, 50)
        channel.setGeometry(175, y+60, 160, 50)
        combo_box.setGeometry(175, y+72, 150, 50)
        status.setGeometry(175, y+60, 100, 50)
        '''

        return {"videoBackground": videoBackground, "thumbnail": thumbnail,
                "title": title, "channel": channel, "combo_box": combo_box, "status": status, "btn_link": btn_link, "btn_delete": btn_delete}

    def ActionPasteLink(self, event):
        if not self.IsProcessing:
            cprint('[INFO] ActionPasteLink', "green")
            text_clipborad = QApplication.clipboard().text()
            message = "Clipboard: " + text_clipborad
            global_log.info(message)
            self.FooterUpdate(message)
            self.IsProcessing = True
            self.GetInfo(text_clipborad)
            self.IsProcessing = False
            self.ContentContainer()

    def ActionAddFile(self, event):
        if not self.IsProcessing:
            cprint('[INFO] ActionAddFile', "green")
            fileName = QFileDialog.getOpenFileName(self, 'OpenFile')
            if type(fileName) == str:
                fr = open(fileName, 'r')
                for url_link in fr:
                    self.GetInfo(url_link.rstrip("\n"))
                fr.close()

    def ActionDownload(self, event):
        if not self.IsProcessing:
            cprint('[INFO] ActionDownload', "green")
            self.FooterUpdate("[INFO] Starting download", "green")
            self.IsProcessing = True
            self.MenuHideButton()
            # self.GLOBAL_THREAD = functions.KThread(target=self.RunDownloadedScript)
            # self.GLOBAL_THREAD.start()
            self.thread = ThreadClass(
                parent=None, force=self.forceDownload.isChecked(), listOfLinks=self.listOfLinks["data"], DEFAULT_PATH_DOWNLOADED=self.DEFAULT_PATH_DOWNLOADED, DEFAULT_PATH_STORAGE=self.DEFAULT_PATH_STORAGE)
            self.thread.start()
            self.thread.update_content_signal.connect(
                self.CallThreadUpdateContent)
            self.thread.update_database_signal.connect(
                self.CallThreadUpdateDatabase)
            self.thread.update_process_signal.connect(
                self.CallThreadUpdateProcess)
            self.thread.update_done_signal.connect(self.CallThreadUpdateDone)
            # self.thread.update_error_signal.connect(self.CallThreadUpdateError)

    def CallThreadUpdateContent(self, temp_list):
        self.listOfLinks["data"] = temp_list
        self.ContentContainer()

    def CallThreadUpdateDatabase(self, temp_list):
        self.listOfLinks["data"] = temp_list
        self.UpdateDatabase()

    def CallThreadUpdateProcess(self, temp_str):
        self.FooterUpdate(temp_str)

    def CallThreadUpdateDone(self, is_done):
        if is_done:
            self.IsProcessing = False
            self.MenuShowButton()
            self.ContentContainer()
            self.FooterUpdate("Done", "green")

    # def CallThreadUpdateError(self, temp_str):
        # global_log.error(temp_str)

    def ActionPause(self, event):
        if self.IsProcessing and not self.IsProcessingSetting:
            cprint('[INFO] ActionPause', "green")
            self.thread.stop()
            for idx, video in enumerate(self.listOfLinks["data"]):
                if video["status"] == "Downloading":
                    video["status"] = "Paused"
                    self.ContentContainer()
                    break
            self.IsProcessing = False
            self.MenuShowButton()
            self.ContentContainer()
            self.FooterUpdate("Paused", "yellow")

    def ActionOpenFolder(self, event):
        cprint('[INFO] ActionOpenFolder', "green")
        self.FooterUpdate("Opening the video folder", "green")
        if(sys.platform == "win32"):
            os.startfile(self.DEFAULT_PATH_STORAGE)
        elif(sys.platform == "darwin"):
            os.system('open "%s"' % self.DEFAULT_PATH_STORAGE)
        elif(sys.platform == "linux"):
            os.system('xdg-open "%s"' % self.DEFAULT_PATH_STORAGE)

    def ActionSort(self, event):
        if not self.IsProcessing:
            cprint('[INFO] ActionAddFile', "green")
            temp_list = list()
            temp_list2 = list()
            for idx, video in enumerate(self.listOfLinks["data"]):
                if(video["status"] == "Downloaded"):
                    temp_list2.append(video)
                else:
                    temp_list.append(video)
            self.listOfLinks["data"] = temp_list + temp_list2
            self.UpdateDatabase()
            self.ContentContainer()

    def ActionClear(self, event):
        if not self.IsProcessing:
            cprint('[INFO] ActionAddFile', "green")
            temp_list = []
            for idx, video in enumerate(self.listOfLinks["data"]):
                if video["status"] != "Downloaded":
                    temp_list.append(video)
            self.listOfLinks["data"] = temp_list.copy()
            self.UpdateDatabase()
            self.ContentContainer()

    def ActionSetting(self, event):
        if not self.IsProcessing:
            cprint('[INFO] ActionSetting', "green")
            self.IsProcessing = True
            self.IsProcessingSetting = True
            self.MenuHideButton(is_all_icons=True)
            self.scroll.setHidden(True)
            self.settingsPanelWidget.setHidden(False)

    def SettingsPanel(self):
        self.settingsPanelWidget = QWidget(self)
        self.settingsPanelWidget.setFont(QFont("Arial", 12))

        self.settingUsername = QLineEdit(self.DEFAULT_USERNAME)
        self.settingPassword = QLineEdit(self.DEFAULT_PASSWORD)
        self.settingPassword.setEchoMode(QLineEdit.Password)
        self.settingPathStorage = QLineEdit(self.DEFAULT_PATH_STORAGE)
        self.settingPathStorage.setMaximumWidth(500)
        self.settingPathStorage.setReadOnly(True)
        b3 = QPushButton("Open")
        b3.setStyleSheet("QWidget {background-color:white}")
        b3.setMaximumWidth(100)
        b3.clicked.connect(self.SelectStoragePath)
        self.settingPathDownloaded = QLineEdit(self.DEFAULT_PATH_DOWNLOADED)
        self.settingPathDownloaded.setMaximumWidth(500)
        self.settingPathDownloaded.setReadOnly(True)
        b4 = QPushButton("Open")
        b4.setStyleSheet("QWidget {background-color:white;}")
        b4.setMaximumWidth(100)
        b4.clicked.connect(self.SelectDownloadArchivePath)
        b5 = QPushButton("Save")
        b5.setStyleSheet("QWidget {background-color:green;color:white}")
        b5.setMaximumWidth(100)
        b5.clicked.connect(self.SaveSettings)
        b6 = QPushButton("Cancel")
        b6.setStyleSheet("QWidget {background-color:red;color:white}")
        b6.setMaximumWidth(100)
        b6.clicked.connect(self.CancelSetting)

        flo = QFormLayout()
        flo.addRow("Username", self.settingUsername)
        flo.addRow("Password", self.settingPassword)
        vbox1 = QHBoxLayout()
        vbox1.addWidget(self.settingPathStorage)
        vbox1.addWidget(b3)
        flo.addRow("Videos Storage ", vbox1)
        vbox2 = QHBoxLayout()
        vbox2.addWidget(self.settingPathDownloaded)
        vbox2.addWidget(b4)
        flo.addRow("Download Archive", vbox2)
        vbox3 = QHBoxLayout()
        vbox3.addWidget(b5)
        vbox3.addWidget(b6)
        flo.addRow("", vbox3)

        self.settingsPanelWidget.setLayout(flo)
        self.settingsPanelWidget.setStyleSheet(
            "QWidget {background-color:#ddb892}")
        self.settingsPanelWidget.setGeometry(0, 100, 800, 380)

    def Footer(self, text):
        self.footerBackground = QFrame(self)
        self.footerBackground.setStyleSheet(
            "QWidget {background-color:%s}" % self.colorDarkGreen)
        self.footerMessage = QLabel(text, self)
        self.footerMessage.setStyleSheet("QWidget {color: white}")

        self.footerProgress = QProgressBar(self)
        self.footerProgress.setHidden(True)
        self.footerProgress.setTextVisible(False)
        self.footerProgress.setMaximum(100)
        self.footerProgress.setStyleSheet(
            "QProgressBar{ color: yellow; } ")

    def FooterUpdate(self, message, color="white"):
        # TODO need to create a function for footer message, to prevent repeat
        cprint(message, color)
        list_number_str = [str(i) for i in range(10)]
        if(self.IsProcessing) and any(i in message for i in list_number_str):
            try:
                self.footerProgress.setHidden(False)
                self.footerProgress.setValue(
                    round(float(message.split("%")[0].replace(" ", ""))))
                self.footerMessage.setGeometry(
                    310, self.window_height-self.sizeFooterContainer, self.window_width-310, self.sizeFooterContainer)
                self.ReloadWindows()
            except Exception as e:
                self.footerProgress.setHidden(True)
        else:
            self.footerProgress.setHidden(True)
            self.footerMessage.setGeometry(
                5, self.window_height-self.sizeFooterContainer, self.window_width, self.sizeFooterContainer)
        self.footerMessage.setText(message)
        self.footerMessage.setStyleSheet("QWidget {color: "+color+"}")

    def InitData(self):
        # init data
        self.DEFAULT_PATH_CONFIG = os.path.normpath(
            os.path.join(os.getcwd(), "./config.json"))
        self.DEFAULT_PATH_STORAGE = os.path.normpath(
            os.path.join(os.getcwd(), "./videos"))
        self.DEFAULT_PATH_DOWNLOADED = os.path.normpath(
            os.path.join(os.getcwd(), "./downloaded.txt"))
        self.DEFAULT_PATH_DATABASE = os.path.normpath(
            os.path.join(os.getcwd(), "./database.json"))
        self.DEFAULT_PATH_VIDEO_ERROR_LOG = os.path.normpath(
            os.path.join(os.getcwd(), "./error_video.log"))
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
            self.DEFAULT_PATH_STORAGE = data_config["path_storage"]
            self.DEFAULT_PATH_DOWNLOADED = data_config["path_downloaded"]
            self.DEFAULT_USERNAME = data_config["username"]
            self.DEFAULT_PASSWORD = data_config["password"]
        else:
            with open(self.DEFAULT_PATH_CONFIG, 'w') as outfile:
                json.dump({
                    "username": "",
                    "password": "",
                    "path_storage": self.DEFAULT_PATH_STORAGE,
                    "path_downloaded": self.DEFAULT_PATH_DOWNLOADED
                }, outfile, indent=2
                )
            self.DEFAULT_USERNAME = ""
            self.DEFAULT_PASSWORD = ""

        if not os.path.exists(self.DEFAULT_PATH_STORAGE):
            os.mkdir(self.DEFAULT_PATH_STORAGE)

        cprint("[INFO] {} {}".format(self.DEFAULT_PATH_STORAGE,
                                     self.DEFAULT_PATH_DOWNLOADED), 'green')

        # Load database
        if os.path.exists(self.DEFAULT_PATH_DATABASE):
            with open(self.DEFAULT_PATH_DATABASE) as json_file:
                self.listOfLinks = json.load(json_file)
            for idx, video in enumerate(self.listOfLinks["data"]):
                if(video["status"] in global_video_status) and (video["status"] != "Downloaded"):
                    video["status"] = "Wait"
            with open(self.DEFAULT_PATH_DATABASE, 'w') as outfile:
                json.dump(self.listOfLinks, outfile, indent=2)
        else:
            self.listOfLinks = {"data": []}
        self.LoadDownloadedTxt()
        if not os.path.exists(self.DEFAULT_PATH_VIDEO_ERROR_LOG):
            with open(self.DEFAULT_PATH_VIDEO_ERROR_LOG, 'w') as fw:
                pass

    def LoadDownloadedTxt(self):
        # Load downloaded video ids
        if os.path.exists(self.DEFAULT_PATH_DOWNLOADED):
            self.listOfLinksDownloaded = []
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
                answer = MessageBox(self,
                                    "Comfirmation", url_link+" is a playlist. Do you want download them?")
                if answer:
                    self.PlaylistVideosLink(url_link)
            elif "youtube.com" in url_link and any(temp in url_link for temp in ["/channel/", "/c/"]):
                self.FooterUpdate(url_link + " is a youtube channel", "green")
                # Youtube channel
                answer = MessageBox(self,
                                    "Comfirmation", url_link+" is a channel. Do you want download all videos?")
                if answer:
                    self.PlaylistVideosLink(url_link)
            else:
                message = "[!] get_info_py: " + url_link
                self.FooterUpdate(message, "red")

    def SingleVideoLink(self, url_link, temp_id, restricted=False):
        is_restricted = restricted
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
                    url_link, self.listOfLinksDownloaded, restricted=is_restricted)
                if(check == False and data_video == None):
                    message = "[!] Link is already downloaded: " + temp_id
                    self.FooterUpdate(message, "red")
                elif(check == True):
                    self.FooterUpdate(
                        "[*] Trying to extract info video", "green")

                    data_video = functions.ExtractInfoData(
                        data_video, restricted=is_restricted)

                    self.FooterUpdate(
                        "[*] Extract info video SUCCESSFUL", "green")
                    self.listOfLinks["data"].append(data_video)
                    with open(self.DEFAULT_PATH_DATABASE, 'w') as outfile:
                        json.dump(self.listOfLinks, outfile, indent=2)

                    self.ContentContainer()

                else:   # link cant be get info by age, ...
                    # TODO restrict by age, login to download
                    '''
                    ERROR: Sign in to confirm your age
                    This video may be inappropriate for some users.
                    '''
                    global_log.error(
                        "ERROR: Sign in to confirm your age " + url_link)
                    if not is_restricted and "Sign in to confirm your age" in data_video:
                        message = "[!] " + data_video
                        self.FooterUpdate(message, "red")
                        self.SingleVideoLink(
                            url_link, temp_id, restricted=True)
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
        check, list_videos_data = functions.GetYoutubePlaylistInfo(
            url_link)
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
            global_log.error(list_videos_data)
            self.FooterUpdate(list_videos_data, "red")

            temp_list = []
            with open(self.DEFAULT_PATH_VIDEO_ERROR_LOG, "r") as fr:
                for line in fr:
                    temp_list.append(line.strip("\r\n"))
            if not any(url_link == x for x in temp_list):
                with open(self.DEFAULT_PATH_VIDEO_ERROR_LOG, "a") as fa:
                    fa.write(url_link+"\n")

    def UpdateSelectFormat(self, video_id, combo_current_text):
        cprint("[INFO] UpdateSelectFormat", "green")
        new_video_format = combo_current_text.split(",")[0]
        for idx, video in enumerate(self.listOfLinks["data"]):
            if video["id"] == video_id:
                video["select_format"] = new_video_format
                if new_video_format != "bestaudio":
                    # format_index = next((index for (index, v) in enumerate( video["formats"]) if v["format_id"] == new_video_format), None)
                    for idx, formatt in enumerate(video["formats"]):
                        if(formatt != "bestaudio"):
                            if formatt["format_id"] == new_video_format:
                                break
                    video["formats"].insert(
                        0, video["formats"].pop(idx))
                else:
                    video["formats"].remove("bestaudio")
                    video["formats"].insert(0, "bestaudio")
                break
        self.UpdateDatabase()

    def OpenVideoUrlLink(self, event, url_link=None):
        if(url_link != None):
            webbrowser.open(url_link)

    def DeleteVideoInList(self, event, video_id=None):
        if not self.IsProcessing:
            if(video_id != None):
                for idx, video in enumerate(self.listOfLinks["data"]):
                    if(video["id"] == video_id):
                        self.listOfLinks["data"].remove(video)
                        self.UpdateDatabase()
                        self.ContentContainer()
                        break

    def UpdateDatabase(self):
        with open(self.DEFAULT_PATH_DATABASE, 'w') as json_outfile:
            json.dump(self.listOfLinks, json_outfile, indent=2)

        self.FooterUpdate("[INFO] Updated database.js", "green")

    def SelectStoragePath(self):
        dir_path = QFileDialog.getExistingDirectory(
            self, "Choose Directory")
        self.settingPathStorage.setText(dir_path)

    def SelectDownloadArchivePath(self):
        dir_path = QFileDialog.getExistingDirectory(
            self, "Choose Directory")
        self.settingPathDownloaded.setText(dir_path+"/downloaded.txt")

    def SaveSettings(self):
        # cprint(self.settingUsername.text(), 'yellow')
        # cprint(self.settingPassword.text(), 'yellow')
        # cprint(self.settingPathStorage.text(), 'yellow')
        # cprint(self.settingPathDownloaded.text(), 'yellow')
        self.DEFAULT_USERNAME = self.settingUsername.text()
        self.DEFAULT_PASSWORD = self.settingPassword.text()
        self.DEFAULT_PATH_STORAGE = self.settingPathStorage.text()
        self.DEFAULT_PATH_DOWNLOADED = self.settingPathDownloaded.text()
        with open(self.DEFAULT_PATH_CONFIG, 'w') as json_file:
            json.dump({
                "username": self.DEFAULT_USERNAME,
                "password": self.DEFAULT_PASSWORD,
                "path_storage": self.DEFAULT_PATH_STORAGE,
                "path_downloaded": self.DEFAULT_PATH_DOWNLOADED
            }, json_file, indent=2)

        self.FooterUpdate("[INFO] Updated setting in config.json", "green")
        self.LoadDownloadedTxt()
        self.CancelSetting()

    def CancelSetting(self):
        self.IsProcessing = False
        self.IsProcessingSetting = False
        self.MenuShowButton()
        self.scroll.setHidden(False)
        self.settingsPanelWidget.setHidden(True)


def Main():
    app = QApplication(sys.argv)
    w = UIApp()
    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    Main()
