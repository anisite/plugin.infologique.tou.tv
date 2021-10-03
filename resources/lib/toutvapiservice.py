import os
import sys
import re
import xbmc

if sys.version_info.major >= 3:
    # Python 3 stuff
    from urllib.parse import quote_plus, unquote_plus
    import urllib.parse
    from urllib.request import FancyURLopener, build_opener, HTTPCookieProcessor, HTTPHandler, Request, urlopen
    from io import StringIO as StringIO 
    import http.cookiejar as cookielib
else:
    # Python 2 stuff
    from urllib import quote_plus, unquote_plus, FancyURLopener, urlopen
    import urllib
    from urllib2 import build_opener, HTTPCookieProcessor, HTTPHandler, Request
    from StringIO import StringIO
    import cookielib

import gzip

try:
    import json
except ImportError:
    import simplejson as json

from .utilities import *

DEBUG = False

API_SERVICE_URL         = "http://api.tou.tv/v1/toutvapiservice.svc/json/"
THEPLATFORM_CONTENT_URL = "http://release.theplatform.com/content.select?pid=%s&format=SMIL" #+"&mbr=true"
#VALIDATION_MEDIA_URL        = "http://api.radio-canada.ca/validationMedia/v1/Validation.html?appCode=thePlatform&connectionType=broadband&output=json&"
VALIDATION_MEDIA_URL         = "http://api.radio-canada.ca/validationMedia/v1/Validation.html?connectionType=broadband&appCode=toutv&output=json&multibitrate=true&deviceType=samsung&timeout=1058&idMedia=%s"

CLIENT_ID = "d6f8e3b1-1f48-45d7-9e28-a25c4c514c60"
clientKey = get_clientKey()

HTTP_USER_AGENT         = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.1) Gecko/20090715 Firefox/3.5.1"
#HTTP_USER_AGENT         = "Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1"

def POST_HTML(url, POST, AUTH=False, METHOD="POST"):

    cookiejar = cookielib.LWPCookieJar()
    cookie_handler = HTTPCookieProcessor(cookiejar)
    opener = build_opener(cookie_handler)
    post_data = json.dumps(POST, separators=(',',':'))

    opener.addheaders = [
    ('Connection', 'keep-alive'),
    ('Cache-Control','max-age=0'),
    ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
    ('Origin', 'https://services.radio-canada.ca'),
    ('User-Agent', 'Mozilla/5.0 (Linux; Android 5.0.2; GT-N7105 Build/LRX22G) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/37.0.0.0 Mobile Safari/537.36'),
    ('Content-Type', 'application/x-www-form-urlencoded'),
    ('Referer', 'https://services.radio-canada.ca/auth/oauth/v2/authorize'),
    ('Accept-Encoding','gzip,deflate'),
    ('Accept-Language','fr-CA,en-US;q=0.8'),
    ('Cookie', 'l7otk2a=; s_cc=true; s_fid=129B0FEF1E58DAB0-00C1D057FFBBE1B5; s_sq=rc-toutv-all%3D%2526pid%253Dcentredesmembres%25253Aconnexion%25253Aformulaire%25253Adebut%25253Apage%2526pidt%253D1%2526oid%253DOuvrir%252520une%252520session%2526oidt%253D3%2526ot%253DSUBMIT'),
    ('X-Requested-With', 'tv.tou.android')
    ]
    
    if AUTH:
        opener.addheaders = [('Authorization', 'Bearer ' +  GET_ACCESS_TOKEN())]
    
    request = Request(url, data=post_data)
    request.get_method = lambda: METHOD
    
    response = opener.open(request)
    
    return handleHttpResponse(response)

def POST_HTML_CLIENT_KEY(url, POST):
    cookiejar = cookielib.LWPCookieJar()
    cookie_handler = urllib2.HTTPCookieProcessor(cookiejar)
    opener = urllib2.build_opener(cookie_handler)
    post_data = json.dumps(POST)

    opener.addheaders = [
    ('Host','services.radio-canada.ca'),
    ('Connection', 'keep-alive'),
    ('Authorization', 'client-key ' + clientKey),
    ('Accept', '*/*'),
    ('Origin', 'https://ici.tou.tv'),
    ('User-Agent', 'Mozilla/5.0 (Linux; Android 5.0.2; GT-N7105 Build/LRX22G) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/37.0.0.0 Mobile Safari/537.36'),
    ('Content-Type', 'application/json;charset=UTF-8'),
    ('Referer', 'https://ici.tou.tv/'),
    ('Accept-Encoding','gzip,deflate'),
    ('Accept-Language','fr-CA,fr;q=0.9,en-US;q=0.8,en-CA;q=0.7,en;q=0.6,fr-FR;q=0.5')
    ]
    
    response = opener.open(url,post_data)
    
    return handleHttpResponse(response)

    
def POST_HTML_TOKEN(url, POST):
    cookiejar = cookielib.LWPCookieJar()
    cookie_handler = urllib2.HTTPCookieProcessor(cookiejar)
    opener = urllib2.build_opener(cookie_handler)
    post_data = urllib.urlencode(POST)

    opener.addheaders = [
    ('Connection', 'keep-alive'),
    ('Cache-Control','max-age=0'),
    ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
    ('Origin', 'https://services.radio-canada.ca'),
    ('User-Agent', 'Mozilla/5.0 (Linux; Android 5.0.2; GT-N7105 Build/LRX22G) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/37.0.0.0 Mobile Safari/537.36'),
    ('Content-Type', 'application/x-www-form-urlencoded'),
    ('Referer', 'https://services.radio-canada.ca/auth/oauth/v2/authorize'),
    ('Accept-Encoding','gzip,deflate'),
    ('Accept-Language','fr-CA,en-US;q=0.8'),
    ('Cookie', 'l7otk2a=; s_cc=true; s_fid=129B0FEF1E58DAB0-00C1D057FFBBE1B5; s_sq=rc-toutv-all%3D%2526pid%253Dcentredesmembres%25253Aconnexion%25253Aformulaire%25253Adebut%25253Apage%2526pidt%253D1%2526oid%253DOuvrir%252520une%252520session%2526oidt%253D3%2526ot%253DSUBMIT'),
    ('X-Requested-With', 'tv.tou.android')
    ]
    
    try:
        print ("tring open : " + url)
        response = opener.open(url,post_data)
        accessToken = response.geturl().split('#access_token=')[1][:36]
    except:
        print ("oups 401...")
        accessToken = None

    return accessToken

def GET_HTML( url):
    print ("GET_HTML")
    request = urllib2.Request(url)
    #try:
    request.add_header('Accept-encoding', 'gzip')
    response = urllib2.urlopen(request)
    return handleHttpResponse(response)
    #except:
    #    print "fail"

    return ""

def _GetUserInfo():
    infos = GET_HTML_AUTH("https://services.radio-canada.ca/toutv/profiling/accounts/me?device=web&version=4", True)
    #print "_GetUserInfo : " + infos
    connected = True
    extra = False
    name = None
    if not infos:
        connected = False
        name = "Bonjour, impossible de se connecter, verifiez votre mot de passe"
    else:
        #print infos
        name = json.loads(infos)["FirstName"]
        name = u"Connecté: " + name
        infos = GET_HTML_AUTH("https://services.radio-canada.ca/toutv/profiling/userprofile", True)
        extra = json.loads(infos)["IsPremium"]
        
        if extra:
            name = name + " (Compte EXTRA)"
        
        
    return (connected, name, extra)
  
def CheckLogged():
    print ("---------------------PREMIUM CHECK--------------------------------")
   
    #Connecte, Bienvenue, Extra
    premiumData = (False,"Bonjour, connectez-vous ici", False)
    
    if (ADDON.getSetting( "username" ) != "") and (ADDON.getSetting( "password" ) != ""):
        print ("Continue premium check")
        #ADDON.setSetting( "access_token_" + ADDON.getSetting( "username"), "" )
        
        if (ADDON.getSetting( "lastData" ) != ADDON.getSetting( "username" ) + ADDON.getSetting( "password" )):
            ADDON.setSetting( "lastData", ADDON.getSetting( "username" ) + ADDON.getSetting( "password" ))
            ADDON.setSetting( "accessToken", "" )

        try:
            premiumData = _GetUserInfo();
        except:
            print ("Check fail, try another time!")
            try:
                TEST()
                premiumData = _GetUserInfo();
            except:
                print ("ne rien faire!")
                
        if not GET_ACCESS_TOKEN():
            TEST()
            premiumData = _GetUserInfo();
    else:
        ADDON.setSetting( "accessToken", "" )
    return premiumData;

def GET_ACCESS_TOKEN():
    return ADDON.getSetting("accessToken")
    
def isLoggedIn():
    return (GET_ACCESS_TOKEN() != "")
    
def GET_HTML_AUTH( url, PreventLoop=False ):

    if not GET_ACCESS_TOKEN():
        return ""
    #print "---------------------GET_HTML_AUTH--------------------------------"
    if not PreventLoop:
        CheckLogged()
    #print "GET_HTML: " + url
    request = Request(url)
    request.add_header('Accept', 'application/json, text/plain, */*')
    request.add_header('Origin', 'https://ici.tou.tv')
    request.add_header('Accept-Language', 'fr-CA,fr;q=0.9,en-CA;q=0.8,en;q=0.7,fr-FR;q=0.6,en-US;q=0.5')
    request.add_header('Accept-encoding', 'gzip')
    request.add_header('Authorization', 'Bearer ' +  GET_ACCESS_TOKEN())
    request.add_header('User-Agent', 'Mozilla/5.0 (Linux; Android 5.0.2; GT-N7105 Build/LRX22G) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/37.0.0.0 Mobile Safari/537.36')
    response = urlopen(request)
    return handleHttpResponse(response)
    
def GET_AUTHORISE( url ):
    print("GO!")
    #if not GET_ACCESS_TOKEN():
    #    return ""
    #print "---------------------GET_HTML_AUTH--------------------------------"
    #if not PreventLoop:
    #    CheckLogged()
    #print "GET_HTML: " + url
    cookiejar = cookielib.LWPCookieJar()
    cookie_handler = HTTPCookieProcessor(cookiejar)
    opener = build_opener(cookie_handler)
    
    #request = Request(url)
    print("GO2!")
    opener.addheaders = [
    ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'),
    ('Referer', 'https://ici.tou.tv/'),
    ('Accept-Language', 'fr-CA,fr;q=0.9,en-CA;q=0.8,en;q=0.7,fr-FR;q=0.6,en-US;q=0.5'),
    ('Accept-Encoding', 'gzip, deflate, br'),
    ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36')
    ]
    print("GO3!")
    #opener.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9')
    #opener.add_header('Referer', 'https://ici.tou.tv/')
    #opener.add_header('Accept-Language', 'fr-CA,fr;q=0.9,en-CA;q=0.8,en;q=0.7,fr-FR;q=0.6,en-US;q=0.5')
    #opener.add_header('Accept-Encoding', 'gzip, deflate, br')
    ##request.add_header('Authorization', 'Bearer ' +  GET_ACCESS_TOKEN())
    #opener.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36')
    
    request = Request(url)
    request.get_method = lambda: "GET"
    
    response = opener.open(request)
    print("ca marche")
    print(response)
    print(cookiejar)
    
    #print(cookiejar["x-ms-cpim-csrf"])
    
    for c in cookiejar:
        if c.name == "x-ms-cpim-csrf":
            return c.value
    
def CALL_HTML_AUTH( url, method = "GET", json_data=None, Authorization="Bearer" ):

    if Authorization=="Bearer" and not GET_ACCESS_TOKEN():
        return ""
    print ("---------------------CALL_HTML_AUTH--------------------------------")

    #print "GET_HTML: " + url
    opener = build_opener(HTTPHandler)
    if json_data is None:
        request = Request(url)
    else:
        binary_data = json_data.encode('utf-8') 
        request = Request(url, binary_data)

    request.add_header('Accept', '*/*')
    request.add_header('Origin', 'https://ici.tou.tv')
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36')
    request.add_header('Accept-Language', 'fr-CA,fr;q=0.9,en-CA;q=0.8,en;q=0.7,fr-FR;q=0.6,en-US;q=0.5')
    request.add_header('Accept-encoding', 'gzip, deflate')
    request.add_header('Content-Type', 'application/json;charset=UTF-8')
    request.get_method = lambda: method
    
    if Authorization == "Bearer":
        request.add_header('Authorization', 'Bearer ' +  GET_ACCESS_TOKEN())
    else:
        request.add_header('Authorization', Authorization)
        
    request.add_header('User-Agent', 'Mozilla/5.0 (Linux; Android 5.0.2; GT-N7105 Build/LRX22G) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/37.0.0.0 Mobile Safari/537.36')

    response = None 

    response = opener.open(request)
    return handleHttpResponse(response)


def handleHttpResponse(response):
    if sys.version_info.major >= 3:
        if response.info().get('Content-Encoding') == 'gzip':
            f = gzip.GzipFile(fileobj=response)
            data = f.read()
            return data
        else:
            data = response.read()
            return data
    else:
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO( response.read() )
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
            return data
        else:
            return response.read()


def API_HTML_AUTH( type, url ):
    #print "---------------------GET_HTML_AUTH--------------------------------"

    CheckLogged()
    #print "GET_HTML: " + url
    request = Request(url,"")
    request.get_method = lambda: type
    request.add_header('Accept', 'application/json')
    
    request.add_header('Authorization', 'Bearer ' + GET_ACCESS_TOKEN())
    request.add_header('User-Agent', 'TouTvApp/2.1.2.2 (samsung/t0lte/(GT-N7105); API/21/-/21; fr-ca)')
    request.add_header('Content-Length', '0')
    response = urlopen(request)
    return handleHttpResponse(response)

def GET_CLAIM():
    print ("Start GET_CLAIM")
    return GET_HTML_AUTH('https://services.radio-canada.ca/media/validation/v2/GetClaims?token=' + GET_ACCESS_TOKEN())
#https://rcmnb2cprod.b2clogin.com/rcmnb2cprod.onmicrosoft.com/B2C_1A_ExternalClient_FrontEnd_Login/oauth2/v2.0/authorize?client_id=ebe6e7b0-3cc3-463d-9389-083c7b24399c&nonce=85e7800e-15ba-4153-ac2f-3e1491918111&redirect_uri=https%3A%2F%2Fici.tou.tv%2Fauth-changed&scope=openid%20offline_access%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Foidc4ropc%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fprofile%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Femail%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fid.write%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fmedia-validation.read%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fmedia-validation%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fmedia-meta%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fmedia-drmt%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Ftoutv-presentation%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Ftoutv-profiling%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fmetrik%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fsubscriptions.write%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fid.account.info%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fid.account.create%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fid.account.modify%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fid.account.reset-password%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fid.account.send-confirmation-email%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fid.account.delete%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fsubscriptions.validate%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Ftoutv&response_type=id_token%20token&response_mode=fragment&prompt=login&state=ZDY1Nzg2YzctZDQ4YS00YWRjLWEwNDMtMGI2MWIyM2UyZjUxfHsiYWN0aW9uIjoibG9naW4iLCJyZXR1cm5VcmwiOiIvIiwiZnJvbVN1YnNjcmlwdGlvbiI6ZmFsc2V9&state_value=ZDY1Nzg2YzctZDQ4YS00YWRjLWEwNDMtMGI2MWIyM2UyZjUxfHsiYWN0aW9uIjoibG9naW4iLCJyZXR1cm5VcmwiOiIvIiwiZnJvbVN1YnNjcmlwdGlvbiI6ZmFsc2V9&ui_locales=fr


def TEST():
    print ("================= Start TEST user ======================")
    #session = GET_SESSIONID_AND_SESSION_DATA()
    
    val = GET_AUTHORISE("https://rcmnb2cprod.b2clogin.com/rcmnb2cprod.onmicrosoft.com/B2C_1A_ExternalClient_FrontEnd_Login/oauth2/v2.0/authorize?client_id=ebe6e7b0-3cc3-463d-9389-083c7b24399c&nonce=85e7800e-15ba-4153-ac2f-3e1491918111&redirect_uri=https%3A%2F%2Fici.tou.tv%2Fauth-changed&scope=openid%20offline_access%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Foidc4ropc%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fprofile%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Femail%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fid.write%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fmedia-validation.read%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fmedia-validation%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fmedia-meta%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fmedia-drmt%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Ftoutv-presentation%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Ftoutv-profiling%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fmetrik%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fsubscriptions.write%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fid.account.info%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fid.account.create%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fid.account.modify%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fid.account.reset-password%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fid.account.send-confirmation-email%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fid.account.delete%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Fsubscriptions.validate%20https%3A%2F%2Frcmnb2cprod.onmicrosoft.com%2F84593b65-0ef6-4a72-891c-d351ddd50aab%2Ftoutv&response_type=id_token%20token&response_mode=fragment&prompt=login&state=ZDY1Nzg2YzctZDQ4YS00YWRjLWEwNDMtMGI2MWIyM2UyZjUxfHsiYWN0aW9uIjoibG9naW4iLCJyZXR1cm5VcmwiOiIvIiwiZnJvbVN1YnNjcmlwdGlvbiI6ZmFsc2V9&state_value=ZDY1Nzg2YzctZDQ4YS00YWRjLWEwNDMtMGI2MWIyM2UyZjUxfHsiYWN0aW9uIjoibG9naW4iLCJyZXR1cm5VcmwiOiIvIiwiZnJvbVN1YnNjcmlwdGlvbiI6ZmFsc2V9&ui_locales=fr")
    
    GET_SELF_ASSERTED()
    #https://rcmnb2cprod.b2clogin.com/rcmnb2cprod.onmicrosoft.com/B2C_1A_ExternalClient_FrontEnd_Login/SelfAsserted?tx=StateProperties=eyJUSUQiOiJjYTdkODkzNi1jOWZhLTRlZWMtYjIxYy1hNTMxNmFhNTNlZmMifQ&p=B2C_1A_ExternalClient_FrontEnd_Login
    
    
    print val
    
    #print session
    
    POST = {'Email': ADDON.getSetting( "username" ),
            'Password': ADDON.getSetting( "password" ),
            'ClientId' : clientKey,#CLIENT_ID,
            'ClientSecret': '34026772-244b-49b6-8b06-317b30ac9a20',
            'Scope' : 'openid profile email id.write media-validation.read media-validation media-meta media-drmt toutv-presentation toutv-profiling metrik subscriptions.write id.account.info id.account.create id.account.modify id.account.reset-password id.account.send-confirmation-email id.account.delete'
            }
            
    content = CALL_HTML_AUTH('https://services.radio-canada.ca/toutv/profiling/accounts/login?device=web&version=4',"POST", json.dumps(POST), "client-key " + clientKey)
    
    jT = json.loads(content)
    #listform = ["action", "sessionID", "sessionData", "lang" ]
    
    #output = {'action': None, 'sessionID': None, 'sessionData': None, 'lang': None}
    
    #otrimput = html_proc.findAll('input', {'name': listform})
    #for elem in otrimput:
    #    output[elem.get('name')] = elem.get('value')
    
    #POST = {'action' : output['action'],
    #        'sessionData' : output['sessionData'],
    #        'sessionID' : output['sessionID'],
    #        'lang' :	output['lang']
    #        }
    
    #accessToken = POST_HTML_TOKEN('https://services.radio-canada.ca/auth/oauth/v2/authorize/consent',POST)
    ADDON.setSetting( "accessToken", jT['access_token'] )
    return jT['access_token']
    
def setDebug( yesno ):
    global DEBUG
    DEBUG = yesno


def _print( msg, debug=False ):
    if DEBUG or debug:
        print (msg)


def json_dumps( data, sort_keys=True, indent=2, debug=False ):
    try:
        str_dump = json.dumps( data, sort_keys=sort_keys, indent=indent )
        if DEBUG or debug:
            _print( str_dump, debug )
            _print( "-"*100, debug )
        return str_dump
    except:
        return "%r" % data


def get_html_source( url, refresh=False, uselocal=False ):
    """ fetch the html source """
    source = ""
    try:
        # set cached filename
        source, sock, c_filename = get_cached_source( url, refresh, uselocal, debug=_print )

        if not source or sock is None:
            _print( "Reading online source: %r" % url )
            sock = urllib.urlopen( url )
            source = sock.read()
            if c_filename:
                try: file( c_filename, "w" ).write( source )
                except: print_exc()
        sock.close()
    except:
        print_exc()
    return source


class _urlopener( FancyURLopener ):
    version = os.environ.get( "HTTP_USER_AGENT" ) or HTTP_USER_AGENT
_urlopener = _urlopener()


class TouTvApi:
    def __init__( self ):
        self.__handler_cache = {}

    def __getattr__( self, method ):
        if method in self.__handler_cache:
            return self.__handler_cache[ method ]

        def handler( *args, **kwargs ):
            if method.lower() == "theplatform":
                return self.content_select( args[ 0 ], kwargs.get( "refresh", True ) )
            elif method.lower() == "validation":
                return self.validation( **kwargs )
            else:
                return self.getRepertoire( method, **kwargs )

        handler.method = method
        self.__handler_cache[ method ] = handler
        return handler

    def getRepertoire( self, method, **kwargs ):
        start_time = time.time()
        # get params
        refresh = False
        if kwargs.has_key( "refresh" ):
            refresh = kwargs[ "refresh" ]
            kwargs.pop( "refresh" )
        uselocal = False
        if kwargs.has_key( "uselocal" ):
            uselocal = kwargs[ "uselocal" ]
            kwargs.pop( "uselocal" )
        #
        url = API_SERVICE_URL + method
        query = urllib.urlencode( kwargs )
        if query: url += "?" + query
        #
        content = get_html_source( url, refresh, uselocal )
        data = json.loads( content ).get( "d" )
        #
        _print( "[TouTvApi] %s took %s" % ( method, time_took( start_time ) ) )
        json_dumps( data )
        return data
        
    def content_select( self, PID, refresh=True ):
        start_time = time.time()
        content = get_html_source( VALIDATION_MEDIA_URL % PID, refresh )
        val = json.loads(content)

        _print( "[TouTvApi] thePlatform took %s" % time_took( start_time ) )

        return val

    def validation( self, **kwargs ):
        print ("deprecated")
        #start_time = time.time()
        #kwargs[ "deviceType" ] = kwargs.get( "deviceType" ) or "iphone4" #ipad"
        #refresh = True
        #if kwargs.has_key( "refresh" ):
        #    refresh = kwargs[ "refresh" ]
        #    kwargs.pop( "refresh" )
        #content = get_html_source( VALIDATION_MEDIA_URL + urllib.urlencode( kwargs ), refresh )
        #data = json.loads( content )
        ##
        #_print( "[TouTvApi] Validation took %s" % time_took( start_time ) )
        #json_dumps( data )
        #return data


if ( __name__ == "__main__" ):
    setDebug( True )
    toutvapi = TouTvApi()
    
    toutvapi.GetPays()

    #toutvapi.GetPageRepertoire()
    #toutvapi.GetPageAccueil()
    #toutvapi.GetGenres()
    #toutvapi.GetCollections()
    #toutvapi.GetEmissions()
    #toutvapi.GetPageGenre( genre="animation" )
    #toutvapi.GetPageEmission( emissionId=2041271036 ) # digit
    #toutvapi.GetPageEpisode( episodeId=2060099162 ) # digit
    #toutvapi.GetCarrousel( playlistName="carrousel-animation" )
    #toutvapi.SearchTerms( query="vie de quartier"  )

    #print toutvapi.theplatform( '2S7KnmMzf3qdFokIL61ORofYT7vh73Am', refresh=True )

    # not supported on xbmc is m3u8 file type
    #toutvapi.validation( idMedia='2S7KnmMzf3qdFokIL61ORofYT7vh73Am', refresh=True )
