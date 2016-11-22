
import xbmc
import xbmcgui

import scraper

DIALOG_PROGRESS = xbmcgui.DialogProgress()

try:
    DIALOG_PROGRESS.create( "TouTV", "Refresh all emissions..." )
    xbmc.sleep( 1000 )
    #while xbmc.( 'Dialog.Close(10101)' )
    scraper.refreshAllEmissions( DIALOG_PROGRESS )
except:
    pass

xbmc.executebuiltin( 'Dialog.Close(10101)' )
#try: DIALOG_PROGRESS.close()
#except: pass

xbmc.executebuiltin( 'Container.Refresh' )
