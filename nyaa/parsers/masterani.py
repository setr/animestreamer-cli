#!/usr/bin/env python2.7
from __future__ import absolute_import
import cfscrape
from bs4 import BeautifulSoup
import json, re
from .classes import WebEpisode, WebSeries, WebVideo, WebFetcher

base = "http://www.masterani.me/anime"
api_base = "http://www.masterani.me/api/anime/"
scraper = cfscrape.create_scraper() # to get past cloudflare

def fetch_masterani(search_query):
    params = {"search": search_query,
                "sb" : "true"} # masterani will use a much better string matcher with this
    jsonresults = scraper.get(api_base + "search", params = params).content

    # json results has the actual results we care about
    # the html just contains some additional metadata we can use
    videolist = []
    for anime in json.loads(jsonresults.decode('utf-8')):
        link = base + "/info/" + anime['slug']
        name = anime['title']
        animeid = str(anime['id'])

        detailjson = scraper.get( api_base + animeid + "/detailed").content
        d = json.loads(detailjson.decode('utf-8'))
        episode_count = d['info']['episode_count']
        synopsis = d['info']['synopsis']

        # since getting the episode count got us all the info for making WebEpisode objects too,
        # we might as well make them now.
        episodes = []
        for ep in d['episodes']:
            ep_number = ep['info']['episode']
            ep_title = ep['info']['title']
            if ep['info']['description']:
                description = ep['info']['description'] 
            else: 
                description = "description not available"

            if not ep_title: # then this is actually a movie, not a series
                ep_title = name  # in which case, the name of the only episode is actually the name of the series.
            ep_link = "{}/watch/{}/{}".format(base, anime['slug'], ep_number)
            episode = WebEpisode(
                        ep_number = ep_number,
                        ep_title = ep_title,
                        ep_link = ep_link,
                        get_videos = get_videos,
                        description = description)
            episodes.append(episode)
         
        series = WebSeries(
                    name = name,
                    link = link,
                    ep_count = episode_count,
                    description = synopsis,
                    get_episodelist = lambda x, episodes=episodes: episodes) 
        videolist.append(series)
    return videolist

def get_videos(link):
    html = scraper.get(link).content
    soup = BeautifulSoup(html, 'html.parser')
    js = soup.find_all("script")[3].text

    # and now we have a js dict, which we need to make a valid JSON
    # so we can properly go through it. So now we do some horrendously brittle substitutions
    vidjson = re.search("({.*})", js, re.DOTALL).group(1)
    vidjson = re.sub(r":(\d+),", r':"\1",', vidjson)
    vidjson = re.sub(r"(\d+)([\]}])", r'"\1"\2', vidjson)
    vidjson = re.sub(r"([\[{])(\d+)", r'\1"\2"', vidjson)
    vidjson = re.sub(r"(  +)(\.?[\w\v]+): ", r'\1"\2": ', vidjson)
    vidjson = re.sub(r"null", r'"null"', vidjson)
    d = json.loads(vidjson)

    videos = [ WebVideo( 
        host = m['host']['name'],
        link = m['host']['embed_prefix'] + m['embed_id'] + m['host']['embed_suffix'],
        resolution = m['quality'])
    for m in d['mirrors']]
    return videos

parser = WebFetcher(
            sitename="masterani", 
            fetch_shows = fetch_masterani)
