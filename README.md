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

## TODO

### Torrent
* ``` webtorrent --download "magnet-link" --mpv ``` dl and stream
* add bakabt, kickass

### Stream
1. query against multiple anime sites
2. parse and gather results
 * site, resolution, size, name, sub/dub
3. display options in order of resolution
4. stream to mpv ```mpv "video-url"```

* ~~kissanime~~, masterani

### Options
* stream / torrent
* arbitrary args to pass to mpv
* mpv pick
* download / stream / both

## UI
* multi-select playlist
* ask for search term if not given
* fast way to drop in options
* possibly not quit python when webtorrent dies; instead offer list to choose another episode
