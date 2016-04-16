import requests
import json
import pprint
from collections import namedtuple
from hashlib import sha1
import os

Entry = namedtuple("Entry", ["lat", "lon", "name"])

# be polite and only scrape oaklandiwki once
file_cache = { }
file_cache_dir = "cache"
try:
    os.mkdir(file_cache_dir)
except OSError:
    pass

def cached_get(url):
    url_sha = sha1(url).hexdigest()
    if url_sha in file_cache:
        return file_cache[url_sha]
    else:
        print "cache miss on %s; loading from localwiki" % url
        resp = requests.get(url)
        obj = json.loads(resp.text)
        with open("%s/%s" % (file_cache_dir, url_sha), 'w') as file_:
            file_.write(resp.text)
        return obj

def load_cache_from_disk():
    for filename in os.listdir(file_cache_dir):
        with open("%s/%s" % (file_cache_dir, filename)) as file_:
            obj = json.loads(file_.read())
            file_cache[filename] = obj

load_cache_from_disk()

BASE_URL = "https://localwiki.org/api/v4/"
omj_path = "maps/?tags=oaklandmapjam"
map_objs = cached_get(BASE_URL + omj_path)
entries = []
for map_obj in map_objs['results']:
    map_obj_page = cached_get(map_obj.get('page'))
    name = map_obj_page.get('name')
    map_points = map_obj.get('points')
    if map_points:
        point = map_points.get('coordinates')[0]
        entry = Entry(lat=point[0], lon=point[1], name=name)
        entries.append(entry)

pprint.pprint(entries)
