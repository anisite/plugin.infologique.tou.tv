
import os
import sys
import time
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
    #ADDON_CACHE       = os.path.join( translatePath( ADDON.getAddonInfo( 'profile' ) ), ".cache" )
    #CACHE_EXPIRE_TIME = float( ADDON.getSetting( "expiretime" ).replace( "0", ".5" ).replace( "25", "0" ) )
except:
    BASE_CACHE_PATH   = ""
    #ADDON_CACHE       = ""
    #CACHE_EXPIRE_TIME = 72

#if not os.path.exists( ADDON_CACHE ):
#    os.makedirs( ADDON_CACHE )


#def is_expired( lastUpdate, hrs=CACHE_EXPIRE_TIME ):
#    expired = time.time() >= ( lastUpdate + ( hrs * 60**2 ) )
#    return expired


def time_took( t ):
    t = ( time.time() - t )
    #minute
    if t >= 60: return "%.3fm" % ( t / 60.0 )
    #millisecond
    if 0 < t < 1: return "%.3fms" % ( t )
    #second
    return "%.3fs" % ( t )


def get_cached_filename( fpath ):
    c_filename = "%s.json" % _hash( repr( fpath ) ).hexdigest()
    return os.path.join( ADDON_CACHE, c_filename )


def get_cached_source( url, refresh=False, uselocal=False, debug=None ):
    """ fetch the cached source """
    c_source, sock, c_filename = "", None, None
    try:
        # set cached filename
        c_filename = get_cached_filename( url )
        # if cached file exists read this, only is expired
        if uselocal: refresh = False
        if not refresh and os.path.exists( c_filename ):
            if uselocal or not is_expired( os.path.getmtime( c_filename ) ):
                if debug: debug( "Reading local source: %r" % c_filename )
                sock = open( c_filename )
                c_source = sock.read()
    except:
        print_exc()
    return c_source, sock, c_filename
