# -*- coding:utf-8 -*-
# dpstreammovieslist version 0.2 par JUL1EN094
# dpstreamproperties version 0.2 par JUL1EN094
#---------------------------------------------------------------------
#Imports
import urllib, urllib2, sys, re, os
import getopt
import xbmc, xbmcgui, xbmcaddon
import cPickle as pickle
from traceback import print_exc 
#---------------------------------------------------------------------
#Web variables
URL_PREFIX   = 'http://dpstream.net/'
URL_SYNOPSIS = URL_PREFIX+'histoire.php?url='
URL_LIST     = URL_PREFIX+'fichiers/includes/inc_liste_film/fonction_liste_film.php?p='
USERAGENT    = "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.2.12) Gecko/20101031 Firefox/3.6.12 (.NET CLR 3.5.30729)"
#---------------------------------------------------------------------
#Addon variables
__addonID__  = "plugin.video.dpstream"
__addon__    = xbmcaddon.Addon(__addonID__)
__addonDir__ = __addon__.getAddonInfo( "path" )
#---------------------------------------------------------------------
#PurgeNoThumb Variables
purgeNoThumb = os.path.join(__addonDir__, 'resources', 'lib', 'purge_no_thumb.py')
#---------------------------------------------------------------------
#Cache variables
ADDON_DATA               = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )
cachedirectory           = os.path.join( ADDON_DATA, "cache")
CACHE_MOVIES_PATH        = os.path.join( cachedirectory,'movies')
CACHE_SERIES_PATH        = os.path.join( cachedirectory,'series_and_mangas' )
CACHE_LISTS_FILMS_PATH   = os.path.join( CACHE_MOVIES_PATH,'lists')
CACHE_INFOS_FILMS_PATH   = os.path.join( CACHE_MOVIES_PATH,'infos')
CACHE_LISTS_SERIES_PATH  = os.path.join( CACHE_SERIES_PATH,'lists')
CACHE_INFOS_SERIES_PATH  = os.path.join( CACHE_SERIES_PATH,'infos')
#---------------------------------------------------------------------
class dpstreampicture(object):
    def __init__(self, picture):
        self.basepicture    = picture
#         self.realPictureUrl = self.realPictureUrl()
#         self.isJpg          = self.is_jpg()
#         self.isGif          = self.is_gif()
#         self.isPng          = self.is_png() 

    def is_jpg(self,filename=False):
        if not filename :
            filename = self.basepicture
        is_jpg = False
        try :
            data = open(filename,'rb').read(2)
            if (data.startswith('\xff\xd8')) : 
                is_jpg = True
            else :
                is_jpg = False
        except :
            is_jpg = False
        print 'IS JPG : '+str(is_jpg)
        return is_jpg
    
    def is_gif(self,filename=False):
        if not filename :
            filename = self.basepicture        
        is_gif = False
        try :
            data = open(filename,'rb').read(3)
            if (data.startswith('GIF')) :
                is_gif = True
            else :
                is_gif = False
        except :
            is_gif = False
        print 'GIF : '+str(is_gif)
        return is_gif
    
    def is_png(self,filename=False):
        if not filename :
            filename = self.basepicture    
        is_png = False
        try :
            data = open(filename,'rb').read(8)
            if (data.startswith('\x89PNG\x0d\x0a\x1a\x0a')) :
                is_png = True
            else :
                is_png = False
        except :
            is_png = False
        print 'PNG : '+str(is_png)
        return is_png

class dpstreammovieslist(object):
    def __init__(self, genre='Tous', qualite='Toutes', classement='Alpha', alpha='Toutes', langue='Toutes', pays='Tous', host='Toutes', nbmaxmovies=10):
        print 'INIT MOVIESLIST CLASS'
        self.alpha_s      = ["Toutes", "0..9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        self.genre_s      = ['Tous', 'Documentaires', 'Spectacles', 'Action', 'Animation', 'Aventure', 'Biographie', 'Catastrophe', 'Comedie', 'Conte', 'Crime', 'Dessin anime', 'Drame', 'Espionnage', 'Fantastique', 'Guerre', 'Histoire', 'Horreur', 'Musical', 'Policier', 'Romance', 'Science-fiction', 'Sport', 'Thriller', 'Western' ]
        self.qualite_s    = ['Toutes', 'DVDRIP', 'CAM', 'TS', 'R5', 'HD']
        self.classement_s = ['Alpha', 'Chronologique', 'Annee', 'Note']
        self.langue_s     = ['Toutes', 'FR', 'VostFR']
        self.pays_s       = ['Tous', 'Afrique du Sud','Algerie','Allemagne','Argentine','Australie','Autriche','Belgique','Bresil','Bulgarie','Canada','Chine','Coree du Sud','Danemark','Espagne','Etats-Unis','Finlande','France','Hong Kong','Inde','Iran','Irlande','Islande','Israel','Italie','Japon','Lituanie','Malaisie','Maroc','Mexique','Nouvelle-Zelande','Norvege','Pays-Bas','Porto Rico','Pologne','Portugal','Quebec','Roumanie','Royaume-Uni','Russie','Suede','Suisse','Taiwan','Thailande','Turquie','Uruguay']
        self.host_s       = ['Toutes', 'Dailymotion', 'Youtube', 'StageVU', 'Veoh', 'PutLocker', 'MixtureVideo', 'PureVid']
        #init genre
        if genre in self.genre_s :
            self.genre = genre
        else :
            self.genre = 'Tous'
        #init pays
        if pays in self.pays_s :
            self.pays = pays
        else :
            self.pays = 'Tous'
        #init qualite
        if qualite in self.qualite_s :
            self.qualite = qualite
        else :
            self.qualite = 'Toutes'            
        #init classement
        if classement in self.classement_s :
            self.classement = classement
        else :
            self.classement = 'Alpha'           
        #init langue
        if langue in self.langue_s :
            self.langue = langue
        else :
            self.langue = 'Toutes'
        #init plateforme 
        if host in self.host_s :
            self.host = host
        else :
            self.host = 'Toutes'
        #init nbmovies
        if type(nbmaxmovies) == int :
            if 0 < nbmaxmovies :
                self.nbmaxmovies = nbmaxmovies
            else :
                self.nbmaxmovies = 10
        else :
            self.nbmaxmovies = 10
        # init alpha :
        if alpha in self.alpha_s :
            self.alpha = alpha
        else :
            self.alpha = 'Toutes'            
        # init url            
        self.url = self.getUrl()
        # init movieslist
        self.movieslist = self.getMoviesList()

    def getCachedInfos(self,movieId) :
        print 'GET CACHED MOVIE'
        urlcachemovie = os.path.join(CACHE_INFOS_FILMS_PATH, str(movieId))
        try:
            infos = pickle.load( open(urlcachemovie, "rb" ) )
            return infos
        except:
            return False
        else :
            return False

    def getMovieInfos(self, infos) :
        print 'GET MOVIE INFOS'
        cachedinfos = self.getCachedInfos(infos['id'])
        if not cachedinfos :        
            url   = URL_SYNOPSIS + infos['Syn']
            try :
                link1 = self.getWebContent(url,timeout=5)
                link  = link1.decode("iso-8859-1")
            except:
                link = ''
            ## Recuperation du resume du film ##
            regex ='<td class="td-syno-3"><center><b>.+?</center><br>(.+?)</td>'
            match=re.compile(regex).findall(link)
            if match:
                match[0]               = self.htmlDecode(match[0])
                match[0]               = match[0].encode("utf-8")
                infos['Plot']          = match[0]
            ## Recuperation de l'affiche ##
            regex = '<td class="td-syno-2"><img src="(.+?)" class="img-syno"></img></td>'
            match=re.compile(regex).findall(link)
            if match:
                match[0]               = self.htmlDecode(match[0])
                match[0]               = match[0].encode("utf-8") 
                RealPictureUrl         = self.getRealPictureUrl(match[0])  
                urlcacheicon           = os.path.join(CACHE_INFOS_FILMS_PATH, str(infos['id'])+'.jpg')
                try :
                    urllib.urlretrieve(RealPictureUrl,urlcacheicon)
                    isjpg = bool
                    isjpg = dpstreampicture(urlcacheicon).is_jpg
                    if isjpg :
                        infos['Thumb'] = urlcacheicon
                    elif not isjpg :
                        isgif = bool
                        isgif = dpstreampicture(urlcacheicon).is_gif
                        if isgif :
                            os.rename(urlcacheicon,urlcacheicon.replace('.jpg','.gif'))
                            infos['Thumb'] = urlcacheicon.replace('.jpg','.gif') 
                        elif not isgif :
                            ispng = bool
                            ispng = dpstreampicture(urlcacheicon).is_png
                            if ispng :
                                os.rename(urlcacheicon,urlcacheicon.replace('.jpg','.png'))
                                infos['Thumb'] = urlcacheicon.replace('.jpg','.png') 
                            elif not isjpg and not isgif and not ispng :
                                infos['Thumb'] = ''
                                os.remove(urlcacheicon)
                except:
                    print_exc()
                    infos['Thumb'] = ''                                              
            ## Recuperation du realisateur ##
            regex = '<b>R.alisateur : </b>(.+?)<br>'
            match=re.compile(regex).findall(link)
            if match:
                match[0]               = self.htmlDecode(match[0])
                match[0]               = match[0].encode("utf-8")                
                infos['Director']      = match[0].lstrip().rstrip()
            ## Recuperation des acteurs ##
            regex = '<b>Acteurs : </b>(.+?)<br>'
            match=re.compile(regex).findall(link)
            if match:
                match[0]               = self.htmlDecode(match[0])
                match[0]               = match[0].encode("utf-8")                
                infos['Cast']          = map(self.removeSpaces, match[0].replace('...','').split(','))
            ## Recuperation du genre ##
            regex = '<b> Genre : </b>(.+)'
            match=re.compile(regex).findall(link)
            if match:
                match[0]               = self.htmlDecode(match[0])
                match[0]               = match[0].encode("utf-8")                
                infos['Genre']         = match[0].lstrip().rstrip()
            ## Recuperation de l'annee ##
            regex = '<b> Ann.*e : </b>(.+)'
            match=re.compile(regex).findall(link)
            if match:
                match[0]               = self.htmlDecode(match[0])
                match[0]               = match[0].encode("utf-8") 
                infos['Year']          = match[0].lstrip().rstrip()
                if infos['Year'] != '' :
                    infos['Year']=int(infos['Year'])
            ## Recuperation de la Duree
            regex = '<b> Dur.*e : </b>(.+)'
            match = re.compile(regex).findall(link)
            if match:
                match[0]               = self.htmlDecode(match[0])
                match[0]               = match[0].encode("utf-8")           
                # Ameliorer le formatage du temps, voir si c'est ecrit: 1h20 ou 88 minutes ou 70 min etc
                infos['Duration']      = match[0].replace('min','').lstrip().rstrip()
            ## Recuperation du pays
            regex = '<b> Pays : </b>(.+)'
            match = re.compile(regex).findall(link)
            if match:
                match[0]               = self.htmlDecode(match[0])
                match[0]               = match[0].encode("utf-8")           
                infos['Country']       = match[0].lstrip()
            ## Recuperation du titre original
            regex = '<br>Titre original :(.+?)<br>'
            match = re.compile(regex).findall(link)
            if match:
                match[0]               = self.htmlDecode(match[0])
                match[0]               = match[0].encode("utf-8")                
                infos['OriginalTitle'] = match[0].lstrip().rstrip()
            ## Set cachedinfos
            if link != '':
                print 'INFOS : '+str(infos)
                self.setCachedInfos(infos)
            return infos 
        elif cachedinfos :
            print 'CACHEDINFOS : '+str(cachedinfos)
            return cachedinfos
    
    def getMoviesList(self) :
        print 'GET MOVIES LIST'
        soup       = self.getWebContent(self.url, timeout=60)
        html       = soup.decode("iso-8859-1")
        html       = html.replace("\n", "")
        pattern    = u'<tr valign="center"(.+?)</tr>'
        movies     = re.compile(pattern).findall(html)
        movieslist = []
        n          = 0
        print "TEST 1"
        for film in movies :
            if n < self.nbmaxmovies :
                print "N = "+str(n)
                moviedict          = {}
                pattern_vote       = u'<span id="sp1">(.+?)</span>.+? \| (.+?) votes</span>'
                pattern_synopsys   = u'onmouseover="montre\(\'(.+?)\'\);" onmouseout="cache\(\);" href="(.+?)">(.+?)</a></td>'
                synopsis           = re.compile(pattern_synopsys).findall(film)[0]
                vote               = re.compile(pattern_vote).findall(film)[0]
                movie_info         = synopsis + vote
                moviedict['Syn']   = movie_info[0]
                moviedict['url']   = movie_info[1]
                moviedict['id']    = str(hash(movie_info[1]))
                moviedict['Title'] = self.htmlDecode(movie_info[2]).encode('utf-8')
                try :
                    moviedict['Rating'] = float(movie_info[3])
                except :
                    moviedict['Rating'] = 0
                try:
                    moviedict['Votes']  = movie_info[4]
                except :
                    moviedict['Votes']  = 0            
                print 'TEST2'
                movieslist.append(self.getMovieInfos(moviedict))
                n += 1
        return movieslist    

    def getRealPictureUrl(self,url):
        # Mixture images provider
        if re.search('mixture',url) :
            RealPictureUrl = self.getUrlRedirect(url,url,1)
        # Casimage images providers
        elif re.search('casimage',url): 
            try :
                soup              = getWebContent(url,timeout=1)
                html              = soup.decode('iso-8859-1')
                spoonyalamontagne = common.parseDOM(html,'td',attrs={'id':'spoonyalamontagne'}) [0]
                RealPictureUrl    = common.parseDOM(spoonyalamontagne,'img',ret='src') [0]   
            except :
                RealPictureUrl    = url
        # Quebec-Team images provider
        elif re.search('quebec-team',url): 
            try :
                soup              = getWebContent(url,timeout=1)
                html              = soup.decode('iso-8859-1')
                RealPictureUrl    = re.findall(u'.*img=(.*)',url) [0]
            except :
                RealPictureUrl    = url            
        # All other images provider
        else :
            RealPictureUrl = url
        return RealPictureUrl
    
    def getUrl(self) :
        url = URL_LIST
        # Plateforme
        url = url + str(self.host_s.index(self.host))
        # Alpha - lettre
        url = url + '-' + str(self.alpha_s.index(self.alpha))
        # 0 + Genre
        url = url + '-0-' + str(self.genre_s.index(self.genre))
        # Classement
        if self.classement == 'Chronologique' :
            url = url + '-1-0-0'
        elif self.classement == 'Annee' :
            url = url + '-0-1-0'
        elif self.classement == 'Note' :
            url = url + '-0-0-1'
        else :
            url = url + '-0-0-0'
        # Langue
        url = url + '-' + str(self.langue_s.index(self.langue))
        # Qualite
        url = url + '-' + str(self.qualite_s.index(self.qualite))
        # Pays
        url = url + '-' + str(self.pays_s.index(self.pays))
        return url

    def getUrlRedirect(self,url,referer = 'http://www.dpstream.net/',timeout=3):
        req  = urllib2.Request(url)
        req.add_header('User-Agent',USERAGENT)           
        req.add_header('Referer',referer)    
        try :
            f = urllib2.urlopen(req,timeout=timeout)
            RedirectUrl = f.geturl()
            f.close()
        except : 
            RedirectUrl = url
        return RedirectUrl
    
    def getWebContent(self, url, referer='http://www.dpstream.net/',timeout=3):
        request = urllib2.Request(url)
        request.add_header('User-Agent', USERAGENT)
        request.add_header('Host','dpstream.net')
        request.add_header('Cookie','PHPSESSID=true; cookie_test=true; cookie_pub=true; __utma=true; 7tagacc=1; __utmb=true; sdp_cache=true; sdp_png=true; sdp_etag=true; session_id_php_dp=true; __utmc=true; __utmz=true.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)')
        request.add_header('Referer',referer) 
        response = urllib2.urlopen(request, timeout=timeout)
        return response.read()    
    
    def htmlDecode(self,text):
        text = text.replace(u"&eacute;",u"é")
        text = text.replace(u"&egrave;",u"è")
        text = text.replace(u"&ecirc;",u"ê")
        text = text.replace(u"&quot;",u"\"")
        text = text.replace(u"&#039;",u"'")
        text = text.replace(u"&agrave;",u"à")
        text = text.replace(u"&acirc;",u"â")
        text = text.replace(u"&iuml;",u"ï")
        text = text.replace(u"&ocirc;",u"ô")
        text = text.replace(u"&deg;",u"°")
        text = text.replace(u"&amp;",u"&")
        text = text.replace(u"&#39;",u"'")
        text = text.replace(u"%27",u"'")
        text = text.replace(u"<b>",u"")
        text = text.replace(u"</b>",u"")
        text = text.replace(u"<i>",u"")
        text = text.replace(u"</i>",u"")
        text = text.replace(u"<br>",u"\n")
        text = text.replace(u"<em>",u"")
        text = text.replace(u"</em>",u"")
        return text
        
    def removeSpaces(self,text):
        return text.lstrip().rstrip()

    def setCachedInfos(self,infos) :
        print 'SET MOVIE INFOS'
        urlcachemovie = os.path.join(CACHE_INFOS_FILMS_PATH, str(infos['id']))
        if not os.path.exists(urlcachemovie):
            try:        
                file(urlcachemovie, 'w')
                pickle.dump(infos,open(urlcachemovie, "wb" ))
            except :
                print_exc()        

class dpstreamproperties(object) :
    def __init__(self, dpstreammovieslist={}, basepropname='DPStreamMoviesList', window=10000):
        print 'INIT PROP CLASS'
        #init dpstreammovieslist
        self.dpstreammovieslist = dpstreammovieslist
        #init basepropname
        self.basepropname       = str(basepropname)
        #init window
        self.window             = xbmcgui.Window(int(window))
        #init nbmovies
        if len(dpstreammovieslist) == 0 :
            self.nbmovies       = 0
        elif len(dpstreammovieslist) > 0 :
            self.nbmovies       = len(dpstreammovieslist)
        
        self.clear_properties()
        self.set_properties()
        
    def clear_properties(self) :
        print 'CLEAR PROP'
        # Boucle Clear Properties
        i = 0
        isProp = True
        while isProp :
            i += 1
            if self.window.getProperty(str(self.basepropname)+'.Title.'+str(i)) :
                if self.window.getProperty(str(self.basepropname)+'.Title.'+str(i)) : 
                    self.window.clearProperty(str(self.basepropname)+'.Title.'+str(i))
                if self.window.getProperty(str(self.basepropname)+'.Rating.'+str(i)) : 
                    self.window.clearProperty(str(self.basepropname)+'.Rating.'+str(i))
                if self.window.getProperty(str(self.basepropname)+'.Votes.'+str(i)) : 
                    self.window.clearProperty(str(self.basepropname)+'.Votes.'+str(i))
                if self.window.getProperty(str(self.basepropname)+'.Thumb.'+str(i)) : 
                    self.window.clearProperty(str(self.basepropname)+'.Thumb.'+str(i))
                if self.window.getProperty(str(self.basepropname)+'.Plot.'+str(i)) : 
                    self.window.clearProperty(str(self.basepropname)+'.Plot.'+str(i))
                if self.window.getProperty(str(self.basepropname)+'.url.'+str(i)) : 
                    self.window.clearProperty(str(self.basepropname)+'.url.'+str(i))
                if self.window.getProperty(str(self.basepropname)+'.Country.'+str(i)) : 
                    self.window.clearProperty(str(self.basepropname)+'.Country.'+str(i))
                if self.window.getProperty(str(self.basepropname)+'.Duration.'+str(i)) : 
                    self.window.clearProperty(str(self.basepropname)+'.Duration.'+str(i))
                if self.window.getProperty(str(self.basepropname)+'.Syn.'+str(i)) : 
                    self.window.clearProperty(str(self.basepropname)+'.Syn.'+str(i))
                if self.window.getProperty(str(self.basepropname)+'.Director.'+str(i)) : 
                    self.window.clearProperty(str(self.basepropname)+'.Director.'+str(i))
                if self.window.getProperty(str(self.basepropname)+'.Cast.'+str(i)) : 
                    self.window.clearProperty(str(self.basepropname)+'.Cast.'+str(i))
                if self.window.getProperty(str(self.basepropname)+'.Year.'+str(i)) : 
                    self.window.clearProperty(str(self.basepropname)+'.Year.'+str(i))
                if self.window.getProperty(str(self.basepropname)+'.Genre.'+str(i)) : 
                    self.window.clearProperty(str(self.basepropname)+'.Genre.'+str(i))
                if self.window.getProperty(str(self.basepropname)+'.OriginalTitle.'+str(i)) : 
                    self.window.clearProperty(str(self.basepropname)+'.OriginalTitle.'+str(i))
            else :
                isProp = False
        if self.window.getProperty(str(self.basepropname)+'.nbmaxmovies') : 
                    self.window.clearProperty(str(self.basepropname)+'.nbmaxmovies')  
                    
    def set_properties(self):  
        print 'SET PROP'
        # Set Properties
        self.window.setProperty(str(self.basepropname)+'.nbmaxmovies', str(self.nbmovies))
        index  = 0
        for movie in self.dpstreammovieslist :
            index += 1
            for info, value in movie.items() :
                print str(self.basepropname)+'.'+str(info)+'.'+str(index)+' : '+str(value)
                self.window.setProperty(str(self.basepropname)+'.'+str(info)+'.'+str(index), str(value))    

def main() :
    # gestion des arguments
    basepropname = 'DPStreamMoviesList' #class dpstreamproperties 
    windowprop   = 10000                #class dpstreamproperties
    genre        = 'Tous'               #class dpstreammovieslist
    qualite      = 'Toutes'             #class dpstreammovieslist
    classement   = 'Alpha'              #class dpstreammovieslist
    alpha        = 'Toutes'             #class dpstreammovieslist
    langue       = 'Toutes'             #class dpstreammovieslist
    pays         = 'Tous'               #class dpstreammovieslist
    host         = 'Toutes'             #class dpstreammovieslist
    nbmaxmovies  = 10                   #class dpstreammovieslist
    show         = False                #class dpstreammovieslist
    if len(sys.argv) > 1 :
        opts, args = getopt.getopt(sys.argv[1:], "b:g:q:c:a:l:p:h:n:w:s", ["basepropname=", "genre=", "qualite=", "classement", "alpha=", "langue=", "pays=", "host=", "nbmaxmovies=","windowprop=", "show"])
        for opt, arg in opts :
            if opt in ('-g','--genre'):
                genre = arg.lstrip('=')
            elif opt in ('-b','--basepropname'):
                basepropname = arg.lstrip('=')                
            elif opt in ('-q','--qualite'):
                qualite = arg.lstrip('=')
            elif opt in ('-c','--classement'):
                classement = arg.lstrip('=')
            elif opt in ('-a','--alpha'):
                alpha = arg.lstrip('=')
            elif opt in ('-l','--langue'):
                langue = arg.lstrip('=') 
            elif opt in ('-p','--pays'):
                pays = arg.lstrip('=') 
            elif opt in ('-h','--host'):
                host = arg.lstrip('=') 
            elif opt in ('-n','--nbmaxmovies'):
                nbmaxmovies = int(arg.lstrip('=')) 
            elif opt in ('-w','--windowprop'):
                windowprop = int(arg.lstrip('='))                 
            elif opt in ('-s','--show'):
                show = True                
    # Purge no thumb infos :
    xbmc.executebuiltin('XBMC.RunScript('+purgeNoThumb+' --dialog="no")')        
    
    # Get_movieslist --> Appel à la class dpstreammovieslist
    x = dpstreammovieslist(genre,qualite,classement,alpha,langue,pays,host,nbmaxmovies)
    print str(x.movieslist)
    
    # output/print
    if show :
        for movie in x.movieslist :
            print '-------------'
            for info, value in movie.items() :
                print str(info)+' : '+str(value)
    
    # Set_properties --> Appel à la class dpstreamproperties
    dpstreamproperties(x.movieslist,str(basepropname),int(windowprop))

if __name__ == "__main__":
    try :
        main()       
    except :
        print_exc()
