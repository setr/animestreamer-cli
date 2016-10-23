#!/usr/bin/env python2.7
from __future__ import absolute_import
import click, subprocess, time
from nyaa.webtorrent import *

# show list
def pick(objtype, options, quickpick):
    if len(options) == 0:
        return None
    if len(options) == 1 and quickpick:
        click.echo("Only one option... Autoselecting: {}".format(options[0]))
        return options[0]
    
    for i, option in enumerate(options):
        index = click.style("{}]".format(i+1), fg="magenta")
        click.echo(u"{:<13} {}".format(index, option))

    #p = click.prompt("Pick {}".format(objtype), type=click.IntRange(1, len(options)))
    # if there are multiple options available, then show them.
    if options[0].options and not quickpick:
        selected = False
        while not selected:
            p = click.prompt("Pick {}".format(objtype), type=click.IntRange(1, len(options)))

            click.secho(u"Options:", fg="white")
            for letter, text in options[0].options:
                letter = click.style(letter, fg="magenta")
                click.echo(u"    [{}] {}".format(letter, text))

            modifier = click.prompt("Pick", default="s", show_default=True, type=click.Choice(map(lambda x: x[0], options[0].options)))
            modifier = modifier.strip()
            if modifier == 's':
                selected = True
            else:
                if modifier == 'd':
                    click.echo( options[p-1] )
                    click.echo( '    ' + options[p-1].description )
    else: # otherwise, just select it and move on.
        p = click.prompt("Pick {}".format(objtype), type=click.IntRange(1, len(options)))
    return options[p-1]

def select(text, options, quickvar, sh_quick=True, quickpick=False):
    # sh_quick --> should we consider quickvar? loops only want to use it once.
    if quickvar and sh_quick:
        try:
            return options[quickvar-1]
        except IndexError:
            click.echo("{}: Index out of range.".format(text))
    return pick(text, options, quickpick)

@click.group()
def cli():
    pass

@click.command('torrent', short_help='Search from available streaming websites')
@click.option('--search_query' , '-s' , prompt="Please enter a search term")
@click.option('--quick', '-q', multiple=True, type=int, help="quick select menu items. Only makes sense with -n")
@click.option('--quickpick', '-qp', is_flag=True, help="disables option menu for all items")
@click.option('--sortbyname'  ,  '-n' , is_flag=True)
@click.option('--mpvpass', '-m', default=None, type=unicode, help="cli options directly passed to mpv. ---TODO")
@click.option('--webtorrentpass', '-w', default=None, type=unicode, help="cli options directly passed to webtorrent")
@click.option('-x', type=click.IntRange(0,2), default=0, help="set 0 to stream. set 1 to dl. set 2 to dl & stream. use webtorrent's -o flag to set dl location. default = 0.")

def torrent(search_query, quick, quickpick, sortbyname, mpvpass, webtorrentpass, x):
    # pick a torrent
    # pick a video from the torrent
    # play
    from nyaa.parsers.nyaa import parser as nyaa

    q_torrent = quick[0] if quick else None
    q_filenum = quick[1] if len(quick) > 1 else None

    torrents = nyaa.fetch_torrentlist("urusei")

    if sortbyname:
        torrents = sorted(torrents, key=lambda t: t.name)

    torrent = select("Torrent", torrents, q_torrent, quickpick=quickpick)
    magnet = torrent.get_magnet(torrent)

    click.echo("getting filelist...")
    click.echo("")
    filelist = webtorrent_filelist(magnet)

    first = True
    while True:
        filen = select("Torrent File", filelist, q_filenum, sh_quick=first, quickpick=quickpick)

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
@click.option('--search_query' , '-s' , prompt="Please enter a search term")
@click.option('--quick', '-q', multiple=True, type=int)
@click.option('--quickpick', '-qp', is_flag=True, help="disables option menu for all items")
@click.option('--mpvpass', '-m', default=None, type=unicode, help="cli options directly passed to mpv.")
def web(search_query, quick, quickpick, mpvpass):
    from nyaa.parsers.masterani import parser as masterani
    # pick a show
    # pick an episode
    # pick a host
    # play
    q_show   = quick[0] if quick else None
    q_epnum = quick[1] if len(quick) > 1 else None
    q_host   = quick[2] if len(quick) > 2 else None


    shows = masterani.fetch_shows(search_query)
    show = select("Show", shows, q_show, quickpick=quickpick)
    episodes = show.nextlist()
    #episodes = show.get_episodelist(show.link)

    first = True
    while True:
        episode = select("Episode", episodes, q_epnum, sh_quick=first, quickpick=quickpick)
        hosts = episode.nextlist()
        url = select("Host", hosts, q_host, sh_quick=first, quickpick=quickpick)
        url = url.link

        try:
            name = click.style(show.name, underline=True)
            ep = click.style(episode.ep_number, fg="magenta")
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
