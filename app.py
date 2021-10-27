'''

'''
from __future__ import unicode_literals
import youtube_dl
import eel
from termcolor import cprint
import functions
import json
import os
import multiprocessing
import threading
# Set web files folder and optionally specify which file types to check for eel.expose()
#   *Default allowed_extensions are: ['.js', '.html', '.txt', '.htm', '.xhtml']
eel.init('web', allowed_extensions=['.js', '.html'])

if not os.path.exists("videos"):
    os.mkdir('./videos')
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
global GLOBAL_THREAD
# Load database
if os.path.exists(DEFAULT_PATH_DATABASE):
    with open(DEFAULT_PATH_DATABASE) as json_file:
        listOfLinks = json.load(json_file)
    for idx, video in enumerate(listOfLinks["data"]):
        if(video["status"] == "Downloading"):
            video["status"] = "Wait"
    with open(DEFAULT_PATH_DATABASE, 'w') as outfile:
        json.dump(listOfLinks, outfile)
else:
    listOfLinks = {"data": []}

# Load downloaded video ids
listOfLinksDownloaded = []
if os.path.exists("downloaded.txt"):
    with open("downloaded.txt", "r") as fr:
        for line in fr:
            temp_id = line.split(" ")[1]
            listOfLinksDownloaded.append(temp_id)


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
            if(check == False and data_video == None):
                eel.error_message_js(
                    "Youtube link is already downloaded: " + linkData)
            elif(check == True):
                data_video = functions.ExtractInfoData(
                    data_video)
                listOfLinks["data"].append(data_video)
                with open(DEFAULT_PATH_DATABASE, 'w') as outfile:
                    json.dump(listOfLinks, outfile)
                # need add data_video to bottom of undownload list, before downloaded list
                eel.update_listOfLinks_js(listOfLinks["data"])
            else:
                eel.error_message_js(linkData+" "+data_video)
        else:
            cprint("Link added", "red")
            eel.error_message_js(
                "Youtube link is already added: " + linkData)


@eel.expose
def update_listOfLinks_py(temp_data):
    global listOfLinks
    cprint("[INFO] Update select_format", "green")
    listOfLinks["data"] = temp_data.copy()
    with open(DEFAULT_PATH_DATABASE, 'w') as outfile:
        json.dump(listOfLinks, outfile)


def my_hook(d):
    try:
        if(d['status'] == 'finished'):
            status = 'Finished'
            temp_check = False
            for idx, video in enumerate(listOfLinks["data"]):
                if(video["status"] == "Downloading"):
                    video["status"] = "Wait"
                    temp_check = True
            if(temp_check):
                with open(DEFAULT_PATH_DATABASE, 'w') as outfile:
                    json.dump(listOfLinks, outfile)
            eel.update_listOfLinks_js(listOfLinks["data"])
        else:
            status = d['_percent_str']+" of "+d['_total_bytes_str'] + \
                " at "+d['_speed_str']+" ETA "+d['_eta_str']
        eel.download_process_js(status)
    except Exception as e:
        cprint("[!] my_hook: Error downloading", 'red')
        print(e)
        status = "Downloaded" if(
            "already been recorded in archive" in str(d)) else "Error"
        eel.download_process_js(status)


def run_downloaded_script():
    if(listOfLinks["data"]):
        for idx, video in enumerate(listOfLinks["data"]):
            if(video["status"] in ["Wait", "Paused", "Error"]):
                video["status"] = "Downloading"
                eel.update_listOfLinks_js(listOfLinks["data"])
                ydl_opts = {
                    'format': video["select_format"],
                    'download_archive': './downloaded.txt',
                    'outtmpl': DEFAULT_PATH_STORAGE+video["channel"]+'-'+video["title"]+".%(ext)s",
                    'noplaylist': True,
                    'progress_hooks': [my_hook],
                }
                try:
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video["webpage_url"]])
                    video["status"] = "Downloaded"
                    with open(DEFAULT_PATH_DATABASE, 'w') as outfile:
                        json.dump(listOfLinks, outfile)
                except Exception as e:
                    cprint("[!] run_downloaded_script: Error downloading", 'red')
                    print(e)
                    eel.error_message_js(video["title"][:20]+" "+e)
                    video["status"] = "Error"
                    eel.update_listOfLinks_js(listOfLinks["data"])
                    continue


@eel.expose
def start_download_py():
    cprint("[INFO] Start download videos", "green")

    global GLOBAL_THREAD
    #GLOBAL_THREAD = threading.Thread(target=run_downloaded_script, args=())
    #GLOBAL_THREAD = multiprocessing.Process(target=run_downloaded_script)
    GLOBAL_THREAD = functions.KThread(target=run_downloaded_script)
    #GLOBAL_THREAD.daemon = True
    GLOBAL_THREAD.start()
    # run_downloaded_script()


@eel.expose
def stop_download_py():
    cprint("\n[!] Stop download", "red")
    # GLOBAL_THREAD.terminate()
    GLOBAL_THREAD.kill()
    for idx, video in enumerate(listOfLinks["data"]):
        if(video["status"] == "Downloading"):
            video["status"] = "Paused"
            eel.update_listOfLinks_js(listOfLinks["data"])
            eel.download_process_js("Paused")
            break


@eel.expose                         # Expose this function to Javascript
def say_hello_py(x):
    print('Hello from %s' % x)


say_hello_py('Python World!')
eel.say_hello_js('Python World!')   # Call a Javascript function
eel.update_listOfLinks_js(listOfLinks["data"])
eel.start('main.html')
# if __name__ == "__main__":
#    eel.start('main.html')
