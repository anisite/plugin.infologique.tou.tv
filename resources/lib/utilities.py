import os
import sys
import time

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer
cache = StorageServer.StorageServer("toutv.data", 1)

if sys.version_info.major >= 3:
    # Python 3 stuff
    from urllib.parse import quote_plus, unquote_plus
    from urllib.request import Request, urlopen
else:
    # Python 2 stuff
    from urllib import quote_plus, unquote_plus
    from urllib2 import Request, urlopen

try:
    import json
except ImportError:
    import simplejson as json
    

from traceback import print_exc

if sys.version >= "2.5":
    from hashlib import md5 as _hash
else:
    from md5 import new as _hash

try:
    from xbmcaddon import Addon
    from xbmc import translatePath
    BASE_CACHE_PATH   = translatePath( "special://profile/Thumbnails/Video" )
    ADDON             = Addon( "plugin.infologique.tou.tv" )
except:
    BASE_CACHE_PATH   = ""


def time_took( t ):
    t = ( time.time() - t )
    #minute
    if t >= 60: return "%.3fm" % ( t / 60.0 )
    #millisecond
    if 0 < t < 1: return "%.3fms" % ( t )
    #second
    return "%.3fs" % ( t )


def get_clientKey():
    return cache.cacheFunction(get_clientKey_internal)

def get_clientKey_internal():
    url="https://services.radio-canada.ca/toutv/presentation/settings?device=web&version=4"  
    try:
        req  = Request(url)
        req.add_header('Accept', 'application/json')
        resp = urlopen(req)
        clientKey = json.loads(resp.read().decode('utf8'))["LoginClientIdWeb"]
    except:
        print ("Oups, probleme avec "  + url + ": on utilise la valeur par default")
        clientKey = "90505c8d-9c34-4f34-8da1-3a85bdc6d4f4" # valeur par defaut si erreur
    return clientKey
