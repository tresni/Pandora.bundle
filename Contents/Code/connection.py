import crypt

class AuthenticationError(Exception):
	"""Raised when an operation encountered authentication issues."""
	pass

class PandoraConnection(object):
	partner_id = None
	partner_auth_token = None
	
	user_id = None
	user_auth_token = None
	premium_account = None
	
	time_offset = None
	
	PROTOCOL_VERSION = 'NQ__'
	RPC_URL = "Oi8vdHVuZXIucGFuZG9yYS5jb20vc2VydmljZXMvanNvbi8@"
	DEVICE_MODEL = "YW5kcm9pZC1nZW5lcmlj"
	PARTNER_USERNAME = 'YW5kcm9pZA__'
	PARTNER_PASSWORD = 'QUM3SUJHMDlBM0RUU1lNNFI0MVVKV0wwN1ZMTjhKSTc_'
	AUDIO_FORMAT_MAP = {'aac': 'HTTP_64_AACPLUS_ADTS',
						'mp3': 'HTTP_128_MP3'}
	
	def __init__(self):
		self.rid = "%07i" % (Datetime.TimestampFromDatetime(Datetime.Now()) % 1e7)
		self.timedelta = 0
		
	def authenticate(self, user, pwd):
		#try:
			# partner login
			partner = self.do_request(
				'auth.partnerLogin',
				True,
				False,
				deviceModel=String.Decode(self.DEVICE_MODEL),
				username=String.Decode(self.PARTNER_USERNAME),
				password=String.Decode(self.PARTNER_PASSWORD),
				version=String.Decode(self.PROTOCOL_VERSION)
				)
			self.partner_id = partner['partnerId']
			self.partner_auth_token = partner['partnerAuthToken']
			
			# sync
			pandora_time = int(crypt.pandora_decrypt(partner['syncTime'])[4:14])
			self.time_offset = pandora_time - Datetime.TimestampFromDatetime(Datetime.Now())
			
			# user login
			user = self.do_request('auth.userLogin', True, True, username=user, password=pwd, loginType="user")
			self.user_id = user['userId']
			self.user_auth_token = user['userAuthToken']
			self.premium_account = not user['hasAudioAds']
			
			return True
		#except:
		#	self.partner_id = None
		#	self.partner_auth_token = None
		#	self.user_id = None
		#	self.user_auth_token = None
		#	self.time_offset = None
		#	self.premium_account = None
		#	
		#	return False
	
	def get_stations(self):
		return self.do_request('user.getStationList', False, True)['stations']
	
	def get_listener(self):
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
		url = ('https' if secure else 'http') + String.Decode(self.RPC_URL) + '&'.join(url_arg_strings)
		
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
		text = HTTP.Request(url, data=data, headers={'User-agent': "02strich", 'Content-type': 'text/plain'}).content

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
			
