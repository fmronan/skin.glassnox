import xbmc
from xbmcgui import Window
from urllib import quote_plus, unquote_plus
import re
import sys
import os


class Main:
    def _parse_argv( self ):
        try:
            # parse sys.argv for params
            params = dict( arg.split( "=" ) for arg in sys.argv[ 1 ].split( "&" ) )
        except:
            # no params passed
            params = {}
        # set our preferences
        self.Menu = params.get( "Menu", "" )
        self.SubMenu = params.get( "SubMenu", "" )

    def __init__( self ):
        # parse argv for any preferences
        self._parse_argv()
        print "Menu:"    + self.Menu
        print "SubMenu:" + self.SubMenu
        Menu_Run=xbmc.getInfoLabel("skin.string(Menu_%s_%s_run)" % (self.Menu,self.SubMenu))
        Menu_Back=xbmc.getInfoLabel("skin.string(Menu_%s_%s_back)" % (self.Menu,self.SubMenu))
        Menu_Default=xbmc.getInfoLabel("skin.string(Home_Custom_Back_%s_Folder)" % (self.Menu))
        print "RUN    :" + Menu_Run
        print "Back   :" + Menu_Back
        print "Default:" + Menu_Default

        if Menu_Back:
            xbmc.executebuiltin ("Skin.SetString(CurrentBackground,%s)" % Menu_Back)
        else:
            xbmc.executebuiltin ("Skin.SetString(CurrentBackground,%s)" % Menu_Default)
        
        xbmc.executebuiltin (Menu_Run)
if ( __name__ == "__main__" ):
    Main()
