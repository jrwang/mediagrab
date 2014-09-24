import subprocess


deluged = subprocess.call(['deluged'])
pgrep = subprocess.Popen(['pgrep', 'deluged'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = pgrep.communicate()
print '*', out, err, '*'
