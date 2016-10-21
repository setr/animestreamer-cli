import os, subprocess, re, click
from parsers.classes import Torrent_File

name_color = "white"

def webtorrent_filelist(magnet):
    get_filelist = ["webtorrent", magnet,
                        "--mpv", "--select"]
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
            if 'To select a specific file, re-run `webtorrent` with "--select [index]"' in line:
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

