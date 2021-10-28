import os
import sys
print()

foldername = "H:/Backup/youtube"
if(sys.platform == "win32"):
    os.startfile(foldername)
elif(sys.platform == "darwin"):
    os.system('open "%s"' % foldername)
elif(sys.platform == "linux"):
    os.system('xdg-open "%s"' % foldername)
