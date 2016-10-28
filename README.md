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
cli menu for torrents and websites

depends on webtorrent to handle torrent-streaming

calls mpv for viewing

Keep in mind that webtorrent fails to initialize for some magnet urls. I don't know why. If it takes more than a minute to find peers, it's probably fucked. 


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

when selecting, the following commands are also available

Command  | Effect
:--------|:-------
d [index]| describe the item
r        | repeat the list
b        | go back to the previous list
h        | print help.
