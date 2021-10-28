
from __future__ import unicode_literals
import sys
import youtube_dl
import eel
from termcolor import cprint
import functions
import json
import os
import subprocess
# Set web files folder and optionally specify which file types to check for eel.expose()
#   *Default allowed_extensions are: ['.js', '.html', '.txt', '.htm', '.xhtml']
eel.init('web', allowed_extensions=['.js', '.html'])


# init data
DEFAULT_PATH_CONFIG = "./config.json"
DEFAULT_PATH_STORAGE = "./videos/"
DEFAULT_PATH_DOWNLOADED = "./downloaded.txt"
DEFAULT_PATH_DATABASE = "./database.json"
DEFAULT_PATH_VIDEO_ERROR_LOG = "./error_video.log"

# Load config from config.js
if os.path.exists(DEFAULT_PATH_CONFIG):
    with open(DEFAULT_PATH_CONFIG) as json_file:
        data_config = json.load(json_file)
    DEFAULT_PATH_STORAGE = data_config["path_storage"]+"/"
    DEFAULT_PATH_DOWNLOADED = data_config["path_downloaded"] + \
        "/downloaded.txt"

# Send the setup to js
eel.setup_config_js({
    "path_storage": DEFAULT_PATH_STORAGE[:len(DEFAULT_PATH_STORAGE)-1],
    "path_downloaded": DEFAULT_PATH_DOWNLOADED[:len(DEFAULT_PATH_DOWNLOADED)-len("/downloaded.txt")]
}
)

if not os.path.exists(DEFAULT_PATH_STORAGE):
    os.mkdir(DEFAULT_PATH_STORAGE)


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
            listOfLinksDownloaded.append(temp_id.replace("\n", ""))


@eel.expose
def get_info_py(linkData):
    cprint("getInfo: "+linkData, "blue")
    temp = "youtube.com/watch?v="
    if(temp not in linkData):
        eel.error_message_js("Not youtube link: " + linkData)
        cprint("Not youtube link " + linkData, "red")
    else:
        temp_id = linkData.split('watch?v=')[1]
        if(temp_id in listOfLinksDownloaded):
            eel.error_message_js(
                "Youtube link is already downloaded: " + temp_id)
        else:
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
                        "Youtube link is already downloaded: " + temp_id)
                elif(check == True):
                    data_video = functions.ExtractInfoData(
                        data_video)
                    listOfLinks["data"].append(data_video)
                    with open(DEFAULT_PATH_DATABASE, 'w') as outfile:
                        json.dump(listOfLinks, outfile)
                    # need add data_video to bottom of undownload list, before downloaded list
                    eel.update_listOfLinks_js(listOfLinks["data"])
                else:   # link cant be get info by age, ...
                    eel.error_message_js(linkData+" "+data_video)
                    fw = open(DEFAULT_PATH_VIDEO_ERROR_LOG, "a")
                    fw.write(linkData+"\n")
                    fw.close()

            else:
                cprint("Link added", "red")
                eel.error_message_js(
                    "Youtube link is already added: " + temp_id)


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


def my_hook(d):
    try:
        if(d['status'] == 'finished'):
            status = 'Finished'
            temp_check = False
            for idx, video in enumerate(listOfLinks["data"]):
                if(video["status"] == ["Downloading", "Error"]):
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
                    'download_archive': DEFAULT_PATH_DOWNLOADED,
                    'outtmpl': DEFAULT_PATH_STORAGE+video["channel"]+'-'+video['id']+'-'+video["title"]+".%(ext)s",
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
                    eel.error_message_js(
                        "[!] run_downloaded_script: Error downloading" + video["id"])
                    video["status"] = "Error"
                    eel.update_listOfLinks_js(listOfLinks["data"])
                    continue
    eel.download_process_js("Done")


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
def add_file_action_py():
    path_filename = functions.DialogSelectFile()
    if os.path.exists(path_filename) and path_filename[len(path_filename)-4:len(path_filename)] == ".txt":
        eel.add_file_response_js()
        eel.notify_message_js("Reading "+path_filename)
        try:
            fr = open(path_filename, 'r')
            for line in fr:
                eel.notify_message_js("Processing...")
                get_info_py(line.replace("\n", ""))
            fr.close()
        except Exception as e:
            eel.error_message_js(e)
        eel.notify_message_js("Done.")
    else:
        eel.error_message_js("File is not exist")


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
    eel.notify_message_js("Done.")


@eel.expose
def clear_action_py():
    listOfLinks["data"] = []
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
    cprint("[INFO] open_folder_storage_py")
    if(sys.platform == "win32"):
        os.startfile(DEFAULT_PATH_STORAGE)
    elif(sys.platform == "darwin"):
        os.system('open "%s"' % foldername)
    elif(sys.platform == "linux"):
        os.system('xdg-open "%s"' % foldername)


@eel.expose                         # Expose this function to Javascript
def say_hello_py(x):
    print('Hello from %s' % x)


say_hello_py('Python World!')
eel.say_hello_js('Python World!')   # Call a Javascript function
eel.update_listOfLinks_js(listOfLinks["data"])
eel.start('main.html')
# if __name__ == "__main__":
#    eel.start('main.html')

# D:\github\letuan317\youtube_download_app\links.txt
