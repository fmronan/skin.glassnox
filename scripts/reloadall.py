# Import des classes
import re
import sys
import os
import xbmcvfs

if ( __name__ == "__main__" ):
    try:
        # Parcours du repertoire pour connaitre les vues installees
        dirList=os.listdir(xbmc.translatePath('special://masterprofile/GlassNoxViews/'))
        # Recopie de chaque fichier present
        for fileName in dirList:
            # Test si le fichier a traiter est une Custom View
            if fileName.startswith("View_Custom"):
                # Suppression de l ancien fichier
                xbmcvfs.delete(xbmc.translatePath('special://skin/1080i/%s' % fileName))
                # Recopie du fichier sauvegarde
                retour = xbmcvfs.copy(xbmc.translatePath('special://masterprofile/GlassNoxViews/%s' % fileName), xbmc.translatePath('special://skin/1080i/%s' % fileName))
        # Tous les fichiers ont ete copies
        # On recharge le skin
        xbmc.executebuiltin( "ReloadSkin()")
    except:
        print("Erreur de recopie des custom views")
