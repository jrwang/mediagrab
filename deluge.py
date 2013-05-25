import subprocess
import re


a = '''Name: Star.Trek.Into.Darkness.2013.CAM.XviD-Lum1x
ID: 23b4a838fc78617214ae90dfe0131390063192c3
State: Downloading Down Speed: 508.3 KiB/s Up Speed: 0.0 KiB/s ETA: 9m 8s
Seeds: 190 (5653) Peers: 8 (1436) Availability: 201.82
Size: 1.1 GiB/1.3 GiB Ratio: 0.001
Seed time: 0 days 00:00:00 Active: 0 days 00:41:37
Tracker status: openbittorrent.com: Announce OK
Progress: 80.08% [###############################################~~~~~~~~~~~~]'''

b = '''Name: Star.Trek.Into.Darkness.2013.CAM.XviD-Lum1x
ID: 23b4a838fc78617214ae90dfe0131390063192c3
State: Seeding Up Speed: 0.0 KiB/s
Seeds: 0 (5577) Peers: 0 (1426) Availability: 0.00
Size: 1.3 GiB/1.3 GiB Ratio: 0.001
Seed time: 0 days 00:29:26 Active: 0 days 01:21:05
Tracker status: openbittorrent.com: Announce OK'''

dl_pat = "Name: (.*)\n\
ID: (.*)\n\
State: (.*) Down Speed: (.*) Up Speed: (.*) ETA: (.*)\n\
Seeds: (.*) Peers: (.*) Availability: (.*)\n\
Size: (.*) Ratio: (.*)\n\
Seed time: (.*) Active: (.*)\n\
Tracker status: (.*)\n\
Progress: (.*)"

seed_pat = "Name: (.*)\n\
ID: (.*)\n\
State: (.*) Up Speed: (.*)\n\
Seeds: (.*) Peers: (.*) Availability: (.*)\n\
Size: (.*) Ratio: (.*)\n\
Seed time: (.*) Active: (.*)\n\
Tracker status: (.*)"

dl = re.compile(dl_pat)
seed = re.compile(seed_pat)

torrent_id = "23b4"

def add(name, torrent, path="./"):
    '''Returns True if successful, False if otherwise'''
    print ["deluge-console", "add -p {} {}".format(path+name, torrent)]
    return subprocess.call(["deluge-console", "add -p {} {}".format(path+name, torrent)]) == 0 # adds and returns status code

def info(torrent_id):
    text = subprocess.call(["deluge-console", "info -i {}".format(torrent_id)])
    print text
    raw_input()
    #progress bar 60 char
    if "Progress" in text: # if still downloading:
        result = dl.match(text)
        print [result.group(i) for i in range(1, dl_pat.count("(.*)"))]

    else:
        result = seed.match(text)
        print [result.group(i) for i in range(1, seed_pat.count("(.*)"))]
    return result
        
    #print name, t_id, state, down, up, eta, seeds, peers, avail, size, ratio, seed_time, active, tracker, progress
    #return d

info(torrent_id)
print info(a)
print info(b)
