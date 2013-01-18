import re
import sys
import os

if ( __name__ == "__main__" ):
    try: NumView = sys.argv[ 1 ]
    except: print "erreur parametre"
    else:
        # Custom View Filename
        filename = xbmc.translatePath('special://skin/1080i/View_Custom%s.xml' % NumView)
        try:
            # Open file with write access
            file = open(filename,"w")
            # Overwrite existing file
            file.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
            file.write("<includes>\n")
            file.write("<!--Script by Frost,YiarkYiark and MikeBZH44-->\n")
            file.write("<include name=\"InitOrNotCustomView%s\">\n" % NumView)
            file.write("<onload>Skin.SetString(ReinstallCustomView,1)</onload>\n")
            file.write("</include>\n")
            file.write("</includes>\n")
            # Close file
            file.close()
        except:
            print ("Erreur file.write(%s)" % filename)
	try: os.remove(xbmc.translatePath('special://masterprofile/GlassNoxViews/View_Custom%s.xml' % NumView))
        except: print "erreur os.remove(%s)" % xbmc.translatePath('special://masterprofile/GlassNoxViews/View_Custom%s.xml' % NumView)
        try: os.rmdir(xbmc.translatePath('special://skin/media/Custom_Media%s' % NumView))
        except: print "erreur os.rmdir('%s')" % xbmc.translatePath('special://skin/media/Custom_Media%s' % NumView)
