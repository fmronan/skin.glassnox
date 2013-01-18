"""
    Script Meet Dependencies!
    by Frost (passion-xbmc.org)

    Method use:
      - RunScript(SCRIPT[,INFO,DATADIR,ADDON1,ADDON2,ADDON?,silent])
        SCRIPT = le chemin du dependencies.py

    Params: (si aucun params est indiquer, le script va scanner pour les deps du skin.)
      - INFO       = [opt] URL du addons.xml ou ce trouve la dep
      - DATADIR    = [opt] URL du repertoire des addons du repo pour la dep
      - ADDONS     = [opt] l'id de(s) dep(s) (peut etre multiple, juste a separer par une virgule)
      - Last param = [opt] silent, si on veut pas voir la progression et ni de dialog ok (suffit de mettre silent comme bon dernier)

    Exemple: (Pour tous les deps du skin)
      - RunScript(special://skin/scripts/dependencies.py)
        RunScript(special://skin/scripts/dependencies.py,silent)

    Exemple: (Pour une seule dep)
      - RunScript(special://skin/scripts/dependencies.py,http://passion-xbmc.org/addons/addons.php/11.0,http://passion-xbmc.org/addons/Download.php,script.metadata.actors)
        RunScript(special://skin/scripts/dependencies.py,http://passion-xbmc.org/addons/addons.php/11.0,http://passion-xbmc.org/addons/Download.php,script.metadata.actors,silent)

    Exemple: (Pour plusieurs deps sur le meme repo)
      - RunScript(special://skin/scripts/dependencies.py,http://passion-xbmc.org/addons/addons.php/11.0,http://passion-xbmc.org/addons/Download.php,script.metadata.actors,script.moviesets)
        RunScript(special://skin/scripts/dependencies.py,http://passion-xbmc.org/addons/addons.php/11.0,http://passion-xbmc.org/addons/Download.php,script.metadata.actors,script.moviesets,silent)
"""


import time
START_TIME = time.time()

import os
import sys
import Queue
import random
import socket
import urllib
from traceback import print_exc

import xbmc
import xbmcgui
import xbmcvfs

ADDONS_DIR      = "special://home/addons/"
PACKAGES_DIR    = ADDONS_DIR + "packages/"


class Stack( Queue.Queue ):
    "Thread-safe stack"
    # method aliases
    push = Queue.Queue.put
    pop  = Queue.Queue.get
    pop_nowait = Queue.Queue.get_nowait
    def _put( self, item ):
        # add at the end, if not exists
        if item not in self.queue:
            self.queue.append( item )
    def add( self, items ):
        for item in items:
            self.push( item )


class _urlopener( urllib.FancyURLopener ):
    version = random.choice( [ "Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko/20100101 Firefox/11.0",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19" ] )
urllib._urlopener = _urlopener()
socket.setdefaulttimeout( 20 )


def updateLocalAddonsAndAddonRepos():
    # update local addons and repos
    for up in [ 'UpdateLocalAddons', 'UpdateAddonRepos' ]:
        xbmc.executebuiltin( up )
        xbmc.sleep( 100 )
updateLocalAddonsAndAddonRepos()


def getAddons( info, datadir, addonsid ):
    addons = []
    dom = None
    xbmc.executebuiltin( 'ActivateWindow(busydialog)' )
    try:
        from xml.dom.minidom import parseString
        dom = parseString( urllib.urlopen( info ).read() )
        for item in dom.getElementsByTagName( "addon" ):
            addonID = item.getAttribute( "id" )
            if addonID in addonsid:
                version = item.getAttribute( "version" )
                url     = "%s/%s/%s-%s.zip" % ( datadir, addonID, addonID, version )
                addons.append( ( item.getAttribute( "name" ), url, addonID, version ) )
                if len( addons ) == len( addonsid ): break
    except:
        print_exc()
    xbmc.executebuiltin( 'Dialog.Close(busydialog,true)' )
    if hasattr( dom, "unlink" ): dom.unlink()
    print "Dependencies for %r : %r" % ( addonsid, addons )
    return addons

def openDB():
    conn = None
    try:
        import sqlite3
        # connect to Addons database
        conn = sqlite3.connect( xbmc.translatePath( "special://Database/Addons15.db" ) )
    except:
        print_exc()
    return conn

def closeDB( conn ):
    if hasattr( conn, "close" ):
        # close database
        conn.close()

def getDependencies( conn, addonID=xbmc.getSkinDir() ):
    deps = []
    try:
        SQL_DEPS = """SELECT addon.name, addon.path, addon.addonID, addon.version FROM addon WHERE addon.addonID IN (SELECT dependencies.addon FROM dependencies WHERE dependencies.id=(SELECT addon.id FROM addon WHERE addon.addonID="%s")) AND addon.addonID NOT IN (SELECT broken.addonID FROM broken) ORDER BY addon.addonID, addon.version""" % addonID # DESC
        #print SQL_DEPS
        deps = conn.execute( SQL_DEPS ).fetchall()
    except:
        print_exc()
    print "Dependencies for %r : %r" % ( addonID, deps )
    return deps


def download( addons, silent=False ):
    DIALOG_PROGRESS = xbmcgui.DialogProgress()
    def _pbhook( numblocks, blocksize, filesize, ratio=1.0 ):
        if not silent:
            try: pct = int( min( ( numblocks * blocksize * 100 ) / filesize, 100 ) * ratio )
            except: pct = 100
            DIALOG_PROGRESS.update( pct )
            if DIALOG_PROGRESS.iscanceled():
                raise IOError
    REPORTHOOK = lambda nb, bs, fs: _pbhook( nb, bs, fs )

    if not silent: DIALOG_PROGRESS.create( "Skin Meet Dependencies!" )
    totals = len( addons )
    diff = 100.0 / totals
    percent = 0
    installed = 0
    for i, dep in enumerate( addons ):
        percent += diff
        name, url, addonID, version = dep
        line1 = "Dep %i of %i (%s)" % ( i+1, totals, name )
        if not silent: DIALOG_PROGRESS.update( int( percent ), line1, url, "Downloading Please wait..." )

        print url
        fp = None
        dest = xbmc.translatePath( PACKAGES_DIR + os.path.basename( url ) )
        try: fp, h = urllib.urlretrieve( url, dest, REPORTHOOK )
        except IOError: xbmcvfs.delete( dest )
        except: print_exc()

        if fp and xbmcvfs.exists( fp ):
            if not silent: DIALOG_PROGRESS.update( int( percent ), line1, ADDONS_DIR + addonID, "Installing Please wait..." )
            xbmc.executebuiltin( "XBMC.Extract(%s,%s)" % ( fp, xbmc.translatePath( ADDONS_DIR ) ) )
            xbmc.sleep( 1000 )
            installed += 1

        print fp #, str( h ).replace( "\r", "" )
        print "-"*100
        if not silent and DIALOG_PROGRESS.iscanceled():
            break

    print time.time()-START_TIME
    if not silent: DIALOG_PROGRESS.close()

    return installed


def Main():
    # parse sys.argv
    silent = sys.argv[ -1 ].lower() == "silent"
    args   = sys.argv[ 1: ]
    if silent: args = args[ :-1 ]

    # connect to Addons database
    conn  = openDB()
    stack = Stack( 0 )
    # push deps on stack
    if not args: stack.add( getDependencies( conn ) )
    else: stack.add( getAddons( args[ 0 ], args[ 1 ].rstrip( "/" ), args[ 2: ] ) )

    # meet only if system has not addon
    meet = []
    try:
        while stack.qsize():
            dep = stack.pop()
            #don't visit if in meet
            if dep not in meet:
                addonID = dep[ 2 ]
                stack.add( getDependencies( conn, addonID ) )
                cond = "System.HasAddon(%s)" % addonID
                if xbmc.getCondVisibility( cond ):
                    print cond
                else:
                    meet.append( dep )
    except Queue.Empty:
        pass
    closeDB( conn )

    print "Meet: %r" % meet
    # if missing addons download this
    if meet:
        installed = download( meet, silent ) or 0
        message = "Installed %i of %i Dependencies" % ( installed, len( meet ) )
        # update local addons and repos
        updateLocalAddonsAndAddonRepos()
    else:
        message = "Dependencies are already installed or not found!"
    if not silent:
        xbmcgui.Dialog().ok( "Skin Meet Dependencies!", message )



if ( __name__ == "__main__" ):
    Main()
