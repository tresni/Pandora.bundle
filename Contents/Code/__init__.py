import crypt

NAMESPACES = {'pandora':'http://www.pandora.com/rss/1.0/modules/pandora/'}
ART = 'art-default.jpg'
ICON = 'icon-default.jpg'
ICON_PREFS = 'icon-prefs.png'
ICON_SEARCH = 'icon-search.png'

FEED_URL = 'http://feeds.pandora.com/feeds/people/%s/%s.xml'

####################################################################################################
def Start():
    # Current artwork.jpg free for personal use only - http://squaresailor.deviantart.com/art/Apple-Desktop-52188810
    Plugin.AddPrefixHandler('/music/pandora', MainMenu, 'Pandora', ICON, ART)
    
    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = 'Pandora'
    
    DirectoryObject.thumb = R(ICON)
    Dict['PandoraObject'] = None

####################################################################################################
def PandoraObject():
    if Dict['PandoraObject']:
        return Dict['PandoraObject']
    else:
        return None

####################################################################################################  
def MainMenu():
    oc = ObjectContainer(no_cache=True)
    pandora = Pandora()
    Dict['PandoraObject'] = pandora
    
    if not Prefs['pan_user'] or not Prefs['pan_pass']:
        oc.add(PrefsObject(title='Set your Pandora Preferences', thumb=R(ICON_PREFS)))
    else:
        authed = pandora.authenticate(Prefs['pan_user'], Prefs['pan_pass'])
        if not authed:
            oc.add(PrefsObject(title='Set your Pandora Preferences', summary='Unable to log in. Please check your settings.', thumb=R(ICON_PREFS)))
        else:
            oc.add(DirectoryObject(key=Callback(StationList), title='Your Stations'))
#        dir.Append(Function(DirectoryItem(Bookmarks, title='Your Stations'), webname=webname, feed='stations'))
#        dir.Append(Function(DirectoryItem(Bookmarks, title='Your Bookmarked Songs'), webname=webname, feed='favorites'))
#        dir.Append(Function(DirectoryItem(Bookmarks, title='Your Bookmarked Artists'), webname=webname, feed='favoriteartists'))

#        dir.Append(Function(InputDirectoryItem(ArtistSearch, title='Search Station by Artist', prompt='Search Station by Artist', thumb=R(ICON_SEARCH))))
#        dir.Append(Function(InputDirectoryItem(EmailSearch, title='Search for User Stations by Email', prompt='Search for User Stations by Email', thumb=R(ICON_SEARCH))))
#        dir.Append(Function(InputDirectoryItem(WebnameSearch, title='Search for User Stations by ID', prompt='Search for User Stations by ID', thumb=R(ICON_SEARCH))))
#        dir.Append(PrefsItem(title='Change your Pandora Preferences', thumb=R(ICON_PREFS)))
    return oc

####################################################################################################
def StationList():
    
    pandora = PandoraObject()
    
    oc = ObjectContainer(no_cache=True)
    
    stations = pandora.get_station_list()
    
    for station in stations:
        oc.add(DirectoryObject(key=Callback(NextTrack, station=station), title = station['stationName']))
    
    return oc

####################################################################################################
def NextTrack(station):
    oc = ObjectContainer(no_cache=True)
    pandora = PandoraObject()
    pandora.switch_station(station['stationToken'])
    Dict['PandoraObject'] = pandora
    song = pandora.get_next_song()
    if song['adToken']:
        song = pandora.get_next_song()
    Log(song['songDetailUrl'])
    
    oc.add(TrackObject(
        key=song['songDetailUrl'],
        rating_key=song['songDetailUrl'],
        title = song['songName'],
        album=song['albumName'],
        artist = song['artistName'],
        thumb = song['albumArtUrl'],
        items = [
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
        ])
    )
    return oc

####################################################################################################
def PlayAudio(song, quality):
    Log(quality)
    QUALITY_MAP = ['lowQuality', 'mediumQuality', 'highQuality']
    index = QUALITY_MAP.index(quality)
    Log(index)
    while index > -1:
        try:
            song_url = song['audioUrlMap'][QUALITY_MAP[index]]['audioUrl']
            break
        except:
            index = index - 1
    Log(song_url)
    return Redirect(song_url)

####################################################################################################

#def Bookmarks(sender, webname, feed):
#    dir = MediaContainer(title2=sender.itemTitle)
#    url = FEED_URL % (webname, feed)

#    for item in XML.ElementFromURL(url, errors='ignore').xpath('//item'):
#        title = item.xpath('./title')[0].text
#        link = item.xpath('./link')[0].text
#        desc = item.xpath('./description')[0].text

#        try:
#            if feed == 'stations':
#                thumb = item.xpath('./pandora:stationAlbumArtImageUrl', namespaces=NAMESPACES)[0].text
#            elif feed == 'favorites':
#                thumb = item.xpath('./pandora:albumArtUrl', namespaces=NAMESPACES)[0].text
#            elif feed == 'favoriteartists':
#                thumb = item.xpath('./pandora:artistPhotoUrl', namespaces=NAMESPACES)[0].text
#        except:
#            thumb = None

#        dir.Append(WebVideoItem(link, title=title, summary=desc, thumb=Function(GetThumb, url=thumb)))

#    return dir
        
####################################################################################################  s
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
#def GetThumb(url):
#    if url:
#        try:
#            data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
#            return DataObject(data, 'image/jpeg')
#        except:
#            pass

#    return Redirect(R(ICON))

####################################################################################################
####################################################################################################  

class Pandora(object):
	station_id = None
	authenticated = False
	backlog = []
	
	def __init__(self):
		self.connection = PandoraConnection()
	
	def authenticate(self, username, password):
		self.authenticated = self.connection.authenticate(username, password)
		return self.authenticated
		
	def get_station_list(self):
		return self.connection.get_stations()
	
	def switch_station(self, station_id):
		if type(station_id) is dict:
			station_id = station_id['stationId']
		
		if not self.authenticated: raise ValueError("User not yet authenticated")
		
		self.backlog = []
		self.station_id = station_id
		self.backlog = self.connection.get_fragment(station_id) + self.backlog
	
	def get_next_song(self):
		if not self.authenticated: raise ValueError("User not yet authenticated")
		if not self.station_id: raise ValueError("No station selected")
		
		# get more songs
		if len(self.backlog) < 2:
			self.backlog = self.connection.get_fragment(self.station_id) + self.backlog
		
		# get next song
		return self.backlog.pop()
		
		
#if __name__ == "__main__":
#	pandora = Pandora()
#	
#	# read username
#	print "Username: "
#	username = raw_input()
#	
#	# read password
#	print "Password: "
#	password = raw_input()
#	
#	# read proxy config
#	print "Proxy: "
#	proxy = raw_input()
#	if proxy:
#		proxy_support = urllib2.ProxyHandler({"http" : proxy})
#		opener = urllib2.build_opener(proxy_support)
#		urllib2.install_opener(opener)
	
	# authenticate
#	print "Authenthicated: " + str(pandora.authenticate(username, password))
	
	# output stations (without QuickMix)
#	print "users stations:"
#	for station in pandora.getStationList():
#		if station['isQuickMix']: 
#			quickmix = station
#			print "\t" + station['stationName'] + "*"
#		else:
#			print "\t" + station['stationName']
	
#	# switch to quickmix station
#	pandora.switchStation(quickmix)
	
#	# get one song from quickmix
#	print "next song from quickmix:"
#	next =  pandora.getNextSong()
#	print next['artistName'] + ': ' + next['songName']
#	print next['audioUrlMap']['highQuality']['audioUrl']
	
####################################################################################################
####################################################################################################

class AuthenticationError(Exception):
	"""Raised when an operation encountered authentication issues."""
	pass

class PandoraConnection(object):
	partner_id = None
	partner_auth_token = None
	
	user_id = None
	user_auth_token = None
	
	time_offset = None
	
	PROTOCOL_VERSION = '5'
	RPC_URL = "://tuner.pandora.com/services/json/?"
	DEVICE_MODEL = 'android-generic'
	PARTNER_USERNAME = 'android'
	PARTNER_PASSWORD = 'AC7IBG09A3DTSYM4R41UJWL07VLN8JI7'
	AUDIO_FORMAT_MAP = {'aac': 'HTTP_64_AACPLUS_ADTS',
						'mp3': 'HTTP_128_MP3'}
	
	def __init__(self):
                self.rid = "%07i" % (Datetime.TimestampFromDatetime(Datetime.Now()) % 1e7)
		self.timedelta = 0
		
	def authenticate(self, user, pwd):
		try:
			# partner login
			partner = self.do_request('auth.partnerLogin', True, False, deviceModel=self.DEVICE_MODEL, username=self.PARTNER_USERNAME, password=self.PARTNER_PASSWORD, version=self.PROTOCOL_VERSION)
			self.partner_id = partner['partnerId']
			self.partner_auth_token = partner['partnerAuthToken']
			
			# sync
			pandora_time = int(crypt.pandora_decrypt(partner['syncTime'])[4:14])
			#self.time_offset = pandora_time - time.time()
                        self.time_offset = pandora_time - Datetime.TimestampFromDatetime(Datetime.Now())
			
			# user login
			user = self.do_request('auth.userLogin', True, True, username=user, password=pwd, loginType="user")
			self.user_id = user['userId']
			self.user_auth_token = user['userAuthToken']
			
			return True
		except:
			self.partner_id = None
			self.partner_auth_token = None
			self.user_id = None
			self.user_auth_token = None
			self.time_offset = None
			
			return False
	
	def get_stations(self):
		return self.do_request('user.getStationList', False, True)['stations']
	
	def get_fragment(self, stationId=None, additional_format="mp3"):
		songlist = self.do_request('station.getPlaylist', True, True, stationToken=stationId, additionalAudioUrl=self.AUDIO_FORMAT_MAP[additional_format])['items']
				
		self.curStation = stationId
		#self.curFormat = format
		
		return songlist
	
	def do_request(self, method, secure, crypted, **kwargs):
		url_arg_strings = []
		if self.partner_id:
			url_arg_strings.append('partner_id=%s' % self.partner_id)
		if self.user_id:
			url_arg_strings.append('user_id=%s' % self.user_id)
		if self.user_auth_token:
			url_arg_strings.append('auth_token=%s' % String.Quote(self.user_auth_token, usePlus=True))
		elif self.partner_auth_token:
			url_arg_strings.append('auth_token=%s' % String.Quote(self.partner_auth_token, usePlus=True))
		
		url_arg_strings.append('method=%s'%method)
		url = ('https' if secure else 'http') + self.RPC_URL + '&'.join(url_arg_strings)
		
		if self.time_offset:
			kwargs['syncTime'] = int(Datetime.TimestampFromDatetime(Datetime.Now())+self.time_offset)
		if self.user_auth_token:
			kwargs['userAuthToken'] = self.user_auth_token
		elif self.partner_auth_token:
			kwargs['partnerAuthToken'] = self.partner_auth_token
		data = JSON.StringFromObject(kwargs)
		
		if crypted:
			data = crypt.pandora_encrypt(data)

		# execute request
                text = HTTP.Request(url=url, data=data, headers={'User-agent': "02strich", 'Content-type': 'text/plain'}).content

		# parse result
		tree = JSON.ObjectFromString(text)
		if tree['stat'] == 'fail':
			code = tree['code']
			msg = tree['message']
			if code == 1002:
				raise AuthenticationError()
			else:
				raise ValueError("%d: %s" % (code, msg))
		elif 'result' in tree:
			return tree['result']
			

#if __name__ == "__main__":
#	pandora = PandoraConnection()
#	
#	# read username
#	print "Username: "
#	username = raw_input()
#	
#	# read password
#	print "Password: "
#	password = raw_input()
#	
#	# authenticate
#	print "Authenthicated: " + str(pandora.authenticate(username, password))
#	
#	# output stations (without QuickMix)
#	print "users stations:"
#	for station in pandora.getStations():
#		if station['isQuickMix']: 
#			quickmix = station
#			print "\t" + station['stationName'] + "*"
#		else:
#			print "\t" + station['stationName']
#	
#	# get one song from quickmix
#	print "next song from quickmix:"
#	next =  pandora.getFragment(quickmix)[0]
#	print next['artistName'] + ': ' + next['songName']
#	print next['audioUrlMap']['highQuality']['audioUrl']
	
####################################################################################################
####################################################################################################

