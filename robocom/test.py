import urllib2
import json
server = "http://192.168.0.5:5000/"
f = urllib2.urlopen(server)
print json.loads(f.read())
