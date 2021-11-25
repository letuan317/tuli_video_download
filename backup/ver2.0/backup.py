
   def HookGetStatus(self, d):
        try:
            if (d['status'] == 'finished'):
                status = 'Finished'
                # self.ContentContainer()
                # TODO Finish download, process is false now
            else:
                status = d['_percent_str'] + " of " + d['_total_bytes_str'] + \
                    " at " + d['_speed_str'] + " ETA " + d['_eta_str']
            # self.FooterDownloadProcess(status)
            cprint(status)
        except Exception as e:
            cprint("[!] my_hook: Error downloading", 'red')
            print(e)
            status = "Downloaded" if (
                "already been recorded in archive" in str(d)) else "Error"
            # self.FooterDownloadProcess(status)
            cprint(status)

    def RunDownloadedScript(self):
        cprint("[INFO] RunDownloadedScript", "green")
        if(self.listOfLinks["data"]):
            for idx, video in enumerate(self.listOfLinks["data"]):
                if(video["status"] in ["Wait", "Paused", "Error"]):
                    video["status"] = "Downloading"
                    #self.IsUpdateUI =True
                    self.ContentContainer()
                    ydl_opts = {
                        'format': video["select_format"]+'+bestaudio',
                        'download_archive': self.DEFAULT_PATH_DOWNLOADED,
                        'outtmpl': os.path.normpath(os.path.join(self.DEFAULT_PATH_STORAGE, video["channel"]+'-'+video['id']+'-'+video["title"]+".%(ext)s")),
                        'noplaylist': True,
                        'progress_hooks': [self.HookGetStatus],
                        'logger': MyLogger(),
                    }
                    try:
                        cprint("[*] Starting download", "yellow")
                        # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        #    ydl.download([video["webpage_url"]])
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.add_post_processor(MyCustomPP())
                            ydl.extract_info(video["webpage_url"])
                            # ydl.download([video["webpage_url"]])
                        video["status"] = "Downloaded"
                        self.UpdateDatabase()
                        self.ContentContainer()
                        #self.IsUpdateUI =True
                    except Exception as e:
                        self.FooterUpdate(
                            "[!] Video get error download", "red")
                        cprint(e, "red")
                        video["status"] = "Error"
                        if("LP_OVERLAPPED" not in str(e)):
                            self.UpdateDatabase()
                            self.ContentContainer()
                            #self.IsUpdateUI =True
                        else:
                            video["status"] = "Downloaded"
                            self.UpdateDatabase()
                            self.ContentContainer()
                        continue
        self.IsProcessing = False
        self.MenuShowButton()
