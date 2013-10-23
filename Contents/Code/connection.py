import blowfish

class AuthenticationError(Exception):
	"""Raised when an operation encountered authentication issues."""
	pass

class PandoraConnection(object):
	partner_id = None
	partner_auth_token = None
	
	user_id = None
	user_auth_token = None
	premium_account = None
	
	time_offset = 0
	
	PROTOCOL_VERSION = 'NQ__'
	#RPC_URL = 'Oi8vaW50ZXJuYWwtdHVuZXIucGFuZG9yYS5jb20vc2VydmljZXMvanNvbi8@'
	#DEVICE_MODEL = 'RDAx'
	#PARTNER_USERNAME = 'cGFuZG9yYSBvbmU_'
	#PARTNER_PASSWORD = 'VFZDS0lCR1M5QU85VFNZTE5ORlVNTDA3NDNMSDgyRA__'
	#ENCRYPT_KEY = 'MiUzV0NMKkpVJE1QXTQ_'
	#DECRYPT_KEY = 'VSNJTyRSWlBBQiVWWDI_'

	RPC_URL = 'Oi8vdHVuZXIucGFuZG9yYS5jb20vc2VydmljZXMvanNvbi8@'
	DEVICE_MODEL = 'YW5kcm9pZC1nZW5lcmlj'
	PARTNER_USERNAME = 'YW5kcm9pZA__'
	PARTNER_PASSWORD = 'QUM3SUJHMDlBM0RUU1lNNFI0MVVKV0wwN1ZMTjhKSTc_'
	ENCRYPT_KEY = 'NiMyNkZSTCRaV0Q_'
	DECRYPT_KEY = 'Uj1VIUxIJE8yQiM_'	

	def __init__(self):
		pass
		
	def authenticate(self, user, pwd):
		
		# partner login
		try:
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
			pandora_time = int(blowfish.pandora_decrypt(String.Decode(self.DECRYPT_KEY), partner['syncTime'])[4:14])
			self.time_offset = pandora_time - Datetime.TimestampFromDatetime(Datetime.Now())
			
			# user login
			user = self.do_request('auth.userLogin', True, True, username=user, password=pwd, loginType="user")
			self.user_id = user['userId']
			self.user_auth_token = user['userAuthToken']
			self.premium_account = not user['hasAudioAds']
		except:
			pass
		
		if self.partner_auth_token is not None and self.user_auth_token is not None:
			return True
		else:
			return False
	
	def get_stations(self):
		return self.do_request('user.getStationList', False, True)['stations']
	
	def get_fragment(self, stationId=None):
		return self.do_request('station.getPlaylist', True, True, stationToken=stationId)['items']
	
	def music_search(self, query):
		return self.do_request('music.search', False, True, searchText=query)
	
	def create_station(self, music_token):
		return self.do_request('station.createStation', False, True, musicToken=music_token)
	
	def delete_station(self, station_token):
		return self.do_request('station.deleteStation', False, True, stationToken=station_token)

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
		
		url_arg_strings.append('method=%s' % method)
		url = ('https' if secure else 'http') + String.Decode(self.RPC_URL) + '&'.join(url_arg_strings)
				
		kwargs['syncTime'] = int(Datetime.TimestampFromDatetime(Datetime.Now())+self.time_offset)
		if self.user_auth_token:
			kwargs['userAuthToken'] = self.user_auth_token
		elif self.partner_auth_token:
			kwargs['partnerAuthToken'] = self.partner_auth_token
		data = JSON.StringFromObject(kwargs)
		#Log ('request data --> ' + data)
		
		if crypted:
			data = blowfish.pandora_encrypt(String.Decode(self.ENCRYPT_KEY), data)

		# execute request
		text = HTTP.Request(url, data=data, headers={'Content-type': 'text/plain'}, cacheTime=0).content
		#Log ('response data --> ' + text)

		tree = JSON.ObjectFromString(text)
		if tree['stat'] == 'fail':
			raise RuntimeError("%d: %s" % (tree['code'], tree['message']))
			return tree['result']
		elif 'result' in tree:
			return tree['result']



			
