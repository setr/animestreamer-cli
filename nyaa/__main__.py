#!/usr/bin/env python2.7
from __future__ import absolute_import
import click, subprocess, time
from nyaa.webtorrent import *

def pick(objtype, options):
    if len(options) == 1:
        click.echo("Only one option... Autoselecting: {}".format(options[0]))
        return options[0]
    for i, option in enumerate(options):
        index = click.style("{}]".format(i+1), fg="magenta")
        click.echo(u"{:<13} {}".format(index, option))
    p = click.prompt("Pick {}".format(objtype), type=click.IntRange(1, len(options)))
    return options[p-1]

@click.group()
def cli():
    pass

@click.command('torrent', short_help='Search from available streaming websites')
@click.option('--search_query' , '-s' , prompt="Please enter a search term")
@click.option('--torrent'      , '-t' , default=None, type=int)
@click.option('--file-number'  , '-f' , default=None, type=int)
def torrent(search_query, torrent, file_number):
    # pick a torrent
    # pick a video from the torrent
    # play
    from nyaa.parsers.nyaa import parser as nyaa

    torrents = nyaa.fetch_torrentlist("urusei")
    torrent = torrents[torrent-1] if torrent else pick("Torrent", torrents)
    magnet = torrent.get_magnet(torrent)

    click.echo("getting filelist...")
    click.echo("")
    filelist = webtorrent_filelist(magnet)

    first = True
    while True:
        select = file_number if file_number and first else pick("Torrent File", filelist).index

        name = click.style(torrent.name, underline=True)
        f  = click.style(filelist[select].name, fg="magenta")
        click.echo(u"Playing: File {} {}".format(f, name))
        try:
            subprocess.call( ["webtorrent", magnet,
                                "--mpv",
                                "--select", str(select)])
        except KeyboardInterrupt:
            time.sleep(0.5) # so the user has a chance to interrupt again to kill python, in the case of a single torrent-file
        first = False


@click.command('web', short_help='Search from available streaming websites')
@click.option('--search_query' , '-s' , prompt="Please enter a search term")
@click.option('--show'         , '-w' , default=None, type=int)
@click.option('--episode_num'  , '-e' , default=None, type=int)
@click.option('--host'         , '-h' , default=None, type=int)
def web(search_query, show, episode_num, host):
    from nyaa.parsers.masterani import parser as masterani
    # pick a show
    # pick an episode
    # pick a host
    # play
    shows = masterani.fetch_shows(search_query)
    show = shows[show] if show else pick("Show", shows)
    episodes = show.get_episodelist(show.link)

    first = True
    while True:
        episode = episodes[episode_num-1] if episode_num and first else pick("Episode", episodes) 
        hosts = episode.get_videos(episode.ep_link)
        url = hosts[host-1] if host and first else pick("Host", hosts)
        url = url.link

        try:
            name = click.style(show.name, underline=True)
            ep = click.style(episode.ep_number, fg="magenta")
            click.echo("Playing: episode {} {}".format(ep, name))
            subprocess.call( ["mpv", url] )
        except KeyboardInterrupt:
            time.sleep(0.5) # so the user has a chance to interrupt again to kill python, in the case where theres 1 ep, 1 host
        first = False


def main():
    cli.add_command(torrent)
    cli.add_command(web)
    cli()

if __name__ == "__main__":
    main()
