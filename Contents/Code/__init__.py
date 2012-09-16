from pandora import Pandora

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
        return oc
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
        oc.add(PrefsObject(title='Change your Pandora Preferences', thumb=R(ICON_PREFS)))
    return oc

####################################################################################################
def Pandora_Authenticate():
    
    try:
        pandora = PandoraObject()
        authed = pandora.authenticated
    except:
        pandora = Pandora()
        authed = pandora.authenticate(Prefs['pan_user'], Prefs['pan_pass'])
        
    
    if authed:
        Dict['PandoraConnection']['authed'] = True
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
                    song = pandora.get_next_song()
            except:
                pass

            track = GetTrack(song)
            oc.add(track)
        
        except:
            break            
    
    return oc

####################################################################################################
def GetTrack(song):

    items = []
    for quality in song['audioUrlMap']:
        
        encoding = song['audioUrlMap'][quality]['encoding']
        if 'aac' in encoding:
            container = Container.MP4
            audio_codec = AudioCodec.AAC
            ext = 'aac'
        else:
            container = Container.MP3
            audio_codec = AudioCodec.MP3
            ext = 'mp3'
        items.append(MediaObject(
            parts = [PartObject(key=Callback(PlayAudio, url=song['audioUrlMap'][quality]['audioUrl'], ext=ext, quality=quality))],
            container = container,
            bitrate = song['audioUrlMap'][quality]['bitrate'],
            audio_codec = audio_codec,
            audio_channels = 2
        ))
        
    track = TrackObject(
        key=song['songDetailUrl'],
        rating_key=song['songDetailUrl'],
        title = song['songName'],
        album=song['albumName'],
        artist = song['artistName'],
        thumb = song['albumArtUrl'],
        items = items
    )
    return track

####################################################################################################
def PlayAudio(url='', ext='', quality=''):
    return Redirect(url)

####################################################################################################