from pandora import Pandora

NAMESPACES = {'pandora':'http://www.pandora.com/rss/1.0/modules/pandora/'}
ART = 'art-default.jpg'
ICON = 'icon-default.jpg'
ICON_PREFS = 'icon-prefs.png'
ICON_SEARCH = 'icon-search.png'

PLAYLIST_LENGTH = 12
PLAYLIST_RESET_INTERVAL = 600

FEED_URL = 'http://feeds.pandora.com/feeds/people/%s/%s.xml?max=%s'

####################################################################################################
def Start():
    # Current artwork.jpg free for personal use only - http://squaresailor.deviantart.com/art/Apple-Desktop-52188810
    Plugin.AddPrefixHandler('/music/pandora', MainMenu, 'Pandora', ICON, ART)
    
    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = 'Pandora'
    
    DirectoryObject.thumb = R(ICON)
    
    HTTP.CacheTime = 0

    if 'PandoraPlaylist' not in Dict:
        Dict['PandoraPlaylist'] = {}

    Dict['PandoraPlaylist']['station_id'] = ''
    Dict['PandoraPlaylist']['timestamp'] = 0

        
####################################################################################################     
def MainMenu():

    oc = ObjectContainer(no_cache=True)
    if not Prefs['pan_user'] or not Prefs['pan_pass']:
        oc.add(PrefsObject(title='Set your Pandora Preferences', thumb=R(ICON_PREFS)))
        return oc
    else:
        oc.add(DirectoryObject(key=Callback(StationList), title='Your Stations'))
        oc.add(DirectoryObject(key=Callback(ManageStations), title='Manage Stations'))
        oc.add(PrefsObject(title='Change your Pandora Preferences', thumb=R(ICON_PREFS)))

    return oc

####################################################################################################
def PandoraObject():
    
    pandora = Pandora()
    authed = pandora.authenticate(Prefs['pan_user'], Prefs['pan_pass'])
    if authed:
        return pandora
    else:
        return None

####################################################################################################
def StationList(action='play'):
    
    pandora = PandoraObject()
    if pandora is None:
        return ObjectContainer(header="Pandora Error",
                 message="Unable to log in.  Please check your settings.  The Pandora channel requires a paid Pandora One account."
               )

    oc = ObjectContainer(no_cache=True)
    stations = pandora.get_station_list()

    if Prefs['station_sort_order'] == 'Alphabetical':
        stations = sorted(stations, key=lambda k: k['stationName'])

    for station in stations:
        if action == 'play':
            oc.add(DirectoryObject(key=Callback(Station, station=station), title = station['stationName']))
        elif action == 'delete':
            oc.add(PopupDirectoryObject(key=Callback(ConfirmDelete, station=station, station_name=station['stationName']), title = station['stationName']))
    
    return oc

####################################################################################################
def ManageStations():
    
    oc = ObjectContainer()

    oc.add(InputDirectoryObject(key=Callback(SearchStations), title="Add Station...", prompt="Search Pandora"))
    oc.add(DirectoryObject(key=Callback(StationList, action='delete'), title="Remove Stations"))
    
    return oc

####################################################################################################
def SearchStations(query):
    
    pandora = PandoraObject()
    results = pandora.music_search(query)
    matches = results['artists'] + results['songs']

    oc = ObjectContainer()
    for match in matches:
        title = match['artistName']
        try:
            title = title + ' - ' + match['songName']
        except:
            pass

        oc.add(DirectoryObject(key=Callback(CreateStation, music_token=match['musicToken']), title=title))

    return oc

####################################################################################################
def CreateStation(music_token):

    pandora = PandoraObject()
    pandora.create_station(music_token)
    
    return StationList(action='play')

####################################################################################################
def ConfirmDelete(station, station_name):
    
    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(DeleteStation, station=station), title='Delete ' + station_name))
    oc.add(DirectoryObject(key=Callback(StationList, action='delete'), title='Cancel'))
    
    return oc

####################################################################################################
def DeleteStation(station):
    
    pandora = PandoraObject()
    pandora.delete_station(station['stationToken'])

    return StationList(action='delete')

####################################################################################################
def Station(station=None, station_id=None):
    
    title2 = station['stationName']
    station_id = station['stationToken']
    oc = ObjectContainer(title2=title2, no_cache=True)
    pandora = PandoraObject()
    playlist_stale = False

    Log('Dict timestamp: ' + str(Dict['PandoraPlaylist']['timestamp']))
    Log('Now: ' + str(int(Datetime.TimestampFromDatetime(Datetime.Now()))))

    if Dict['PandoraPlaylist']['timestamp'] + PLAYLIST_RESET_INTERVAL < int(Datetime.TimestampFromDatetime(Datetime.Now())):
        playlist_stale = True
    
    Log('Dict station_id: ' + Dict['PandoraPlaylist']['station_id'])
    Log('requested station_id: ' + station_id)

    if Dict['PandoraPlaylist']['station_id'] != station_id or playlist_stale:
        Log('Rebuilding playlist due to timeout... playlist_stale: ' + str(playlist_stale))
        try:
            pandora.switch_station(station_id)
            Dict['PandoraPlaylist']['station_id'] = station_id
            Dict['PandoraPlaylist']['timestamp'] = int(Datetime.TimestampFromDatetime(Datetime.Now()))
            Dict['PandoraPlaylist']['playlist'] = []
        except:
            return ObjectContainer(header="Pandora Error",
                     message="Unable to switch station.  Hourly limit reached.  Try again in a few minutes."
                   )
    else:
        pandora.set_station(station_id)    
        
    while len(Dict['PandoraPlaylist']['playlist']) < PLAYLIST_LENGTH:
        try:
            Dict['PandoraPlaylist']['playlist'].append(pandora.get_next_song())
            Dict['PandoraPlaylist']['timestamp'] = int(Datetime.TimestampFromDatetime(Datetime.Now()))
        except:
            Log('Unable to add track.')
            break

    for song in Dict['PandoraPlaylist']['playlist']:
        track = GetTrack(song)
        oc.add(track)

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
            parts = [PartObject(key=Callback(PlayAudio, url=song['audioUrlMap'][quality]['audioUrl'], ext=ext, quality=quality, song=song))],
            container = container,
            bitrate = song['audioUrlMap'][quality]['bitrate'],
            audio_codec = audio_codec,
            audio_channels = 2
        ))
        
    track = TrackObject(
        key=Callback(GetTrack, song=song),
        rating_key=song['songDetailUrl'],
        title = song['songName'],
        album=song['albumName'],
        artist = song['artistName'],
        thumb = song['albumArtUrl'],
        items = items
    )
    return track

####################################################################################################
def PlayAudio(url='', ext='', quality='', song=None):
    try:
        Dict['PandoraPlaylist']['playlist'].remove(song)
    except:
        pass
    return Redirect(url)

####################################################################################################