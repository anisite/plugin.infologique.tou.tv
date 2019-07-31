
import os
import re
import sys
import time
import urllib
import xbmcgui
from traceback import print_exc

from utilities import get_clientKey
from toutvapiservice import *

toutvapi = TouTvApi()
clientKey = get_clientKey()

TOU_TV_URL = 'http://www.tou.tv'

def getVideo( PID, refresh=True ):
    return toutvapi.theplatform( PID, refresh=refresh )

#def getVideoExtra( PID, refresh=True ):
#    print "START getVideoExtra - -----"
#    PID = PID.replace("%2F", "/").replace("%2f", "/");
#    emission = CALL_HTML_AUTH('https://services.radio-canada.ca/toutv/presentation' + PID + '?device=web&version=4', 'GET', None, 'client-key ' + clientKey)
#    emission = json.loads(emission)
#    IdMedia = emission['IdMedia']
#    isDRM = emission['IsDrm']
#    
#
#    content = None
#    widevineLicenseUrl = None
#    widevineAuthToken = None
#    
#    #Si nous somme authentifié, il nous faut un CLAIMS    
#    if CheckLogged()[2] and ADDON.getSetting( "disableDRM" ) == "false": # and False:
#        claims = json.loads(GET_CLAIM())['claims']
#        print "CLAIMS " + claims
#        
#        if ADDON.getSetting( "typeflux" ) == "WIDEVINE":
#            isDRM = True
#
#        if isDRM:
#            content = GET_HTML_AUTH('https://services.radio-canada.ca/media/validation/v2/?connectionType=hd&output=json&multibitrate=true&deviceType=androidams&appCode=toutv&idMedia=' + IdMedia + '&claims=' + claims)
#            content = json.loads(content)
#
#            if content['params'] != None:
#                for param in content['params']:
#                    if param.get('name') == "widevineLicenseUrl" :
#                       widevineLicenseUrl = param['value']
#                    if param.get('name') == "widevineAuthToken" :
#                       widevineAuthToken = param['value']
#            else:
#                url = None
#
#        else:
#            content = GET_HTML_AUTH('https://services.radio-canada.ca/media/validation/v2/?appCode=toutv&deviceType=ioscenc&connectionType=hd&idMedia=' + IdMedia + '&claims=' + claims + '&output=json')
#            content = json.loads(content)
#    else:
#        isDRM = False
#        print "NO EXTRA ACCESS"
#        content = GET_HTML('http://api.radio-canada.ca/validationMedia/v1/Validation.html?connectionType=broadband&appCode=toutv&output=json&multibitrate=true&deviceType=samsung&timeout=1058&idMedia=' + IdMedia)
#        content = json.loads(content)
#        
#    #content = GET_HTML_AUTH('https://services.radio-canada.ca/media/validation/v2/?appCode=toutv&deviceType=ioscenc&connectionType=hd&idMedia=' + IdMedia + '&claims=' + claims + '&output=json')
#    #content = json.loads(content)
#        
#
#    if content['message'] is not None:
#        xbmcgui.Dialog().ok("Le serveur vous parle",content['message'])
#        url = None
#    else:
#        # cette ligne permet de jouer du HD meme si nous ne sommes pas membre "Extra"
#        url = content['url'].replace(",.mp4",",3000,.mp4").replace(",3000,3000",",3000")
#        #print url
#
#    return {'url':url,'IdMedia': IdMedia, 'emission': emission, 'isDRM' : isDRM, 'widevineLicenseUrl' : widevineLicenseUrl, 'widevineAuthToken' : widevineAuthToken }

def getVideoExtra( PID, refresh=True ):
    print "START getVideoExtra - -----"
    PID = PID.replace("%2F", "/").replace("%2f", "/");
    emission = CALL_HTML_AUTH('https://services.radio-canada.ca/toutv/presentation' + PID + '?device=web&version=4', 'GET', None, 'client-key ' + clientKey)
    emission = json.loads(emission)
    IdMedia = emission['IdMedia']
    isDRM = emission['IsDrm']
    
    content = None
    widevineLicenseUrl = None
    widevineAuthToken = None
    claims = ""
    
    #Si nous somme authentifié, il nous faut un CLAIMS    
    if CheckLogged()[2]: # and ADDON.getSetting( "disableDRM" ) == "false": # and False:
        claims = json.loads(GET_CLAIM())['claims']
        print "CLAIMS " + claims
        content = GET_HTML_AUTH('https://services.radio-canada.ca/media/validation/v2/?connectionType=hd&output=json&multibitrate=true&deviceType=multiams&appCode=toutv&idMedia=' + IdMedia + '&claims=' + claims)
    else:
        print "ANONYMOUS LOGON "
        content = CALL_HTML_AUTH('https://services.radio-canada.ca/media/validation/v2/?connectionType=hd&output=json&multibitrate=true&deviceType=multiams&appCode=toutv&idMedia=' + IdMedia, 'GET', None, 'client-key ' + clientKey)
    

    content = json.loads(content)
    print content

    if content['params'] != None:
        for param in content['params']:
            if param.get('name') == "widevineLicenseUrl" :
               widevineLicenseUrl = param['value']
            if param.get('name') == "widevineAuthToken" :
               widevineAuthToken = param['value']
    #else:
    #    url = None
    #
    #    #else:
    #    #    content = GET_HTML_AUTH('https://services.radio-canada.ca/media/validation/v2/?appCode=toutv&deviceType=ioscenc&connectionType=hd&idMedia=' + IdMedia + '&claims=' + claims + '&output=json')
    #    #    content = json.loads(content)
    #else:
    #    isDRM = False
    #    print "NO EXTRA ACCESS"
    #    content = GET_HTML('http://api.radio-canada.ca/validationMedia/v1/Validation.html?connectionType=broadband&appCode=toutv&output=json&multibitrate=true&deviceType=samsung&timeout=1058&idMedia=' + IdMedia)
    #    content = json.loads(content)
        
    #content = GET_HTML_AUTH('https://services.radio-canada.ca/media/validation/v2/?appCode=toutv&deviceType=ioscenc&connectionType=hd&idMedia=' + IdMedia + '&claims=' + claims + '&output=json')
    #content = json.loads(content)
        

    if content['message'] is not None:
        xbmcgui.Dialog().ok("Le serveur vous parle",content['message'])
        url = None
    #else:
    #    # cette ligne permet de jouer du HD meme si nous ne sommes pas membre "Extra"
    #    url = content['url'].replace(",.mp4",",3000,.mp4").replace(",3000,3000",",3000")
    #    #print url

    return {'url':content['url'],'IdMedia': IdMedia, 'emission': emission, 'isDRM' : isDRM, 'widevineLicenseUrl' : widevineLicenseUrl, 'widevineAuthToken' : widevineAuthToken }

def getDate( jsondate ):
    #not really used
    try:
        d = jsondate.replace( "-62", "", 1 )
        d = float( "".join( re.findall( '(\\d{10})', d ) ) )
        return time.strftime( "%d-%m-%Y", time.localtime( d ) )
    except:
        pass
    return ""


def getPageAccueil():
    results = toutvapi.GetPageAccueil()
    return results


def searchTerms( strSearch ):
    results = toutvapi.SearchTerms( query=strSearch  ) or {}
    return results.get( "Results", [] )


def getCarrousel( playlistName ):
    carrousel = toutvapi.GetCarrousel( playlistName=playlistName )
    return carrousel


def getCollections():
    collections = toutvapi.GetCollections()
    return collections


def getPageRepertoire( cat='Emissions', refresh=False ):
    # cat : string 'Pays', 'Genres', 'Emissions'
    repertoire = toutvapi.GetPageRepertoire( refresh=refresh ) or {}
    return repertoire.get( cat )


def getEmissions():
    emissions = toutvapi.GetEmissions() or []
    return emissions


def getPremiered( emissionId ):
    premiered = ""
    try:
        url = API_SERVICE_URL + "GetPageEmission?emissionId=" + str( emissionId )
        c_filename = get_cached_filename( url )
        if os.path.exists( c_filename ):
            c_infos = getPageEmission( emissionId, uselocal=True )
            premiered = c_infos[ "Episodes" ][ -1 ][ "AirDateLongString" ] or ""
    except:
        print_exc()
    return premiered


def getAllEpisodesId( emissionId ):
    try:
        episodes = getPageEmission( emissionId )[ "Episodes" ]
        return [ str( e[ "Id" ] ) for e in episodes ]
    except:
        print_exc()
    return []


def getEmissionsWithFullDescription():
    t = time.time()
    #emissions up to date
    up_emissions = getPageRepertoire()
    #emissions outdated
    out_emissions = dict( [ ( e[ "Id" ], e ) for e in getEmissions() ] )

    emissions = []
    #emissions uptodate, set with max infos
    for e in up_emissions:
        try: e.update( out_emissions.pop( e[ "Id" ] ) )
        except: pass #print e
        # slowly if all cached filename exists
        #e[ "AirDateLongString" ] = getPremiered( e[ "Id" ] )
        emissions.append( e )

    full_emissions = {}
    full_emissions[ "Emissions" ] = emissions

    #emissions outdated, with base infos
    full_emissions[ "Outdated" ] = sorted( [ e for i, e in out_emissions.items() ], key=lambda e: e[ "Title" ].lower() )

    return full_emissions

    #print len( emissions )
    #print len( full_emissions[ "Outdated" ] )
    #print time_took( t )
    json_dumps( full_emissions )
    #print time_took( t )


def getGenres():
    genres = toutvapi.GetGenres()
    return genres


def getPageGenre( genre ):
    page = toutvapi.GetPageGenre( genre=genre )
    return page


def getPageEmission( emissionId, cat='Episodes', uselocal=False, refresh=False ):
    emission = toutvapi.GetPageEmission( emissionId=emissionId, uselocal=uselocal, refresh=refresh ) or {}
    return emission#.get( cat )


def getPageEpisode( episodeId ):
    episodes = toutvapi.GetPageEpisode( episodeId=episodeId )
    return episodes


def setCastAndRole( data ):
    castandrole = []
    try:
        PeopleCharacters = ( data.get( "PeopleCharacters" ) or "" ).replace( " & ", ", " ).replace( " et ", ", " ).split( ", " )
        PeopleComedian   = ( data.get( "PeopleComedian" )   or "" ).replace( " & ", ", " ).replace( " et ", ", " ).split( ", " )
        return [ ( c, "" ) for c in PeopleComedian if c ] or [ ( c, "" ) for c in PeopleCharacters if c ]

        #print PeopleCharacters
        #print PeopleComedian
        #print "-"*100
        #NOT GOOD
        for i, a in enumerate( PeopleComedian ):
            if not a: continue
            try: castandrole.append( ( a, PeopleCharacters[ i ] ) )
            except: castandrole.append( ( a, "" ) )

        castandrole = castandrole or [ ( c, "" ) for c in PeopleCharacters ]
    except:
        pass
    return castandrole


def refreshAllEmissions( dialog_update=None ):
    t = time.time()

    emissions = getPageRepertoire( refresh=True )
    totals = float( len( emissions ) or 1 )
    for count, emission in enumerate( emissions ):
        pct = int( ( float( count+1 ) / totals ) * 100.0 )
        if hasattr( dialog_update, 'update' ):
            if dialog_update.iscanceled(): break
            dialog_update.update( pct, "Refresh emission %i of %i" % ( count+1, int( totals ) ), emission[ "Titre" ], "Please wait..." )
        else:
            print "%i%%" % pct, emission[ "Titre" ]
        getPageEmission( emission[ "Id" ], refresh=True )

    print "[TouTV] Refresh all emissions took %s" % time_took( t )


def toutvdb( refresh=False ):
    #not used in features
    t = time.time()
    toutv_db = os.path.join( os.path.dirname( ADDON_CACHE ), "toutv.json" )
    if not refresh and os.path.exists( toutv_db ):
        if not is_expired( os.path.getmtime( toutv_db ) ):
            try:
                data = json.loads( open( toutv_db ).read() )
                print time_took( t )
                return data
            except: pass
    #create db
    all = {}
    full_emissions = getEmissionsWithFullDescription()

    for emission in full_emissions[ "Emissions" ]:
        emission[ "AirDateLongString" ] = getPremiered( emission[ "Id" ] )
        all[ emission[ "Id" ] ] = emission

    for emission in full_emissions[ "Outdated" ]:
        emission[ "AirDateLongString" ] = "(Outdated)"
        all[ emission[ "Id" ] ] = emission

    str_all = json_dumps( all, debug=False )
    #print str_all
    try: file( toutv_db, "wb" ).write( str_all )
    except: print_exc()

    data = json.loads( str_all )
    #print time_took( t )
    return data


#if ( __name__ == "__main__" ):
    #setDebug( True )
    #print toutvdb().keys()

    #getEmissionsWithFullDescription()
    #refreshAllEmissions()

    #emissions, episodes = getFavourites()
    #print emissions

    #getPageAccueil()
    #searchTerms( "vie de quartier" )
    #getPageGenre( "animation" )
    #getGenres()
    #getCollections()
    #getCarrousel( "carrousel-animation" )
    #getPageRepertoire()
    #getPageRepertoire('Pays')
    #getPageRepertoire('Genres')
    #getPageEmission( 1852377904 )#, 'Emission' )
    #getPageEpisode( 2060099162 )

    #print getDate( '/Date(-62135578800000-0500)/' )

