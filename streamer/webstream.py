import os, subprocess, re, click
from parsers.classes import Torrent_File

name_color = "white"
def pick_show(shows):
    for i, show in enumerate(shows):
        index = click.style("{}] ".format(i+1), fg="magenta")
        ep_count = click.style("({:3})".format(show.ep_count), fg="blue")
        name = click.style(show.name, fg= name_color)
        click.echo(u"{:<14}{} {:100}".format(index, ep_count , name))

    p = click.prompt("Pick Show", type=click.IntRange(1, len(shows)))
    return shows[p-1]

def pick_episode(episodes):
    for i, ep in enumerate(episodes):
        index = click.style("{}] ".format(i+1), fg="magenta")
        ep_num = click.style("({:>3})".format(ep.ep_number), fg="blue")
        name = click.style(ep.ep_title, fg= name_color)
        click.echo(u"{:<14}{} {:100}".format(index, ep_num, name))

    p = click.prompt("Pick Episode", type=click.IntRange(1, len(episodes)))
    return episodes[p-1]

def pick_host(hosts):
    for i, host in enumerate(hosts):
        index = click.style("{}] ".format(i+1), fg="magenta")
        res = host.resolution + "p"
        resolution = click.style("({:>5})".format(res), fg="blue")
        name = click.style(host.host, fg= name_color)
        click.echo(u"{:<14}{} {:100}".format(index, resolution, name))

    p = click.prompt("Pick Stream", type=click.IntRange(1, len(hosts)))
    return hosts[p-1].link
