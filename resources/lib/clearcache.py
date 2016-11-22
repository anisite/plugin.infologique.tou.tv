
import os
import sys

import xbmc
import xbmcgui
import xbmcvfs
from xbmcaddon import Addon

ADDON = Addon( "plugin.infologique.tou.tv" )
ADDON_CACHE = os.path.join( xbmc.translatePath( ADDON.getAddonInfo( 'profile' ) ), ".cache" )

if sys.argv[ 1 ].lower() == "full":
    print "[TouTv] deleting full cache"
    for root, dirs, files in os.walk( ADDON_CACHE ):
        for file in files:
            xbmcvfs.delete( os.path.join( root, file ) )
    xbmcgui.Dialog().ok( ADDON.getAddonInfo( 'name' ), "Clean Cache...", "Success" )

elif sys.argv[ 1 ].lower() == "badthumbs":
    print "[TouTv] delete: %r" % os.path.join( ADDON_CACHE, "badthumbs.txt" )
    xbmcvfs.delete( os.path.join( ADDON_CACHE, "badthumbs.txt" ) )
    xbmcgui.Dialog().ok( ADDON.getAddonInfo( 'name' ), "Clear debug infos of thumbails", "Success" )
