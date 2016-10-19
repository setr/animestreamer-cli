import attr

@attr.s
class TorrentFetcher(object):
    sitename = attr.ib()
    fetch_torrentlist = attr.ib()

@attr.s
class Torrent(object):
    name       = attr.ib()
    trusted    = attr.ib()
    size       = attr.ib()
    seeders    = attr.ib()
    leechers   = attr.ib()
    link       = attr.ib()
    get_magnet = attr.ib()

@attr.s
class Torrent_File(object):
    name     = attr.ib()
    size     = attr.ib()

@attr.s
class WebFetcher(object):
    sitename = attr.ib()
    fetch_shows = attr.ib()

@attr.s
class WebSeries(object):
    name            = attr.ib()
    link            = attr.ib()
    get_episodelist = attr.ib()
    ep_count        = attr.ib(default = None)

@attr.s
class WebEpisode(object):
    ep_number  = attr.ib()
    ep_title   = attr.ib()
    ep_link    = attr.ib()
    get_videos = attr.ib()

@attr.s
class WebVideo(object):
    host       = attr.ib()
    resolution = attr.ib()
    link       = attr.ib()
