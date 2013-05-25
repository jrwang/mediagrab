import requests
import subprocess


import list.py, deluge.py

# run deluged?

path = "~/mediaGrab_files/"

def tpb_get(query, top=1):
    '''Search the pirate bay for the title and returns a list of (torrent_name, magnet URI)s'''
    # use this nifty pirate bay API
    
    params = {"id" : query, "$filter": "category eq 'Movies' or category eq 'HD - Movies'", "top" : top}
    #params = {"id" : title}

    r = requests.get("http://apify.ifc0nfig.com/tpb/search", params=params)
    return [(t['name'], t['magnet'], id_from_magnet(t['magnet'])) for t in r.json()]

def id_from_magnet(magnet):
    '''Extracts and returns torrent_id (BTIH hash ID) from a magnet URI link'''
    parts = magnet.split('&')
    for p in parts:
        if 'xt=urn:btih:' in p:
            torrent_id = p.split('xt=urn:btih:')[-1]
    return torrent_id

def get(item):
    if isinstance(item, list.Movie):
        torrents = tpb_get(item.title + item.details['Year'])
        for name, magnet, torrent_id in torrents:
           if deluge.add(name, magnet): # if successful
               item.dl, item.tid = 0, torrent_id
               break
    elif isinstance(item, list.Album):
        torrents = tpb_get(item.title + item.details['Year'])
        for name, magnet, torrent_id in torrents:
           if deluge.add(name, magnet): # if successful
               item.dl, item.tid = 0, torrent_id
               break
    elif isinstance(item, list.Album):
        torrents = tpb_get(item.title + item.details['Year'])
        for name, magnet, torrent_id in torrents:
           if deluge.add(name, magnet): # if successful
               item.dl, item.tid = 0, torrent_id
               break



