import os

cmd = "youtube-dl -o \"%(uploader)s-%(title)s.%(ext)s\" "


def select_format(format_code):
    return "youtube-dl -o \"%(uploader)s-%(title)s.%(ext)s\" -f "+format_code+"+bestaudio --download-archive downloaded.txt "


while True:
    url_link = input("URL: ")
    status = os.system("youtube-dl -F " + url_link)
    choice = int(input("\nSelect: "))
    if(choice == 0):
        status = os.system(cmd+url_link)
    else:
        new_cmd = select_format(str(choice))+url_link
        status = os.system(new_cmd)
