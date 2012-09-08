from pandora import Pandora

#RE_STATION_ID = Regex('/play/([0-9]+)')

NAMESPACES = {'pandora':'http://www.pandora.com/rss/1.0/modules/pandora/'}
ART = 'art-default.jpg'
ICON = 'icon-default.jpg'
ICON_PREFS = 'icon-prefs.png'
ICON_SEARCH = 'icon-search.png'

FEED_URL = 'http://feeds.pandora.com/feeds/people/%s/%s.xml?max=%s'

####################################################################################################
def Start():
    # Current artwork.jpg free for personal use only - http://squaresailor.deviantart.com/art/Apple-Desktop-52188810
    Plugin.AddPrefixHandler('/music/pandora', MainMenu, 'Pandora', ICON, ART)
    
    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = 'Pandora'
    
    DirectoryObject.thumb = R(ICON)
    
    HTTP.CacheTime = 0
    
####################################################################################################
def ValidatePrefs():
    return
    
####################################################################################################     
def MainMenu():
    oc = ObjectContainer(no_cache=True)
    
    if 'PandoraConnection' not in Dict:
        Dict['PandoraConnection'] = {}
    
    if not Prefs['pan_user'] or not Prefs['pan_pass']:
        oc.add(PrefsObject(title='Set your Pandora Preferences', thumb=R(ICON_PREFS)))
    elif 'authed' in Dict['PandoraConnection']:
        if Dict['PandoraConnection']['authed']:
            authed = Dict['PandoraConnection']['authed']
        else:
            authed = Pandora_Authenticate()
    else :
        authed = Pandora_Authenticate()
    
    if not authed:
        oc.add(PrefsObject(title='Set your Pandora Preferences', summary='Unable to log in. Please check your settings.', thumb=R(ICON_PREFS)))
    elif not Dict['PandoraConnection']['premium_account']:
        oc.add(PrefsObject(title='Enter Pandora Premium membership details', sumamry='The Pandora channel requires a paid subscription to Pandora.', thumb=R(ICON_PREFS)))
    else:
        oc.add(DirectoryObject(key=Callback(StationList), title='Your Stations'))
#        oc.add(DirectoryObject(key=Callback(Bookmarks, title2='Your Bookmarked Songs', feed='favorites'), title='Your Bookmarked Songs'))
#        oc.add(DirectoryObject(key=Callback(Bookmarks, title2='Your Bookmarked Artists', feed='favoriteartists'), title='Your Bookmarked Artists'))

#        dir.Append(Function(InputDirectoryItem(ArtistSearch, title='Search Station by Artist', prompt='Search Station by Artist', thumb=R(ICON_SEARCH))))
#        dir.Append(Function(InputDirectoryItem(EmailSearch, title='Search for User Stations by Email', prompt='Search for User Stations by Email', thumb=R(ICON_SEARCH))))
#        dir.Append(Function(InputDirectoryItem(WebnameSearch, title='Search for User Stations by ID', prompt='Search for User Stations by ID', thumb=R(ICON_SEARCH))))
        oc.add(PrefsObject(title='Change your Pandora Preferences', thumb=R(ICON_PREFS)))
    return oc

####################################################################################################
def Pandora_Authenticate():
    
    pandora = Pandora()
    authed = pandora.authenticate(Prefs['pan_user'], Prefs['pan_pass'])
    
    if authed:
        Dict['PandoraConnection']['authed'] = pandora.authenticated
        Dict['PandoraConnection']['partner_id'] = pandora.connection.partner_id
        Dict['PandoraConnection']['partner_auth_token'] = pandora.connection.partner_auth_token
        Dict['PandoraConnection']['user_id'] = pandora.connection.user_id
        Dict['PandoraConnection']['user_auth_token'] = pandora.connection.user_auth_token
        Dict['PandoraConnection']['time_offset'] = pandora.connection.time_offset
        Dict['PandoraConnection']['premium_account'] = pandora.connection.premium_account
        return True
    else:
        Dict['PandoraConnection']['authed'] = False
        return False

####################################################################################################
def PandoraObject():
    
    pandora = Pandora()
    
    pandora.authenticated = Dict['PandoraConnection']['authed']
    pandora.connection.partner_id = Dict['PandoraConnection']['partner_id']
    pandora.connection.partner_auth_token = Dict['PandoraConnection']['partner_auth_token']
    pandora.connection.user_id = Dict['PandoraConnection']['user_id']
    pandora.connection.user_auth_token = Dict['PandoraConnection']['user_auth_token']
    pandora.connection.time_offset = Dict['PandoraConnection']['time_offset']
    pandora.connection.premium_account = Dict['PandoraConnection']['premium_account']
    
    return pandora

####################################################################################################
def StationList():
    
    pandora = PandoraObject()
    
    oc = ObjectContainer(no_cache=True)
    
    stations = pandora.get_station_list()
    
    for station in stations:
        oc.add(DirectoryObject(key=Callback(Station, station=station), title = station['stationName']))
    
    return oc

####################################################################################################
def Station(station=None, station_id=None):
    if station:
        title2 = station['stationName']
        station_id = station['stationToken']
    else:
        title2=station_id
    oc = ObjectContainer(title2=title2, no_cache=True)
    pandora = PandoraObject()
    pandora.switch_station(station_id)
    
    while len(oc) < int(Prefs['playlist_length']):
        try:
            song = pandora.get_next_song()
            try:
                if song['adToken']:
                    Log(song)
                    song = pandora.get_next_song()
            except:
                pass
            
            track = GetTrack(song)
            oc.add(track)
        
        except:
            break            
    
    return oc

####################################################################################################
#def Webname():
#    if Dict['webname']:
#        webname = Dict['webname']
#    else:
#        webname = WebnameFromEmail(Prefs['pan_user'])
#        Dict['webname'] = webname
#    
#    return webname
#
####################################################################################################
#def WebnameFromEmail(email, authenticate=False):
#    jsonUrl = 'http://feeds.pandora.com/services/ajax/?method=authenticate.emailToWebname&email=' + email
#
#    if authenticate:
#        values = {'loginform': '',
#                  'login_username': Prefs['pan_user'],
#                  'login_password': Prefs['pan_pass']}
#        dict = JSON.ObjectFromURL(jsonUrl, values=values)
#    else:
#        dict = JSON.ObjectFromURL(jsonUrl)
#
#    if dict['stat'] == 'ok':
#        return dict['result']['webname']
#    else:
#        return False
#    
####################################################################################################
#def Bookmarks(title2, feed, webname=None):
#    oc = ObjectContainer(title2=title2)
#    
#    if not webname:
#        webname = Webname()
#    
#    url = FEED_URL % (webname, feed, Prefs['playlist_length'])
#    for item in XML.ElementFromURL(url, errors='ignore').xpath('//item'):
#        title = item.xpath('./title')[0].text
#        link = item.xpath('./link')[0].text
#        desc = item.xpath('./description')[0].text
#        stationLink = item.xpath('./pandora:stationLink', namespaces=NAMESPACES)[0].text
#        station_id = StationTokenFromStationLink(stationLink)
#        
#        try:
#            if feed == 'stations':
#                thumb = item.xpath('./pandora:stationAlbumArtImageUrl', namespaces=NAMESPACES)[0].text
#            elif feed == 'favorites':
#                thumb = item.xpath('./pandora:albumArtUrl', namespaces=NAMESPACES)[0].text
#            elif feed == 'favoriteartists':
#                thumb = item.xpath('./pandora:artistPhotoUrl', namespaces=NAMESPACES)[0].text
#        except:
#            thumb = None
#
#        #dir.Append(WebVideoItem(link, title=title, summary=desc, thumb=Function(GetThumb, url=thumb)))
#        oc.add(DirectoryObject(key=Callback(Station, station_id=station_id), title=title, summary=desc, thumb=thumb))
#
#    return oc
#
####################################################################################################
#def StationTokenFromStationLink(stationLink):
#    new_url = ''
#    #HTTP.Headers['Cookie'] = "{'at': '%s'}" % Dict['PandoraConnection']['partner_auth_token']
#    HTTP.Headers['Cookie'] = {'user_segment':'Prospect', 'v2regbstage':'true',  'atn':'AT-1347128172694-850', 'at':'wfG26CwcLF5rJjjFZo/ISxvXK+OFmuiaA'}
#    content = HTTP.Request(stationLink, follow_redirects = False).content
#    try:
#        headers = HTTP.Request(stationLink, follow_redirects = False).headers
#    except Ex.RedirectError, e:
#        try:
#            new_url = e.location
#        except:
#            pass
#    
#    stationToken = RE_STATION_ID.search(new_url).group(1)
#    
#    return stationToken
#
####################################################################################################
#def ArtistSearch(sender, query):
#    dir = MediaContainer(title2=sender.itemTitle)
#    content = HTML.ElementFromURL('http://www.pandora.com/backstage?type=all&q=' + query).xpath('//table[@id="tbl_artist_search_results"]/tbody/tr')

#    for artist in content:
#        thumb = artist.xpath('./td/a/img')[0].get('src')
#        a = artist.xpath('./td/a')
#        href = a[1].get('href')
#        url = 'http://www.pandora.com/?search=' + href[href.rfind('/')+1:]
#        title = a[1].text
#        dir.Append(WebVideoItem(url, title=title, thumb=Function(GetThumb, url=thumb)))

#    return dir

####################################################################################################  
#def EmailSearch(sender, query):
#    dir = MediaContainer(title2=sender.itemTitle)

#    if WebnameFromEmail(query):
#        dir = Bookmarks(sender, query, 'stations')
#        return dir
#    else:
#        return MessageContainer('Invalid Email', 'Search for User Stations by Email')

####################################################################################################  
#def WebnameSearch(sender, query):
#    dir = MediaContainer(title2=sender.itemTitle)
#
#    try:
#        dir = Bookmarks(sender, query, 'stations')
#        return dir
#    except:
#        return MessageContainer('Invalid Webname', 'Search for User Stations by Webname')

####################################################################################################
def GetTrack(song):
    
    track = TrackObject(
        key=song['songDetailUrl'],
        rating_key=song['songDetailUrl'],
        title = song['songName'],
        album=song['albumName'],
        artist = song['artistName'],
        thumb = song['albumArtUrl'],
        items = [
            MediaObject(
                parts = [PartObject(key=Callback(PlayAudio, song=song, ext='mp3', quality='mp3'))],
                container = Container.MP3,
                bitrate = 128,
                audio_codec = AudioCodec.MP3,
                audio_channels = 2
            ),
            MediaObject(
                parts = [PartObject(key=Callback(PlayAudio, song=song, ext='aac', quality='highQuality'))],
                container = Container.MP4,
                bitrate = 64,
                audio_codec = AudioCodec.AAC,
                audio_channels = 2
            ),
            MediaObject(
                parts = [PartObject(key=Callback(PlayAudio, song=song, ext='aac', quality='mediumQuality'))],
                container = Container.MP4,
                bitrate = 64,
                audio_codec = AudioCodec.AAC,
                audio_channels = 2
            ),
            MediaObject(
                parts = [PartObject(key=Callback(PlayAudio, song=song, ext='aac', quality='lowQuality'))],
                container = Container.MP4,
                bitrate = 32,
                audio_codec = AudioCodec.AAC,
                audio_channels = 2
            )
        ]
    )
    return track

####################################################################################################
def PlayAudio(song, quality):
    QUALITY_MAP = ['lowQuality', 'mediumQuality', 'highQuality']
    
    if quality == 'mp3':
        return Redirect(song['additionalAudioUrl'])
    
    index = QUALITY_MAP.index(quality)
    while index > -1:
        try:
            song_url = song['audioUrlMap'][QUALITY_MAP[index]]['audioUrl']
            break
        except:
            index = index - 1
    return Redirect(song_url)

####################################################################################################