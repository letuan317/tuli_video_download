from __future__ import unicode_literals
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from PIL import Image, ImageTk
import pyperclip as pc
import pyglet
import json
import subprocess
import youtube_dl
import requests
from termcolor import cprint

pyglet.font.add_file('./assets/SourceCodePro-Regular.ttf')

default_font = "SourceCodePro"
color_dark_green = "#264653"
color_light_green = "#b7b7a4"
color_green = "#2a9d8f"
color_yellow = "#e9c46a"
color_orange = "#f4a261"
color_red = "#e76f51"

color_menu = color_light_green

# download button


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def download_clicked():
    showinfo(
        title='Information',
        message='Download button clicked!'
    )


with open('./data.json') as f:
    data = json.load(f)


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


class App(object):
    def __init__(self):
        self.listOfLinks = [data]
        self.listOfComplete = []

    def GUI(self):
        root = tk.Tk()
        root.iconbitmap(
            './assets/bonfire_stake_campfire_blaze_fire_log_icon_194257.ico')
        root.geometry('800x500')
        root.resizable(False, False)
        #root.minsize(800, 500)
        root.title('Youtube Download Demo')

        frame1 = tk.Frame(master=root, width=800,
                          height=90, bg=color_menu)
        frame1.place(x=0, y=0)

        # Paste link Button
        pasteLinkBtnImage = Image.open("./assets/icons8-plus-+-48.png")
        pasteLinkBtnPhoto = ImageTk.PhotoImage(pasteLinkBtnImage)
        pasteLinkBtn = tk.Label(root, image=pasteLinkBtnPhoto, bg=color_menu)
        pasteLinkBtn.place(x=30, y=10)
        pasteLinkBtn.bind('<Button-1>', self.PasteLinkBtnAction)
        pasteLinkText = tk.Label(root, text="Paste Link", bg=color_menu)
        pasteLinkText.place(x=30, y=60)

        # Start Button
        startBtnImage = Image.open("./assets/icons8-play-48.png")
        startBtnPhoto = ImageTk.PhotoImage(startBtnImage)
        startBtn = tk.Label(root, image=startBtnPhoto, bg=color_menu)
        startBtn.place(x=130, y=10)
        startBtn.bind('<Button-1>', self.StartBtnAction)
        startText = tk.Label(root, text="Start", bg=color_menu)
        startText.place(x=142, y=60)

        # Pause Button
        pauseBtnImage = Image.open("./assets/icons8-pause-48.png")
        pauseBtnPhoto = ImageTk.PhotoImage(pauseBtnImage)
        pauseBtn = tk.Label(root, image=pauseBtnPhoto, bg=color_menu)
        pauseBtn.place(x=230, y=10)
        pauseBtn.bind('<Button-1>', self.PauseBtnAction)
        pauseText = tk.Label(root, text="Pause", bg=color_menu)
        pauseText.place(x=240, y=60)

        # Setting Button
        settingBtnPhoto = ImageTk.PhotoImage(
            Image.open("./assets/icons8-settings-48.png"))
        settingBtn = tk.Label(root, image=settingBtnPhoto, bg=color_menu)
        settingBtn.place(x=700, y=10)
        settingBtn.bind('<Button-1>', self.SettingBtnAction)
        settingText = tk.Label(root, text="Setting", bg=color_menu)
        settingText.place(x=705, y=60)

        # list of links
        default_list_x = 0
        default_list_y = 100
        for i in range(0, len(self.listOfLinks)):
            print(self.listOfLinks[i]["id"])
            # 1280 720
            testPhoto = ImageTk.PhotoImage(
                Image.open("./temp/"+self.listOfLinks[i]["id"]+".png").resize((128, 72), Image.ANTIALIAS))
            test = tk.Label(root, image=testPhoto)
            test.place(x=0, y=default_list_y+i*100)

            print(self.listOfLinks[i]["channel"].replace(" ", ""))
            print(self.listOfLinks[i]["thumbnail"])
            print(self.listOfLinks[i]["webpage_url"])
            formats = self.listOfLinks[i]["formats"]
            for f in range(0, len(formats)):
                print(formats[f]["format_id"], formats[f]["format_note"], formats[f]
                      ["filesize"], formats[f]["fps"], formats[f]["quality"], formats[f]["ext"])

        frame = ScrollableFrame(root)

        for i in range(50):
            ttk.Label(frame.scrollable_frame,
                      text="Sample scrolling labelSample scrolling labelSample scrolling labelSample scrolling labelSample scrolling labelSample scrolling labelSample scrolling labelSample scrolling label").pack()

        frame.place(x=0, y=90)

        root.mainloop()

    def PasteLinkBtnAction(self, event):
        yt_link = pc.paste()
        print(yt_link)
        if("https://www.youtube.com/watch?v=" in yt_link):
            yt_link = yt_link.split("&")[0]
            checkAdded = False
            for i in range(0, len(self.listOfLinks)):
                self.listOfLinks[i]["webpage_url"]
                if(yt_link == self.listOfLinks[i]["webpage_url"]):
                    showinfo(
                        title='Notify',
                        message='This link was added'
                    )
                    checkAdded = True
                    break
            if not checkAdded:

                cprint("Its a youtube link", "green")
                ydl_opts = {
                    'logger': MyLogger(),
                    'progress_hooks': [my_hook],
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
                self.listOfLinks.append(video_data)
                thumbnail = requests.get(video_data["thumbnail"])
                open('./temp/'+video_data["id"]+'.png',
                     'wb').write(thumbnail.content)

                cprint("Done info", "green")
        else:
            cprint("Not youtube link", "red")

    def StartBtnAction(self, event):
        print("Start Button clicked!")

    def PauseBtnAction(self, event):
        print("Pause Button clicked!")

    def SettingBtnAction(self, event):
        print("Setting Button clicked!")


if __name__ == '__main__':
    app = App()
    app.GUI()


'''
id
channel
formats:
    format_id
    format_note
    filesize
    fps
    quality
    ext


'''
