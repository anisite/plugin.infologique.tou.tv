
import os
import sys
import xbmc
import xbmcgui
import scraper
import inputstreamhelper

from scraper import getVideo
from scraper import getVideoExtra
from traceback import print_exc
from xbmcaddon import Addon

ADDON             = Addon( "plugin.infologique.tou.tv" )

# set our infolabels
infoLabels = {
    "tvshowtitle": unicode( xbmc.getInfoLabel( "ListItem.TvShowTitle" ), "utf-8" ),
    "title":       unicode( xbmc.getInfoLabel( "ListItem.Title" ),       "utf-8" ),
    "genre":       unicode( xbmc.getInfoLabel( "ListItem.Genre" ),       "utf-8" ),
    "plot":        unicode( xbmc.getInfoLabel( "ListItem.Plot" ),        "utf-8" ),
    "Aired":       unicode( xbmc.getInfoLabel( "ListItem.Premiered" ),   "utf-8" ),
    "mpaa":        unicode( xbmc.getInfoLabel( "ListItem.MPAA" ),        "utf-8" ),
    "duration":    unicode( xbmc.getInfoLabel( "ListItem.DUration" ),    "utf-8" ),
    "studio":      unicode( xbmc.getInfoLabel( "ListItem.Studio" ),      "utf-8" ),
    "cast":        [unicode( xbmc.getInfoLabel( "ListItem.Cast" ),        "utf-8" )],
    "writer":      unicode( xbmc.getInfoLabel( "ListItem.Writer" ),      "utf-8" ),
    "director":    unicode( xbmc.getInfoLabel( "ListItem.Director" ),    "utf-8" ),
    "season":      int(     xbmc.getInfoLabel( "ListItem.Season" )    or "-1"    ),
    "episode":     int(     xbmc.getInfoLabel( "ListItem.Episode" )   or "1"     ),
    "year":        int(     xbmc.getInfoLabel( "ListItem.Year" )      or "0"     ),
    }
# set our thumbnail
g_thumbnail = unicode( xbmc.getInfoImage( "ListItem.Thumb" ), "utf-8" )

savedTime = 0
totalTime = 0
key = 0
url = ""
listitem = None
dataEmission = None

#def playVideo( PID, startoffset=None, strwatched=None, listitem=None ):
#    #global g_strwatched
#    #if not g_strwatched and strwatched is not None:
#    #    g_strwatched = strwatched
#
#    # set our play path
#    rtmp_url = getVideo( PID )
#    rtmp_url = rtmp_url["url"].replace(",.mp4",",3000,.mp4")
#    #rtmp_url += " playpath=" + playpath + " app=ondemand/" + other
#
#    #set listitem
#    #if listitem is None:
#    #    listitem = xbmcgui.ListItem( infoLabels[ "title" ], '', "DefaultVideo.png", g_thumbnail )
#    #    listitem.setInfo( "Video", infoLabels )
#
#    #listitem.setProperty( "PlayPath", playpath )
#    #listitem.setProperty( "swfUrl", "http://lg.tou.tv/SSRtmpPlayer.swf" )
#    #listitem.setProperty( "PID", PID )
#
#    #if str( startoffset ).isdigit():
#    #    listitem.setProperty( "startoffset", str( startoffset ) ) #in second
#
#    # play media
#    #player = TouTvPlayer( xbmc.PLAYER_CORE_DVDPLAYER )
#    #player._play( rtmp_url, listitem )
#    #setWatched( listitem )
#    player = None
#    try:
#        player = XBMCPlayer( xbmc.PLAYER_CORE_DVDPLAYER )
#    except Exception:
#        player = XBMCPlayer( )
#        pass
#
#    player.play( rtmp_url )


def playVideoExtra( PID, pKEY, startoffset=None, listitem_in=None ):
    global  savedTime, totalTime, key, listitem, url, dataEmission
    
    listitem = listitem_in

    data = getVideoExtra( PID )
    
    if listitem is None:
        listitem = xbmcgui.ListItem( infoLabels[ "title" ], '', "DefaultVideo.png", g_thumbnail )
        listitem.setInfo( "Video", infoLabels )

    listitem.setProperty( "startoffset", str( startoffset ) ) #in second
    
    if data['url'] is None:
        return
        #xbmcgui.Dialog().ok("Oups","Le contenu n'est pas disponible pour les non abonnés EXTRA.")
    else:
        #if data['isDRM']:
        PROTOCOL = 'mpd'
        DRM = 'com.widevine.alpha'
        BEARER  = data['widevineAuthToken']
        url = data['url']
        url = url.replace('(filter=2000)','(filter=3000)')
        url = url.replace('(filter=3000)', '(filter=3000,format=mpd-time-csf)')
        
        is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
        if is_helper.check_inputstream():
            listitem.setProperty('path', url)
            listitem.setProperty('inputstreamaddon', is_helper.inputstream_addon)
            listitem.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
            listitem.setMimeType('application/dash+xml')
            listitem.setProperty('inputstream.adaptive.license_type', DRM)
            listitem.setProperty('inputstream.adaptive.license_key', data['widevineLicenseUrl'] + '|Authorization=' + BEARER +'|R{SSM}|')
            listitem.setProperty('inputstream.stream_headers', 'Authorization=' + BEARER)

        # play media
        player = None
        try:
            player = XBMCPlayer(xbmc.PLAYER_CORE_AUTO)
        except Exception:
            player = XBMCPlayer()
            pass
     
        print "================== URL =================="
        

        
        if ADDON.getSetting( "typeflux" ) == "RTSP":
            #Replace URL to listen RTSP serveur
            path = url.split("~acl=/i/", 1)[1].split("*~hmac=",1)[0]
            url = "rtsp://medias-rtsp.tou.tv/vodtoutv/_definst_/mp4:" + path +  "3000.mp4"

        player.play( url, listitem )
        
        key = data['IdMedia']
        dataEmission = data['emission']
        url = PID
        
        while player.is_active:
            try:
                savedTime = player.getTime()
                totalTime = player.getTotalTime()
            except:
                pass
            xbmc.sleep(100)

    
def SetWatchedExterne(time=-1, Refresh=False):
    global savedTime, totalTime, key, url, dataEmission
    
    if time == -1 :
        time = savedTime
    
    try:
        del dataEmission['Details2']
    except KeyError:
        pass
    
    try:
        new = {}
        new[str(url)] = {
                    "key": str(key),
                    "currentTime" : time,
                    "totalTime" : totalTime,
                    "timestamp" : sys.modules[ 'resources.lib.toutv' ].getGMTunixtimestamp(),
                    "data" : dataEmission
                    }
    
        sys.modules[ 'resources.lib.toutv' ].goSync( new, Refresh )
    except: print_exc()
    
class XBMCPlayer(xbmc.Player):

    def __init__( self, *args, **kwargs ):
        self.is_active = True
        print "#XBMCPlayer#"
    
    def onPlayBackPaused( self ):
        xbmc.log("#Im paused#")
        print self.getTime()
        SetWatchedExterne(time=self.getTime(), Refresh=False)
        #streams = self.getAvailableAudioStreams()
        #print "streams ======================================================="
        #print streams
        
    def onPlayBackResumed( self ):
        xbmc.log("#Im Resumed #")
        
    def onPlayBackStarted( self ):
        print "#Playback Started#"
        
    def onPlayBackEnded( self ):
        #Fin du fichier, ou une coupure d'internet.
        print "PlayBack- END ------"
        #print self.getTime()
        self.is_active = False
        SetWatchedExterne(Refresh=True)
        #setWatched()

    def onPlayBackStopped( self ):
        #Fin avec le bouton stop
        print "PlayBack- KILLED ------"
        #print self.getTime()
        self.is_active = False
        SetWatchedExterne(Refresh=True)
    

if ( __name__ == "__main__" ):
    try:
        # get pid
        PID = sys.argv[ 1 ]
        playVideoExtra( PID )
    except:
        print_exc()

