#!/usr/bin/env python2.7
from __future__ import absolute_import
import click, subprocess
from nyaa.webstream import *
from nyaa.webtorrent import *

@click.group()
def cli():
    pass

@click.command()
@click.argument('search_query')
def torrent(search_query):
    from nyaa.parsers.nyaa import parser as nyaa
    torrents = nyaa.fetch_torrentlist("urusei")
    torrent = pick_torrent(torrents)
    magnet = torrent.get_magnet(torrent.link)
    filelist = webtorrent_filelist(magnet)
    select = pick_file(filelist)
    subprocess.call( ["webtorrent", magnet,
                        "--mpv",
                        "--select", str(select)])


@click.command()
@click.argument('search_query')
def web(search_query):
    from nyaa.parsers.masterani import parser as masterani
    # pick a show
    # pick an episode
    # pick a host
    # play
    shows = masterani.fetch_shows(search_query)
    show = pick_show(shows)
    episodes = show.get_episodelist(show.link)
    episode = pick_episode(episodes)
    hosts = episode.get_videos(episode.ep_link)
    url = pick_host(hosts)
    subprocess.call( ["mpv", url] )


def main():
    cli.add_command(torrent)
    cli.add_command(web)
    cli()

if __name__ == "__main__":
    main()
