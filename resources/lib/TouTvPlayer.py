﻿
import os
import sys
import re
import xbmc
import xbmcgui
from . import scraper
import inputstreamhelper

from .scraper import getVideo
from .scraper import getVideoExtra
from traceback import print_exc
from xbmcaddon import Addon

ADDON             = Addon( "plugin.infologique.tou.tv" )
BUILD_NUMBER      = int(xbmc.getInfoLabel('System.BuildVersion').split('.')[0])
# set our infolabels
infoLabels = {
    "tvshowtitle": xbmc.getInfoLabel( "ListItem.TvShowTitle" ),
    "title":       xbmc.getInfoLabel( "ListItem.Title" ),      
    "genre":       xbmc.getInfoLabel( "ListItem.Genre" ),      
    "plot":        xbmc.getInfoLabel( "ListItem.Plot" ),       
    "Aired":       xbmc.getInfoLabel( "ListItem.Premiered" ),  
    "mpaa":        xbmc.getInfoLabel( "ListItem.MPAA" ),       
    "duration":    xbmc.getInfoLabel( "ListItem.DUration" ),   
    "studio":      xbmc.getInfoLabel( "ListItem.Studio" ),     
    "cast":        [xbmc.getInfoLabel( "ListItem.Cast" )],
    "writer":      xbmc.getInfoLabel( "ListItem.Writer" ),   
    "director":    xbmc.getInfoLabel( "ListItem.Director" ), 
    "season":      int(     xbmc.getInfoLabel( "ListItem.Season" )    or "-1"    ),
    "episode":     int(     xbmc.getInfoLabel( "ListItem.Episode" )   or "1"     ),
    "year":        int(     xbmc.getInfoLabel( "ListItem.Year" )      or "0"     ),
    }
# set our thumbnail
g_thumbnail = xbmc.getInfoImage( "ListItem.Thumb" )

savedTime = 0
totalTime = 0
key = 0
url = ""
urlemi = ""
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


def playVideoExtra( URLE, PID, startoffset=None, listitem_in=None ):
    global  savedTime, totalTime, key, listitem2, url, dataEmission, urlemi
    
    listitem = listitem_in
    urlemi = URLE
    data = getVideoExtra( URLE, PID )
    
    if listitem is None:
        #listitem = xbmcgui.ListItem( infoLabels[ "title" ], '', "DefaultVideo.png", g_thumbnail )
        listitem = xbmcgui.ListItem( infoLabels[ "title" ], '', "DefaultVideo.png" )
        listitem.setArt( { 'thumb' : g_thumbnail } )
        
    listitem.setInfo( type="video", infoLabels=None)

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
        is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
        if is_helper.check_inputstream():
            listitem.setProperty('path', url)
            if BUILD_NUMBER >= 19:
                listitem.setProperty('inputstream', is_helper.inputstream_addon)
            else:
                listitem.setProperty('inputstreamaddon', is_helper.inputstream_addon)
            listitem.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
            listitem.setMimeType('application/dash+xml')
            listitem.setProperty('inputstream.adaptive.license_type', DRM)
            listitem.setProperty('inputstream.adaptive.license_key', data['widevineLicenseUrl'] + '|x-dt-auth-token=' + BEARER +'&Content-Type=&Origin=https://ici.tou.tv&Referer=https://ici.tou.tv&User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36|R{SSM}|')
            listitem.setProperty('inputstream.stream_headers', 'Authorization=' + BEARER)

        # play media
        player = None
        try:
            player = XBMCPlayer(xbmc.PLAYER_CORE_AUTO)
        except Exception:
            player = XBMCPlayer()
            pass
     
        print ("================== URL ==================")
        
        #if ADDON.getSetting( "typeflux" ) == "RTSP":
        #    #Replace URL to listen RTSP serveur
        #    path = url.split("~acl=/i/", 1)[1].split("*~hmac=",1)[0]
        #    url = "rtsp://medias-rtsp.tou.tv/vodtoutv/_definst_/mp4:" + path +  "3000.mp4"

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
    global savedTime, totalTime, key, url, dataEmission, urlemi
    
    if time == -1 :
        time = savedTime
    
    try:
        del dataEmission['Details2']
    except KeyError:
        pass
    
    try:
        new = {
                "url": str(urlemi),
                "key": str(key),
                "currentTime" : time,
                "action": "increment",
                "totalTime": totalTime
               }
    
        sys.modules[ 'resources.lib.toutv' ].goSync( new, Refresh )
    except: print_exc()
    
class XBMCPlayer(xbmc.Player):

    def __init__( self, *args, **kwargs ):
        self.is_active = True
        print ("#XBMCPlayer#")
        xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    
    def onAVStarted( self ):
        # Force la derniere source audio pour eviter la video description
        # Generalement 2 sources:
        #   0 => video description, 
        #   1 => original
        self.setAudioStream(len(self.getAvailableAudioStreams()) - 1)
        self.setVideoStream(len(self.getAvailableVideoStreams()) - 1)

    def onPlayBackPaused( self ):
        xbmc.log("#Im paused#")
        print (self.getTime())
        SetWatchedExterne(time=self.getTime(), Refresh=False)
        #streams = self.getAvailableAudioStreams()
        #print "streams ======================================================="
        #print streams
        
    def onPlayBackResumed( self ):
        xbmc.log("#Im Resumed #")
        
    def onPlayBackStarted( self ):
        print ("#Playback Started#")
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
        
    def onPlayBackEnded( self ):
        #Fin du fichier, ou une coupure d'internet.
        print ("PlayBack- END ------")
        #print self.getTime()
        self.is_active = False
        SetWatchedExterne(Refresh=True)
        #setWatched()

    def onPlayBackStopped( self ):
        #Fin avec le bouton stop
        print ("PlayBack- KILLED ------")
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

