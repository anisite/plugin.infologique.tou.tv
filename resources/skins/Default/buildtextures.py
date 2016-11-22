
import os
import shutil

prefix = "toutv-"

skin_sources_dir = r"E:\coding\Windows\xbmc\addons\skin.confluence"
skin_sources_dir = skin_sources_dir.replace( "\\", "/" ).strip( "/" )

# get xml content
str_xml = ""
for root, dirs, files in os.walk( "720p" ):
    for file in files:
        str_xml += open( os.path.join( root, file ) ).read()


# media source
media = skin_sources_dir + "/media"

for root, dirs, files in os.walk( media ):#, topdown=False ):
    for file in files:
        fpath = os.path.join( root, file )
        img = fpath.replace( media, "" ).replace( "\\", "/" ).strip( "/" )
        if img in str_xml:
            dst = "media/" + prefix + img
            #print dst
            if not os.path.exists( os.path.dirname( dst ) ):
                os.makedirs( os.path.dirname( dst ) )
            shutil.copy( fpath, dst )


# backgrounds source
backgrounds = skin_sources_dir + "/backgrounds"

for root, dirs, files in os.walk( backgrounds ):#, topdown=False ):
    for file in files:
        fpath = os.path.join( root, file )
        img = fpath.replace( backgrounds, "" ).replace( "\\", "/" ).strip( "/" )
        if img in str_xml:
            dst = "backgrounds/" + prefix + img
            print dst
            if not os.path.exists( os.path.dirname( dst ) ):
                os.makedirs( os.path.dirname( dst ) )
            shutil.copy( fpath, dst )
