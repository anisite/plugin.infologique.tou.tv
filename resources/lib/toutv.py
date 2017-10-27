# -*- coding: utf-8 -*-
#import ptvsd
#ptvsd.enable_attach(secret = 'mysecret')
#ptvsd.wait_for_attach

#Modules general
import os
import re
import sys
import urllib
import datetime
import time
import calendar

try:
    import json
except ImportError:
    import simplejson as json

from urllib import quote_plus, unquote_plus
from traceback import print_exc

#modules XBMC
import xbmc
import xbmcgui
from xbmcaddon import Addon
import scraper

MYNAME            = "plugin.infologique.tou.tv" 
ADDON             = Addon( MYNAME )
ADDON_NAME        = ADDON.getAddonInfo( "name" )
ADDON_CACHE       = xbmc.translatePath( ADDON.getAddonInfo( "profile" ) )
#CACHE_EXPIRE_TIME = float( ADDON.getSetting( "expiretime" ).replace( "0", ".5" ).replace( "25", "0" ) )
#SCRIPT_REFRESH    = os.path.join( ADDON.getAddonInfo( 'path' ), "resources", "lib", "refresh.py" )
LOGIN             = scraper.CheckLogged()
#LangXBMC          = xbmc.getLocalizedString

STRING_FOR_ALL = "[B]CONTENU accessible à TOUS[/B] - Cette émission peut être regardée partout dans le monde."

#FAVOURITES_XML = os.path.join( ADDON_CACHE, "favourites.xml" )

G_GENRE     = unicode( xbmc.getInfoLabel( "ListItem.Genre" ), "utf-8" )
#ACTION_INFO = not bool( xbmc.getInfoLabel( "ListItem.Episode" ) )
import xbmcgui

WINDOW_PROGRESS = None
CONTROLS_PROGRESS = {}

def getDialogProgress():
    '''global WINDOW_PROGRESS, CONTROLS_PROGRESS
    try:
        # get window
        WINDOW_PROGRESS = xbmcgui.Window( 10101 )
        # give window time to initialize
        xbmc.sleep( 100 )
        # get our controls http://wiki.xbmc.org/index.php?title=List_of_Built_In_Controls#DialogProgress.xml
        #CONTROLS_PROGRESS[ "heading" ] = WINDOW_PROGRESS.getControl( 1 )
        #CONTROLS_PROGRESS[ "line1" ]   = WINDOW_PROGRESS.getControl( 2 )
        CONTROLS_PROGRESS[ "line2" ]   = WINDOW_PROGRESS.getControl( 3 )
        #CONTROLS_PROGRESS[ "line3" ]   = WINDOW_PROGRESS.getControl( 4 )
        #CONTROLS_PROGRESS[ "bar" ]     = WINDOW_PROGRESS.getControl( 20 )
    except TypeError:
        pass #Non-Existent Control
    except:
        print_exc()'''


def progressUpdate( **kwargs ):
    OK = False
    #if kwargs.get( "heading" ) and CONTROLS_PROGRESS.get( "heading" ):
    #    try:
    #        CONTROLS_PROGRESS[ "heading" ].setLabel( kwargs[ "heading" ] )
    #        OK = True
    #    except: print_exc()

    #if kwargs.get( "line1" ) and CONTROLS_PROGRESS.get( "line1" ):
    #    try:
    #        CONTROLS_PROGRESS[ "line1" ].setLabel( kwargs[ "line1" ] )
    #        OK = True
    #    except: print_exc()

    if kwargs.get( "line2" ) and CONTROLS_PROGRESS.get( "line2" ):
        try:
            CONTROLS_PROGRESS[ "line2" ].setLabel( kwargs[ "line2" ] )
            OK = True
        except: print_exc()

    #if kwargs.get( "line3" ) and CONTROLS_PROGRESS.get( "line3" ):
    #    try:
    #        CONTROLS_PROGRESS[ "line3" ].setLabel( kwargs[ "line3" ] )
    #        OK = True
    #    except: print_exc()

    #if kwargs.get( "percent" ) and CONTROLS_PROGRESS.get( "bar" ):
    #    try:
    #        CONTROLS_PROGRESS[ "bar" ].setPercent( int( kwargs[ "percent" ] ) )
    #        OK = True
    #    except: print_exc()

    if ( not OK ):
        getDialogProgress()

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

watched_pending_db = ""
watched_db = ""


def getFolders():
    global watched_db, watched_pending_db
    watched_pending_db = os.path.join( ADDON_CACHE, "watched_pending_" + str(ADDON.getSetting( "username" )) + ".db" )
    watched_db = os.path.join( ADDON_CACHE, "watched_" + str(ADDON.getSetting( "username" )) + ".db" )

if not ADDON.getSetting( "setupOK" ):
    ADDON.openSettings()
    ADDON.setSetting( "setupOK", "True" )

getFolders()
LOGIN = scraper.CheckLogged()

def getPendingWatchFile():
    global LOGIN, watched_db, watched_pending_db

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
    global LOGIN, watched_db, watched_pending_db
    
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
    global LOGIN, watched_db, watched_pending_db
    
    watched = getWatchedFile()
    
    if LOGIN[0]:
        
        pending = getPendingWatchFile()
     
        try:

            if new:
                url = new.keys()[0]
                watched['watched'][url] = new[url]
                pending[url] = new[url]

            post_data = {'loginEmail': Addon( "plugin.infologique.tou.tv" ).getSetting( "username" ), "watched": pending, "lastUpdate": watched['updateTime'] }
            response = scraper.POST_HTML("http://tv.infologique.net/TouTv/watched/", post_data)
            
            toUpdate = json.loads(response)
            
            for key in toUpdate.keys():
                watched['watched'][key] = toUpdate[key]
            
        except:
            print_exc()
            f = open( watched_pending_db, "w" )
            f.write( json.dumps(pending) )
            f.close()
        else:
            f = open( watched_pending_db, "w" )
            f.write( "{}" )
            f.close()
            watched['updateTime'] = getGMTunixtimestamp() #On change la date de mise a jour
        finally:
            if new:
                url = new.keys()[0]
                try:
                    del watched['watched'][url]['data']
                except KeyError:
                    pass
            file( watched_db, "w" ).write( json.dumps(watched) )
            
        if refresh:
            xbmc.executebuiltin( 'Container.Refresh' )
    
    return watched

class Info:
    def __init__( self, *args, **kwargs ):
        # update dict with our formatted argv
        #print sys.argv
        try: exec "self.__dict__.update(%s)" % ( sys.argv[ 2 ][ 1: ].replace( "&", ", " ).replace("%22",'"'), )
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

if  sys.argv[ 2 ] == "?url=%22carrousel%22":
    #print "guiview"
    from GuiView import GuiView as viewtype
else:
    #print "PluginView"
    from PluginView import PluginView as viewtype

class Main( viewtype ):
    global LOGIN
    
    def __init__( self ):
        viewtype.__init__( self )
        
        self.args = Info()
        self.watched = goSync()

        if self.args.isempty():
            self._add_directory_root_extra()

        #elif self.args.GetCarrousel:
        #     self._add_directory_carrousel( self.args.GetCarrousel )

        elif self.args.PIDEXTRA:
            #print "PID EXTRA"
            start_player = True
            #startoffset  = None
            #if self.args.ChapterStartTimes:
            #    try:
            #        chapters = [ "00:00:00" ] + self.args.ChapterStartTimes.split( "," )
            #        selected = xbmcgui.Dialog().select( "Chapters Start Times",
            #            [ "%s %i (%s)" % ( LangXBMC( 21396 ), i+1, c )  for i, c in enumerate( chapters ) ] )
            #        if selected != -1:
            #            h, m, s = chapters[ selected ].split( ":" )
            #            startoffset = str( eval( "(%s*60*60)+(%s*60)+%s" % ( h, m, s ) ) )
            #        else:
            #            start_player = False
            #    except:
            #        print_exc()
            if start_player:
                import TouTvPlayer as player
                #print "CALL player : player.playVideoExtra"
                #print self.args.KEY
                #print "POPUP ????????????????????????????????????????????"

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
                
                #print "FIN."
                #watched['watched']
                xbmc.executebuiltin( 'Container.Refresh' )

        elif self.args.PID:
            start_player = True
            startoffset  = None
            #if self.args.ChapterStartTimes:
            #    #try:
            #    #    chapters = [ "00:00:00" ] + self.args.ChapterStartTimes.split( "," )
            #    #    selected = xbmcgui.Dialog().select( "Chapters Start Times",
            #    #        [ "%s %i (%s)" % ( LangXBMC( 21396 ), i+1, c )  for i, c in enumerate( chapters ) ] )
            #    #    if selected != -1:
            #    #        h, m, s = chapters[ selected ].split( ":" )
            #    #        startoffset = str( eval( "(%s*60*60)+(%s*60)+%s" % ( h, m, s ) ) )
            #    #    else:
            #    #        start_player = False
            #    #except:
            #    #    print_exc()
            if start_player:
                import TouTvPlayer as player
                try: player.playVideo( self.args.PID, startoffset=startoffset )
                except: print_exc()

        elif self.args.emissionIdExtra:
            self._add_directory_episodesExtra( self.args.emissionIdExtra )
                
        elif self.args.emissionId:
             self._add_directory_episodes( self.args.emissionId )

        #elif self.args.GetPageGenre:
        #     self._add_directory_genre( self.args.GetPageGenre )

        elif self.args.webbrowser:
            import webbrowser
            webbrowser.open( unquote_plus( self.args.webbrowser ) )

        elif self.args.addtofavourites or self.args.removefromfavourites:
            #add to my favourites
            #print "----111111------------------------------------------------------------------"
            favourite = self.args.addtofavourites or self.args.removefromfavourites
            response = scraper.POST_HTML("http://ici.tou.tv/profiling/bookmark/" + favourite, None, AUTH=True, METHOD= ("POST", "DELETE")[bool(self.args.removefromfavourites)])
            
            if bool(self.args.removefromfavourites):
                xbmc.executebuiltin( 'Container.Refresh' )
            
            #print response
            
            #print favourite
            #if os.path.exists( FAVOURITES_XML ):
            #    favourites = open( FAVOURITES_XML ).read()
            #else:
            #    favourites = '<favourites>\n</favourites>\n'
            #if self.args.removefromfavourites or favourite not in favourites:
            #    if self.args.removefromfavourites:
            #        favourites = favourites.replace( '  %s\n' % favourite, '' )
            #        refresh = True
            #    else:
            #        favourites = favourites.replace( '</favourites>', '  %s\n</favourites>' % favourite )
            #        refresh = False
            #    file( FAVOURITES_XML, "w" ).write( favourites )
            #    if refresh:
            #        if favourites == '<favourites>\n</favourites>\n':
            #            try: os.remove( FAVOURITES_XML )
            #            except: pass
            #            xbmc.executebuiltin( 'Action(ParentDir)' )
            #            xbmc.sleep( 1000 )
            #        xbmc.executebuiltin( 'Container.Refresh' )

        elif self.args.setwatched or self.args.setunwatched:
            key = self.args.setwatched or self.args.setunwatched
            
            #print "PID"
            #print self.args.IdMedia
            
            new = {}
            
            time=0
            totalTime=0
            
            if bool( self.args.setunwatched ): #setUnwatched
                time=0
                totalTime=0
            else:
                time=100000
                totalTime=100000
                
            new[key] = {
                        "currentTime" : time,
                        "totalTime" : totalTime,
                        "timestamp" : getGMTunixtimestamp(),
                        "key" : self.args.IdMedia
                        }
            goSync(new,True)
            #setWatched( key, remove=bool( self.args.setunwatched ) )

        elif self.args.url == "bookmark":
            self._add_api_favourites()
            
        elif self.args.url == "enecoute":
            self._add_api_enecoute()
            
        elif self.args.url != "":
            self._add_api_url()
            
        elif self.args.category == "extra":
            if  str(ADDON.getSetting( "username" )) == "":
                dialog = xbmcgui.Dialog()
                dialog.ok("Section Extra","Vous devez fournir vos infos d'authentification.")
            else:
                self._add_directory_extra()
            #dialog = xbmcgui.Dialog()
            #dialog.yesno("Bienvenue!","Voulez-vous vous connecter au serveur de Tou.Tv?")
            #dialog = xbmcgui.Dialog()
            
            #dialog.input('Enter secret code', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
            
            
        #elif self.args.category == "genres":
        #    self._add_directory_genres()

        #elif self.args.category in [ "outdated", "repertoire" ]:
        #    self._add_directory_emissions( self.args.category == "outdated" )

        elif self.args.category == "collection":
            self._add_directory_collection()

        elif self.args.category == "recherche":
            self._add_directory_search()

        #elif self.args.category == "countries":
        #    self._add_directory_countries()

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

    #def _add_directory_root( self ):
    #    OK = False
    #    listitems = []
    #    try:
    #        uri = sys.argv[ 0 ]
    #        items = [
    #            ( ( uri, 'genres'      ), ( LangXBMC( 135 ),          '', 'DefaultAddonRepository.png'       ) ),
    #            ( ( uri, 'repertoire'  ), ( LangXBMC( 369 ),          '', 'DefaultAddonSubtitles.png'        ) ),
    #            ( ( uri, 'countries'   ), ( LangXBMC( 20451 ),        '', 'DefaultAddonVisualization.png'    ) ),
    #            ( ( uri, 'collection'  ), ( 'Collections',            '', 'DefaultMusicAlbums.png'           ) ),
    #            ( ( uri, 'adecouvrir'  ), ( 'À Découvrir',            '', 'DefaultMusicArtists.png'          ) ),
    #            ( ( uri, 'favoris'     ), ( 'Les Favoris Sur TouTV',  '', 'DefaultAddonScreensaver.png'      ) ),
    #            ( ( uri, 'carrousel'   ), ( 'Carrousel TouTV',        '', 'DefaultAddonVisualization.png'    ) ),
    #            ( ( uri, 'outdated'    ), ( 'A à Z + Outdated',       '', 'DefaultMusicYears.png'            ) ),
    #            ( ( uri, 'plusrecents' ), ( LangXBMC( 20387 ),        '', 'DefaultRecentlyAddedEpisodes.png' ) ),
    #            ( ( uri, 'recherche'   ), ( LangXBMC( 137 ),          '', 'DefaultAddonWebSkin.png'          ) ),
    #            ]
    #        if os.path.exists( FAVOURITES_XML ):
    #            fav = ( uri, 'myfavourites' ), ( 'Mes Favoris',       '', 'DefaultAddonScreensaver.png'      )
    #            items.append( fav )
    #        fanart = ADDON.getAddonInfo( "fanart" )
    #        for uri, item in items:
    #            listitem = xbmcgui.ListItem( *item )
    #            listitem.setProperty( "fanart_image", fanart )
    #            self._add_context_menu_items( [], listitem )
    #            url = '%s?category="%s"' % uri
    #            listitems.append( ( url, listitem, True ) )
    #    except:
    #        print_exc()
    #
    #    if listitems:
    #        OK = self._add_directory_items( listitems )
    #    # fake content movies to show container.foldername
    #    self._set_content( OK, "movies", False )

    def _add_directory_root_extra( self ):
        global LOGIN
        
        OK = False
        listitems = []
        try:
            uri = sys.argv[ 0 ]

            sections = scraper.GET_HTML('https://ici.tou.tv/presentation/section/')
            sections = json.loads(sections)
            #login = scraper.CheckLogged()
            items = []
                        
            items.append(( 'Addon.OpenSettings(plugin.infologique.tou.tv)' , ( '[COLOR blue][B]' + LOGIN[1] + '[/B][/COLOR]',       '', 'DefaultAddonScreensaver.png'      )))
            if LOGIN[0]:
                items.append((( uri, 'bookmark' ), ( 'Mes Favoris [COLOR red]<3[/COLOR]',       'Mes Favoris', 'DefaultAddonScreensaver.png'      )))
                items.append((( uri, 'enecoute' ), ( u'En cours d\'écoute',       'En cours d\'écoute', 'DefaultAddonScreensaver.png'      )))
            #items.append((( uri, 'bookmark' ), ( 'Infoman - Épisode 11',       'Mes Favoris', 'DefaultAddonScreensaver.png'      )))
            items.append(('Addon.OpenSettings(plugin.infologique.tou.tv)', ( u'[COLOR blue][B]Menu[/B][/COLOR]',       'Mes Favoris', 'DefaultAddonScreensaver.png'      )))
            #items.append(( ( uri, 'carrousel'   ), ( 'Carrousel TouTV',        '', 'DefaultAddonVisualization.png'    ) ))
            for section in sections:
                print section
                items.append((( uri, section['Name'] ), ( section['Title'],       section['Title'], 'DefaultAddonScreensaver.png'      )))
            
            #items = [
            #    ( ( uri, 'extra'       ), ( 'Extra',                  '', 'DefaultAddonRepository.png'       ) ),
            #    ( ( uri, 'genres'      ), ( LangXBMC( 135 ),          '', 'DefaultAddonRepository.png'       ) ),
            #    ( ( uri, 'repertoire'  ), ( LangXBMC( 369 ),          '', 'DefaultAddonSubtitles.png'        ) ),
            #    ( ( uri, 'countries'   ), ( LangXBMC( 20451 ),        '', 'DefaultAddonVisualization.png'    ) ),
            #    ( ( uri, 'collection'  ), ( 'Collections',            '', 'DefaultMusicAlbums.png'           ) ),
            #    ( ( uri, 'adecouvrir'  ), ( 'À Découvrir',            '', 'DefaultMusicArtists.png'          ) ),
            #    ( ( uri, 'favoris'     ), ( 'Les Favoris Sur TouTV',  '', 'DefaultAddonScreensaver.png'      ) ),
            #    ( ( uri, 'carrousel'   ), ( 'Carrousel TouTV',        '', 'DefaultAddonVisualization.png'    ) ),
            #    ( ( uri, 'outdated'    ), ( 'A à Z + Outdated',       '', 'DefaultMusicYears.png'            ) ),
            #    ( ( uri, 'plusrecents' ), ( LangXBMC( 20387 ),        '', 'DefaultRecentlyAddedEpisodes.png' ) ),
            #    ( ( uri, 'recherche'   ), ( LangXBMC( 137 ),          '', 'DefaultAddonWebSkin.png'          ) ),
            #    ]
            #if os.path.exists( FAVOURITES_XML ):
            #    fav = ( uri, 'bookmark' ), ( 'Mes Favoris',       '', 'DefaultAddonScreensaver.png'      )
            #    items.append( fav )
            fanart = ADDON.getAddonInfo( "fanart" )
            for uri, item in items:
                listitem = xbmcgui.ListItem( *item )
                listitem.setProperty( "fanart_image", fanart )
                self._add_context_menu_items( [], listitem )
                url=None
                #print  uri 
                if isinstance(uri,tuple):
                    #url = '%s?category="%s"' % uri
                    FOLDER = " / " + item[1]
                    url = '%s?url="%s"&folder="%s"' % (uri[0], uri[1], FOLDER)
                else:
                    print "uri" + uri
                    url = uri
                #print "url: " + url
                listitems.append( ( url, listitem, True ) )
        except:
            print_exc()

        if listitems:
            OK = self._add_directory_items( listitems )
        # fake content movies to show container.foldername
        self._set_content( OK, "movies", False )

    #def _add_directory_accueil( self, section ):
    #    OK = False
    #    listitems = []
    #    try:
    #        # get toutv home page
    #        accueil = scraper.getPageAccueil()
    #        # get section
    #        results = accueil[ section ]
    #        if section == "EpisodesFavoris": episodes = results
    #        else: episodes = results[ "Episodes" ]
    #
    #        for episode in episodes:
    #            # set listitem
    #            url, listitem = self._get_episode_listitem( episode )
    #            listitems.append( ( url, listitem, False ) )
    #    except:
    #        print_exc()
    #
    #    if listitems:
    #        OK = self._add_directory_items( listitems )
    #    self._set_content( OK, "episodes" )

    #def _add_directory_countries( self ):
    #    OK = False
    #    listitems = []
    #    try:
    #        countries = scraper.toutvapi.GetPays()
    #        for country in countries:
    #            if not country: continue
    #            listitem = xbmcgui.ListItem( country )
    #            self._add_context_menu_items( [], listitem )
    #
    #            url = '%s?category="repertoire"&filter="byCountry"&country="%s"' % ( sys.argv[ 0 ], country )
    #            listitems.append( ( url, listitem, True ) )
    #    except:
    #        print_exc()
    #
    #    if listitems:
    #        OK = self._add_directory_items( listitems )
    #    # fake content movies to show container.foldername
    #    self._set_content( OK, "movies", False )

    def AppendFolder(self, FOLDER, liste):
        FOLDER = urllib.unquote(FOLDER)
        listitem = xbmcgui.ListItem( "[B][COLOR white]* " + FOLDER + "[/COLOR][/B]")
        liste.append((None, listitem, True))
        self._add_context_menu_items( [], listitem )

    def _add_api_favoris( self, listitems, item ) :
        if (item[ "Title" ] is not None) and (item["Template"] != 'letter') and (item["Template"] != 'espace-partenaire') and (item['BookmarkKey']):
            color = ""
            if not item["IsFree"]:
                Title = "[COLOR gold][Extra][/COLOR] "
            else:
                Title = ""
                
            if not item["IsActive"]:
                #color = "[COLOR red] "
                Title += " [COLOR red] " + item['DepartureDescription'] + "[/COLOR]"
        
            #if item["Template"] == "multiple-content":
            #    Title = Title + item[ "Title" ] + " (*)"
            #else:
            #    Title = Title + item[ "Title" ]
            Title =  color + item[ "Title" ] + " " + Title

            if not item["Description"] is None:
                Title = Title + " - " + item["Description"]
                
            listitem = xbmcgui.ListItem( Title)
            #print item[ "ImageUrl" ]
            listitem.setProperty( "fanart_image", item[ "ImageUrl" ] or "" )
            infoLabels = {
                "label" : Title,
                "plot":  item[ "Description" ] or "",
                }
            listitem.setInfo( "Video", infoLabels )
            
            #if item['Template'] == "multiple-content":
            #self._add_context_menu_items( [], listitem )
            self._add_favoris_context_menu_extra( item, listitem, False, False )
            #url2 = '%s?emissionIdExtra="%s"' % ( sys.argv[ 0 ], item[ "Url" ] )
            url2 = '%s?emissionIdExtra="%s"&Key="%s"' % ( sys.argv[ 0 ], item[ "Url" ], item["Key"] )
            #else:
            #    url2 = '%s?PIDEXTRA="%s"' % ( sys.argv[ 0 ], item[ "IdMedia" ] )
            #    self._add_episode_context_menu_extra( item, listitem, True, False )

            listitems.append( ( url2, listitem, True ) )
            
    def _add_api_enecoutelist( self, listitems, item, episodeContextMenu=False ) :
        if (item[ "Title" ] is not None) and (item["Template"] != 'letter'):
            color = ""
            if not item["IsFree"]:
                Title = "[COLOR gold][Extra][/COLOR] "
            else:
                Title = ""
                
            if not item["IsActive"]:
                #color = "[COLOR red] "
                Title += " [COLOR red] " + item['DepartureDescription'] + "[/COLOR]"
        
            #if item["Template"] == "multiple-content":
            #    Title = Title + item[ "Title" ] + " (*)"
            #else:
            #    Title = Title + item[ "Title" ]
            Title =  color + item[ "Title" ] + " " + Title

            if not item["Description"] is None:
                Title = Title + " - " + item["Description"]
                
            listitem = xbmcgui.ListItem( Title)
            listitem.setProperty( "fanart_image", item[ "ImageUrl" ] or "" )
            infoLabels = {
                "tvshowtitle" : Title,
                "label" : Title,
                "title" : Title,
                "plot":  item[ "Description" ] or "",
                }

            listitem.setInfo( "Video", infoLabels )
            
            #if item['Template'] == "multiple-content":
            #self._add_context_menu_items( [], listitem )
            if episodeContextMenu:
                self._add_episode_context_menu_extra( item['MediaUrl'], item['IdMedia'], item, listitem, False, False )
            #url2 = '%s?emissionIdExtra="%s"' % ( sys.argv[ 0 ], item[ "Url" ] )
            url2 = '%s?emissionIdExtra="%s"&Key="%s"' % ( sys.argv[ 0 ], item[ "Url" ], item["Key"] )
            #else:
            #    url2 = '%s?PIDEXTRA="%s"' % ( sys.argv[ 0 ], item[ "IdMedia" ] )
            #    self._add_episode_context_menu_extra( item, listitem, True, False )

            listitems.append( ( url2, listitem, True ) )

    def _add_api_enecoute( self ):
        OK = False
        FOLDER = self.args.folder
        
        listitems = []
        self.AppendFolder(FOLDER, listitems)
        try:
            #genres = scraper.getGenres()
            emissions = scraper.GET_HTML('http://tv.infologique.net/TouTv/watched/uncompleted/'+str(ADDON.getSetting( "username" ))+'/')
            emissions = json.loads(emissions)

            for emission in emissions.keys():
                #print emissions[emission]
                if emissions[emission]['data']:
                    self._add_api_enecoutelist(listitems, emissions[emission]['data'], episodeContextMenu=True)

        except:
            print_exc()

        if listitems:
            OK = self._add_directory_items( listitems )

        # fake content movies to show container.foldername
        self._set_content( OK, "movies", False )
    
    def _add_api_favourites( self ):
        OK = False
        FOLDER = self.args.folder
        
        listitems = []
        self.AppendFolder(FOLDER, listitems)
        try:
            #genres = scraper.getGenres()
            emissions = scraper.GET_HTML_AUTH('http://ici.tou.tv/profiling/' + self.args.url + '?smallWidth=188&mediumWidth=1600&largeWidth=1600&includePartnerTeaser=false&v=2&d=phone-android')
            emissions = json.loads(emissions)

            for emission in emissions['LineupItems']:
                self._add_api_favoris(listitems, emission)

        except:
            print_exc()

        if listitems:
            OK = self._add_directory_items( listitems )
        # fake content movies to show container.foldername
        
        self._set_content( OK, "movies", False )
        
    def _add_api_url( self ):
        print "_add_api_url"
        
        OK = False
        FOLDER = self.args.folder
        
        listitems = []
        self.AppendFolder(FOLDER, listitems)
        
        try:
            #genres = scraper.getGenres()
            genres = scraper.GET_HTML('http://ici.tou.tv/presentation/section/' + self.args.url + '?smallWidth=188&mediumWidth=1600&largeWidth=1600&includePartnerTeaser=false&v=2')
            genres = json.loads(genres)
            for Lineup in genres['Lineups']:
                FOLDER = self.args.folder + " / " + Lineup[ "Title" ]
                url = '%s?url="%s"&folder="%s"&lineup="%s"' % ( sys.argv[ 0 ], self.args.url, FOLDER, Lineup[ "Name" ])
                if self.args.lineup == "":
                    listitem = xbmcgui.ListItem( "[B][COLOR blue]" + Lineup[ "Title" ] + "[/COLOR][/B]")
                    self._add_context_menu_items( [], listitem )
                    listitems.append((url, listitem, True))

                else:
                    print self.args.lineup
                    print Lineup["Name"]
                    if Lineup["Name"] == self.args.lineup:
                        for genre in Lineup['LineupItems']:
                            self._add_api_favoris(listitems, genre)
                        
        except:
            print_exc()

        if listitems:
            OK = self._add_directory_items( listitems )
        # fake content movies to show container.foldername
        
        self._set_content( OK, "movies", False )
        
    def _add_directory_extra( self ):
        OK = False
        listitems = []
        try:
            #genres = scraper.getGenres()
            genres = scraper.GET_HTML('http://ici.tou.tv/presentation/section/extra?smallWidth=188&mediumWidth=1600&largeWidth=1600&includePartnerTeaser=false&v=2&d=phone-android')
            genres = json.loads(genres)
            genres = genres['Lineups'][0]['LineupItems']
            for genre in genres:
                if genre[ "Title" ] is not None:
                    listitem = xbmcgui.ListItem( genre[ "Title" ])
                    listitem.setProperty( "fanart_image", genre[ "ImageUrl" ] or "" )
                    infoLabels = {
                        "tagline" : "DefaultAddonSubtitles.png",
                        "plot":  genre[ "Description" ] or "",
                        }
                    listitem.setInfo( "Video", infoLabels )
                    self._add_context_menu_items( [], listitem )
                    

                    url = '%s?emissionIdExtra="%s"' % ( sys.argv[ 0 ], genre[ "Url" ] )
                    listitems.append( ( url, listitem, True ) )
        except:
            print_exc()

        if listitems:
            OK = self._add_directory_items( listitems )
        # fake content movies to show container.foldername
        self._set_content( OK, "movies", False )
        
    #def _add_directory_genres( self ):
    #    OK = False
    #    listitems = []
    #    try:
    #        genres = scraper.getGenres()
    #        for genre in genres:
    #            listitem = xbmcgui.ListItem( genre[ "Title" ] )
    #            listitem.setProperty( "fanart_image", genre[ "ImageBackground" ] or "" )
    #            infoLabels = {
    #                "title": genre[ "Title" ],
    #                "genre": genre[ "Title" ],
    #                "plot":  genre[ "Description" ] or "",
    #                }
    #            listitem.setInfo( "Video", infoLabels )
    #            self._add_context_menu_items( [], listitem )
    #
    #            url = '%s?GetPageGenre="%s"' % ( sys.argv[ 0 ], genre[ "CategoryURL" ] )
    #            listitems.append( ( url, listitem, True ) )
    #    except:
    #        print_exc()
    #
    #    if listitems:
    #        OK = self._add_directory_items( listitems )
    #    # fake content movies to show container.foldername
    #    self._set_content( OK, "movies", False )

    #def _add_directory_genre( self, genre ):
    #    OK = False
    #    listitems = []
    #    try:
    #        # get show element instance
    #        page = scraper.getPageGenre( genre )
    #        recents = page[ "SelectionPlusRecents" ][ "Episodes" ]
    #
    #        # ADD GENRE A TO Z
    #        genreTitle = page[ "Genre" ][ "Title" ]
    #        fanart = page[ "Genre" ][ "ImageBackground" ] or ""
    #        sep  = "[CR]%s " % unichr( 8226 )# bullet
    #        plot = "%s %s" % ( unichr( 8226 ), sep.join( set( [ e[ "Show" ] for e in page[ "SelectionCarrousel" ][ "Episodes" ] ] ) ) )
    #
    #        A_TO_Z = genreTitle.encode( "utf-8" ) + " de A à Z"
    #        listitem = xbmcgui.ListItem( A_TO_Z, '', 'DefaultAddonSubtitles.png' )
    #        listitem.setProperty( "fanart_image", fanart )
    #        listitem.setInfo( "Video", { "title": A_TO_Z, "genre": genreTitle, "plot": plot } )
    #        self._add_context_menu_items( [], listitem )
    #        #
    #        url = '%s?category="repertoire"&filter="byGenre"&genre="%s"' % ( sys.argv[ 0 ], genreTitle )
    #        listitems.append( ( url, listitem, True ) )
    #
    #        #ADD CARROUSEL MODE
    #        listitem = xbmcgui.ListItem(  "Carrousel " + genreTitle, '', 'DefaultAddonVisualization.png' )
    #        listitem.setProperty( "fanart_image", fanart )
    #        listitem.setInfo( "Video", { "title": genreTitle + "   Carrousel", "genre": genreTitle, "plot": plot } )
    #        self._add_context_menu_items( [], listitem )
    #        #
    #        url = '%s?genre="%s"&GetCarrousel="%s"' % ( sys.argv[ 0 ], genreTitle, page[ "SelectionCarrousel" ][ "Title" ] )
    #        listitems.append( ( url, listitem, True ) )
    #
    #        #ADD RECENTS FOR THIS GENRE
    #        for recent in recents:
    #            url, listitem = self._get_episode_listitem( recent, genreTitle=genreTitle )
    #            listitems.append( ( url, listitem, False ) )
    #    except:
    #        print_exc()
    #
    #    if listitems:
    #        OK = self._add_directory_items( listitems )
    #    self._set_content( OK, "episodes" )

    #def _add_directory_carrousel( self, carrousel ):
    #    OK = False
    #    listitems = []
    #    try:
    #        carrousel = scraper.getCarrousel( carrousel )
    #        for emission in carrousel:
    #            title = emission[ "title" ]
    #            thumb = emission[ "imgNR" ] or ""
    #            listitem = xbmcgui.ListItem( title, "", "DefaultTVShows.png", thumb )
    #            listitem.setProperty( "fanart_image", emission[ "imgXR" ] or "" )
    #            listitem.setProperty( "thumb", thumb )#used in carrousel mode
    #            listitem.setInfo( "Video", { "tvshowtitle": title,"title": title, "genre": self.args.genre, "plot": emission[ "subTitle" ] } )
    #            self._add_emission_context_menu( emission, listitem )
    #
    #            url = '%s?emissionId="%s"' % ( sys.argv[ 0 ], emission[ "EmissionId" ] )
    #            listitems.append( ( url, listitem, True ) )
    #    except:
    #        print_exc()
    #
    #    if listitems:
    #        OK = self._add_directory_items( listitems )
    #    self._set_content( OK, "tvshows" )

    #def _add_directory_emissions( self, plusoutdated=False ):
    #    OK = False
    #    listitems = []
    #    try:
    #        full_emissions = scraper.getEmissionsWithFullDescription()
    #        emissions = full_emissions[ "Emissions" ]
    #
    #        if plusoutdated:
    #            outdated = full_emissions[ "Outdated" ]
    #            for out in outdated:
    #                out[ "premiered" ] = "(Outdated)"
    #            emissions += outdated
    #
    #        getDialogProgress()
    #        totals = len( emissions )
    #        for emission in emissions:
    #            genre = emission[ "Genre" ]
    #            try: genre = genre[ "Title" ]
    #            except: pass
    #            filter = self.args.filter
    #            if self.args.genre and filter == "byGenre" and self.args.genre != genre.encode( "utf-8" ):
    #                totals -= 1
    #                continue
    #            country = emission.get( "Country" ) or emission.get( "Pays" ) or ""
    #            if self.args.country and filter == "byCountry" and self.args.country != country.encode( "utf-8" ):
    #                totals -= 1
    #                continue
    #
    #            #set emission base infos
    #            title = emission.get( "Titre" ) or emission[ "Title" ]
    #            #fix title for context menu
    #            emission[ "Title" ] = title
    #            self._progress_update( title )
    #
    #            emissionId = emission[ "Id" ]
    #            
    #            watched = len( self.watched.get( str( emissionId ) ) or [] )
    #            NombreEpisodes = int( emission.get( "NombreEpisodes" ) or "1" )
    #            unwatched = NombreEpisodes - watched
    #            outdated = emission.get( "premiered" ) == "(Outdated)"
    #            if outdated:
    #                unwatched = 0
    #                NombreEpisodes = 0
    #
    #            year = ( emission.get( "AnneeProduction" ) or emission[ "Year" ] or "0" )
    #            GeoTargeting = emission.get( "IsGeolocalise" ) or emission[ "GeoTargeting" ]
    #
    #            infoLabels = {
    #                "tvshowtitle": title,
    #                "title":       title,
    #                "genre":       genre,
    #                "year":        int( year.split()[ 0 ] ),
    #                "tagline":     ( STRING_FOR_ALL, "" )[ bool( GeoTargeting ) ],
    #                "duration":    emission.get( "CategorieDuree" ) or "",
    #                "episode":     NombreEpisodes,
    #                "season":      -1,
    #                "plot":        emission.get( "Description" ) or "",
    #                "premiered":   emission.get( "premiered" ) or "",
    #                }
    #            thumb = emission[ "ImagePromoNormalK" ] or ""
    #            
    #            try: fanart = emission[ "ImagePromoLargeI" ] or emission[ "ImageBackground" ] or emission[ "Genre" ][ "ImageBackground" ] or ""
    #            except: fanart = "" #all request keys error
    #
    #            if not infoLabels[ "premiered" ]:
    #                infoLabels[ "premiered" ] = scraper.getPremiered( emissionId )
    #
    #            infoLabels[ "plot" ] = infoLabels[ "plot" ].encode( "utf-8" )
    #            if not GeoTargeting:
    #                try:
    #                    if infoLabels[ "plot" ]: infoLabels[ "plot" ] += "[CR][CR]"
    #                    infoLabels[ "plot" ] +=  STRING_FOR_ALL
    #                except:
    #                    pass
    #
    #            plot_plus = emission.get( "DescriptionOffline" ) or emission.get( "DescriptionUnavailable" )
    #            if plot_plus: infoLabels[ "plot" ] = plot_plus.encode( "utf-8" ) + "[CR][CR]" + infoLabels[ "plot" ]
    #
    #            # set listitem
    #            listitem = xbmcgui.ListItem( title, "", "DefaultTVShows.png", thumb )
    #            listitem.setProperty( "fanart_image", fanart )
    #
    #            listitem.setProperty( "WatchedEpisodes", str( watched ) )
    #            listitem.setProperty( "UnWatchedEpisodes", str( unwatched ) )
    #
    #            playCount = ( 0, 1 )[ not unwatched and not outdated ]
    #            overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_WATCHED )[ playCount ]
    #            infoLabels.update( { "playCount": playCount, "overlay": overlay } )
    #
    #            listitem.setInfo( "Video", infoLabels )
    #            self._add_emission_context_menu( emission, listitem, bool( playCount ), outdated )
    #
    #            url = '%s?emissionId="%s"' % ( sys.argv[ 0 ], emissionId )
    #            #listitems.append( ( url, listitem, bool( NombreEpisodes ) ) )
    #            OK = self._add_directory_item( url, listitem, bool( NombreEpisodes ), totals )
    #    except:
    #        print_exc()
    #
    #    #if listitems:
    #    #    OK = self._add_directory_items( listitems )
    #    OK = OK or bool( self.args.country )
    #    self._set_content( OK, "tvshows" )

    def _add_directory_episodesExtra( self, emissionId ):
        OK = False
        listitems = []
        try:
            # get show element instance
            #episodes = scraper.getPageEmission( emissionId )[ "Episodes" ]
            print "-------------------ATTENTION----------------"
            print emissionId
            emissionId = emissionId.replace("%2F", "/").replace("%2f", "/")
            
            print emissionId
            episodes = scraper.GET_HTML('http://ici.tou.tv/presentation' + emissionId + '?excludeLineups=False&smallWidth=660&mediumWidth=660&largeWidth=660&v=2&d=phone-android')
            show = json.loads(episodes)
            #episodes = show['SeasonLineups'][0]['LineupItems']
            
            if show['SeasonLineups']:
                for season in reversed(show['SeasonLineups']):
                    listitem = xbmcgui.ListItem( "[COLOR blue][B]" + season[ "Title" ] + "[/B][/COLOR]")
                    getDialogProgress()
                    totals = len( season )
                    OK = self._add_directory_item(None,listitem, False, totals)
                    for episode in reversed(season['LineupItems']):
                        #print "START PRINT ==="
                        #print episode
                        # set listitem
                        url, listitem = self._get_episode_listitem_extra( show, season, episode, episode['Key'], False )
                        #listitems.append( ( url, listitem, False ) )
                        
                        if episode["Key"] == self.args.Key:
                            listitem.select(True)
                        
                        OK = self._add_directory_item( url, listitem, False, totals )
            else:
                listitem = xbmcgui.ListItem( "[COLOR blue][B]" + show[ "Title" ] + "[/B][/COLOR]")
                url, listitem = self._get_episode_listitem_extra( show, show, show, show['IdMedia'], False )
                OK = self._add_directory_item( url, listitem, False, 1 )
                        
        except:
            print_exc()

        if listitems:
            OK = self._add_directory_items( listitems )
        if not OK:#elif ACTION_INFO:
            xbmc.executebuiltin( "Action(info)" )
            return
        self._set_content( OK, "episodes" )
        
    #def _add_directory_episodes( self, emissionId ):
    #    OK = False
    #    listitems = []
    #    try:
    #        # get show element instance
    #        episodes = scraper.getPageEmission( emissionId )[ "Episodes" ]
    #        getDialogProgress()
    #        totals = len( episodes )
    #        for episode in episodes:
    #            # set listitem
    #            url, listitem = self._get_episode_listitem( episode, False )
    #            #listitems.append( ( url, listitem, False ) )
    #            OK = self._add_directory_item( url, listitem, False, totals )
    #    except:
    #        print_exc()
    #
    #    #if listitems:
    #    #    OK = self._add_directory_items( listitems )
    #    if not OK:#elif ACTION_INFO:
    #        xbmc.executebuiltin( "Action(info)" )
    #        return
    #    self._set_content( OK, "episodes" )

    #def _add_directory_collection( self ):
    #    OK = False
    #    listitems = []
    #    try:
    #        collections = scraper.getCollections()
    #        for collection in collections:
    #            emissions = collection.pop( "Items" )
    #            for emission in emissions:
    #                # get only emission, don't parse episodes
    #                emission = emission[ "Emission" ]
    #                # set listitem
    #                listitem = xbmcgui.ListItem( emission[ "Title" ], "", "DefaultTVShows.png", emission[ "ImagePromoNormalK" ] or "" )
    #                fanart = emission[ "ImagePromoLargeI" ] or emission[ "ImageBackground" ] or ""
    #                listitem.setProperty( "fanart_image", fanart )
    #
    #                watched, unwatched = 0, 0 #int( emission[ "NombreEpisodes" ] or "1" )
    #
    #                listitem.setProperty( "WatchedEpisodes", str( watched ) )
    #                listitem.setProperty( "UnWatchedEpisodes", str( unwatched ) )
    #
    #                infoLabels = {
    #                    "tvshowtitle": emission[ "Title" ],
    #                    "title":       emission[ "Title" ],
    #                    "genre":       emission[ "Genre" ][ "Title" ],
    #                    "year":        int( ( emission[ "Year" ] or "0" ).split()[ 0 ] ),
    #                    "tagline":     ( STRING_FOR_ALL, "" )[ emission[ "GeoTargeting" ] ],
    #                    #"duration":    emission[ "CategorieDuree" ] or "",#
    #                    "episode":     unwatched,
    #                    "season":      -1,
    #                    "plot":        emission[ "Description" ] or "",
    #                    }
    #                listitem.setInfo( "Video", infoLabels )
    #                self._add_emission_context_menu( emission, listitem )
    #
    #                url = '%s?emissionId="%s"' % ( sys.argv[ 0 ], emission[ "Id" ] )
    #                listitems.append( ( url, listitem, True ) )
    #    except:
    #        print_exc()
    #
    #    if listitems:
    #        OK = self._add_directory_items( listitems )
    #    self._set_content( OK, "tvshows" )

    #def _add_directory_search( self ):
    #    OK = False
    #    listitems = []
    #    try:
    #        results = []
    #        xbmc.sleep( 10 )
    #        kb = xbmc.Keyboard( '', LangXBMC( 137 ), False )
    #        kb.doModal()
    #        xbmc.sleep( 100 )
    #        if kb.isConfirmed():
    #            text = kb.getText()
    #            if text:
    #                results = scraper.searchTerms( text )
    #                getDialogProgress()
    #        totals = len( results )
    #        for result in results:
    #            emission = result[ "Emission" ] or {}
    #            episode  = result[ "Episode" ] or {}
    #
    #            if emission:
    #                self._progress_update( emission[ "Title" ] )
    #                # set listitem
    #                listitem = xbmcgui.ListItem( emission[ "Title" ], "", "DefaultTVShows.png", emission[ "ImagePromoNormalK" ] or "" )
    #                fanart = emission[ "ImagePromoLargeI" ] or emission[ "ImageBackground" ] or ""
    #                listitem.setProperty( "fanart_image", fanart )
    #
    #                watched, unwatched = 0, 0 #int( emission[ "NombreEpisodes" ] or "1" )
    #
    #                listitem.setProperty( "WatchedEpisodes", str( watched ) )
    #                listitem.setProperty( "UnWatchedEpisodes", str( unwatched ) )
    #
    #                infoLabels = {
    #                    "tvshowtitle": emission[ "Title" ],
    #                    "title":       emission[ "Title" ],
    #                    "genre":       emission[ "Genre" ][ "Title" ],
    #                    "year":        int( ( emission[ "Year" ] or "0" ).split()[ 0 ] ),
    #                    "tagline":     ( STRING_FOR_ALL, "" )[ emission[ "GeoTargeting" ] ],
    #                    #"duration":    emission[ "CategorieDuree" ] or "",#
    #                    "episode":     unwatched,
    #                    "season":      -1,
    #                    "plot":        emission[ "Description" ] or "",
    #                    }
    #                listitem.setInfo( "Video", infoLabels )
    #                self._add_emission_context_menu( emission, listitem )
    #
    #                url = '%s?emissionId="%s"' % ( sys.argv[ 0 ], emission[ "Id" ] )
    #                #listitems.append( ( url, listitem, True ) )
    #                OK = self._add_directory_item( url, listitem, True, totals )
    #
    #            if episode:
    #                # set listitem
    #                url, listitem = self._get_episode_listitem( episode )
    #                #listitems.append( ( url, listitem, False ) )
    #                OK = self._add_directory_item( url, listitem, False, totals )
    #    except:
    #        print_exc()
    #
    #    #if listitems:
    #    #    OK = self._add_directory_items( listitems )
    #    self._set_content( OK, "episodes" )

    #def _add_directory_favourites( self ):
    #    OK = False
    #    listitems = []
    #    content = "episodes"
    #    try:
    #        emissions, episodes = scraper.getFavourites()
    #        if not episodes: content = "tvshows"
    #        getDialogProgress()
    #        for emission in emissions:
    #            self._progress_update( emission[ "Title" ] )
    #            # set listitem
    #            listitem = xbmcgui.ListItem( emission[ "Title" ], "", "DefaultTVShows.png", emission[ "ImagePromoNormalK" ] or "" )
    #            fanart = emission[ "ImagePromoLargeI" ] or emission[ "ImageBackground" ] or ""
    #            listitem.setProperty( "fanart_image", fanart )
    #
    #            watched_id = self.watched.get( str( emission[ "Id" ] ) ) or []
    #            watched = len( watched_id )
    #            try: all_id = eval( emission[ "all_id" ] )
    #            except: all_id = []
    #            NombreEpisodes = len( all_id ) or 1
    #            unwatched = NombreEpisodes - watched
    #            if unwatched < 0: unwatched = 0
    #
    #            listitem.setProperty( "WatchedEpisodes", str( watched ) )
    #            listitem.setProperty( "UnWatchedEpisodes", str( unwatched ) )
    #
    #            infoLabels = {
    #                "tvshowtitle": emission[ "Title" ],
    #                "title":       emission[ "Title" ],
    #                "genre":       emission[ "Genre" ][ "Title" ],
    #                "year":        int( ( emission[ "Year" ] or "0" ).split()[ 0 ] ),
    #                "tagline":     ( STRING_FOR_ALL, "" )[ emission[ "GeoTargeting" ] ],
    #                #"duration":    emission[ "CategorieDuree" ] or "",#
    #                "episode":     NombreEpisodes,
    #                "season":      emission.get( "season" ) or -1,
    #                "plot":        emission[ "Description" ] or "",
    #                "premiered":   emission.get( "premiered" ) or "",
    #                "castandrole": emission.get( "cast" ) or [],
    #                }
    #
    #            playCount = ( 0, 1 )[ not unwatched ]
    #            overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_WATCHED )[ playCount ]
    #            infoLabels.update( { "playCount": playCount, "overlay": overlay } )
    #
    #            listitem.setInfo( "Video", infoLabels )
    #            self._add_emission_context_menu( emission, listitem, playCount )
    #
    #            url = '%s?emissionId="%s"' % ( sys.argv[ 0 ], emission[ "Id" ] )
    #            listitems.append( ( url, listitem, True ) )
    #
    #        for episode in episodes:
    #            # set listitem
    #            url, listitem = self._get_episode_listitem( episode, False )
    #            listitems.append( ( url, listitem, False ) )
    #    except:
    #        print_exc()
    #
    #    if listitems:
    #        OK = self._add_directory_items( listitems )
    #    self._set_content( OK, content )

    def _progress_update( self, line2 ):
        progressUpdate( line2=line2 )

    def _getWatchedState( self, key, listitem ):
        #print "GET WATCHED"
        try:
            data = self.watched['watched'].get(key, None)
            if data is None:
                return False
            else:
                time = int(data['currentTime']) - 10
                if time <= 0:
                    time = int(data['currentTime'])
                if (int(data['totalTime']) - int(data['currentTime'])) < 40:
                    return True
                else:
                    time = data['currentTime']
                    listitem.setProperty("ResumeTime", str(time))
                    listitem.setProperty("TotalTime","") #hack pour skipper le popup de "resume"
                    return True
                    
        except:
            print_exc()
            return False
                
    def _get_episode_listitem_extra( self, show, season, episode, key, gototvshow=True, genreTitle=None ):
        title = episode[ "Title" ]
        #if title.strip( "#" ).isdigit():
        #    title = episode[ "Show" ] + " - " + episode[ "SeasonAndEpisodeLong" ]
        title = title + " - " + episode["Description"]
        #
        self._progress_update( episode[ "Title" ] )
        thumb = episode[ "ImageUrl" ] or ""
        listitem = xbmcgui.ListItem( title, "", "DefaultTVShows.png", thumb )

        fanart = show[ "BackgroundImageUrl" ]
        listitem.setProperty( "fanart_image", fanart or "" )
        listitem.setProperty( "thumb", thumb )#used in carrousel mode

        #set property for player set watched
        #strwatched = "%s-%s" % ( str( episode.get( "CategoryId" ) ), episode[ "Id" ] )
        strwatched = "%s" % ( key )
        listitem.setProperty( "strwatched", strwatched )
        listitem.setProperty( "PID", key )

        #genreTitle = genreTitle or G_GENRE or episode[ "GenreTitle" ] or "" # pas bon tout le temps pour episode[ "GenreTitle" ]
        infoLabels = {
            "tvshowtitle": season['Title'],
            "title":       title,
            "genre":       genreTitle,
            "plot":        episode["Details"][ "Description" ] or "",
            "season":      -1,
            "episode":     -1,
            #"year":        int( episode[ "Year" ] or "0" ),
            #"Aired":       episode[ "AirDateLongString" ] or "",
            #"mpaa":        episode[ "Rating" ] or "",
            #"duration":    episode[ "LengthString" ] or "",
            #"studio":      episode[ "Copyright" ] or "",
            #"castandrole": scraper.setCastAndRole( episode ) or [],
            #"writer":      episode[ "PeopleWriter" ] or episode[ "PeopleAuthor" ] or "",
            #"director":    episode[ "PeopleDirector" ] or "",
            }
        # set overlay watched
        watched = self._getWatchedState(episode[ "Url" ] or episode["MediaUrl"], listitem)

        #watched = str( episode[ "Key" ] ) in self.watched['watched'].get( 'currentTime' )
        #overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_ZIP )[ watched ]
        infoLabels.update( { "playCount": ( 0, 1 )[ watched ] } )

        listitem.setInfo( "Video", infoLabels )
        
        if str(listitem.getProperty("ResumeTime")) != "0.000000":
            watched = not watched
        
        self._add_episode_context_menu_extra( episode['Url'] or episode["MediaUrl"], key, episode, listitem, gototvshow, watched )

        #print "LISTITEM"
        #print repr(listitem)
        
        #import TouTvPlayer as player
        #try: player.playVideoExtra( episode[ "Url" ], episode[ "Key" ], startoffset=0, listitem_in=listitem )
        #except: print_exc()
        
        url = '%s?PIDEXTRA="%s"&KEY="%s"&starttime="%s"' % ( sys.argv[ 0 ], episode[ "Url" ] or episode["MediaUrl"],  key, listitem.getProperty("ResumeTime") )

        return url, listitem
        
    #def _get_episode_listitem( self, episode, gototvshow=True, genreTitle=None ):
    #    title = episode[ "Title" ]
    #    if title.strip( "#" ).isdigit():
    #        title = episode[ "Show" ] + " - " + episode[ "SeasonAndEpisodeLong" ]
    #    episode[ "Title" ] = title
    #    #
    #    self._progress_update( episode[ "Title" ] )
    #    thumb = episode[ "ImagePlayerNormalC" ] or ""
    #    listitem = xbmcgui.ListItem( episode[ "Title" ], "", "DefaultTVShows.png", thumb )
    #
    #    fanart = episode[ "ImageBackground" ] or episode[ "ImagePlayerLargeA" ]
    #    listitem.setProperty( "fanart_image", fanart or "" )
    #    listitem.setProperty( "thumb", thumb )#used in carrousel mode
    #
    #    #set property for player set watched
    #    strwatched = "%s-%s" % ( str( episode.get( "CategoryId" ) ), episode[ "Id" ] )
    #    listitem.setProperty( "strwatched", strwatched )
    #    listitem.setProperty( "PID", episode[ "PID" ] )
    #
    #    genreTitle = genreTitle or G_GENRE or episode[ "GenreTitle" ] or "" # pas bon tout le temps pour episode[ "GenreTitle" ]
    #    infoLabels = {
    #        "tvshowtitle": episode[ "Show" ],
    #        "title":       title,
    #        "genre":       genreTitle,
    #        "plot":        episode[ "Description" ] or "",
    #        "season":      episode[ "SeasonNumber" ] or -1,
    #        "episode":     episode[ "EpisodeNumber" ] or -1,
    #        "year":        int( episode[ "Year" ] or "0" ),
    #        "Aired":       episode[ "AirDateLongString" ] or "",
    #        "mpaa":        episode[ "Rating" ] or "",
    #        "duration":    episode[ "LengthString" ] or "",
    #        "studio":      episode[ "Copyright" ] or "",
    #        "castandrole": scraper.setCastAndRole( episode ) or [],
    #        "writer":      episode[ "PeopleWriter" ] or episode[ "PeopleAuthor" ] or "",
    #        "director":    episode[ "PeopleDirector" ] or "",
    #        }
    #    # set overlay watched
    #    watched = str( episode[ "Id" ] ) in self.watched.get( str( episode.get( "CategoryId" ) ), [] )
    #    overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_WATCHED )[ watched ]
    #    infoLabels.update( { "playCount": ( 0, 1 )[ watched ], "overlay": overlay } )
    #
    #    listitem.setInfo( "Video", infoLabels )
    #    self._add_episode_context_menu( episode, listitem, gototvshow, watched )
    #
    #    url = '%s?PID="%s"' % ( sys.argv[ 0 ], episode[ "PID" ] )
    #
    #    return url, listitem

    #def _add_emission_context_menu( self, emission, listitem, watched=False, hidewatched=False ):
    #
    #    try:
    #        c_items = [ ( LangXBMC( 20351 ), "Action(Info)" ) ]
    #
    #        if emission.get( "Id" ):
    #            #add to my favoris
    #            format = '<favourite tvshowtitle="%s" emissionId="%s" />'
    #            favourite = format % ( emission[ "Title" ], str( emission[ "Id" ] ), )
    #            uri = '%s?addtofavourites=\"%s\"' % ( sys.argv[ 0 ], quote_plus( favourite.encode( "utf-8" ) ) )
    #
    #            if self.args.category == "myfavourites":
    #                c_items += [ ( "Retirer de mes favoris", "RunPlugin(%s)" % uri.replace( "addto", "removefrom" ) ) ]
    #            else:
    #                c_items += [ ( "Ajouter à mes favoris TouTv", "RunPlugin(%s)" % uri ) ]
    #
    #        #
    #        if not hidewatched:
    #            if not watched:
    #                i_label, action = 16103, "setwatched"
    #            else:
    #                i_label, action = 16104, "setunwatched"
    #            uri = '%s?%s="%s"&all=True' % ( sys.argv[ 0 ], action, str( emission[ "Id" ] ) )
    #            c_items += [ ( LangXBMC( i_label ), "RunPlugin(%s)" % uri ) ]
    #
    #        if emission.get( "Url" ):
    #            # view emission on sitequote_plus
    #            try:
    #                url = "%s/%s" % ( scraper.TOU_TV_URL, emission[ "Url" ].strip( "/" ) )
    #                uri = '%s?webbrowser=\"%s\"' % ( sys.argv[ 0 ], quote_plus( url ) )
    #                c_items += [ ( "Visit Emission", "RunPlugin(%s)" % uri ) ]
    #            except:
    #                pass
    #
    #        self._add_context_menu_items( c_items, listitem )
    #    except:
    #        print_exc()

    def _add_favoris_context_menu_extra( self, episode, listitem, gototvshow=True, watched=False ):
        c_items = []
        try:
            #print "EPISODE KEY == "
            #print episode["Key"]
            #uri = "%s?PIDEXTRA='%s'&KEY='%s'" % ( sys.argv[ 0 ], episode[ "Url" ], episode["Key"] )
            
            #self._getWatchedState(episode[ "Url" ], listitem)
            #uri = "%s?PIDEXTRA='%s'&KEY='%s'&starttime='%s'" % ( sys.argv[ 0 ], episode[ "Url" ],  episode[ "Key" ], listitem.getProperty("ResumeTime") )
            #print uri
            #print uri
            #c_items += [ ( "Lire l'épisode", "RunPlugin(%s)" % uri ) ]

            #if episode.get( "ChapterStartTimes" ):
            #    uri = '%s?PIDEXTRA=\"%s\"&KEY=\"%s\"&ChapterStartTimes=\"%s\"' % ( sys.argv[ 0 ], episode[ "Url" ], episode["IdMedia"], episode[ "ChapterStartTimes" ] )
            #    c_items += [ ( "Chapters", "RunPlugin(%s)" % uri ) ]

            c_items += [ ( "Afficher les détails", "Action(Info)" ) ]
            #print "77777777777777777777777777777777777777777777777777777"
            #if episode.get( "Key" ):
            #    if gototvshow:
            #        uri = '%s?emissionId=\"%s\"' % ( sys.argv[ 0 ], str( episode[ "CategoryId" ] ) )
            #        c_items += [ ( LangXBMC( 20384 ).replace( "une ", "" ), "Container.Update(%s)" % uri ) ]
            #
            #    #add to my favoris
            #format = '<favourite tvshowtitle="%s" title="%s" emissionId="%s" episodeId="%s" />'
            #favourite = format % ( episode[ "Show" ], episode[ "Title" ], str( episode[ "CategoryId" ] ), str( episode[ "Id" ] ) )
            #print "episode['BookmarkKey']: " + episode['BookmarkKey']
            #format = '<favourite tvshowtitle="%s" emissionId="%s" />'
            #favourite = format % ( episode[ "Title" ], str( episode[ "BookmarkKey" ] ), )
            uri = "%s?addtofavourites='%s'" % ( sys.argv[ 0 ], episode[ "BookmarkKey" ] )
            #print "URI : " + uri
            #    print "8888888888888888888888888888888888888888888888888888888888"
            if self.args.url == "bookmark":
                c_items += [ ( "Retirer de mes favoris", "RunPlugin(%s)" % uri.replace( "addto", "removefrom" ) ) ]
            else:
                c_items += [ ( "Ajouter à mes favoris TOU.TV", "RunPlugin(%s)" % uri ) ]
            ##
            if not watched:
                i_label, action = "Marquer comme DÉJÀ écouté", "setwatched"
            else:
                i_label, action = "Mqrquer comme NON écouté", "setunwatched"
            #print "Episode Key" + episode['Key']
            #uri = "%s?%s='%s'&IdMedia='%s'" % ( sys.argv[ 0 ], action, url, id )
            #c_items += [ (  i_label , "RunPlugin(%s)" % uri ) ]

            #buy episode
            #if episode.get( "iTunesLinkUrl" ):
            #    uri = '%s?webbrowser=\"%s\"' % ( sys.argv[ 0 ], quote_plus( episode[ "iTunesLinkUrl" ] ) )
            #    c_items += [ ( "iTunes", "RunPlugin(%s)" % uri ) ]

            # view episode on site
            #url = "%s/%s" % ( scraper.TOU_TV_URL, episode[ "Url" ].strip( "/" ) )
            #uri = '%s?webbrowser=\"%s\"' % ( sys.argv[ 0 ], quote_plus( url ) )
            #c_items += [ ( "Visit Episode", "RunPlugin(%s)" % uri ) ]

            self._add_context_menu_items( c_items, listitem )
        except:
            print_exc()

    def _add_episode_context_menu_extra( self, url, id, episode, listitem, gototvshow=True, watched=False ):
        c_items = []
        try:
            #print "EPISODE KEY == "
            #print episode["Key"]
            #uri = "%s?PIDEXTRA='%s'&KEY='%s'" % ( sys.argv[ 0 ], episode[ "Url" ], episode["Key"] )
            
            self._getWatchedState(url, listitem)
            uri = "%s?PIDEXTRA='%s'&KEY='%s'&starttime='%s'" % ( sys.argv[ 0 ], url,  id, listitem.getProperty("ResumeTime") )
            #print uri
            #print uri
            c_items += [ ( "Lire l'épisode", "RunPlugin(%s)" % uri ) ]

            #if episode.get( "ChapterStartTimes" ):
            #    uri = '%s?PIDEXTRA=\"%s\"&KEY=\"%s\"&ChapterStartTimes=\"%s\"' % ( sys.argv[ 0 ], episode[ "Url" ], episode["IdMedia"], episode[ "ChapterStartTimes" ] )
            #    c_items += [ ( "Chapters", "RunPlugin(%s)" % uri ) ]

            c_items += [ ( "Afficher les détails", "Action(Info)" ) ]
            #print "77777777777777777777777777777777777777777777777777777"
            #if episode.get( "Key" ):
            #    if gototvshow:
            #        uri = '%s?emissionId=\"%s\"' % ( sys.argv[ 0 ], str( episode[ "CategoryId" ] ) )
            #        c_items += [ ( LangXBMC( 20384 ).replace( "une ", "" ), "Container.Update(%s)" % uri ) ]
            #
            #    #add to my favoris
            #format = '<favourite tvshowtitle="%s" title="%s" emissionId="%s" episodeId="%s" />'
            #favourite = format % ( episode[ "Show" ], episode[ "Title" ], str( episode[ "CategoryId" ] ), str( episode[ "Id" ] ) )
            #print "episode['BookmarkKey']: " + episode['BookmarkKey']
            #format = '<favourite tvshowtitle="%s" emissionId="%s" />'
            #favourite = format % ( episode[ "Title" ], str( episode[ "BookmarkKey" ] ), )
            uri = "%s?addtofavourites='%s'" % ( sys.argv[ 0 ], episode[ "BookmarkKey" ] )
            #print "URI : " + uri
            #    print "8888888888888888888888888888888888888888888888888888888888"
            if self.args.url == "bookmark":
                c_items += [ ( "Retirer de mes favoris", "RunPlugin(%s)" % uri.replace( "addto", "removefrom" ) ) ]
            else:
                c_items += [ ( "Ajouter à mes favoris TOU.TV", "RunPlugin(%s)" % uri ) ]
            ##
            if not watched:
                i_label, action = "Marquer comme DÉJÀ écouté", "setwatched"
            else:
                i_label, action = "Mqrquer comme NON écouté", "setunwatched"
            #print "Episode Key" + episode['Key']
            uri = "%s?%s='%s'&IdMedia='%s'" % ( sys.argv[ 0 ], action, url, id )
            c_items += [ (  i_label , "RunPlugin(%s)" % uri ) ]

            #buy episode
            #if episode.get( "iTunesLinkUrl" ):
            #    uri = '%s?webbrowser=\"%s\"' % ( sys.argv[ 0 ], quote_plus( episode[ "iTunesLinkUrl" ] ) )
            #    c_items += [ ( "iTunes", "RunPlugin(%s)" % uri ) ]

            # view episode on site
            #url = "%s/%s" % ( scraper.TOU_TV_URL, episode[ "Url" ].strip( "/" ) )
            #uri = '%s?webbrowser=\"%s\"' % ( sys.argv[ 0 ], quote_plus( url ) )
            #c_items += [ ( "Visit Episode", "RunPlugin(%s)" % uri ) ]

            self._add_context_menu_items( c_items, listitem )
        except:
            print_exc()
            
    #def _add_episode_context_menu( self, episode, listitem, gototvshow=True, watched=False ):
    #    c_items = []
    #    try:
    #        uri = '%s?PID=\"%s\"' % ( sys.argv[ 0 ], episode[ "PID" ] )
    #        c_items += [ ( LangXBMC( 13358 ), "RunPlugin(%s)" % uri ) ]
    #
    #        if episode.get( "ChapterStartTimes" ):
    #            uri = '%s?PID=\"%s\"&ChapterStartTimes=\"%s\"' % ( sys.argv[ 0 ], episode[ "PID" ], episode[ "ChapterStartTimes" ] )
    #            c_items += [ ( "Chapters", "RunPlugin(%s)" % uri ) ]
    #
    #        c_items += [ ( LangXBMC( 20352 ), "Action(Info)" ) ]
    #
    #        if episode.get( "CategoryId" ):
    #            if gototvshow:
    #                uri = '%s?emissionId=\"%s\"' % ( sys.argv[ 0 ], str( episode[ "CategoryId" ] ) )
    #                c_items += [ ( LangXBMC( 20384 ).replace( "une ", "" ), "Container.Update(%s)" % uri ) ]
    #
    #            #add to my favoris
    #            format = '<favourite tvshowtitle="%s" title="%s" emissionId="%s" episodeId="%s" />'
    #            favourite = format % ( episode[ "Show" ], episode[ "Title" ], str( episode[ "CategoryId" ] ), str( episode[ "Id" ] ) )
    #            uri = '%s?addtofavourites=\"%s\"' % ( sys.argv[ 0 ], quote_plus( favourite.encode( "utf-8" ) ) )
    #
    #            if self.args.category == "myfavourites":
    #                c_items += [ ( "Retirer de mes favoris", "RunPlugin(%s)" % uri.replace( "addto", "removefrom" ) ) ]
    #            else:
    #                c_items += [ ( "Ajouter à mes favoris TouTv", "RunPlugin(%s)" % uri ) ]
    #        #
    #        if not watched:
    #            i_label, action = 16103, "setwatched"
    #        else:
    #            i_label, action = 16104, "setunwatched"
    #        uri = '%s?%s="%s"' % ( sys.argv[ 0 ], action, listitem.getProperty( "strwatched" ) )
    #        c_items += [ ( LangXBMC( i_label ), "RunPlugin(%s)" % uri ) ]
    #
    #        #buy episode
    #        if episode.get( "iTunesLinkUrl" ):
    #            uri = '%s?webbrowser=\"%s\"' % ( sys.argv[ 0 ], quote_plus( episode[ "iTunesLinkUrl" ] ) )
    #            c_items += [ ( "iTunes", "RunPlugin(%s)" % uri ) ]
    #
    #        # view episode on site
    #        url = "%s/%s" % ( scraper.TOU_TV_URL, episode[ "Url" ].strip( "/" ) )
    #        uri = '%s?webbrowser=\"%s\"' % ( sys.argv[ 0 ], quote_plus( url ) )
    #        c_items += [ ( "Visit Episode", "RunPlugin(%s)" % uri ) ]
    #
    #        self._add_context_menu_items( c_items, listitem )
    #    except:
    #        print_exc()

    def _add_context_menu_items( self, c_items, listitem, replaceItems=True ):
        #always add visit site
        #uri = '%s?webbrowser=\"%s\"' % ( sys.argv[ 0 ], quote_plus( scraper.TOU_TV_URL ) )
        
        #c_items += [ ( "Visit TouTV", "RunPlugin(%s)" % uri ) ]
        #c_items += [ ( "Refresh Emissions", "RunScript(%s)" % SCRIPT_REFRESH ) ]

        c_items += [ ( "Aller à l'écran principale", "Container.Update(%s,replace)" % ( sys.argv[ 0 ], ) ) ]
        c_items += [ ("Paramètres de TOU.TV", "Addon.OpenSettings(plugin.infologique.tou.tv)" ) ]

        listitem.addContextMenuItems( c_items, replaceItems )

if ( __name__ == "__main__" ):
    Main()
