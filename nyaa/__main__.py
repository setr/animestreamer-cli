#!/usr/bin/env python2.7
from __future__ import absolute_import
import click, subprocess, time
from nyaa.webtorrent import *
import attr
import sys
from functools import wraps

def handleEmptyMenu(fn):
    def handleExc(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except AttributeError:
            print("No items were found. Exiting.")
            sys.exit(1)
    return handleExc

class goBackErr(Exception):
    pass 

modopts = ['d']
def pickloop(options):
    def checkrange(i):
        err = None
        if p < 1 or p > len(options):
            err = "Input not in range: 1 - {}".format(len(options))
        return err

    index = None
    while index is None:
        userin = click.prompt("")
        err = None
        try:
            p = int(userin)
            err = checkrange(p)
            if not err:
                index = p-1
        except ValueError: # integer + modifier ie 10 d 
            try: 
                match = re.search("([A-Za-z])|([A-Za-z]) *?(\d+)", userin)
                modifier = match.group(1).lower()
                if modifier not in modopts:
                    err = "Not a valid option for this menu."
                p = match.group(2)
                if p: # handle menu modifiers requiring an option selected
                    p = int(p)
                    err = checkrange(p)
                    if not err:
                        if modifier == 'd':
                            click.echo( options[p-1] )
                            click.echo( '    ' + options[p-1].description() )
                else: # handle modifiers not selecting a menu
                    if modifier == 'b':
                        raise goBackErr
            except AttributeError:
                i = click.style('[index]', fg="magenta")
                m = click.style('(modifier)', fg="blue")
                msg = click.style('invalid input.', fg="red")
                err = "{} Correct form: {} {}".format(msg, i, m)
        if err:
            click.echo(err)
    click.echo("selected: {} {}".format(index, options[index]))
    return options[index]


def select(options, quickvar, sh_quick=True):
    # sh_quick --> should we consider quickvar? the big loop only wants to use it once.
    if quickvar and sh_quick:
        try:
            click.echo("selected: {}".format(options[quickvar-1]))
            return options[quickvar-1]
        except IndexError:
            click.echo("Index out of range.")

    if not options:
        click.echo("No data found")
        raise goBackErr

    if len(options) == 1 and sh_quick: # we don't want to go into an autoselect loop
        click.echo("Only one option... Autoselecting: {}".format(options[0]))
        return options[0]
    
    for i, option in enumerate(options):
        index = click.style("{:03d}".format(i+1), fg="magenta")
        click.echo(u"{} {}".format(index, option))

    return pickloop(options)

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

#@handleEmptyMenu
def torrent(search_query, menuopts, mpvpass, webtorrentpass, x):
    # pick a torrent
    # pick a video from the torrent
    # play

    # quick-select options, from the cli
    q_torrent = menuopts[0] if menuopts else None
    q_filenum = menuopts[1] if len(menuopts) > 1 else None
    firstrun = True

    @attr.s
    class Storage(object):
        search_query = attr.ib(init=False),
        torrents     = attr.ib(init=False),
        torrentname  = attr.ib(init=False),
        magnet       = attr.ib(init=False),
        filelist     = attr.ib(init=False),
        filen        = attr.ib(init=False),

    def get_query(s):
        from nyaa.parsers.nyaa import parser as nyaa
        if not s.search_query:
            s.search_query = click.prompt("Please enter a search term")
        s.torrents = nyaa.fetch_torrentlist(s.search_query)
        s.torrents = sorted(s.torrents, key=lambda t: t.name)

    def select_torrent(s):
        try:
            torrent = select(s.torrents, q_torrent, sh_quick=firstrun)
        except goBackErr:
            #s.torrents = None
            s.search_query = None
            raise
        s.magnet = torrent.get_magnet()
        s.torrentname = torrent.name
        s.filelist = webtorrent_filelist(s.magnet)

    def select_filen(s):
        click.echo("getting filelist...")
        click.echo("")
        try:
            filen = select(s.filelist, q_filenum, sh_quick=firstrun)
        except goBackErr:
            s.filelist = None
            s.torrentname = None
            s.magnet = None
            raise
        s.filen = filen

    def execute_file(s):
        name = click.style(s.torrentname, underline=True)
        f  = click.style(s.filen.name, fg="magenta")
        click.echo(u"Playing: File {} {}".format(f, name))
        try:
            download = "download" if x in [1,2] else ""
            stream = "--mpv" if x in [0,2] else ""
            command = ["webtorrent", s.magnet, "--select", str(s.filen.index)]
            if webtorrentpass:
                command.insert(5, webtorrentpass)
            if x in [0,2]:
                command.insert(2, "--mpv")
            if x in [1,2]:
                command.insert(1, "download")
            subprocess.call( command )
        except KeyboardInterrupt:
            time.sleep(0.5) # so the user has a chance to interrupt again to kill python, in the case of a single torrent-file
            raise goBackErr
    menu = [
        get_query,
        select_torrent,
        select_filen,
        execute_file]

    s = Storage()
    s.search_query = search_query
    i = 0
    while i < len(menu):
        try:
            menu[i](s)
            i += 1
        except goBackErr:
            firstrun = False
            if i > 0:
                i -= 1
            else:
                print "Cannot go back."


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
    show = select(shows, q_show)
    episodes = show.nextlist()
    #episodes = show.get_episodelist(show.link)

    first = True
    while True:
        episode = select(episodes, q_epnum, sh_quick=first)
        hosts = episode.nextlist()
        url = select(hosts, q_host, sh_quick=first)
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
