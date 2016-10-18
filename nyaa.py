#!/usr/bin/env python2.7

import urllib2
from bs4 import BeautifulSoup
import click, re, attr
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool 
import subprocess

pool = ThreadPool() 

@attr.s
class Torrent(object):
    name     = attr.ib()
    trusted  = attr.ib()
    link     = attr.ib()
    size     = attr.ib()
    seeders  = attr.ib()
    leechers = attr.ib()
@attr.s
class Torrent_File(object):
    name     = attr.ib()
    size     = attr.ib()

def fetch_nyaa(search_query):
    def getsoup(pgnum, link):
        response = urllib2.urlopen(link)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        return pgnum, soup

    nyaa_url = "https://www.nyaa.se"
    search_url = nyaa_url + "/?page=search&term=" + search_query + "&sort=2";
    soup = getsoup(0, search_url)[1]

    pages = soup.find("div", {"class": "pages"})

    def getsoup_wrapper(a):
        pgnum = a[0] + 1
        link = a[1]['href']
        link = "http://"+ link[2:]
        return getsoup(pgnum, link)


    results = pool.map(getsoup_wrapper, enumerate(pages.find_all("a", {"class": "pagelink"})[:5]))
    results = sorted(results, key=lambda x: x[0])
    results = [i[1] for i in results]

    data = []
    initial = parse_nyaa(soup, data) # since we already have the html, no need to do it again
    map(lambda soup: parse_nyaa(soup, data), results)

    return data



def parse_nyaa(soup, data):
    temp = []
    for row in soup.findAll("tr", {"class": "tlistrow"}):
        torrent = Torrent(
            trusted  = 'trusted' in row['class'],
            name     = row.contents[1].a.text.strip(),
            link     = row.contents[1].a['href'],
            size     = row.contents[3].text.strip(),
            seeders  = row.contents[4].text.strip(),
            leechers = row.contents[5].text.strip())
        try:
            if int(torrent.seeders) > 5:
                temp.append(torrent)
        except ValueError:
            pass
    data += temp

def pick_torrent(torrents):
    for i, tor in enumerate(torrents):
        # de-highlight the group info ([ translator ] ANIME [ nonsense ])
        cname = ""
        j = 0
        for match in re.finditer("\[.*?\]", tor.name):
            cname += click.style(tor.name[j: match.start()], fg="white") 
            j = match.end()
            cname += match.group(0)
        cname += click.style(tor.name[j:], fg="white")

        click.secho("{}) ".format(int(i)+1) , fg="magenta"  , nl=False)
        seeders = click.style(tor.seeders   , fg="green")
        leechers = click.style(tor.leechers , fg="red")
        size = click.style(tor.size         , fg="blue")
        click.echo(u" {:13} {:13} {:<20} {:100}".format(seeders, leechers, size, cname))

    p = click.prompt("Pick Torrent", type=click.IntRange(1, len(torrents)))
    return torrents[p-1]

def pick_file(filelist):
    for i, torfile in enumerate(filelist):
        # de-highlight the group info ([ translator ] ANIME [ nonsense ])
        cname = ""
        j = 0
        for match in re.finditer("\[.*?\]", torfile.name):
            cname += click.style(torfile.name[j: match.start()], fg="white") 
            j = match.end()
            cname += match.group(0)
        cname += click.style(torfile.name[j:], fg="white")

        click.secho("{}) ".format(int(i)+1), fg="magenta"  , nl=False)

        size = click.style(torfile.size , fg="blue")
        click.echo(u" {:17} {:100}".format(size, cname))

    p = click.prompt("Pick File", type=click.IntRange(1, len(filelist)))
    return p-1


@click.command()
@click.argument('search_query')
def nyaa(search_query):
    torrents = fetch_nyaa(search_query)
    torrent = pick_torrent(torrents)

    # we need to fix nyaa's url to fetch the actual magnet link
    # we'll update the links asynchronously.
    def fetch_magnet(tor):
        tid = re.search("&tid=(\d+)", tor.link).group(1)
        magnet = "https://www.nyaa.se/?page=download&tid=" + tid + "&magnet=1"
        # we actually need it to fail, as nyaa redirects to the magnetlink and baffles urllib
        try:
            response = urllib2.urlopen(magnet)
        except urllib2.HTTPError, e:
            tor.link = e.geturl().replace("magnet:/?", "magnet:?")
        return tor

    tor = fetch_magnet(torrent)
    get_filelist = ["webtorrent", tor.link,
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

    select = pick_file(filelist)
    subprocess.call( ["webtorrent", tor.link,
                        "--mpv", 
                        "--select", str(select)])

if __name__ == "__main__":
    nyaa()


