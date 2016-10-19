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
                print line
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

        tfile = Torrent_File(name= gutted.group(2),
                             size = gutted.group(3))
        filelist.append(tfile)
    return filelist

def pick_torrent(torrents):
    for i, tor in enumerate(torrents):
        # de-highlight the group info ([ translator ] ANIME [ nonsense ])
        cname = ""
        j = 0
        for match in re.finditer("\[.*?\]", tor.name):
            cname += click.style(tor.name[j: match.start()], fg= name_color)
            j = match.end()
            cname += match.group(0)
        cname += click.style(tor.name[j:], fg= name_color)

        click.secho("{}) ".format(i+1) , fg="magenta"  , nl=False)
        seeders  = click.style("{:3}".format(tor.seeders)   , fg    = "green")
        leechers = click.style("{:3}".format(tor.leechers) , fg     = "red")
        size     = click.style("{:10}".format(tor.size)          , fg = "blue")
        click.echo(u"{} {} {} {:100}".format(seeders, leechers, size, cname))

    p = click.prompt("Pick Torrent", type=click.IntRange(1, len(torrents)))
    return torrents[p-1]

def pick_file(filelist):
    for i, torfile in enumerate(filelist):
        # de-highlight the group info ([ translator ] ANIME [ nonsense ])
        cname = ""
        j = 0
        for match in re.finditer("\[.*?\]", torfile.name):
            cname += click.style(torfile.name[j: match.start()], fg= name_color)
            j = match.end()
            cname += match.group(0)
        cname += click.style(torfile.name[j:], fg= name_color)

        click.secho("{:3d}] ".format(int(i)+1), fg="magenta"  , nl=False)

        size = click.style(torfile.size , fg="blue")
        click.echo(u" {:17} {:100}".format(size, cname))

    p = click.prompt("Pick File", type=click.IntRange(1, len(filelist)))
    return p-1
