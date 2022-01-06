# -*- coding: utf-8 -*-
#import ptvsd
#ptvsd.enable_attach(secret = 'mysecret')
#ptvsd.wait_for_attach

#Modules general
import os
import re
import sys
import datetime
import time
import calendar

if sys.version_info.major >= 3:
    # Python 3 stuff
    from urllib.parse import quote_plus, unquote_plus, unquote
else:
    # Python 2 stuff
    from urllib import quote_plus, unquote_plus, unquote

try:
    import json
except ImportError:
    import simplejson as json
    
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from traceback import print_exc

#modules XBMC
import xbmc
import xbmcvfs
import xbmcgui
from xbmcaddon import Addon
from . import scraper
from .utilities import get_clientKey

MYNAME            = "plugin.infologique.tou.tv" 
ADDON             = Addon( MYNAME )
ADDON_NAME        = ADDON.getAddonInfo( "name" )

ADDON_CACHE = None
try:
    ADDON_CACHE = xbmcvfs.translatePath( ADDON.getAddonInfo( 'profile' ))
except:
    ADDON_CACHE = xbmc.translatePath( ADDON.getAddonInfo( 'profile' ))

#SCRIPT_REFRESH    = os.path.join( ADDON.getAddonInfo( 'path' ), "resources", "lib", "refresh.py" )
LOGIN             = scraper.CheckLogged()

STRING_FOR_ALL = "[B]CONTENU accessible à TOUS[/B] - Cette émission peut être regardée partout dans le monde."

#FAVOURITES_XML = os.path.join( ADDON_CACHE, "favourites.xml" )

G_GENRE     = xbmc.getInfoLabel( "ListItem.Genre")
#ACTION_INFO = not bool( xbmc.getInfoLabel( "ListItem.Episode" ) )

watched_pending_db = ""
watched_db = ""


def getGMTunixtimestamp():
    future = datetime.datetime.utcnow()
    #print calendar.timegm(future.timetuple())
    return calendar.timegm(future.timetuple())

    #
    # 1- load data
    # 2- check last sync
    # 3- send pending data
    # 4- receive new data
    # 5- merge
    # 6- emptying pending file
    # 7- change last sync date
    # 8- write back data
    #

def getFolders():
    global watched_db, watched_pending_db
    watched_pending_db = os.path.join( ADDON_CACHE, "watched_pending_" + str(ADDON.getSetting( "username" )) + ".db" )
    watched_db = os.path.join( ADDON_CACHE, "watched_" + str(ADDON.getSetting( "username" )) + ".db" )

if not ADDON.getSetting( "setupOK" ):
    ADDON.openSettings()
    ADDON.setSetting( "setupOK", "True" )

def getPendingWatchFile():
    global watched_db, watched_pending_db

    if os.path.exists( watched_pending_db ):
        pendWatched = open( watched_pending_db ).read()
    else:
        f = open( watched_pending_db, "w" )
        f.write( "{}" )
        f.close()
        pendWatched = "{}"
    
    data = None
    try:
        data = json.loads( pendWatched )
    except:
        f = open( watched_pending_db, "w" )
        f.write( "{}" )
        f.close()
        pendWatched = "{}"
        data = json.loads( pendWatched )

    return data
    
def getWatchedFile():
    global watched_db, watched_pending_db
    
    if os.path.exists( watched_db ):
        watched = open( watched_db ).read()
    else:
        watched = '{"updateTime":0,"watched":{}}'
        f = open( watched_db, "w" )
        f.write( watched )
        f.close()
        
    data = None
    try:
        data = json.loads( watched )
    except:
        watched = '{"updateTime":0,"watched":{}}'
        f = open( watched_db, "w" )
        f.write( watched )
        f.close()
        data = json.loads( watched )
        
    return data

def goSync( new=None, refresh=False):
    global watched_db, watched_pending_db
        
    if scraper.isLoggedIn():
          
        try:

            if new:
                url = list(new.keys())[0]
                put_data = {'SeekTime': int(new[url]['currentTime']), 'Device':'web', 'Version':'4'}
                scraper.CALL_HTML_AUTH('https://services.radio-canada.ca/toutv/profiling/playbackstatus' + url,"PUT", json.dumps(put_data))
                           
        except:
            print_exc()
            
    if refresh:
        xbmc.executebuiltin( 'Container.Refresh' )
    
    return None

class Info:
    def __init__( self, *args, **kwargs ):
        # update dict with our formatted argv
        #print sys.argv
        try: exec ("self.__dict__.update(%s)" % ( sys.argv[ 2 ][ 1: ].replace( "&", ", " ).replace("%22",'"'), ))
        except: print_exc()
        # update dict with custom kwargs
        self.__dict__.update( kwargs )

    def __getattr__( self, namespace ):
        return self[ namespace ]

    def __getitem__( self, namespace ):
        return self.get( namespace )

    def __setitem__( self, key, default="" ):
        self.__dict__[ key ] = default

    def get( self, key, default="" ):
        return self.__dict__.get( key, default )#.lower()

    def isempty( self ):
        return not bool( self.__dict__ )

    def IsTrue( self, key, default="false" ):
        return ( self.get( key, default ).lower() == "true" )

#if  sys.argv[ 2 ] == "?url=%22carrousel%22":
    #print "guiview"
    #from GuiView import GuiView as viewtype
#else:
    #print "PluginView"
from .PluginView import PluginView as viewtype

class Main( viewtype ):
    
    def __init__( self ):
        self.clientKey = get_clientKey()
        viewtype.__init__( self )

        self.args = Info()

        if self.args.isempty():
            self._add_directory_root_extra()
            xbmc.executebuiltin("Container.SetViewMode(500)")

        elif self.args.PIDEXTRA:
            start_player = True
        
            if start_player:
                from . import TouTvPlayer as player
                
                if float(self.args.starttime) > 0:
                    m, s = divmod( round(float(self.args.starttime),0), 60)
                    h, m = divmod(m, 60)

                    dialog = xbmcgui.Dialog()
                    retour = dialog.select	("Reprise",
                                            ['Reprendre la lecture à ' + "%d:%02d:%02d" % (h, m, s), u'Reprendre depuis le début'])
                    
                    if retour == -1:
                        return
                    
                    if retour == 1:
                        self.args.starttime = 0
                    
                try: player.playVideoExtra( self.args.PIDEXTRA, self.args.KEY, startoffset=self.args.starttime )
                except: print_exc()
                
                xbmc.executebuiltin( 'Container.Refresh' )

        elif self.args.PID:
            start_player = True
            startoffset  = None

            if start_player:
                from . import TouTvPlayer as player
                try: player.playVideo( self.args.PID, startoffset=startoffset )
                except: print_exc()

        elif self.args.emissionIdExtra:
            self._add_directory_episodesExtra( self.args.emissionIdExtra )
                
        elif self.args.emissionId:
             self._add_directory_episodes( self.args.emissionId )

        elif self.args.webbrowser:
            import webbrowser
            webbrowser.open( unquote_plus( self.args.webbrowser ) )

        elif self.args.addtofavourites or self.args.removefromfavourites:

            favourite = self.args.addtofavourites or self.args.removefromfavourites
            response = scraper.POST_HTML("https://services.radio-canada.ca/toutv/profiling/bookmark/" + favourite, None, AUTH=True, METHOD= ("POST", "DELETE")[bool(self.args.removefromfavourites)])
            
            if bool(self.args.removefromfavourites):
                xbmc.executebuiltin( 'Container.Refresh' )

        elif self.args.setwatched or self.args.setunwatched:
        
            print ("SET watched/unwatched 0")
            key = self.args.setwatched or self.args.setunwatched
            
            
            
            new = {}
            
            time=0
            totalTime=0
            
            if bool( self.args.setunwatched ): #setUnwatched
                time=0
                totalTime=0
            else:
                time=100000
                totalTime=100000
                
            print ("SET watched/unwatched")
                
            new[key] = {
                        "currentTime" : time,
                        "totalTime" : totalTime,
                        "timestamp" : getGMTunixtimestamp(),
                        "key" : self.args.IdMedia
                        }
            goSync(new,True)

        elif self.args.url == "bookmark":
            self._add_api_favourites()
            xbmc.executebuiltin("Container.SetViewMode(502)")

        elif self.args.url == "ouvrirconfig":
            self._ouvrir_config()
            
        elif self.args.url == "enecoute":
            self._add_api_enecoute()
            
        elif self.args.url == "live":
            self._add_api_live()
            
        elif self.args.url != "":
            self._add_api_url()
            
        elif self.args.category == "extra":
            if  str(ADDON.getSetting( "username" )) == "":
                dialog = xbmcgui.Dialog()
                dialog.ok("Section Extra","Vous devez fournir vos infos d'authentification.")
            else:
                self._add_directory_extra()

        elif self.args.category == "collection":
            self._add_directory_collection()

        elif self.args.category == "recherche":
            self._add_directory_search()

        else:
            #show home
            section = {
                "favoris":     "EpisodesFavoris",      #<type 'list'>
                "adecouvrir":  "SelectionADecouvrir",  #<type 'dict'>
                "carrousel":   "SelectionCarrousel",   #<type 'dict'>
                "plusrecents": "SelectionPlusRecents", #<type 'dict'>
                }.get( self.args.category )
            if section:
                self._add_directory_accueil( section )
            else:
                self._end_of_directory( False )

    def _add_directory_root_extra( self ):
        
        OK = False
        listitems = []
        try:
            uri = sys.argv[ 0 ]

            sections = scraper.CALL_HTML_AUTH('https://services.radio-canada.ca/toutv/presentation/TagMenu?sort=Sequence&device=web&version=4', 'GET', None, 'client-key ' + self.clientKey)
            print ("----------DEBUG root extra---------")
            print (sections)
            sections = json.loads(sections)
            items = []

            items.append(( ( uri, 'ouvrirconfig' ), ( '[COLOR blue][B]' + LOGIN[1] + '[/B][/COLOR]',       '', 'DefaultUser.png'      )))
            if scraper.isLoggedIn():
                goSync()
                items.append((( uri, 'enecoute' ), ( u'Mes visionnements',       'Mes visionnements', 'DefaultInProgressShows.png'      )))
                items.append((( uri, 'bookmark' ), ( 'Mes Favoris',       'Mes Favoris', 'DefaultMusicTop100.png'      )))

            #items.append((None, ( u'[COLOR blue][B]Menu[/B][/COLOR]',       'Mes Favoris', 'DefaultAddonScreensaver.png'      )))
            #print sections
            
            items.append((( uri, 'live' ), ( 'En direct',       'En direct - NON FONCTIONNEL ENCORE', 'DefaultVideo.png'      )))
            items.append((( uri, '/Search?includeMedias=false' ), ( 'A-Z',       'A-Z', 'DefaultTVShowTitle.png'      )))
            items.append((( uri, '/CatchUp' ), ( 'Rattrapage',       'Rattrapage', 'DefaultAddonScreensaver.png'      )))
            
            for section in sections['Types']:
                #print section
                #if section['Category'] != None:
                
                imageicon =  sections['ImagePerTag'][section['Key']]
                
                if "parcourir_types" in imageicon:
                    imageicon = 'DefaultFolder.png'
                
                items.append((( uri, "/Category/" + quote_plus(section['Key'] or "") ), ( section['Title'], section['Title'], imageicon)))
            
            for section in sections['Network']:
                #print section
                #if section['Category'] != None:
                items.append((( uri, "/Category/" + quote_plus(section['Key'] or "") ), ( section['Title'], section['Title'], sections['ImagePerTag'][section['Key']] or 'DefaultFolder.png')))
            
            for section in sections['GenresThemes']:
                #print section
                #if section['Category'] != None:
                items.append((( uri, "/Category/" + quote_plus(section['Key'] or "") ), ( section['Title'], section['Title'], sections['ImagePerTag'][section['Key']] or 'DefaultFolder.png')))
            
            
            fanart = ADDON.getAddonInfo( "fanart" )

            for uri, item in items:
                listitem = xbmcgui.ListItem( *item )
                listitem.setProperty( "fanart_image", fanart )
                listitem.setArt( { 'thumb': item[2] } )
                self._add_context_menu_items( [], listitem )
                
                if isinstance(uri,tuple):
                    FOLDER = " / " + item[1]
                    url = '%s?url="%s"&folder="%s"' % (uri[0], uri[1], FOLDER)
                    listitems.append( ( url, listitem, True ) )
                else:
                    listitems.append( ( uri, listitem, False ) )
        except:
            print_exc()

        if listitems:
            OK = self._add_directory_items( listitems )
        # fake content movies to show container.foldername
        self._set_content( OK, "episodes", False )

    def AppendFolder(self, FOLDER, liste):
        FOLDER = unquote(FOLDER)
        listitem = xbmcgui.ListItem( "[B][COLOR white]* " + FOLDER + "[/COLOR][/B]")
        liste.append((None, listitem, True))
        self._add_context_menu_items( [], listitem )

    def _add_api_favoris( self, listitems, item, ToutesEmissions ) :
        #if (item[ "Title" ] is not None) and (item["Template"] != 'letter') and (item["Template"] != 'espace-partenaire') and (item['BookmarkKey']):
        color = ""
        if not item["IsFree"]:
            Title = "[COLOR gold][Extra][/COLOR] "
        else:
            Title = ""
        
        print(item)
        
        if not item["IsActive"]:
            if item['DepartureDescription'] is None:
                item['DepartureDescription'] = "Ce contenu n'est plus disponible"
            Title += " [COLOR red] " + item['DepartureDescription'] + "[/COLOR]"
    
        Title =  color + item[ "Title" ] + " " + Title

        #if not item["Description"] is None:
        #    Title = Title + " - " + item["Description"]
            
        listitem = xbmcgui.ListItem( Title)

        #fanart finder
        fanart = None
        for i in ToutesEmissions:
            if i['ProgramKey'] == item['ProgramKey']:
                fanart = i['ImageUrl']
                break
        
        if fanart is not None:
            listitem.setProperty( "fanart_image", self.PimpImage(fanart) )
        #listitem.setProperty( "fanart_image", "fanart.jpg" )
        #listitem.setThumbnailImage( self.PimpImage(str(item[ "ImageUrl" ]), 360, 202) )
        listitem.setArt( { 'thumb' : self.PimpImage(str(item[ "ImageUrl" ]), 360, 202) } )
        infoLabels = {
            "label" : Title,
            "plot":  item[ "Description" ] or "",
            }
        listitem.setInfo( "Video", infoLabels )

        self._add_favoris_context_menu_extra( item, listitem, False, False )

        url2 = '%s?emissionIdExtra="%s"&Key="%s"' % ( sys.argv[ 0 ], item[ "Url" ], item["Key"] )
        listitems.append( ( url2, listitem, True ) )
            
    def _add_api_enecoutelist( self, listitems, item, episodeContextMenu=False, MediaPlaybackStatuses = None, ToutesEmissions = None ) :
    
        if (item[ "Title" ] is not None) and (item["Template"] != 'letter'):
            color = ""
            if not item["IsFree"]:
                Title = "[COLOR gold][Extra][/COLOR] "
            else:
                Title = ""
                
            if not item["IsActive"]:
                Title += " [COLOR red] " + item['DepartureDescription'] + "[/COLOR]"
        
            Title =  color + item[ "Title" ] + " - " + item[ "HeadTitle" ]  + " " + Title

            url, listitem = self._get_episode_listitem_extra( item, item, item, item['Key'], False, forceTitle=Title, MediaPlaybackStatuses= MediaPlaybackStatuses, ToutesEmissions = ToutesEmissions)
            listitems.append( ( url, listitem, False ) )
            
    def _add_api_livelist( self, listitems, item, episodeContextMenu=False, ToutesEmissions = None ) :
    
        if (item[ "Title" ] is not None) and (item["Template"] != 'letter'):
            color = ""
            if not item["IsFree"]:
                Title = "[COLOR gold][Extra][/COLOR] "
            else:
                Title = ""
                
            if not item["IsActive"]:
                Title += " [COLOR red] " + item['DepartureDescription'] + "[/COLOR]"
        
            Title =  color + item[ "Title" ] + " - " + item[ "HeadTitle" ]  + " " + Title

            url, listitem = self._get_episode_listitem_extra( item, item, item, item['Key'], False, forceTitle=Title, MediaPlaybackStatuses= MediaPlaybackStatuses, ToutesEmissions = ToutesEmissions)
            listitems.append( ( url, listitem, False ) )

    def _ouvrir_config( self ):
        ADDON.openSettings()
    
    ##1 280 × 720
    def PimpImage( self, imgSrc, w=1280, h=720):
        imgSrcCopy = imgSrc
        if imgSrcCopy == None:
            return None
        else:
            return imgSrcCopy.replace("w_200,h_300", "q_80,w_" + str(w) +",h_" + str(h))

    def ToutesEmissions( self ):
        return json.loads(scraper.CALL_HTML_AUTH_CACHED('https://services.radio-canada.ca/toutv/presentation/search?includeMedias=false&device=web&version=4', 'GET', None, 'client-key ' + self.clientKey ))

    def _add_api_enecoute( self ):
        OK = False
        FOLDER = self.args.folder
        
        listitems = []
        self.AppendFolder(FOLDER, listitems)
        try:

            
            emissionsRC = scraper.GET_HTML_AUTH('https://services.radio-canada.ca/toutv/profiling/MyViews?device=phone_android&version=4')
            emissionsRC = json.loads(emissionsRC)
            
            toutesEmissions = self.ToutesEmissions()
            
            for lineup in emissionsRC['Lineup']['LineupItems']:
                self._add_api_enecoutelist(listitems, lineup, episodeContextMenu=False, MediaPlaybackStatuses=emissionsRC["MediaPlaybackStatuses"], ToutesEmissions = toutesEmissions)

        except:
            print_exc()

        if listitems:
            OK = self._add_directory_items( listitems )

        # fake content movies to show container.foldername
        self._set_content( OK, "episodes", False )
        
    def _add_api_live( self ):
        OK = False
        FOLDER = self.args.folder
        
        listitems = []
        items = []
        uri = sys.argv[ 0 ]
        self.AppendFolder(FOLDER, listitems)
        try:

            items.append((( uri, 'live/17'), ('Acadie'                      ,'En direct - Acadie'                      , 'DefaultVideo.png'      )))
            items.append((( uri, 'live/13'), ('Alberta'                     ,'En direct - Alberta'                     , 'DefaultVideo.png'      )))
            items.append((( uri, 'live/14'), ('Colombie-Britannique–Yukon'  ,'En direct - Colombie-Britannique–Yukon'  , 'DefaultVideo.png'      )))
            items.append((( uri, 'live/18'), ('Est du Québec'               ,'En direct - Est du Québec'               , 'DefaultVideo.png'      )))
            items.append((( uri, 'live/4' ), ('Estrie'                      ,'En direct - Estrie'                      , 'DefaultVideo.png'      )))
            items.append((( uri, 'live/29'), ('Grand Nord'                  ,'En direct - Grand Nord'                  , 'DefaultVideo.png'      )))
            items.append((( uri, 'live/15'), ('Manitoba'                    ,'En direct - Manitoba'                    , 'DefaultVideo.png'      )))
            items.append((( uri, 'live/7' ), ('Mauricie–Centre-du-Québec'   ,'En direct - Mauricie–Centre-du-Québec'   , 'DefaultVideo.png'      )))
            items.append((( uri, 'live/11'), ('Ontario'                     ,'En direct - Ontario'                     , 'DefaultVideo.png'      )))
            items.append((( uri, 'live/12'), ('Ottawa–Gatineau'             ,'En direct - Ottawa–Gatineau'             , 'DefaultVideo.png'      )))
            items.append((( uri, 'live/9' ), ('Québec'                      ,'En direct - Québec'                      , 'DefaultVideo.png'      )))
            items.append((( uri, 'live/10'), ('Saguenay–Lac-St-Jean'        ,'En direct - Saguenay–Lac-St-Jean'        , 'DefaultVideo.png'      )))
            items.append((( uri, 'live/16'), ('Saskatchewan'                ,'En direct - Saskatchewan'                , 'DefaultVideo.png'      )))
            items.append((( uri, 'live/19'), ('Terre-Neuve-et-Labrador'     ,'En direct - Terre-Neuve-et-Labrador'     , 'DefaultVideo.png'      )))
                        
        

            
            #toutesEmissions = json.loads(scraper.CALL_HTML_AUTH('https://services.radio-canada.ca/toutv/presentation/search?includeMedias=false&device=web&version=4', 'GET', None, 'client-key ' + self.clientKey ))
            
      
            
            #for key, value in regions:
            #    items.append((( uri, 'live/' + key ), ( value,  'En direct - ' + value, 'DefaultVideo.png'      )))
            
            for uri, item in items:
                listitem = xbmcgui.ListItem( *item )
                try:
                    id = [int(s) for s in uri[1].split('/') if s.isdigit()]
                    emissionsRC = scraper.CALL_HTML_AUTH('https://services.radio-canada.ca/toutv/presentation/live?device=web&version=4&channel=IciTele&regionId=' + str(id[0]), 'GET', None, 'client-key ' + self.clientKey )
                    emissionsRC = json.loads(emissionsRC)
                    #print emissionsRC
                        
                    #listitem.setProperty( "fanart_image", fanart )
                    listitem.setArt({ 'thumb': emissionsRC['broadcasts'][0]['picture']['url']})
                    #listitem.setLabel(listitem.getLabel() + " - " + str(emissionsRC['broadcasts'][0]['displayTitle']))
                    
                    print (emissionsRC['broadcasts'][0]['displayTitle'])
                    ##listitem.setInfo(type='video', infoLabels={'plot': emissionsRC['broadcasts'][0]['displayTitle'].decode('ascii').encode('utf-8') })
                    
                    self._add_context_menu_items( [], listitem )
                    
                    if isinstance(uri,tuple):
                        FOLDER = " / " + item[1]
                        url = '%s?url="%s"&folder="%s"' % (uri[0], uri[1], FOLDER)
                        listitems.append( ( url, listitem, False ) )
                    else:
                        listitems.append( ( uri, listitem, False ) )
                except:
                    pass
            #for key, value in regions
                #self._add_api_livelist(listitems, emissionsRC, episodeContextMenu=False, ToutesEmissions = toutesEmissions)
            
            #for lineup in emissionsRC['Lineup']['LineupItems']:
            #    self._add_api_enecoutelist(listitems, lineup, episodeContextMenu=False, MediaPlaybackStatuses=emissionsRC["MediaPlaybackStatuses"], ToutesEmissions = toutesEmissions)

        except:
            print_exc()

        if listitems:
            OK = self._add_directory_items( listitems )

        # fake content movies to show container.foldername
        self._set_content( OK, "episodes", False )
    
    def _add_api_favourites( self ):
        OK = False
        FOLDER = self.args.folder
        
        listitems = []
        self.AppendFolder(FOLDER, listitems)
        try:
            #genres = scraper.getGenres()
            emissions = scraper.GET_HTML_AUTH('https://services.radio-canada.ca/toutv/profiling/'+ self.args.url +'?device=web&version=4')
            emissions = json.loads(emissions)

            toutesEmissions = self.ToutesEmissions()

            for emission in emissions['LineupItems']:
                self._add_api_favoris(listitems, emission, toutesEmissions)

        except:
            print_exc()

        if listitems:
            OK = self._add_directory_items( listitems )
        # fake content movies to show container.foldername
        
        self._set_content( OK, "tvshows", False )
        
    def _add_api_url( self ):
        print ("_add_api_url")
        
        OK = False
        FOLDER = self.args.folder
        
        listitems = []
        self.AppendFolder(FOLDER, listitems)
        
        toutesEmissions = self.ToutesEmissions()

        try:
            url = unquote_plus(self.args.url)
            join = '?'
            if '?' in url:
                join = '&'
            genres = scraper.CALL_HTML_AUTH('https://services.radio-canada.ca/toutv/presentation' + unquote_plus(self.args.url) + join +'device=web&version=4', 'GET', None, 'client-key '+ self.clientKey )
            genres = json.loads(genres)
            
            if 'Lineups' in genres:
                for Lineup in genres['Lineups']:
                    FOLDER = self.args.folder + " / " + Lineup[ "Title" ]
                    url = '%s?url="%s"&folder="%s"&lineup="%s"' % ( sys.argv[ 0 ], self.args.url, FOLDER, Lineup[ "Name" ])
                    if self.args.lineup == "":
                        listitem = xbmcgui.ListItem( "[B][COLOR blue]" + Lineup[ "Title" ] + "[/COLOR][/B]")
                        self._add_context_menu_items( [], listitem )
                        listitems.append((url, listitem, True))

                    else:
                        print (self.args.lineup)
                        print (Lineup["Name"])
                        if Lineup["Name"] == self.args.lineup:
                            for genre in Lineup['LineupItems']:
                                self._add_api_favoris(listitems, genre, toutesEmissions)
            else:
                if 'A-Z' in FOLDER:
                    for Lineup in genres:
                        self._add_api_favoris_a_z(listitems, Lineup, toutesEmissions)
                else: 
                    for Lineup in genres['LineupItems']:
                        self._add_api_favoris(listitems, Lineup, toutesEmissions)
                
        except:
            print_exc()

        if listitems:
            OK = self._add_directory_items( listitems )
        # fake content movies to show container.foldername
        
        self._set_content( OK, "episodes", False )

    def _add_api_favoris_a_z( self, listitems, item, ToutesEmissions ) :
        #if (item[ "Title" ] is not None) and (item["Template"] != 'letter') and (item["Template"] != 'espace-partenaire') and (item['BookmarkKey']):
        color = ""
        if not item["IsFree"]:
            Title = "[COLOR gold][Extra][/COLOR] "
        else:
            Title = ""
            
        Title =  color + item[ "DisplayText" ] + " " + Title

        listitem = xbmcgui.ListItem( Title)

        #fanart finder
        for i in ToutesEmissions:
            if i['ProgramKey'] == item['ProgramKey']:
                fanart = i['ImageUrl']
                break
        
        listitem.setProperty( "fanart_image", self.PimpImage(fanart) )
        #listitem.setProperty( "fanart_image", "fanart.jpg" )
        #listitem.setThumbnailImage( self.PimpImage(str(item[ "ImageUrl" ]), 360, 202) )
        listitem.setArt( { 'thumb' : self.PimpImage(str(item[ "ImageUrl" ]), 360, 202) } )
        infoLabels = {
            "label" : Title
            #"plot":  item[ "Description" ] or "",
            }
        listitem.setInfo( "Video", infoLabels )

        self._add_favoris_context_menu_extra( item, listitem, False, False )

        url2 = '%s?emissionIdExtra="%s"&Key="%s"' % ( sys.argv[ 0 ], item[ "Url" ], item["Key"] )
        listitems.append( ( url2, listitem, True ) )

        
    def _add_directory_episodesExtra( self, emissionId ):
        OK = False
        listitems = []
        try:
            # get show element instance
            #episodes = scraper.getPageEmission( emissionId )[ "Episodes" ]
            print ("-------------------ATTENTION----------------")
            print (emissionId)
            emissionId = emissionId.replace("%2F", "/").replace("%2f", "/")
            
            print (emissionId)
            episodes = scraper.CALL_HTML_AUTH('https://services.radio-canada.ca/toutv/presentation' + emissionId + '?device=web&version=4', 'GET', None, 'client-key ' + self.clientKey )
            show = json.loads(episodes)
            
            #load toutes les emissions
            toutesEmissions = self.ToutesEmissions()
            
            if scraper.isLoggedIn():
                playStatus = scraper.CALL_HTML_AUTH('https://services.radio-canada.ca/toutv/profiling/playbackstatus' + emissionId + '?device=phone_android&version=4')
                playStatus = json.loads(playStatus)
                mediaPlaybackStatuses = playStatus["MediaPlaybackStatuses"]
            else:
                mediaPlaybackStatuses = None

            if show['EmisodeLineups']:
                for season in reversed(show['EmisodeLineups']):
                    listitem = xbmcgui.ListItem( "[COLOR blue][B]" + season[ "Title" ] + "[/B][/COLOR]")
               
                    totals = len( season )
                    OK = self._add_directory_item(None,listitem, False, totals)
                    for episode in reversed(season['LineupItems']):
                        #print "START PRINT ==="
                        #print episode
                        # set listitem
                        url, listitem = self._get_episode_listitem_extra( show, season, episode, episode['Key'], False, MediaPlaybackStatuses = mediaPlaybackStatuses, ToutesEmissions = toutesEmissions )
                        #listitems.append( ( url, listitem, False ) )
                        
                        if episode["Key"] == self.args.Key:
                            listitem.select(True)
                        
                        OK = self._add_directory_item( url, listitem, False, totals )
            else:
                listitem = xbmcgui.ListItem( "[COLOR blue][B]" + show[ "Title" ] + "[/B][/COLOR]")
                url, listitem = self._get_episode_listitem_extra( show, show, show, show['IdMedia'], False, ToutesEmissions = toutesEmissions )
                OK = self._add_directory_item( url, listitem, False, 1 )
                        
        except:
            print_exc()

        if listitems:
            OK = self._add_directory_items( listitems )
        if not OK:#elif ACTION_INFO:
            xbmc.executebuiltin( "Action(info)" )
            return
        self._set_content( OK, "episodes" )
       
    def _getWatchedState( self, url, listitem, key = None, MediaPlaybackStatuses=None ):
        #print ("----------GET WATCHED----------------")
        #if key == None:
        #        return False
            
        #if scraper.isLoggedIn() == False:
        #    print "not connected - get watched stopped"
        #    return False
        
        try:
            isLoaded = False
            if key is not None and  MediaPlaybackStatuses:
                print ("MediaPlaybackStatuses = MediaPlaybackStatuses = MediaPlaybackStatuses = MediaPlaybackStatuses")
                element = [element for element in MediaPlaybackStatuses if element['Key'] == key]
                if len(element) == 1:
                    isLoaded = True
                    
                    print (element)
                    
                    if element[0]['Completed']:
                        print ("Élément complété")
                        print (key)
                        return True

                    #print element[0]['SeekInSeconds']
                    #print element[0]['SeekInPercent']
                    percent = element[0]['SeekInPercent']
                    if percent == 0:
                        percent = 1
                    totalTime = 100 * int(element[0]['SeekInSeconds']) / percent
                    time = int(element[0]['SeekInSeconds']) - 10
                    if time <= 0:
                        time = int(element[0]['SeekInSeconds'])
                        return False
                    if (int(totalTime) - int(element[0]['SeekInSeconds'])) < 40:
                        return True
                    else:
                        time = int(element[0]['SeekInSeconds'])
                        listitem.setProperty("ResumeTime", str(time))
                        listitem.setProperty("TotalTime","") #hack pour skipper le popup de "resume"
                        return True
 
            return False
        except:
            print_exc()
            return False
                
    def _get_episode_listitem_extra( self, show, season, episode, key, gototvshow=True, genreTitle=None, forceTitle=None, MediaPlaybackStatuses=None, ToutesEmissions = None):
        title = episode[ "Title" ]
        title = title + " - " + episode["Description"]

        if forceTitle:
            title = forceTitle
        
        #self._progress_update( forceTitle or episode[ "Title" ] )
        
        thumb = episode[ "ImageUrl" ] or ""
        
        #thumb = thumb.replace("c_scale,w_200,h_300","c_scale,w_300,h_200")
        
        #listitem = xbmcgui.ListItem( title, "", "DefaultTVShows.png", thumb )
        listitem = xbmcgui.ListItem( title, "", "DefaultTVShows.png" )

        listitem.setArt( { 'thumb' : self.PimpImage(thumb, 360, 202) } )
    
        if 'BackgroundImageUrl' in show:
            fanart = show[ "BackgroundImageUrl" ] or "https://images.tou.tv/v1/emissions/16x9/" + show["Title"] + ".jpg"
        else:
            fanart = None
        #    fanart = "https://images.tou.tv/v1/emissions/16x9/" + show["ProgramTitle"] + ".jpg"

        #listitem.setProperty( "fanart_image", fanart or "" )
        
        
        #fanart finder
        for i in ToutesEmissions:
            if i['ProgramKey'] == episode['ProgramKey']:
                fanart = i['ImageUrl']
                break
        
        listitem.setProperty( "fanart_image", self.PimpImage(fanart) )
        listitem.setProperty( "thumb", thumb )#used in carrousel mode

        #set property for player set watched
        #strwatched = "%s-%s" % ( str( episode.get( "CategoryId" ) ), episode[ "Id" ] )
        strwatched = "%s" % ( key )
        listitem.setProperty( "strwatched", strwatched )
        listitem.setProperty( "PID", key )

        try:
            if 'LengthInSeconds' in episode["Details"]:
                tempsEnSecondes = episode["Details"]["LengthInSeconds"]
            else:
                tempsEnSecondes = episode["Details"]["Length"]
        except:
            tempsEnSecondes = ""
        
        #genreTitle = genreTitle or G_GENRE or episode[ "GenreTitle" ] or "" # pas bon tout le temps pour episode[ "GenreTitle" ]
        infoLabels = {
            "tvshowtitle": season['Title'],
            "title":       title,
            "genre":       genreTitle,
            "plot":        episode["Details"][ "Description" ] or "",
            "season":      -1,
            "episode":     -1,
            #"year":        int( episode[ "Year" ] or "0" ),
            "Aired":       episode["Details"][ "AirDate" ] or "",
            "Date":       episode["Details"][ "AirDate" ] or "",
            #"mpaa":        episode[ "Rating" ] or "",
            "duration":    tempsEnSecondes,
            #"studio":      episode[ "Copyright" ] or "",
            #"castandrole": scraper.setCastAndRole( episode ) or [],
            #"writer":      episode[ "PeopleWriter" ] or episode[ "PeopleAuthor" ] or "",
            #"director":    episode[ "PeopleDirector" ] or "",
            }
        # set overlay watched
        
        #print ("1")
        #print (key)
        #print ("2")
        #print (episode[ "Key" ])
        
        watched = self._getWatchedState(episode[ "Url" ] or episode["MediaUrl"], listitem, episode[ "Key" ], MediaPlaybackStatuses = MediaPlaybackStatuses)

        #watched = str( episode[ "Key" ] ) in self.watched['watched'].get( 'currentTime' )
        #overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_ZIP )[ watched ]
        infoLabels.update( { "playCount": ( 0, 1 )[ watched ] } )

        listitem.setInfo( "Video", infoLabels )
        
        if str(listitem.getProperty("ResumeTime")) != "0.000000":
            watched = not watched
        
        self._add_episode_context_menu_extra( episode['Url'] or episode["MediaUrl"], key, episode, listitem, gototvshow, watched )
        
        url = '%s?PIDEXTRA="%s"&KEY="%s"&starttime="%s"' % ( sys.argv[ 0 ], episode[ "Url" ] or episode["MediaUrl"],  key, listitem.getProperty("ResumeTime") )

        return url, listitem

    def _add_favoris_context_menu_extra( self, episode, listitem, gototvshow=True, watched=False ):
        c_items = []
        try:

            c_items += [ ( "Afficher les détails", "Action(Info)" ) ]

            key = ""
            try:
                key = episode[ "BookmarkKey" ]
            except:
                key = episode[ "Key" ]
            
            uri = "%s?addtofavourites='%s'" % ( sys.argv[ 0 ], key )

            if self.args.url == "bookmark":
                c_items += [ ( "Retirer de mes favoris", "RunPlugin(%s)" % uri.replace( "addto", "removefrom" ) ) ]
            else:
                c_items += [ ( "Ajouter à mes favoris TOU.TV", "RunPlugin(%s)" % uri ) ]
            ##
            if not watched:
                i_label, action = "Marquer comme DÉJÀ écouté", "setwatched"
            else:
                i_label, action = "Marquer comme NON écouté", "setunwatched"

            self._add_context_menu_items( c_items, listitem  )
        except:
            print_exc()

    def _add_episode_context_menu_extra( self, url, id, episode, listitem, gototvshow=True, watched=False ):
        c_items = []
        try:
            self._getWatchedState(url, listitem)
            uri = "%s?PIDEXTRA='%s'&KEY='%s'&starttime='%s'" % ( sys.argv[ 0 ], url,  id, listitem.getProperty("ResumeTime") )

            c_items += [ ( "Lire l'épisode", "RunPlugin(%s)" % uri ) ]

            c_items += [ ( "Afficher les détails", "Action(Info)" ) ]

            uri = "%s?addtofavourites='%s'" % ( sys.argv[ 0 ], episode[ "BookmarkKey" ] )

            if self.args.url == "bookmark":
                c_items += [ ( "Retirer de mes favoris", "RunPlugin(%s)" % uri.replace( "addto", "removefrom" ) ) ]
            else:
                c_items += [ ( "Ajouter à mes favoris TOU.TV", "RunPlugin(%s)" % uri ) ]
            ##
            if not watched:
                i_label, action = "Marquer comme DÉJÀ écouté", "setwatched"
            else:
                i_label, action = "Marquer comme NON écouté", "setunwatched"

            uri = "%s?%s='%s'&IdMedia='%s'" % ( sys.argv[ 0 ], action, url, id )
            c_items += [ (  i_label , "RunPlugin(%s)" % uri ) ]

            self._add_context_menu_items( c_items, listitem )
        except:
            print_exc()

    def _add_context_menu_items( self, c_items, listitem, replaceItems2=True ):

        c_items += [ ( "Aller à l'écran principale", "Container.Update(%s,replace)" % ( sys.argv[ 0 ], ) ) ]
        c_items += [ ("Paramètres de TOU.TV", "Addon.OpenSettings(plugin.infologique.tou.tv)" ) ]

        listitem.addContextMenuItems( c_items, replaceItems=replaceItems2 )

if ( __name__ == "__main__" ):
    Main()

getFolders()
