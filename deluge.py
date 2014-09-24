import subprocess
import re
import time


#a = '''Name: Star.Trek.Into.Darkness.2013.CAM.XviD-Lum1x
#ID: 23b4a838fc78617214ae90dfe0131390063192c3
#State: Downloading Down Speed: 508.3 KiB/s Up Speed: 0.0 KiB/s ETA: 9m 8s
#Seeds: 190 (5653) Peers: 8 (1436) Availability: 201.82
#Size: 1.1 GiB/1.3 GiB Ratio: 0.001
#Seed time: 0 days 00:00:00 Active: 0 days 00:41:37
#Tracker status: openbittorrent.com: Announce OK
#Progress: 80.08% [###############################################~~~~~~~~~~~~]'''

#b = '''Name: Star.Trek.Into.Darkness.2013.CAM.XviD-Lum1x
#ID: 23b4a838fc78617214ae90dfe0131390063192c3
#State: Seeding Up Speed: 0.0 KiB/s
#Seeds: 0 (5577) Peers: 0 (1426) Availability: 0.00
#Size: 1.3 GiB/1.3 GiB Ratio: 0.001
#Seed time: 0 days 00:29:26 Active: 0 days 01:21:05
#Tracker status: openbittorrent.com: Announce OK'''

#c = '''Name: Brokeback.Mountain[2005]DvDrip[Eng]-aXXo
#ID: bf389e95a789784b0d6207afbc5800c4eddf497b
#State: Seeding Up Speed: 1.4 KiB/s
#Seeds: 0 (160) Peers: 1 (6) Availability: 0.00
#Size: 700.9 MiB/700.9 MiB Ratio: 0.142
#Seed time: 0 days 00:21:52 Active: 0 days 00:33:34
#Tracker status: openbittorrent.com: Announce OK'''

dl_pat = "\s*Name: (.*)\n\
ID: (.*)\n\
State: (.*) Down Speed: (.*) Up Speed: (.*) ETA: (.*)\n\
Seeds: (.*) Peers: (.*) Availability: (.*)\n\
Size: (.*) Ratio: (.*)\n\
Seed time: (.*) Active: (.*)\n\
Tracker status: (.*)\n\
Progress: (.*)\s*"

seed_pat = "\s*Name: (.*)\n\
ID: (.*)\n\
State: (.*) Up Speed: (.*)\n\
Seeds: (.*) Peers: (.*) Availability: (.*)\n\
Size: (.*) Ratio: (.*)\n\
Seed time: (.*) Active: (.*)\n\
Tracker status: (.*)\s*"

dl = re.compile(dl_pat)
seed = re.compile(seed_pat)

CONFIG_DIR = "config"
DOWNLOAD_DIR = "./" #current dir
PORT = "8888" # find an open port instead of just picking one...

# TODO if CONFIG_DIR:
    #connect_str = subprocess.call(["deluge-console", "-c", CONFIG_DIR, 'connect localhost:{}'.format(PORT)])

#TODO: check return codes from processes? 



def daemon_running():
    ls = subprocess.Popen(['ls', CONFIG_DIR], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ls.wait()
    out, err = ls.communicate()
    print repr(out)
    return "deluged.pid" in out

def run_daemon():
    '''Runs the deluge daemon (necesary before running deluge-console'''
    process = subprocess.call(["deluged", "-c", CONFIG_DIR, "-p", "{}".format(PORT)])
    time.sleep(.5) # needed to give daemon time to run, perhaps because of a deluge bug?
    return process

def kill_daemon():
    return subprocess.call(["pkill", "deluged"]) # need to fix this to just delete the deluged that WE started!

def do_cmd(cmd):
    if not daemon_running():
        run_daemon()
    #if CONFIG_DIR:
    print daemon_running()
    line = ["deluge-console", "-c", CONFIG_DIR, "connect localhost:{}; ".format(PORT)]
    line[-1] += cmd
    print line
    process = subprocess.Popen(line, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # return process
    process.wait()

    #kill_daemon() # if we do this, it won't download
    
    return process
    
def add(name, torrent, path=DOWNLOAD_DIR):
    #console = do_cmd("add -p {} {}".format(path+name, torrent))
    console = do_cmd("add -p {} {}".format(path, torrent)) # is this okay? are all torrents in a folder, or are there torrents with just a file?
    out, err = console.communicate()
    print repr(out), repr(err)
    return err == '' # not really meaningful, as it's not clear what an error here would do

def pause(torrent_id):
    return do_cmd("pause {}".format(torrent_id))

def delete(torrent_id):
    return do_cmd("del {} --remove_data".format(torrent_id))

def info(torrent_id = ""):
    if torrent_id == "":
        info = do_cmd("info")
        out, err = info.communicate()
        print out, err
    else:
        info = do_cmd("info -i {}".format(torrent_id))
        out, err = info.communicate()
        #progress bar 60 char
        name, t_id, state, down, up, eta, seeds, peers, avail, size, ratio, seed_time, active, tracker, progress = ''
        if out == '':
            result = ''
            print 'torrent not found!'
        elif "Progress" in out: # if still downloading:
            result = dl.match(out)
            #print [result.group(i) for i in range(1, dl_pat.count("(.*)"))]
            name, t_id, state, down, up, eta, seeds, peers, avail, size, ratio, seed_time, \
                active, tracker, progress = [result.group(i) for i in range(1, dl_pat.count("(.*)"))]
        else:
            result = seed.match(out)
            #print [result.group(i) for i in range(1, seed_pat.count("(.*)"))]
            name, t_id, state, up, seeds, peers, avail, size, ratio, seed_time, \
                active, tracker = [result.group(i) for i in range(1, seed.count("(.*)"))]
        print name, t_id
        return name
            
        #print name, t_id, state, down, up, eta, seeds, peers, avail, size, ratio, seed_time, active, tracker, progress
        #return d


