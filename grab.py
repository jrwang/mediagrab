import requests
import time #

from media import *
import deluge

# deluge needs to be running to download?


m = "magnet:?xt=urn:btih:fbe8968c347735b326da5e7dff02fd93907edd03&dn=Realtime+Web+Apps+Apress+2013&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Ftracker.ccc.de%3A80&tr=udp%3A%2F%2Fopen.demonii.com%3A1337"
n = "magnet:?xt=urn:btih:be8968c347735b326da5e7dff02fd93907edd03&dn=Realtime+Web+Apps+Apress+2013"


def tpb_get(query, top=1):
    '''Search the pirate bay for the title and returns a list of (torrent_name, magnet URI)s'''
    # use this nifty pirate bay API
    
    params = {"id" : query, "$filter": "category eq 'Movies' or category eq 'HD - Movies'", "top" : top}
    #params = {"id" : title}

    r = requests.get("http://apify.ifc0nfig.com/tpb/search", params=params)
    print repr(r.text)
    print
    if r.text == '': # need to fix this to what it actually is
        print "Pirate Bay or Pirate Bay API is down, try again later"
        return None
    else:
        return [(t['name'], t['magnet'], id_from_magnet(t['magnet'])) for t in r.json()]

def id_from_magnet(magnet):
    '''Extracts and returns torrent_id (BTIH hash ID) from a magnet URI link'''
    parts = magnet.split('&')
    for p in parts:
        if 'xt=urn:btih:' in p:
            torrent_id = p.split('xt=urn:btih:')[-1]
    return torrent_id

def grab(item):
    if isinstance(item, Movie):
        torrents = tpb_get(item.title + item.details['Year'])
        # TODO: make sure this works if TPB is down
        for name, magnet, torrent_id in torrents:
            if deluge.add(name, magnet): # if successful
                item.dl, item.tid = 0, torrent_id
                print name, torrent_id
                print item
                break

i = Movie("brokeback")
i.details = {}
i.details['Year'] = ''

#deluge.run_daemon()
#print '*', deluge.daemon_running(), '*'

#grab(i)

#deluge.info()
#deluge.kill_daemon()
#print deluge.daemon_running()

queue = []
def enqueue(item):
    queue.append(item)

def dequeue():
    queue.pop(0)
    return queue[0]

def check_and_update():
    '''Check download status of torrents in the queue and update'''
    pass

