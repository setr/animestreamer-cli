#!/usr/bin/env python2.7
from __future__ import absolute_import
import click, subprocess, time
from nyaa.webtorrent import *
import sys
from functools import wraps

def handleEmptyMenu(fn):
    def handleExc(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except AttributeError:
            print "No items were found. Exiting."
            sys.exit(1)
    return handleExc

modopts = ['d']
def pickloop(objtype, options):
    def checkrange(i):
        err = None
        if p < 1 or p > len(options):
            err = "Input not in range: 1 - {}".format(len(options))
        return err

    index = None
    while not index:
        userin = click.prompt("Pick {}".format(objtype))
        err = None
        try:
            p = int(userin)
            err = checkrange(p)
            if not err:
                index = p 
        except ValueError: # integer + modifier ie 10 d 
            try: 
                match = re.search("(\d+) *?([A-Za-z])", userin)
                p = match.group(1)
                p = int(p)
                modifier = match.group(2).lower()
                err = checkrange(p)
                if not err:
                    if modifier not in modopts:
                        err = "Not a valid option for this menu."
                    # and now we do anything that doesn't actually select the item ie description
                    elif modifier == 'd':
                        click.echo( options[p-1] )
                        click.echo( '    ' + options[p-1].description() )
            except AttributeError:
                i = click.style('[index]', fg="magenta")
                m = click.style('(modifier)', fg="blue")
                msg = click.style('invalid input.', fg="red")
                err = "{} Correct form: {} {}".format(msg, i, m)
        if err:
            click.echo(err)
    return options[index - 1]

def pick(objtype, options):
    if len(options) == 0:
        return None
    if len(options) == 1:
        click.echo("Only one option... Autoselecting: {}".format(options[0]))
        return options[0]
    
    for i, option in enumerate(options):
        index = click.style("{:03d}".format(i+1), fg="magenta")
        click.echo(u"{} {}".format(index, option))
    return pickloop(objtype, options)


def select(text, options, quickvar, sh_quick=True):
    # sh_quick --> should we consider quickvar? the big loop only wants to use it once.
    if quickvar and sh_quick:
        try:
            return options[quickvar-1]
        except IndexError:
            click.echo("{}: Index out of range.".format(text))
    return pick(text, options)

@click.group()
def cli():
    pass

def menuoptfn(ctx, param, value):
    if value:
        t = value.split('.')
        try:
            return map(int, t)
        except ValueError:
            raise click.BadParameter("quick-select must a period delimited list of integers. ie 10.1.2")
    else:
        return []

def searchquery(ctx, param, value):
    if value: # got it from the cli
        return ' '.join(value)
    else: # nothing 
        return click.prompt("Please enter a search term")


@click.command('torrent', short_help='Search from available torrent websites.')

@click.argument('search_query', nargs=-1, 
        callback=searchquery,
        required=False)

@click.option('--menuopts', '-o', callback=menuoptfn, help="period delimited list of integers, to pre-emptively select menu options.")
@click.option('--mpvpass', '-m', default=None, type=unicode, help="cli options directly passed to mpv. ---TODO")
@click.option('--webtorrentpass', '-w', default=None, type=unicode, help="cli options directly passed to webtorrent")
@click.option('-x', type=click.IntRange(0,2), default=0, help="set 0 to stream. set 1 to dl. set 2 to dl & stream. use webtorrent's -o flag to set dl location. default = 0.")

@handleEmptyMenu
def torrent(search_query, menuopts, mpvpass, webtorrentpass, x):
    # pick a torrent
    # pick a video from the torrent
    # play
    from nyaa.parsers.nyaa import parser as nyaa
    if not search_query:
        search_query = click.Prompt("Please enter a search term")
     
    q_torrent = menuopts[0] if menuopts else None
    q_filenum = menuopts[1] if len(menuopts) > 1 else None

    torrents = nyaa.fetch_torrentlist(search_query)
    torrents = sorted(torrents, key=lambda t: t.name)

    torrent = select("Torrent", torrents, q_torrent)
    magnet = torrent.get_magnet()

    click.echo("getting filelist...")
    click.echo("")
    filelist = webtorrent_filelist(magnet)

    first = True
    while True:
        filen = select("Torrent File", filelist, q_filenum, sh_quick=first)

        name = click.style(torrent.name, underline=True)
        f  = click.style(filen.name, fg="magenta")
        click.echo(u"Playing: File {} {}".format(f, name))
        try:
            download = "download" if x in [1,2] else ""
            stream = "--mpv" if x in [0,2] else ""
            command = ["webtorrent", magnet, "--select", str(filen.index)]
            if webtorrentpass:
                command.insert(5, webtorrentpass)
            if x in [0,2]:
                command.insert(2, "--mpv")
            if x in [1,2]:
                command.insert(1, "download")
            subprocess.call( command )
        except KeyboardInterrupt:
            time.sleep(0.5) # so the user has a chance to interrupt again to kill python, in the case of a single torrent-file
        first = False


@click.command('web', short_help='Search from available streaming websites')

@click.argument('search_query', nargs=-1, 
        callback=searchquery,
        required=False)

@click.option('--menuopts', '-o', callback=menuoptfn, help="period delimited list of integers, to pre-emptively select menu options.")
@click.option('--mpvpass', '-m', default=None, type=unicode, help="cli options directly passed to mpv.")

@handleEmptyMenu
def web(search_query, menuopts, mpvpass):
    from nyaa.parsers.masterani import parser as masterani
    if not search_query:
        search_query = click.Prompt("Please enter a search term")
    # pick a show
    # pick an episode
    # pick a host
    # play
    q_show   = menuopts[0] if menuopts else None
    q_epnum =  menuopts[1] if len(menuopts) > 1 else None
    q_host   = menuopts[2] if len(menuopts) > 2 else None

    shows = masterani.fetch_shows(search_query)
    show = select("Show", shows, q_show)
    episodes = show.get_episodelist()
    #episodes = show.get_episodelist(show.link)

    first = True
    while True:
        episode = select("Episode", episodes, q_epnum, sh_quick=first)
        hosts = episode.get_videos()
        url = select("Host", hosts, q_host, sh_quick=first)
        url = url.link

        try:
            name = click.style(show.name, underline=True)
            ep = click.style(str(episode.ep_number), fg="magenta")
            click.echo("Playing: episode {} {}".format(ep, name))
            command = ["mpv", url]
            if mpvpass:
                command.insert(1, mpvpass)
            subprocess.call( command )
        except KeyboardInterrupt:
            time.sleep(0.5) # so the user has a chance to interrupt again to kill python, in the case where theres 1 ep, 1 host
        first = False


def main():
    cli.add_command(torrent)
    cli.add_command(web)
    cli()

if __name__ == "__main__":
    main()
