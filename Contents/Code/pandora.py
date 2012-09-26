from connection import PandoraConnection

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

	def music_search(self, query):
		return self.connection.music_search(query)
	
	def create_station(self, music_token):
		return self.connection.create_station(music_token)
	
	def delete_station(self, station_token):
		return self.connection.delete_station(station_token)
	
	