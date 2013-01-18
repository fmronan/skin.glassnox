import re
import sys
import os

if ( __name__ == "__main__" ):
    try: NumView = sys.argv[ 1 ]
    except: print "erreur parametre"
    else:
	SrcView=open(xbmc.translatePath('special://masterprofile/GlassNoxViews/View_Custom%s.xml' % NumView),'r')
	NewView=open(xbmc.translatePath('special://skin/1080i/View_Custom%s.xml' % NumView),'w')
	f=SrcView.readlines()
	SrcView.close
	for l in f:
		NewView.write(l)
	NewView.close
	xbmc.executebuiltin( "ReloadSkin()")
        
      
        
