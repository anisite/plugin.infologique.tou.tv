
import os
import sys
import urllib
from traceback import print_exc

import xbmc
import xbmcgui
from xbmcaddon import Addon
ADDON = Addon( "plugin.infologique.tou.tv" )

BAD_THUMBS_FILE = os.path.join( xbmc.translatePath( ADDON.getAddonInfo( "profile" ) ), ".cache", "badthumbs.txt" )
BASE_CACHE_PATH = xbmc.translatePath( "special://profile/Thumbnails/Video" )

import toutvapiservice
urllib._urlopener = toutvapiservice.urllib._urlopener

try: STRBADTHUMBS = file( BAD_THUMBS_FILE, "r" ).read()
except: STRBADTHUMBS = ""
badthumbs = open( BAD_THUMBS_FILE, "w" )
badthumbs.write( STRBADTHUMBS )
def get_thumbnail( thumbnail_url, fanart=0, default='DefaultTouTv.png' ):
    global badthumbs, STRBADTHUMBS
    default = ( default, "" )[ fanart ]
    if thumbnail_url and thumbnail_url not in STRBADTHUMBS:
        try:
            filename = xbmc.getCacheThumbName( thumbnail_url )
            if fanart:
                filename = filename.replace( ".tbn", os.path.splitext( thumbnail_url )[ 1 ] )
                basedir  = os.path.dirname( BASE_CACHE_PATH )
            else:
                basedir = BASE_CACHE_PATH
            filepath = os.path.join( BASE_CACHE_PATH, filename[ 0 ], filename )

            if not os.path.exists( filepath ):
                if not os.path.exists( os.path.dirname( filepath ) ):
                    os.makedirs( os.path.dirname( filepath ) )
                fp, h = urllib.urlretrieve( thumbnail_url, filepath )
                if h[ "Content-Type" ] == "text/html":
                    print "bad thumb: %r" % thumbnail_url
                    print fp, str( h ).replace( "\r", "" )
                    try: os.remove( fp )
                    except: pass
                    filepath = ""

                    STRBADTHUMBS += thumbnail_url + "\n"
                    badthumbs.write( thumbnail_url + "\n" )
            thumbnail_url = filepath
        except:
            print_exc()
    elif thumbnail_url and thumbnail_url in STRBADTHUMBS:
        thumbnail_url = ""
    return thumbnail_url or default


class GuiView:

    def __init__( self ):
        self._content = ""
        self._listitems = []

    def _add_directory_item( self, url, listitem, isFolder, totalItems ):
        OK = False
        try:
            listitem.setPath( url )
            listitem.setProperty( "isFolder", str( bool( isFolder ) ).lower() )
            #fix thumb and fanart
            listitem.setThumbnailImage( get_thumbnail( listitem.getProperty( "thumb" ) ) )
            listitem.setProperty( "fanart_image", get_thumbnail( listitem.getProperty( "fanart_image" ), 1 ) )
            self._listitems.append( listitem )
            OK = True
        except:
            pass
        return OK

    def _add_directory_items( self, listitems ):
        OK = False
        for url, listitem, isFolder in listitems:
            OK = self._add_directory_item( url, listitem, isFolder, len( listitems ) )
        return OK

    def _set_content( self, succeeded, content, sort=True ):
        self._content = content
        if sort:
            self._add_sort_methods( succeeded )
        else:
            self._end_of_directory( succeeded )

    def _add_sort_methods( self, succeeded ):
        self._end_of_directory( succeeded )

    def _end_of_directory( self, succeeded ):
        import xbmcplugin
        xbmcplugin.endOfDirectory( int( sys.argv[ 1 ] ), False )

        w = Carrousel( "toutv-carrousel.xml", ADDON.getAddonInfo( 'path' ), listitems=self._listitems )
        w.doModal()
        container = w.container
        #xbmc.executebuiltin( 'Action(ParentDir)' )
        if container:
            if "PID=" in container:
                cmd = 'RunPlugin(%s)'
            else:
                cmd = 'Container.Update(%s)'
            xbmc.executebuiltin( cmd % container )
        del w


class Carrousel( xbmcgui.WindowXML ):
    def __init__( self, *args, **kwargs ):
        self.listitems = kwargs[ "listitems" ]
        self.container = None

        import TouTvPlayer
        self.player = TouTvPlayer

    def onInit( self ):
        try:
            self.clearList()
            [ self.addItem( listitem ) for listitem in self.listitems ]
            self.setFocusId( 50 )
        except:
            print_exc()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            if controlID == 50:
                listitem  = self.getListItem( self.getCurrentListPosition() )
                container = xbmc.getInfoLabel( "Container(50).ListItem.FilenameAndPath" )
                if "PID=" in container:
                    self.player.playVideo( listitem.getProperty( "PID" ), None,
                        listitem.getProperty( "strwatched" ), listitem )
                else:
                    self.container = container
                    self._close()
        except:
            self.container = None
            print_exc()

    def onAction( self, action ):
        if action in [ 9, 10, 92, 117 ]:
            self.container = None
            self._close()

    def _close( self ):
        self.close()
