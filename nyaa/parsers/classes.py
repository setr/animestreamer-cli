import attr
import click
import re

def stylename(name):
    name_color = "white"
    cname = ""
    j = 0
    for match in re.finditer("\[.*?\]", name):
        cname += click.style(name[j: match.start()], fg= name_color)
        j = match.end()
        cname += match.group(0)
    cname += click.style(name[j:], fg= name_color)
    return cname

@attr.s
class TorrentFetcher(object):
    sitename = attr.ib()
    fetch_torrentlist = attr.ib()

    def __format__(self, format_spec):  
        return u"{}".format(sitename)

@attr.s
class Torrent(object):
    name       = attr.ib()
    trusted    = attr.ib()
    size       = attr.ib()
    seeders    = attr.ib()
    leechers   = attr.ib()
    link       = attr.ib()
    get_magnet = attr.ib()
    
    def __format__(self, format_spec):  
        name = stylename(self.name)
        seeders  = click.style("{:3}".format(self.seeders)  , fg = "green")
        leechers = click.style("{:3}".format(self.leechers) , fg = "red")
        size     = click.style("{:10}".format(self.size)    , fg = "blue")
        return u"{} {} {} {:100}".format(seeders, leechers, size, name)

@attr.s
class Torrent_File(object):
    index    = attr.ib()
    name     = attr.ib()
    size     = attr.ib()

    def __format__(self, format_spec):  
        name = stylename(self.name)
        size = click.style(self.size , fg="blue")
        return u"{:17} {:100}".format(size, name)

@attr.s
class WebFetcher(object):
    sitename = attr.ib()
    fetch_shows = attr.ib()

    def __format__(self, format_spec):  
        return u"{}".format(sitename)

@attr.s
class WebSeries(object):
    name            = attr.ib()
    link            = attr.ib()
    get_episodelist = attr.ib()
    ep_count        = attr.ib(default = None)
    def nextlist(self):
        return self.get_episodelist(self.link) 

    def __format__(self, format_spec):  
        ep_count = click.style("({:3})".format(self.ep_count), fg="blue")
        name = stylename(self.name)
        return u"{} {:100}".format(ep_count , name)

@attr.s
class WebEpisode(object):
    ep_number  = attr.ib()
    ep_title   = attr.ib()
    ep_link    = attr.ib()
    get_videos = attr.ib()

    def nextlist(self):
        return self.get_videos(self.ep_link) 
    def __format__(self, format_spec):
        ep_num = click.style("({:>3})".format(self.ep_number), fg="blue")
        name = stylename(self.ep_title)
        return u"{} {:100}".format(ep_num, name)

@attr.s
class WebVideo(object):
    host       = attr.ib()
    resolution = attr.ib()
    link       = attr.ib()
    def __format__(self, format_spec):
        res = self.resolution + "p"
        resolution = click.style("({:>5})".format(res), fg="blue")
        name = stylename(self.host)
        return u"{} {:100}".format(resolution, name)
