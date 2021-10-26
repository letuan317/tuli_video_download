from __future__ import unicode_literals
import youtube_dl
import eel
from termcolor import cprint
import functions
import json
import os
import threading
import multiprocessing

if not os.path.exists("videos"):
    os.system('mkdir videos')
'''
with open('./data.json') as f:
    data = json.load(f)
with open('./data1.json') as f:
    data1 = json.load(f)
data = functions.ExtractInfoData(data)
data1 = functions.ExtractInfoData(data1)
'''

# init data
DEFAULT_PATH_STORAGE = "./videos/"
DEFAULT_PATH_DATABASE = "./database.json"
DOWNLOAD_PROCESSES = None
EXIT_EVENT = threading.Event()
global GLOBAL_THREAD
# Load database
if os.path.exists(DEFAULT_PATH_DATABASE):
    with open(DEFAULT_PATH_DATABASE) as json_file:
        listOfLinks = json.load(json_file)
else:
    listOfLinks = {"data": []}

# Load downloaded video ids
listOfLinksDownloaded = []
if os.path.exists("downloaded.txt"):
    with open("downloaded.txt", "r") as fr:
        for line in fr:
            temp_id = line.split(" ")[1]
            listOfLinksDownloaded.append(temp_id)

# Set web files folder and optionally specify which file types to check for eel.expose()
#   *Default allowed_extensions are: ['.js', '.html', '.txt', '.htm', '.xhtml']
eel.init('web', allowed_extensions=['.js', '.html'])


@eel.expose                         # Expose this function to Javascript
def say_hello_py(x):
    print('Hello from %s' % x)


@eel.expose
def server_log(message):
    print(message)


@eel.expose
def get_info_py(linkData):
    cprint("getInfo: "+linkData, "blue")
    temp = "youtube.com/watch?v="
    if(temp not in linkData):
        eel.error_message_js("Not youtube link: " + linkData)
        cprint("Not youtube link " + linkData, "red")
    else:
        temp_id = linkData.split('watch?v=')[1]
        checkAdded = False
        if(listOfLinks["data"]):
            for item in listOfLinks["data"]:
                if(item["id"] == temp_id):
                    checkAdded = True
                    break
        if not checkAdded:
            cprint("Good link", "green")
            check, data_video = functions.GetYoutubeInfo(
                linkData, listOfLinksDownloaded)
            if(check == False):
                eel.error_message_js(
                    "Youtube link is already downloaded: " + linkData)
            else:
                data_video = functions.ExtractInfoData(
                    data_video)
                listOfLinks["data"].append(data_video)
                with open(DEFAULT_PATH_DATABASE, 'w') as outfile:
                    json.dump(listOfLinks, outfile)
                # need add data_video to bottom of undownload list, before downloaded list
                eel.update_listOfLinks_js(listOfLinks["data"])
        else:
            cprint("Link added", "red")
            eel.error_message_js(
                "Youtube link is already added: " + linkData)


@eel.expose
def update_listOfLinks_py(temp_data):
    cprint("[INFO] Update select_format", "green")
    listOfLinks["data"] = temp_data.copy()


def my_hook(d):
    eel.download_process_js(d)
    try:
        status = 'finished' if(d['status'] == 'finished') else d['_percent_str']+" of "+d['_total_bytes_str'] + \
            " at "+d['_speed_str']+" ETA "+d['_eta_str']
    except Exception as e:
        print(d)
        status = "Downloaded" if(
            "already been recorded in archive" in d) else "Error"

    eel.download_process_js(status)


def run_downloaded_script():
    if(len(listOfLinks["data"]) > 0):
        for idx, video in enumerate(listOfLinks["data"]):
            if(video["status"] == "Wait"):
                ydl_opts = {
                    'format': video["select_format"],
                    'download_archive': './downloaded.txt',
                    'outtmpl': DEFAULT_PATH_STORAGE+video["channel"]+'-'+video["title"]+".%(ext)s",
                    'noplaylist': True,
                    'progress_hooks': [my_hook],
                }

                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video["webpage_url"]])
                video["status"] = "Downloaded"
                with open(DEFAULT_PATH_DATABASE, 'w') as outfile:
                    json.dump(listOfLinks, outfile)


@eel.expose
def start_download_py():
    cprint("[INFO] Start download videos", "green")
    global GLOBAL_THREAD
    #GLOBAL_THREAD = threading.Thread(target=run_downloaded_script, args=())
    GLOBAL_THREAD = multiprocessing.Process(target=run_downloaded_script)
    #GLOBAL_THREAD.daemon = True
    GLOBAL_THREAD.start()


@eel.expose
def stop_download_py():
    cprint("[!] Stop download", "red")
    GLOBAL_THREAD.terminate()


@eel.expose
def windows_close_py():
    cprint("[!] Close windows", "red")


say_hello_py('Python World!')
eel.say_hello_js('Python World!')   # Call a Javascript function
eel.update_listOfLinks_js(listOfLinks["data"])

if __name__ == "__main__":
    eel.start('main.html')


'''
[X] downloaded.txt
[X] load file downloaded.txt
[X] select_format, update format
[X] save temp data, data added to program
[X] load temp data from last work
[X] run download in thread
[X] if downloaded, update item status
[X] stop action, stop thread
[ ] if start, select disable
[ ] refresh button, action sort wait, downloaded
[ ] settings: set videos folder, username, password
[ ] windows close, processes terminate
'''
