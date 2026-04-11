
import os
import re
import sys
import time
import urllib
import xbmcgui
from traceback import print_exc

from .utilities import get_clientKey
from .toutvapiservice import *

toutvapi = TouTvApi()
clientKey = get_clientKey()

TOU_TV_URL = 'http://www.tou.tv'

def getVideoExtra( URL,  PID, refresh=True ):
    print ("START getVideoExtra - -----")
    URL = URL.replace("%2F", "/").replace("%2f", "/");
    emission = CALL_HTML_AUTH('https://services.radio-canada.ca/ott/catalog/v2/toutv/show/' + URL, 'GET', None, 'client-key ' + clientKey)
    emission = json.loads(emission)
    IdMedia = PID
    isDRM = True #emission['IsDrm']
    
    content = None
    widevineLicenseUrl = None
    widevineAuthToken = None
    claims = ""
    
    loginState = CheckLogged()

    #Si nous somme authentifié, il nous faut un CLAIMS    
    if loginState[0]: # and ADDON.getSetting( "disableDRM" ) == "false": # and False:
        claims = loginState[3]
        print ("CLAIMS " + claims)
        content = GET_HTML_AUTH('https://services.radio-canada.ca/media/validation/v2/?appCode=toutv&connectionType=hd&deviceType=multiams&multibitrate=true&output=json&tech=dash&manifestVersion=2&idMedia=' + IdMedia, False, None, claims)
    else:
        print ("ANONYMOUS LOGON ")
        content = CALL_HTML_AUTH('https://services.radio-canada.ca/media/validation/v2/?appCode=toutv&connectionType=hd&deviceType=multiams&multibitrate=true&output=json&tech=dash&manifestVersion=2&idMedia=' + IdMedia, 'GET', None, 'client-key ' + clientKey)

    content = json.loads(content)
    print (content)

    url = content["url"]

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

    return {'url': url, 'IdMedia': IdMedia, 'emission': emission, 'isDRM' : isDRM, 'widevineLicenseUrl' : widevineLicenseUrl, 'widevineAuthToken' : widevineAuthToken }

def getPageRepertoire( cat='Emissions', refresh=False ):
    # cat : string 'Pays', 'Genres', 'Emissions'
    repertoire = toutvapi.GetPageRepertoire( refresh=refresh ) or {}
    return repertoire.get( cat )


def getPageEmission( emissionId, cat='Episodes', uselocal=False, refresh=False ):
    emission = toutvapi.GetPageEmission( emissionId=emissionId, uselocal=uselocal, refresh=refresh ) or {}
    return emission#.get( cat )


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
            print ("%i%%" % pct, emission[ "Titre" ])
        getPageEmission( emission[ "Id" ], refresh=True )

    print ("[TouTV] Refresh all emissions took %s" % time_took( t ))

