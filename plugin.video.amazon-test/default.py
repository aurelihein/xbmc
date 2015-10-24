#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from __future__ import unicode_literals
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup, Tag, NavigableString
from datetime import date
from pyDes import *
import uuid
import cookielib
import mechanize
import sys
import urllib
import urllib2
import re
import os
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
import urlparse
import base64
import binascii
import hmac
import time
import random
import subprocess
import hashlib
import hmac

try: from demjson import demjson
except: import demjson
try: from sqlite3 import dbapi2 as sqlite
except: from pysqlite2 import dbapi2 as sqlite
    
addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
__plugin__ = addon.getAddonInfo('name')
__authors__ = addon.getAddonInfo('author')
__credits__ = ""
__version__ = addon.getAddonInfo('version')
ProfilPath = xbmc.translatePath('special://masterprofile/').decode('utf-8')
PluginPath = addon.getAddonInfo('path').decode('utf-8')
DataPath = xbmc.translatePath('special://profile/addon_data/' + addon.getAddonInfo('id')).decode('utf-8')
HomePath = xbmc.translatePath('special://home').decode('utf-8')
userinput = os.path.join(PluginPath, 'tools', 'userinput.exe' )
waitsec = int(addon.getSetting("clickwait")) * 1000
waitprepin = int(addon.getSetting("waitprepin")) * 1000
pin = addon.getSetting("pin")
waitpin = int(addon.getSetting("waitpin")) * 1000
tvdb_art = addon.getSetting("tvdb_art")
tmdb_art = addon.getSetting("tmdb_art")
showfanart = addon.getSetting("useshowfanart")
dispShowOnly = addon.getSetting("disptvshow")
MaxResults = int(addon.getSetting("items_perpage")) 
osLinux = xbmc.getCondVisibility('system.platform.linux')
osOsx = xbmc.getCondVisibility('system.platform.osx')
osWin = xbmc.getCondVisibility('system.platform.windows')
screenWidth = int(xbmc.getInfoLabel('System.ScreenWidth'))
screenHeight = int(xbmc.getInfoLabel('System.ScreenHeight'))
playPlugin = ['plugin.program.browser.launcher', 'plugin.program.chrome.launcher']
selPlugin = playPlugin[int(addon.getSetting("playmethod"))]
tmdb = base64.b64decode('YjM0NDkwYzA1NmYwZGQ5ZTNlYzlhZjIxNjdhNzMxZjQ=')
tvdb = base64.b64decode('MUQ2MkYyRjkwMDMwQzQ0NA==')
CookieFile = os.path.join(DataPath, 'cookies.lwp')
DefaultFanart = os.path.join(PluginPath, 'fanart.jpg')
country = int(addon.getSetting("country"))
BaseUrl = 'https://www.amazon.' + ['de', 'co.uk', 'com', 'co.jp'][country]
ATVUrl = 'https://atv-ps%s.amazon.com' % ['-eu', '-eu', '', '-fe'][country]
MarketID = ['A1PA6795UKMFR9', 'A1F83G8C2ARO7P', 'ATVPDKIKX0DER', 'A1VC38T7YXB528'][country]
Language = ['de', 'en', 'en', 'jp'][country]
menuFile = os.path.join(DataPath, 'menu-%s.json' % MarketID)
na = 'not available'
LogFile = True
UserAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2532.0 Safari/537.36'
watchlist = 'wl'
library = 'yvl'

#ids: A28RQHJKHM2A2W - ps3 / AFOQV1TK6EU6O - ps4 / A1IJNVP3L4AY8B - samsung / A2E0SNTXJVT7WK - bueller / 
#     ADVBD696BHNV5 - montoya / A3VN4E5F7BBC7S - roku / A1MPSLFC7L5AFK - kindle
TypeIDs = {'GetCategoryList': 'firmware=fmw:15-app:1.1.23&deviceTypeID=A1MPSLFC7L5AFK', 
                       'All': 'firmware=fmw:045.01E01164A-app:4.7&deviceTypeID=A3VN4E5F7BBC7S'}
langID = {'movie':30165, 'series':30166, 'season':30167, 'episode':30173}
OfferGroup = 'OfferGroups=B0043YVHMY'
Dialog = xbmcgui.Dialog()
pDialog = xbmcgui.DialogProgress()

if (addon.getSetting('enablelibraryfolder') == 'true'):
    MOVIE_PATH = os.path.join(xbmc.translatePath(addon.getSetting('customlibraryfolder')),'Movies').decode('utf-8')
    TV_SHOWS_PATH = os.path.join(xbmc.translatePath(addon.getSetting('customlibraryfolder')),'TV').decode('utf-8')
else:
    MOVIE_PATH = os.path.join(DataPath,'Movies')
    TV_SHOWS_PATH = os.path.join(DataPath,'TV')

def setView(content, view=False, updateListing=False):
    # 501-POSTER WRAP 503-MLIST3 504=MLIST2 508-FANARTPOSTER
    if content == 'movie': 
        ctype = 'movies'
        cview = 'movieview'
    elif content == 'series': 
        ctype = 'tvshows'
        cview = 'showview'
    elif content == 'season': 
        ctype = 'tvshows'
        cview = 'seasonview'
    elif content == 'episode': 
        ctype = 'episodes'
        cview = 'episodeview'

    confluence_views = [500,501,502,503,504,508,-1]
    xbmcplugin.setContent(pluginhandle, ctype)
    viewenable = addon.getSetting("viewenable")
    if viewenable == 'true' and view:
        viewid = confluence_views[int(addon.getSetting(cview))]
        if viewid == -1:
            viewid = int(addon.getSetting(cview.replace('view', 'id')))
        xbmc.executebuiltin('Container.SetViewMode(%s)' % viewid)
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=updateListing)
    
def getURL( url, host=BaseUrl.split('//')[1], useCookie=False, silent=False, headers=None):
    cj = cookielib.LWPCookieJar()
    if useCookie and os.path.isfile(CookieFile):
        cj.load(CookieFile, ignore_discard=True, ignore_expires=True)
    Log('getURL: '+url)
    if not headers: headers = [('User-Agent', UserAgent ), ('Host', host)]
    try:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj),urllib2.HTTPRedirectHandler)
        opener.addheaders = headers
        usock = opener.open(url)
        response = usock.read()
        usock.close()
    except urllib2.URLError, e:
        Log('Error reason: %s' % e, xbmc.LOGERROR)
        return False
    return response
    
def getATVData(mode, query='', version=2, useCookie=True):
    if '?' in query: query = query.split('?')[1]
    if query:
        query = '&IncludeAll=T&AID=T&' + query
    if TypeIDs.has_key(mode): deviceTypeID = TypeIDs[mode]
    else: deviceTypeID = TypeIDs['All']
    if not '/' in mode: mode = 'catalog/' + mode
    parameter = '%s&deviceID=%s&format=json&version=%s&formatVersion=3&marketplaceId=%s' % (deviceTypeID, deviceID, version, MarketID)
    data = getURL('%s/cdp/%s?%s%s' % (ATVUrl, mode, parameter, query), useCookie=useCookie)
    if not data: return None
    jsondata = demjson.decode(data)
    if jsondata['message']['statusCode'] != "SUCCESS":
        Log('Error Code: ' + jsondata['message']['body']['code'], xbmc.LOGERROR)
        return None
    return jsondata['message']['body']
    
def addDir(name, mode, url='', infoLabels=None, opt='', catalog='Browse', cm=False, page=1, export=False):
    if type(url) == type(unicode()): url = url.encode('utf-8')
    u = u'%s?mode=%s&url=%s&page=%s&opt=%s&cat=%s' % (sys.argv[0], mode, urllib.quote_plus(url), page, opt, catalog)
    if infoLabels:
        thumb = infoLabels['Thumb']
        fanart = infoLabels['Fanart']
    else: fanart = thumb = DefaultFanart
    if export:
        Export(infoLabels, u)
        return
    item=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=thumb)
    item.setProperty('fanart_image',fanart)
    item.setProperty('IsPlayable', 'false')
    if infoLabels and infoLabels.has_key('TotalSeasons'):
        item.setProperty('TotalSeasons', str(infoLabels['TotalSeasons']))
    if infoLabels: item.setInfo(type='Video', infoLabels=infoLabels)
    if cm: item.addContextMenuItems(cm, replaceItems=False)
    xbmcplugin.addDirectoryItem(pluginhandle, u, item, isFolder=True)

def addVideo(name, asin, infoLabels, cm=[], export=False):
    u  = '%s?asin=%s&mode=PlayVideo&name=%s&adult=%s' % (sys.argv[0], asin, urllib.quote_plus(name.encode('utf-8')), infoLabels['isAdult'])

    item = xbmcgui.ListItem(name, thumbnailImage=infoLabels['Thumb'])
    item.setProperty('fanart_image', infoLabels['Fanart'])
    if infoLabels.has_key('Poster'): item.setArt({'tvshow.poster': infoLabels['Poster']})
    else: item.setArt({'poster': infoLabels['Thumb']})
    item.setProperty('IsPlayable', 'false')
    
    if infoLabels['isHD']:
        item.addStreamInfo('video', { 'width':1280 ,'height' : 720 })
    else:
        item.addStreamInfo('video', { 'width':720 ,'height' : 480 })
    if infoLabels['AudioChannels']: item.addStreamInfo('audio', { 'codec': 'ac3' ,'channels': int(infoLabels['AudioChannels']) })
    if infoLabels['TrailerAvailable']:
        infoLabels['Trailer'] = u + '&trailer=1&selbitrate=0'
    u += '&trailer=0&selbitrate=0'
    if export:
        Export(infoLabels, u)
    else:
        cm.insert(0, (getString(30101), 'Action(ToggleWatched)') )
        item.setInfo(type='Video', infoLabels=infoLabels)
        item.addContextMenuItems( cm , replaceItems=False )
        xbmcplugin.addDirectoryItem(pluginhandle, u, item, isFolder=False)
    
def MainMenu():
    loadCategories()
    cm_wl = [(getString(30185) % 'Watchlist', 'XBMC.RunPlugin(%s?mode=getList&url=%s&export=1)'  % (sys.argv[0], watchlist) )]
    cm_lb = [(getString(30185) % getString(30100), 'XBMC.RunPlugin(%s?mode=getList&url=%s&export=1)'  % (sys.argv[0], library) )]
    addDir('Watchlist', 'getList', watchlist, cm=cm_wl)    
    addDir(getString(30104), 'listCategories', "[0]", opt=30143)
    addDir(getString(30107), 'listCategories', "[1]", opt=30160)
    addDir(getString(30108), 'Search', '')
    addDir(getString(30100), 'getList', library, cm=cm_lb)
    xbmcplugin.endOfDirectory(pluginhandle, updateListing=False)
    
def Search():
    keyboard = xbmc.Keyboard('')
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        searchString=keyboard.getText().strip()
        if searchString:
            url = '%s&searchString=%s' % (OfferGroup, urllib.quote_plus(searchString))
            listContent('Search', url, 1, 'search')

def loadCategories(force=False):
    if os.path.exists(menuFile) and not force:
        ftime = os.path.getmtime(menuFile)
        ctime = time.time()
        if ctime - ftime < 3 * 3600:
            return demjson.decode_file(menuFile)

    data = getATVData('GetCategoryList')
    json = []
    if country < 2:
        json.append(data['categories'][2]['categories'][0]['categories'])
        json.append(data['categories'][3]['categories'][0]['categories'])
    else:
        json.append(data['categories'][2]['categories'][2]['categories'])
        json.append(data['categories'][3]['categories'][2]['categories'])
    demjson.encode_to_file(menuFile, json, overwrite=True)
    return json

def listCategories(path, root=None):
    data = loadCategories()
    exec 'cat = data' + path.__str__()
    if root:
        url = OfferGroup + '&OrderBy=Title&ContentType='
        if root == '30160': url += 'TVSeason&RollupToSeries=T'
        else: url += 'Movie'
        addDir(getString(int(root)), 'listContent', url)
    for pos, item in enumerate(cat):
        mode = None
        opt = ''
        if not item.has_key('title'): continue
        name = item['title']
        if item.has_key('categories'):
            mode = 'listCategories'
            url = "%s[%s]['categories']" % (path, pos)
        elif item.has_key('query'):
            mode = 'listContent'
            opt = 'listcat'
            url = item['query'].replace('RollupToSeason', 'RollupToSeries').replace('\n','').replace("\n",'')
        if mode:
            addDir(name, mode, url, opt=opt)
    xbmcplugin.endOfDirectory(pluginhandle)

def listContent(catalog, url, page, parent, export=False):
    oldurl = url
    page = int(page)
    ResPage = MaxResults
    if export: ResPage = 250
    url += '&NumberOfResults=%s&StartIndex=%s' % (ResPage+1, (page-1)*ResPage)
    
    if page != 1 and not export:
        addDir(' --= %s =--' % (getString(30112) % int(page-1)), 'listContent', oldurl, page=page-1, catalog=catalog, opt=parent)
    titles = getATVData(catalog, url)
    if not titles or not len(titles['titles']):
        if parent == 'search': Dialog.ok(__plugin__, getString(30202))
        else: Dialog.ok(__plugin__, getString(30127))
        return
    titles = titles['titles']
    for item in titles[0:ResPage]:
        mode = None
        if not item.has_key('title'): continue
        contentType, infoLabels = getInfos(item)
        name = infoLabels['Title']
        if infoLabels.has_key('DisplayTitle'): name = infoLabels['DisplayTitle']
        asin = item['titleId']
        cm = []
        wlmode = 0
        if parent == watchlist: wlmode = 1
        cm.append((getString(wlmode+30180) % getString(langID[contentType]), 'XBMC.RunPlugin(%s?mode=WatchList&url=%s&opt=%s)'  % (sys.argv[0], asin, wlmode )))
        cm.append((getString(30185) % getString(langID[contentType]), 'XBMC.RunPlugin(%s?mode=getList&url=%s&export=1)'  % (sys.argv[0], asin)))
        cm.append((getString(30186), 'XBMC.RunPlugin(%s?mode=UpdateLibrary)' % sys.argv[0]))
        name = cleanTitle(name)
        if contentType == 'movie' or contentType == 'episode':
            addVideo(name, asin, infoLabels, cm, export)
        else:
            mode = 'listContent'
            url = item['childTitles'][0]['feedUrl']
            if contentType == 'season': 
                name = formatSeason(infoLabels, parent)
                if parent != library and parent != '':
                    curl = 'SeriesASIN=%s&ContentType=TVEpisode&RollupToSeason=T&IncludeBlackList=T&%s' % (infoLabels['SeriesAsin'], OfferGroup)
                    cm.insert(0, (getString(30182), 'XBMC.Container.Update(%s?mode=listContent&cat=Browse&url=%s&page=1)' % (sys.argv[0], urllib.quote_plus(curl))))

            if export:
                url = re.sub(r'contentype=\w+', 'ContentType=TVEpisode', url, flags=re.IGNORECASE)
                url = re.sub(r'&rollupto\w+=\w+', '', url, flags=re.IGNORECASE)
                listContent('Browse', url, 1, '', export)
            else:
                addDir(name, mode, url, infoLabels, cm=cm, export=export)
    if len(titles) > ResPage:
        if export:
            listContent(catalog, oldurl, page+1, parent, export)
        else:
            addDir(' --= %s =--' % (getString(30111) % int(page+1)), 'listContent', oldurl, page=page+1, catalog=catalog, opt=parent)
    if not export: setView(contentType, True)

def cleanTitle(title):
    if title.isupper():
        title = title.title().replace('[Ov]', '[OV]').replace('Bc', 'BC')
    title = title.replace(u'\u2013', '-').replace(u'\u00A0', ' ').replace('[dt./OV]', '')
    return title.strip()
    
def Export(infoLabels, url):
    content = infoLabels['contentType']
    ExportPath = TV_SHOWS_PATH
    language = 'ger'
    
    if content == 'movie':
        isEpisode = False
        ExportPath = MOVIE_PATH
        nfoType = 'movie'
        title = infoLabels['Title']
    else:
        isEpisode = True
        title = infoLabels['TVShowTitle']
        
    tl = title.lower()
    if '[omu]' in tl or '[ov]' in tl or ' omu' in tl: language = ''
    filename = re.sub(r'\[.*| omu| ov', '', title, flags=re.IGNORECASE).strip()
    
    if isEpisode:
        infoLabels['TVShowTitle'] = filename
        ExportPath = os.path.join(ExportPath, cleanName(filename))
        nfoType = 'episodedetails'
        CreateDirectory(ExportPath)
        filename = 'S%02dE%02d - %s' % (infoLabels['Season'], infoLabels['Episode'], infoLabels['Title'])
    else:
        if infoLabels['Year']: filename = '%s (%s)' % (filename, infoLabels['Year'])
        
    CreateInfoFile(filename, ExportPath, nfoType, infoLabels, language)
    SaveFile(filename + '.strm', url, ExportPath)
    Log('Export: ' + filename)
    
def WatchList(asin, remove):
    action = 'add'
    if remove: action = 'remove'
    url = BaseUrl + '/gp/video/watchlist/?toggleOnWatchlist=1&action=%s&ASIN=%s' % (action, asin)
    data = getURL(url, useCookie=True)
    if asin in data:
        Log(asin + ' added')
    else:
        Log(asin + ' removed')
        xbmc.executebuiltin('Container.Refresh')

def getArtWork(infoLabels, contentType):
    if contentType == 'movie' and tmdb_art == '0': return
    if contentType != 'movie' and tvdb_art == '0': return
    c = db.cursor()
    extra = ''
    season = -2
    asins = infoLabels['Asins']
    infoLabels['Banner'] = None
    if contentType == 'series': season = -1
    if contentType == 'season' or contentType == 'episode': asins = infoLabels['SeriesAsin']
    if infoLabels.has_key('Season'): season = int(infoLabels['Season'])
    if season > -2: extra = ' and season = %s' % season
    for asin in asins.split(','):
        result = c.execute('select poster,fanart,banner from art where asin like (?)' + extra, ('%' + asin + '%',)).fetchone()
        if result:
            if result[0] and contentType != 'episode' and result[0] != na: infoLabels['Thumb'] = result[0]
            if result[0] and contentType != 'movie' and result[0] != na: infoLabels['Poster'] = result[0]
            if result[1] and result[1] != na: infoLabels['Fanart'] = result[1]
            if result[2] and result[2] != na: infoLabels['Banner'] = result[2]
            if season > -1:
                result = c.execute('select poster, fanart from art where asin like (?) and season = -1', ('%' + asin + '%',)).fetchone()
                if result:
                    if result[0] and result[0] != na and contentType == 'episode' : infoLabels['Poster'] = result[0]
                    if result[1] and result[1] != na and showfanart == 'true': infoLabels['Fanart'] = result[1]
            return infoLabels
        elif season > -1 and showfanart == 'true':
            result = c.execute('select poster,fanart from art where asin like (?) and season = -1', ('%' + asin + '%',)).fetchone()
            if result:
                if result[0] and result[0] != na and contentType == 'episode' : infoLabels['Poster'] = result[0]
                if result[1] and result[1] != na: infoLabels['Fanart'] = result[1]
                
    c.close()
    if contentType != 'episode':
        title = infoLabels['Title']
        if contentType == 'season': title = infoLabels['TVShowTitle']
        if type(title) == type(unicode()): title = title.encode('utf-8')
        xbmc.executebuiltin('RunPlugin(%s?mode=loadArtWork&asins=%s&title=%s&year=%s&ct=%s)' % (sys.argv[0], urllib.quote_plus(asins), urllib.quote_plus(title), infoLabels['Year'], contentType))
    return infoLabels
    
def loadArtWork(asins, title, year, contentType):
    seasons = None
    season_number = None
    poster = None
    fanart = None
    title = title.lower().replace('?', '').replace('omu', '').split('(')[0].split('[')[0].strip()

    if contentType == 'movie':
        fanart = getTMDBImages(title, year=year)
    if contentType == 'season' or contentType == 'series':
        seasons, poster, fanart = getTVDBImages(title)
        if not fanart: fanart = getTMDBImages(title, content='tv')
        season_number = -1
        content = getATVData('GetASINDetails', 'ASINList='+asins)['titles'][0]
        asins = getAsins(content, False)
        del content

    cur = db.cursor()
    cur.execute('insert or ignore into art values (?,?,?,?,?,?)', (asins, season_number, poster, None, fanart, date.today()))
    if seasons:
        for season, url in seasons.items():
            cur.execute('insert or ignore into art values (?,?,?,?,?,?)', (asins, season, url, None, None, date.today()))
    db.commit()
    cur.close()
                    
def getTVDBImages(title, imdb=None, id=None):
    posterurl = fanarturl = None
    splitter = [' - ', ': ', ', ']
    if country == 0 or country == 3:
        langcodes = [Language, 'en']
    else: langcodes = ['en']
    TVDB_URL = 'http://www.thetvdb.com/banners/'
    while not id:
        tv = urllib.quote_plus(title)
        result = getURL('http://www.thetvdb.com/api/GetSeries.php?seriesname=%s&language=%s' % (tv, Language), silent=True)
        soup = BeautifulSoup(result)
        id = soup.find('seriesid')
        if id:
            id = id.string
        else:
            oldtitle = title
            for splitchar in splitter:
                if title.count(splitchar):
                    title = title.split(splitchar)[0]
                    break
            if title == oldtitle:
                break
    if not id: return None, None, None
    soup = BeautifulSoup(getURL('http://www.thetvdb.com/api/%s/series/%s/banners.xml' % (tvdb, id), silent=True))
    seasons = {}
    for lang in langcodes:
        for datalang in soup.findAll('language'):
            if datalang.string == lang:
                data = datalang.parent
                if data.bannertype.string == 'fanart' and not fanarturl: fanarturl = TVDB_URL + data.bannerpath.string
                if data.bannertype.string == 'poster' and not posterurl: posterurl = TVDB_URL + data.bannerpath.string
                if data.bannertype.string == data.bannertype2.string == 'season':
                    snr = data.season.string
                    if not seasons.has_key(snr):
                        seasons[snr] = TVDB_URL + data.bannerpath.string
    return seasons, posterurl, fanarturl

def getTMDBImages(title, imdb=None, content='movie', year=None):
    fanart = poster = id = None
    splitter = [' - ', ': ', ', ']
    TMDB_URL = 'http://image.tmdb.org/t/p/original'
    yearorg = year

    while not id:
        str_year = ''
        if year: str_year = '&year=' + str(year)
        movie = urllib.quote_plus(title)
        result = getURL('http://api.themoviedb.org/3/search/%s?api_key=%s&language=%s&query=%s%s' % (content, tmdb, Language, movie, str_year), silent=True)
        if not result:
            Log('Fanart: Pause 5 sec...')
            xbmc.sleep(5000)
            continue
        data = demjson.decode(result)
        if data['total_results'] > 0:
            result = data['results'][0]
            if result['backdrop_path']: fanart = TMDB_URL + result['backdrop_path']
            if result['poster_path']: poster = TMDB_URL + result['poster_path']
            id = result['id']
        elif year:
            year = 0
        else:
            year = yearorg
            oldtitle = title
            for splitchar in splitter:
                if title.count(splitchar):
                    title = title.split(splitchar)[0]
                    break
            if title == oldtitle:
                break
    if content == 'movie' and id and not fanart:
        fanart = na
    return fanart

def formatSeason(infoLabels, parent):
    name = ''
    season = infoLabels['Season']
    if parent:
        name = infoLabels['TVShowTitle'] + ' - '
    if season != 0 and len(str(season)) < 3: name += getString(30167, True) + ' ' + str(season)
    elif len(str(season)) > 2: name += getString(30168, True) + str(season)
    else: name += getString(30169, True)
    return cleanTitle(name)
    
def getList(list, export):
    extraArgs = ''
    if not os.path.isfile(CookieFile):
        MechanizeLogin()
    if list == watchlist or list == library:
        asins_tv = scrapAsins('/gp/aw/%s/?filter=tv&pageSize=1000&sortBy=date' % list)
        asins_movie = scrapAsins('/gp/aw/%s/?filter=movie&pageSize=1000&sortBy=date' % list)
    else:
        asins_movie = list
        asins_tv = ''
    url = 'ASINList='
    if dispShowOnly == 'true': extraArgs = '&RollupToSeries=T'
    if list == watchlist: extraArgs += '&'+OfferGroup
    if export:
        url += asins_movie + ',' + asins_tv
        SetupLibrary()
        listContent('GetASINDetails', url, 1, list, export)
    else:
        addDir(getString(30104), 'listContent', url+asins_movie, catalog='GetASINDetails', opt=list)
        addDir(getString(30107), 'listContent', url+asins_tv+extraArgs, catalog='GetASINDetails', opt=list)
        xbmcplugin.endOfDirectory(pluginhandle, updateListing=False)
    
def Log(msg, level=xbmc.LOGNOTICE):
    if type(msg) == type(unicode()):
        msg = msg.encode('utf-8')
    #WriteLog(msg)
    xbmc.log('[%s] %s' % (__plugin__, msg), level)

def WriteLog(data, path=os.path.join(HomePath, 'amazon-test.log')):
    if not LogFile: return
    if type(data) == type(unicode()): data = data.encode('utf-8')
    file = open(path, 'a')
    data = time.strftime('[%d/%H:%M:%S] ', time.localtime()) + data.__str__()
    file.write(data)
    file.write('\n')
    file.close()
    
def getString(id, enc=False):
    if enc: return addon.getLocalizedString(id).encode('utf-8')
    return addon.getLocalizedString(id)
    
def getAsins(content, crIL=True):
    if crIL:
        infoLabels={'Plot': None, 'MPAA': None, 'Cast': [], 'Year': None, 'Premiered': None, 'Rating': None, 'Votes': None, 'isAdult': 0, 'Director': None,
                    'Genre': None, 'Studio': None, 'Thumb': None, 'Fanart': None, 'isHD': False, 'isPrime': True, 'AudioChannels': 1, 'TrailerAvailable': False}
    asins = ''
    if content.has_key('titleId'):
        asins += content['titleId']
        titleId = content['titleId']
    for format in content['formats']:
        hasprime = False
        for offer in format['offers']:
            if offer['offerType'] == 'SUBSCRIPTION' and crIL:
                hasprime = True
                infoLabels['isPrime'] = True
            elif offer.has_key('asin'):
                newasin = offer['asin']
                if format['videoFormatType'] == 'HD' and crIL:
                    if (hasprime):
                        infoLabels['isHD'] = True
                if newasin not in asins:
                    asins += ',' + newasin
        if crIL:
            if 'STEREO' in format['audioFormatTypes']: infoLabels['AudioChannels'] = 2
            if 'AC_3_5_1' in format['audioFormatTypes']: infoLabels['AudioChannels'] = 6
    del content

    if crIL:
        infoLabels['Asins'] = asins
        return infoLabels
    return asins
    
def getInfos(item):
    infoLabels = getAsins(item)
    infoLabels['Title'] = item['title']
    infoLabels['contentType'] = contentType = item['contentType'].lower()
    
    if item['formats'][0].has_key('images'):
        try:
            thumbnailUrl = item['formats'][0]['images'][0]['uri']
            thumbnailFilename = thumbnailUrl.split('/')[-1]
            thumbnailBase = thumbnailUrl.replace(thumbnailFilename,'')
            infoLabels['Thumb'] = thumbnailBase+thumbnailFilename.split('.')[0]+'.jpg'
        except: pass
    if item.has_key('synopsis'):
        infoLabels['Plot'] = item['synopsis']
    if item.has_key('releaseOrFirstAiringDate'):
        infoLabels['Premiered'] = item['releaseOrFirstAiringDate']['valueFormatted'].split('T')[0]
        infoLabels['Year'] = int(infoLabels['Premiered'].split('-')[0])
    if item.has_key('studioOrNetwork'):
        infoLabels['Studio'] = item['studioOrNetwork']
    if item.has_key('regulatoryRating'):
        if item['regulatoryRating'] == 'not_checked': infoLabels['MPAA'] = getString(30171)
        else: infoLabels['MPAA'] = getString(30170) + item['regulatoryRating']
    if item.has_key('starringCast'):
        infoLabels['Cast'] = item['starringCast'].split(',')
    if item.has_key('director'):
        infoLabels['Director'] = item['director']
    if item.has_key('genres'):
        infoLabels['Genre'] = ' / '.join(item['genres']).replace('_', ' & ').replace('Musikfilm & Tanz', 'Musikfilm, Tanz')
    if item.has_key('customerReviewCollection'):
        infoLabels['Rating'] = float(item['customerReviewCollection']['customerReviewSummary']['averageOverallRating'])*2
        infoLabels['Votes'] = str(item['customerReviewCollection']['customerReviewSummary']['totalReviewCount'])
    elif item.has_key('amazonRating'):
        if item['amazonRating'].has_key('rating'): infoLabels['Rating'] = float(item['amazonRating']['rating'])*2
        if item['amazonRating'].has_key('count'): infoLabels['Votes'] = str(item['amazonRating']['count'])        
    if item.has_key('heroUrl'):
        infoLabels['Fanart'] = item['heroUrl']
    if item.has_key('trailerAvailable'):
        infoLabels['TrailerAvailable'] = item['trailerAvailable']
    if item.has_key('runtime'):
        infoLabels['Duration'] = str(item['runtime']['valueMillis']/1000)
    if item.has_key('restrictions'):
        for rest in item['restrictions']:
            if rest['action'] == 'playback':
                if rest['type'] == 'ageVerificationRequired': infoLabels['isAdult'] = 1

    if contentType == 'series':
        infoLabels['TVShowTitle'] = item['title']
        if item.has_key('childTitles'):
            infoLabels['TotalSeasons'] = item['childTitles'][0]['size']
            
    elif contentType == 'season':
        infoLabels['Season'] = item['number']
        if item['ancestorTitles']:
            try:
                infoLabels['TVShowTitle'] = item['ancestorTitles'][0]['title']
                infoLabels['SeriesAsin'] = item['ancestorTitles'][0]['titleId']
            except: pass
        else:
            infoLabels['SeriesAsin'] = infoLabels['Asins'].split(',')[0]
            infoLabels['TVShowTitle'] = item['title']
        if item.has_key('childTitles'):
            infoLabels['TotalSeasons'] = 1
            infoLabels['Episode'] = item['childTitles'][0]['size']

    elif contentType == 'episode':
        if item.has_key('ancestorTitles'):
            for content in item['ancestorTitles']:
                if content['contentType'] == 'SERIES':
                    if content.has_key('titleId'): infoLabels['SeriesAsin'] = content['titleId']
                    if content.has_key('title'): infoLabels['TVShowTitle'] = content['title']
                elif content['contentType'] == 'SEASON':
                    if content.has_key('number'): infoLabels['Season'] = content['number']
                    if content.has_key('titleId'): infoLabels['SeasonAsin'] = content['titleId']
                    if content.has_key('title'): seasontitle = content['title']
            if not infoLabels['SeriesAsin']:
                infoLabels['SeriesAsin'] = infoLabels['SeasonAsin']
                infoLabels['TVShowTitle'] = seasontitle            
        if item.has_key('number'):
            infoLabels['Episode'] = item['number']
            infoLabels['DisplayTitle'] = '%s - %s' %(item['number'], infoLabels['Title'])
    infoLabels = getArtWork(infoLabels, contentType)
    if not infoLabels['Thumb']: infoLabels['Thumb'] = DefaultFanart
    if not infoLabels['Fanart']: infoLabels['Fanart'] = DefaultFanart
    return contentType, infoLabels

def PlayVideo(name, asin, adultstr, trailer, selbitrate):
    global amazonUrl
    amazonUrl = BaseUrl + "/dp/" + asin
    xbmc.Player().stop()
    
    if trailer == '1':
        if selPlugin == '':
            PLAYTRAILER()
            return
        amazonUrl += "/?autoplaytrailer=1"
    else:
        if selPlugin == '':
            PLAYVIDEOINT()
            return
        amazonUrl += "/?autoplay=1"
    kiosk = 'yes'
    if addon.getSetting("kiosk") == 'false': kiosk = 'no'
    
    xbmc.executebuiltin('RunPlugin(plugin://%s/?url=%s&mode=showSite&kiosk=%s)' % (selPlugin, urllib.quote_plus(amazonUrl), kiosk))

    pininput = 0
    fullscr = 0
    adult = int(adultstr)
    if addon.getSetting("pininput") == 'true': pininput = 1
    if addon.getSetting("fullscreen") == 'true': fullscr = 1

    if adult == 1 and pininput == 1:
        if fullscr == 1: waitsec = waitsec*0.75 
        else: waitsec = waitprepin
        xbmc.sleep(int(waitsec))
        Input(keys=pin)
        if fullscr == 1: xbmc.sleep(waitpin)
        
    if fullscr == 1:
        xbmc.sleep(waitsec)
        Input(mousex=-1,mousey=350)
        if adult == 0: pininput = 1
        if pininput == 1:
            Input(mousex=-1,mousey=350,click=2)
            xbmc.sleep(500)
            Input(mousex=9999,mousey=350)

def Input(mousex=0,mousey=0,click=0,keys=False,delay='200'):
    if mousex == -1: mousex = screenWidth/2
    if mousey == -1: mousey = screenHeight/2

    if osWin:
        app = userinput
        mouse = ' mouse %s %s' % (mousex,mousey)
        mclk = ' ' + str(click)
        keybd = ' key %s{Enter} %s' % (keys,delay)
    elif osLinux:
        app = 'xdotool'
        mouse = ' mousemove %s %s' % (mousex,mousey)
        mclk = ' click --repeat %s 1' % click
        keybd = ' type --delay %s %s && xdotool key Return' % (delay, keys)
    elif osOsx:
        app = 'cliclick'
        mouse = ' m:'
        if click == 1: mouse = ' c:'
        elif click == 2: mouse = ' dc:'
        mouse += '%s,%s' % (mousex,mousey)
        mclk = ''
        keybd = ' -w %s t:%s kp:return' % (delay, keys)

    if keys:
        cmd = app + keybd
    else:
        cmd = app + mouse
        if click: cmd += mclk
    Log('Run command: %s' % cmd)
    subprocess.Popen(cmd, shell=True)

def genID():
    id = addon.getSetting("GenDeviceID")
    if not id:
        id = makeGUID()
        addon.setSetting("GenDeviceID", id)
    return id

def MechanizeLogin():
    cj = cookielib.LWPCookieJar()
    if os.path.isfile(CookieFile):
        cj.load(CookieFile, ignore_discard=True, ignore_expires=True)
        return cj
    Log('Login')
    succeeded = LogIn()
    retrys = 0
    while succeeded == False:
        xbmc.sleep(1000)
        retrys += 1
        Log('Login Retry: %s' % retrys)
        succeeded = LogIn()
        if retrys >= 2:
            Dialog.ok('Login Error','Failed to Login')
            succeeded=True
    return succeeded

def LogIn():
    email = addon.getSetting('login_name')
    password = decode(addon.getSetting('login_pass'))
    changed = False
    
    if addon.getSetting('save_login') == 'false' or email == '' or password == '':
        keyboard = xbmc.Keyboard(addon.getSetting('login_name'), getString(30002))
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            email = keyboard.getText()
            password = setLoginPW()
            if password: changed = True
    if password:
        if os.path.isfile(CookieFile):
            os.remove(CookieFile)
        cj = cookielib.LWPCookieJar()
        br = mechanize.Browser()  
        br.set_handle_robots(False)
        br.set_cookiejar(cj)
        br.addheaders = [('User-agent', UserAgent)]  
        sign_in = br.open(BaseUrl + "/gp/aw/si.html") 
        br.select_form(name="signIn")  
        br["email"] = email
        br["password"] = password
        logged_in = br.submit()
        error_str = "message error"
        if error_str in logged_in.read():
            Dialog.ok(getString(30200), getString(30201))
            return False
        else:
            if addon.getSetting('save_login') == 'true' and changed:
                addon.setSetting('login_name', email)
                addon.setSetting('login_pass', encode(password))
            if addon.getSetting('no_cookie') != 'true':
                cj.save(CookieFile, ignore_discard=True, ignore_expires=True)
            genID()
            return cj
    return True
    
def setLoginPW():
    keyboard = xbmc.Keyboard('', getString(30003), True)
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        password = keyboard.getText()
        return password
    return False
        
def encode(data):
    k = triple_des((str(uuid.getnode())*2)[0:24], CBC, "\0\0\0\0\0\0\0\0", padmode=PAD_PKCS5)
    d = k.encrypt(data)
    return base64.b64encode(d)

def decode(data):
    if not data: return ''
    k = triple_des((str(uuid.getnode())*2)[0:24], CBC, "\0\0\0\0\0\0\0\0", padmode=PAD_PKCS5)
    d = k.decrypt(base64.b64decode(data))
    return d

def remLoginData():
    if os.path.isfile(CookieFile):
        os.remove(CookieFile)
    addon.setSetting('login_name', '')
    addon.setSetting('login_pass', '')
    
def makeGUID():
    import random
    guid = ''
    for i in range(3):
        number = "%X" % (int( ( 1.0 + random.random() ) * 0x10000) | 0)
        guid += number[1:]    
    return hmac.new(UserAgent, guid, hashlib.sha224).hexdigest()

def scrapAsins(url):
    asins = []
    url = BaseUrl + url
    content = getURL(url, useCookie=True)
    asins += re.compile('data-asin="(.+?)"', re.DOTALL).findall(content)
    return ','.join(asins)
    
def createDB():
    c = db.cursor()
    c.execute('''CREATE TABLE art(
                 asin TEXT,
                 season INTEGER,
                 poster TEXT,
                 banner TEXT,
                 fanart TEXT,
                 lastac DATE, 
                 PRIMARY KEY(asin, season)
                 );''')
    db.commit()
    c.close()

def cleanName(name, file=True):
    if file: notallowed = ['<', '>', ':', '"', '\\', '/', '|', '*', '?']
    else:
        notallowed = ['<', '>', '"', '|', '*', '?']
        if not os.path.supports_unicode_filenames: name = name.encode('utf-8')
    for c in notallowed:
        name = name.replace(c,'')
    return name

def UpdateLibrary():
    xbmc.executebuiltin('UpdateLibrary(video)')
    
def SaveFile(filename, data, dir=False, mode='w'):
    if type(data) == type(unicode()): data = data.encode('utf-8')
    if dir:
        filename = cleanName(filename)
        filename = os.path.join(dir, filename)
    filename = cleanName(filename, file=False)
    file = open(filename, mode)
    file.write(data)
    file.close()

def CreateDirectory(dir_path):
    dir_path = cleanName(dir_path.strip(), file=False)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        return True
    return False

def SetupLibrary():
    CreateDirectory(MOVIE_PATH)
    CreateDirectory(TV_SHOWS_PATH) 
    SetupAmazonLibrary()

def CreateInfoFile(file, path, content, Info, language, hasSubtitles = False):
    skip_keys = ('ishd', 'isadult', 'audiochannels', 'genre', 'cast', 'duration', 'asins', 'contentType')
    
    fileinfo = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>'
    fileinfo += '<%s>' % content
    if Info.has_key('Duration'):
        fileinfo += '<runtime>%s</runtime>' % Info['Duration']
    if Info.has_key('Genre'):
        for genre in Info['Genre'].split('/'):
            fileinfo += '<genre>%s</genre>' % genre.strip()
    if Info.has_key('Cast'):
        for actor in Info['Cast']:
            fileinfo += '<actor>'
            fileinfo += '<name>%s</name>' % actor.strip()
            fileinfo += '</actor>'
    for key, value in Info.items():
        lkey = key.lower()
        if lkey == 'tvshowtitle':
            fileinfo += '<showtitle>%s</showtitle>' % value
        elif lkey == 'premiered' and Info.has_key('TVShowTitle'):
            fileinfo += '<aired>%s</aired>' % value
        elif lkey == 'fanart':
            fileinfo += '<%s><thumb>%s</thumb></%s>' % (lkey, value, lkey)
        elif lkey not in skip_keys:
            fileinfo += '<%s>%s</%s>' % (lkey, value, lkey)
    if content != 'tvshow':
        fileinfo += '<fileinfo>'
        fileinfo += '<streamdetails>'
        fileinfo += '<audio>'
        fileinfo += '<channels>%s</channels>' % Info['AudioChannels']
        fileinfo += '<codec>aac</codec>'
        fileinfo += '</audio>'
        fileinfo += '<video>'
        fileinfo += '<codec>h264</codec>'
        fileinfo += '<durationinseconds>%s</durationinseconds>' % (int(Info['Duration']) * 60)
        if Info['isHD'] == True:
            fileinfo += '<height>720</height>'
            fileinfo += '<width>1280</width>'
        else:
            fileinfo += '<height>480</height>'
            fileinfo += '<width>720</width>'        
        if language: fileinfo += '<language>%s</language>' % language
        fileinfo += '<scantype>Progressive</scantype>'
        fileinfo += '</video>'
        if hasSubtitles == True:
            fileinfo += '<subtitle>'
            fileinfo += '<language>ger</language>'
            fileinfo += '</subtitle>'
        fileinfo += '</streamdetails>'
        fileinfo += '</fileinfo>'
    fileinfo += '</%s>' % content

    SaveFile(file + '.nfo', fileinfo, path)
    return
    
def SetupAmazonLibrary():
    Log('Trying to add Amazon source paths...')
    source_path = os.path.join(ProfilPath, 'sources.xml')
    source_added = False
    
    try:
        file = open(source_path)
        soup = BeautifulSoup(file)
        file.close()
    except:
        subtags = ['programs', 'video', 'music', 'pictures', 'files']
        soup = BeautifulSoup('<sources></sources>')
        root = soup.sources
        for cat in subtags:
            cat_tag = Tag(soup, cat)
            def_tag = Tag(soup, 'default')
            def_tag['pathversion'] = 1
            cat_tag.append(def_tag)
            root.append(cat_tag)

    video = soup.find("video")      
        
    if len(soup.findAll(text="Amazon Movies")) < 1:
        movie_source_tag = Tag(soup, "source")
        movie_name_tag = Tag(soup, "name")
        movie_name_tag.insert(0, "Amazon Movies")
        movie_path_tag = Tag(soup, "path")
        movie_path_tag['pathversion'] = 1
        movie_path_tag.insert(0, MOVIE_PATH)
        movie_source_tag.insert(0, movie_name_tag)
        movie_source_tag.insert(1, movie_path_tag)
        video.insert(2, movie_source_tag)
        source_added = True

    if len(soup.findAll(text="Amazon TV")) < 1: 
        tvshow_source_tag = Tag(soup, "source")
        tvshow_name_tag = Tag(soup, "name")
        tvshow_name_tag.insert(0, "Amazon TV")
        tvshow_path_tag = Tag(soup, "path")
        tvshow_path_tag['pathversion'] = 1
        tvshow_path_tag.insert(0, TV_SHOWS_PATH)
        tvshow_source_tag.insert(0, tvshow_name_tag)
        tvshow_source_tag.insert(1, tvshow_path_tag)
        video.insert(2, tvshow_source_tag)
        source_added = True
    
    if source_added:
        Log('Source paths added!')
        SaveFile(source_path, str(soup))
        dialog.ok(getString(30187), getString(30188), getString(30189), getString(30190))
        if dialog.yesno(getString(30191), getString(30192)):
            xbmc.executebuiltin('RestartApp')

dbFile = os.path.join(DataPath, 'art.db')
if not os.path.exists(dbFile):
    db = sqlite.connect(dbFile)
    db.text_factory = str
    createDB()
else:
    db = sqlite.connect(dbFile)
    db.text_factory = str
deviceID = genID()

url = urlparse.urlparse(sys.argv[2])
par = urlparse.parse_qsl(url.query)
url = mode = opt = ''
export = '0'
page = '1'
Log(par)
for name, value in par: exec '%s = "%s"' % (name, value)

if mode == 'listCategories': listCategories(url, opt)
elif mode == 'listContent': listContent(cat, url, page, opt)
elif mode == 'loadArtWork': loadArtWork(asins, title, year, ct)
elif mode == 'PlayVideo': PlayVideo(name, asin, adult, trailer, selbitrate)
elif mode == 'getList': getList(url, int(export))
elif mode == 'WatchList': WatchList(url, int(opt))
elif mode == '': MainMenu()
else: exec mode + '()'
