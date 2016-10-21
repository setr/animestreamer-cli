#!/usr/bin/env python2.7

import cfscrape
import requests
from bs4 import BeautifulSoup
import re
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool 
import subprocess
import classes

scraper = cfscrape.create_scraper()
def fetch_nyaa(search_query):
    def getsoup(pgnum, link):
        html = scraper.get(link).content
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

    pool = ThreadPool() 
    results = pool.map(getsoup_wrapper, enumerate(pages.find_all("a", {"class": "pagelink"})[:5]))
    pool.close()
    results = sorted(results, key=lambda x: x[0])
    results = [i[1] for i in results]

    data = []
    initial = parse_nyaa(soup, data) # since we already have the html, no need to do it again
    map(lambda soup: parse_nyaa(soup, data), results)
    return data

def parse_nyaa(soup, data):
    temp = []

    def get_magnet(torrent):
        link = torrent.link
        tid = re.search("&tid=(\d+)", link).group(1)
        magnet = "https://www.nyaa.se/?page=download&tid=" + tid + "&magnet=1"
        # we actually need it to fail, as nyaa redirects to the magnetlink and baffles urllib/requests
        try:
            response = scraper.get(magnet)
        except requests.exceptions.InvalidSchema, e:
            magnet = e.args[0]
            magnet = re.search("(magnet:.*)'", magnet).group(1)
            #magnet = e.geturl().replace("magnet:/?", "magnet:?")
        return magnet 

    for row in soup.findAll("tr", {"class": "tlistrow"}):
        torrent = classes.Torrent(
            trusted  = 'trusted' in row['class'],
            name     = row.contents[1].a.text.strip(),
            link     = row.contents[1].a['href'],
            size     = row.contents[3].text.strip(),
            seeders  = row.contents[4].text.strip(),
            leechers = row.contents[5].text.strip(),
            get_magnet = get_magnet)
        try:
            if int(torrent.seeders) > 5:
                temp.append(torrent)
        except ValueError:
            pass
    data += temp

parser = classes.TorrentFetcher(
            sitename="nyaa", 
            fetch_torrentlist = fetch_nyaa) 
