# animestreamer-cli
cli menu for torrents and probably website-streamers later

Requires webtorrent, mpv
depends on webtorrent to handle torrent-streaming
calls mpv for viewing streams

nyaa torrent "search_term"
nyaa web "search_term"

Currently:
    torrent => nyaa.se
    web => masterani.me

There are no other sites supported at this time.

# animestreamer-cli
cli menu for torrents and probably website-streamers later

depends on webtorrent to handle torrent-streaming

calls mpv for viewing

Requires:
  * nodejs
  * python2.7
  * mpv

```bash
pip install click attrs bs4
npm install -g webtorrent-cli
# for osx, because pip tries to delete the system's python2 six
pip2 install nyaa-cli --ignore-installed six
# normal install
pip2 install nyaa-cli

Usage:
nyaa [web|torrent] [query]

Ex:
nyaa web "urusei"
```

