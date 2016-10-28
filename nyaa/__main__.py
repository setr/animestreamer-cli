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
class repeatErr(Exception):
    pass
class finishedErr(Exception):
    pass

singleopts = {
            #'n': 'Next page of list', 
            'b' : 'go Back to previous menu',
            'r' : 'Repeat options',
            'h' : 'Print help'
            }
indexopts = {
            'd': 'Describe item'
            }

def printhelp():
    click.echo("")
    click.echo("Usage: [INDEX]")
    click.echo("Usage: [OPTION] (INDEX)")

    click.echo("Options -- no index:")
    for k,v in singleopts.items():
        click.echo("\t", nl=False)
        k = click.style(k, fg="magenta")
        click.echo('{} {}'.format(k, v))

    click.echo("Options -- with index:")
    for k,v in indexopts.items():
        click.echo("\t", nl=False)
        k = click.style(k, fg="magenta")
        click.echo('{} {}'.format(k, v))

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
                match = re.search("([A-Za-z]) *(\d+)?", userin)
                modifier = match.group(1).lower()
                p = match.group(2)
                if p and modifier in indexopts.keys():  # handle menu modifiers requiring an option selected
                    p = int(p)
                    err = checkrange(p)
                    if not err:
                        if modifier == 'd':
                            click.echo('{}'.format( options[p-1] ))
                            click.echo( '    ' + options[p-1].description() )
                # ie d with no index
                elif not p and modifier in indexopts.keys():
                    o = click.style(modifier, fg="magenta")
                    i = click.style("[index]", fg="blue") 
                    err = "Usage: {} {}".format(o, i)

                # a non-index option, but given an index anyways, is accepted and index ignored.
                elif not p and modifier in singleopts.keys():
                    if modifier == 'b':
                        raise goBackErr
                    elif modifier == 'r':
                        raise repeatErr
                    elif modifier == 'h':
                        printhelp()
                else:
                    raise AttributeError
            except AttributeError:
                i = click.style('[index]', fg="magenta")
                o = click.style('(option)', fg="blue")
                o2 = click.style('[option]', fg="blue")
                msg = click.style('Invalid input.', fg="red")
                err = "{} Correct form: {} {} or {}".format(msg, o, i, o2)
        if err:
            click.echo(err)
    click.echo(u"selected: {} {}".format(index+1, options[index]))
    return options[index]


def select(options, quickvar, sh_quick=True):
    # sh_quick --> should we consider quickvar? We only want to when straight from cli.
    if quickvar and sh_quick:
        try:
            click.echo(u"selected: {}".format(options[quickvar-1]))
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
        index = click.style("{:<3}".format(i+1), fg="magenta")
        click.echo(u"{} {}".format(index, option))

    try:
        return pickloop(options)
    except repeatErr:
        return select(options, None, False)

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


@click.command('torrent', short_help='Search from available torrent websites.')

@click.argument('search_query', nargs=-1, 
        callback=lambda ctx, param, val: ' '.join(val),
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

    # quick-select options, from the cli
    q_torrent = menuopts[0] if menuopts else None
    q_filenum = menuopts[1] if len(menuopts) > 1 else None
    firstrun = True

    @attr.s
    class Storage(object):
        torrents     = attr.ib(init=False),
        torrentname  = attr.ib(init=False),
        magnet       = attr.ib(init=False),
        filelist     = attr.ib(init=False),
        filen        = attr.ib(init=False),

    def get_query(s):
        from nyaa.parsers.nyaa import parser as nyaa
        if firstrun and search_query:
            query = search_query
        else:
            query = click.prompt("Please enter a search term")
            if query == 'b':
                raise goBackErr

        s.torrents = nyaa.fetch_torrentlist(query)
        s.torrents = sorted(s.torrents, key=lambda t: t.name)

    def select_torrent(s):
        torrent = select(s.torrents, q_torrent, sh_quick=firstrun)
        s.magnet = torrent.get_magnet()
        s.torrentname = torrent.name
        s.filelist = webtorrent_filelist(s.magnet)

    def select_filen(s):
        click.echo("getting filelist...")
        click.echo("")
        s.filen = select(s.filelist, q_filenum, sh_quick=firstrun)

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
        finally:
            raise finishedErr
            #raise goBackErr

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
        except (goBackErr, finishedErr):
            if i > 0:
                i -= 1
            else:
                click.echo("cannot go back.")
            firstrun = False

@click.command('web', short_help='Search from available streaming websites')

@click.argument('search_query', nargs=-1, 
        callback=lambda ctx, param, val: ' '.join(val),
        required=False)

@click.option('--menuopts', '-o', callback=menuoptfn, help="period delimited list of integers, to pre-emptively select menu options.")
@click.option('--mpvpass', '-m', default=None, type=unicode, help="cli options directly passed to mpv.")

@handleEmptyMenu
def web(search_query, menuopts, mpvpass):
    # pick a show
    # pick an episode
    # pick a host
    # play
    q_show   = menuopts[0] if menuopts else None
    q_epnum =  menuopts[1] if len(menuopts) > 1 else None
    q_host   = menuopts[2] if len(menuopts) > 2 else None
    firstrun = True

    @attr.s
    class Storage(object):
        shows          = attr.ib(init = False),
        episodes       = attr.ib(init = False),
        url            = attr.ib(init = False),
        showname       = attr.ib(init = False),
        episode_number = attr.ib(init = False)

    def get_query(s):
        from nyaa.parsers.masterani import parser as masterani
        if firstrun and search_query:
            query= search_query
        else:
            query = click.prompt("Please enter a search term")
            if query == 'b':
                raise goBackErr
        s.shows = masterani.fetch_shows(query)

    def select_show(s):
        show = select(s.shows, q_show)
        s.showname = show.name
        s.episodes = show.nextlist()

    def select_episode(s):
        episode = select(s.episodes, q_epnum, sh_quick=firstrun)
        s.episode_number = episode.ep_number
        s.hosts = episode.nextlist()

    def select_host(s):
        url = select(s.hosts, q_host, sh_quick=firstrun)
        s.url = url.link

    def execute_file(s):
        try:
            name = click.style(s.showname, underline=True)
            ep = click.style(str(s.episode_number), fg="magenta")
            click.echo("Playing: episode {} {}".format(ep, name))
            command = ["mpv", s.url]
            if mpvpass:
                command.insert(1, mpvpass)
            subprocess.call( command )
        except KeyboardInterrupt:
            time.sleep(0.5) # so the user has a chance to interrupt again to kill python, in the case where theres 1 ep, 1 host
        finally:
            raise finishedErr


    menu = [
        get_query,
        select_show,
        select_episode,
        select_host,
        execute_file]

    s = Storage()
    s.search_query = search_query
    i = 0
    while i < len(menu):
        try:
            menu[i](s)
            i += 1
        except goBackErr: # get_query doesn't throw goBack, so we don't have to worry about menu[0] - 1.
            if i > 0:
                i -= 1
            else:
                click.secho("Error: Cannot go back.", fg="red")
            firstrun = False
        except finishedErr:  # we want to get back to select_episode, not select_host
            i -= 2
            firstrun = False

def main():
    cli.add_command(torrent)
    cli.add_command(web)
    cli()

if __name__ == "__main__":
    main()
