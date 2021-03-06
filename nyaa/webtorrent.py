import os, subprocess, re, click
from nyaa.parsers.classes import Torrent_File

name_color = "white"

def webtorrent_filelist(magnet):
    print("") # because we'll erase 1 line up.
    get_filelist = ["webtorrent", magnet,
                        "--mpv", "--select"]
    print magnet
    print
    import os
    DEVNULL = open(os.devnull, 'wb')
    proc = subprocess.Popen(get_filelist, stdout=subprocess.PIPE, stderr=DEVNULL)
    files = []
    is_filelist= False

    for line in iter(proc.stdout.readline,''):
        line = line.strip().decode('utf8')
        if line:
            if "fetching torrent metadata" in line:
                CURSOR_UP_ONE = '\x1b[1A'
                ERASE_LINE = '\x1b[2K'
                print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)
                print(line)
            elif 'To select a specific file, re-run `webtorrent` with "--select [index]"' in line:
                break
            elif is_filelist:
                files.append(line)
            elif "Select a file to download:" in line:
                is_filelist = True
    filelist = []
    for line in files:
        line = click.unstyle(line)
        gutted = re.match("(\d+) +(.*) \((.*)\)", line)

        tfile = Torrent_File(index = int(gutted.group(1)),
                             name= gutted.group(2),
                             size = gutted.group(3))
        filelist.append(tfile)
    return filelist
