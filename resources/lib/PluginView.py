
import sys
import xbmcplugin

class PluginView :
    def __init__( self ):
        pass

    def _add_directory_item( self, url, listitem, isFolder, totalItems ):
        """ addDirectoryItem(handle, url, listitem [,isFolder, totalItems])
            handle      : integer - handle the plugin was started with.
            url         : string - url of the entry. would be plugin:// for another virtual directory
            listitem    : ListItem - item to add.
            isFolder    : [opt] bool - True=folder / False=not a folder(default).
            totalItems  : [opt] integer - total number of items that will be passed.(used for progressbar)
        """
        return xbmcplugin.addDirectoryItem( int( sys.argv[ 1 ] ), url, listitem, isFolder, totalItems )
    
    def _add_directory_items( self, listitems ):
        """ addDirectoryItems(handle, items [,totalItems])
            handle      : integer - handle the plugin was started with.
            items       : List - list of (url, listitem[, isFolder]) as a tuple to add.
            totalItems  : [opt] integer - total number of items that will be passed.(used for progressbar)
        """
        return xbmcplugin.addDirectoryItems( int( sys.argv[ 1 ] ), listitems, len( listitems ) )

    def _set_content( self, succeeded, content, sort=True ):
        if ( succeeded ):
            #content = ( "addons", "files", "movies", "tvshows", "episodes", "musicvideos", "albums", "artists", "songs" )[ 2 ]
            xbmcplugin.setContent( int( sys.argv[ 1 ] ), content )
            
        #if sort:
        #    self._add_sort_methods( succeeded )
        #else:
        #    self._end_of_directory( succeeded )
        self._end_of_directory( succeeded )

    def _add_sort_methods( self, succeeded ):
        if ( succeeded ):
            xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_UNSORTED )
            xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_EPISODE )
            xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_VIDEO_YEAR )
            xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_GENRE )
            xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_MPAA_RATING )
        self._end_of_directory( succeeded )

    def _end_of_directory( self, succeeded ):
        xbmcplugin.endOfDirectory( int( sys.argv[ 1 ] ), succeeded )
