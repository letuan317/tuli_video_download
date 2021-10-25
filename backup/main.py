from __future__ import unicode_literals
import json
import subprocess
import youtube_dl

'''
username:               Username for authentication purposes.
password:               Password for authentication purposes.
format:                 Video format code. See options.py for more information.
listformats:            Print an overview of available video formats and exit.
geo_bypass:             Bypass geographic restriction via faking X-Forwarded-For HTTP header (experimental)
geo_bypass_country:     Two-letter ISO 3166-2 country code that will be used for explicit geographic restriction bypassing via faking X-Forwarded-For HTTP header (experimental)
progress_hooks:         A list of functions that get called on download
                            progress, with a dictionary with the entries
                            * status: One of "downloading", "error", or "finished".
                                        Check this first and ignore unknown values.
                            If status is one of "downloading", or "finished", the
                            following properties may also be present:
                            * filename: The final filename (always present)
                            * tmpfilename: The filename we're currently writing to
                            * downloaded_bytes: Bytes on disk
                            * total_bytes: Size of the whole file, None if unknown
                            * total_bytes_estimate: Guess of the eventual file size,
                                                    None if unavailable.
                            * elapsed: The number of seconds since download started.
                            * eta: The estimated time in seconds, None if unknown
                            * speed: The download speed in bytes/second, None if
                                        unknown
                            * fragment_index: The counter of the currently
                                                downloaded video fragment.
                            * fragment_count: The number of fragments (= individual
                                                files that will be merged)
                            Progress hooks are guaranteed to be called at least once
                            (with status "finished") if the download is successful.
geo_verification_proxy:     URL of the proxy to use for IP address verification
                                on geo-restricted sites. (Experimental)
proxy:                      URL of the proxy server to use
download_archive:           File name of a file where all downloads are recorded.
                                Videos already present in the file are not downloaded
                                again.
format:                     Video format code. See options.py for more information.
outtmpl:                    Template for output names.
'''
subprocess = subprocess.Popen(
    "echo Hello World", shell=True, stdout=subprocess.PIPE)
subprocess_return = subprocess.stdout.read()
print(subprocess_return)


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


ydl_opts = {
    'listformats': True,
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}

ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})

with ydl:
    result = ydl.extract_info(
        # 'https://www.youtube.com/watch?v=cM0SZQVcc54&ab_channel=MinjeongJeong',
        # 'https://www.youtube.com/watch?v=FtMuFJkGuxI&list=PLQzXZnfwrxEyD6E73WjbiWdion3Nvn8B3&ab_channel=MinjeongJeong',
        'https://www.youtube.com/watch?v=2UMJF4_NmSo',
        download=False  # We just want to extract the info
    )

if 'entries' in result:
    # Can be a playlist or a list of videos
    video = result['entries'][0]
else:
    # Just a video
    video = result
# print(video)

with open('data1.json', 'w') as outfile:
    json.dump(video, outfile)


'''
"1":{
id
channel
formats:
    format_id
    format_note
    filesize
    fps
    quality
    ext
}



https://www.youtube.com/watch?v=cM0SZQVcc54&ab_channel=MinjeongJeong

'''
