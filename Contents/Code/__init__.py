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
def MainMenu():

    oc = ObjectContainer(no_cache=True)
    if not Prefs['pan_user'] or not Prefs['pan_pass']:
        oc.add(PrefsObject(title='Set your Pandora Preferences', thumb=R(ICON_PREFS)))
        return oc
    else:
        oc.add(DirectoryObject(key=Callback(StationList), title='Your Stations'))
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
def StationList():
    
    pandora = PandoraObject()
    if pandora is None:
        return ObjectContainer(header="Pandora Error",
                 message="Unable to log in.  Please check your settings.  The Pandora channel requires a paid Pandora One account."
               )
    
    oc = ObjectContainer(no_cache=True)
    stations = pandora.get_station_list()
    for station in stations:
        oc.add(DirectoryObject(key=Callback(Station, station=station), title = station['stationName']))
    
    return oc

####################################################################################################
def Station(station=None, station_id=None):
    
    title2 = station['stationName']
    station_id = station['stationToken']
    oc = ObjectContainer(title2=title2, no_cache=True)
    pandora = PandoraObject()
    
    try:
        pandora.switch_station(station_id)
    except:
        return ObjectContainer(header="Pandora Error",
                 message="Unable to switch station.  Hourly limit reached.  Try again in a few minutes."
               )

    while len(oc) < int(Prefs['playlist_length']):
        try:
            song = pandora.get_next_song()
            track = GetTrack(song)
            oc.add(track)
        except:
            Log('Unable to add track.')
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