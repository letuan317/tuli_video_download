import eel
from termcolor import cprint
import functions
import json

with open('./data.json') as f:
    data = json.load(f)
with open('./data1.json') as f:
    data1 = json.load(f)

listOfLinks = [data]

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
def getInfo(linkData):
    cprint("getInfo: "+linkData, "blue")
    temp = "youtube.com/watch?v="
    if(temp not in linkData):
        eel.error_message_js("Not youtube link " + linkData)
        cprint("Not youtube link " + linkData, "red")
    else:
        cprint("Good link", "green")
        check, data_video = functions.GetYoutubeInfo(linkData)
        if(check == False):
            eel.error_message_js("Youtube link is already added" + linkData)
        else:
            listOfLinks.append(data_video)
            # need add data_video to bottom of undownload list, before downloaded list
            eel.update_listOfLinks_js(listOfLinks)


say_hello_py('Python World!')
eel.say_hello_js('Python World!')   # Call a Javascript function
eel.update_listOfLinks_js(listOfLinks)

eel.start('main.html')
