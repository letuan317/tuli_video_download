from __future__ import unicode_literals
from xml.etree.ElementTree import indent
import youtube_dl
import json

ydl_opts = {
}
yt_link = ""
ydl = youtube_dl.YoutubeDL(ydl_opts)
result = ydl.extract_info(yt_link, download=False)
with open("test.json", 'w') as out_json:
    json.dump(result, out_json, indent=2)
