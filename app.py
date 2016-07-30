import os
import requests
import json
import telepot
from telepot.delegate import per_chat_id, create_open
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardHide
import geopy
import geopy.distance

TOKEN = os.environ.get('TOKEN', 'TELEGRAM-BOT-TOKEN')
ENDPOINT_LIST = os.environ.get('ENDPOINT_LIST', '')
ENDPOINT_ETA = os.environ.get('ENDPOINT_ETA', '')
TIMEOUT_SEC = 30

msgKeyboardStart = '/start'
msgKeyboardCancel = '/cancel'
msgKeyboardFindStop = 'Find my nearest stop'
msgKeyboardDirectionEast = 'East'
msgKeyboardDirectionWest = 'West'
msgReady = 'Please send '+msgKeyboardStart+' to start.'
msgDirection = 'Please choose your direction.'
msgLocation = 'Please send me your location.'

stops = None
def get_stops():
	global stops
	response = requests.get(ENDPOINT_LIST)
	stops = json.loads(response.text)
	print('Stop loaded.')
	return True

def get_nearest_stop(coordinates, direction):
	location = geopy.Point(coordinates[0],coordinates[1])
	allstops = [ (p, geopy.distance.distance(geopy.Point(p[4], p[5]), location).km) for p in stops[direction] ]
	nearest_stop = min(allstops, key=lambda x: (x[1]))[0]
	code = nearest_stop[0]
	names = (nearest_stop[2], nearest_stop[1])
	coord = (nearest_stop[4], nearest_stop[5])
	print('Nearest Stop for '+str(coordinates)+' is '+code)
	return (code, names, coord)

def get_eta(code):
	response = requests.get(ENDPOINT_ETA+code)
	data = json.loads(response.text)
	records = [ (record['$']['tram_dest_tc'], record['$']['tram_dest_en'], record['$']['arrive_in_minute']+' min') for record in data['root']['metadata'] ]
	print('Eta retrieved for stop '+code)
	return records

keyboardReady = ReplyKeyboardMarkup(keyboard=[
	[KeyboardButton(text=msgKeyboardStart)],
], resize_keyboard=True)

keyboardDirection = ReplyKeyboardMarkup(keyboard=[
	[KeyboardButton(text=msgKeyboardDirectionWest), KeyboardButton(text=msgKeyboardDirectionEast)],
	[KeyboardButton(text=msgKeyboardCancel)],
], resize_keyboard=True)

keyboardLocation = ReplyKeyboardMarkup(keyboard=[
	[KeyboardButton(text=msgKeyboardFindStop, request_location=True)],
	[KeyboardButton(text=msgKeyboardCancel)],
], resize_keyboard=True)

class MessageBot(telepot.helper.ChatHandler):
	def __init__(self, seed_tuple, timeout):
		super(MessageBot, self).__init__(seed_tuple, timeout)
	def open(self, initial_msg, seed):
		self._alive = True
		self._direction = ''
		# return True
	def on_message(self, msg):
		text = msg.get('text', None)
		location = msg.get('location', None)
		print 'Incoming Message :', text, location
		if text is not None:
			if text == msgKeyboardStart:
				self.open(msg, None)
				replyMsg = msgDirection
				keyboard = keyboardDirection
				self.sender.sendMessage(replyMsg, reply_markup=keyboard)
			elif text == msgKeyboardCancel:
				self.on_close(None)
			elif text == msgKeyboardDirectionEast:
				self._direction = 'EB'
				replyMsg = msgLocation
				keyboard = keyboardLocation
				self.sender.sendMessage(replyMsg, reply_markup=keyboard)
			elif text == msgKeyboardDirectionWest:
				self._direction = 'WB'
				replyMsg = msgLocation
				keyboard = keyboardLocation
				self.sender.sendMessage(replyMsg, reply_markup=keyboard)
		elif location is not None:
			coordinates = (location['latitude'], location['longitude'])
			(code, names, coord) = get_nearest_stop(coordinates, self._direction)
			records = get_eta(code)
			replyMsg = u' / '.join(names) + '\n'
			replyMsg = replyMsg + u'\n'.join([ u' / '.join(e) for e in records ])
			keyboard = keyboardDirection
			self.sender.sendMessage(replyMsg, reply_markup=keyboard)
			self.sender.sendLocation(coord[0], coord[1], reply_markup=keyboard)
	def on_close(self, exception):
		if self._alive:
			self._alive = False
			self._direction = ''
			replyMsg = msgReady
			keyboard = keyboardReady
			self.sender.sendMessage(replyMsg, reply_markup=keyboard)

if get_stops(): 
	bot = telepot.DelegatorBot(TOKEN, [
		(per_chat_id(), create_open(MessageBot, timeout=TIMEOUT_SEC))
	])
	bot.message_loop(run_forever='Ready.')