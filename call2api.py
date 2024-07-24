from requests import post
from json import dumps
from xxhash import xxh32

from db import *

global url_pre
url_pre = 'http://127.0.0.1:1111/'

def hash(text):
	text = str(text)
	return xxh32(text).hexdigest()

def call(api_url, data):
	response = post(url_pre + api_url, data=dumps(data))
	print(response.status_code)
	print(response.text)
	return response.text.replace('"', '')

def user_in_db(token, id=None, tg=None, ds=None, mine=None, nick=None):
	data = {'token': token}
	if id:
		data['id'] = id
	elif tg:
		data['tg'] = str(tg)
	elif ds:
		data['ds'] = str(ds)
	elif mine:
		data['mine'] = mine
	elif nick:
		data['nick'] = nick
	#print(data)
	return call('api/user_in_db/', data)

def user_add(token, nick, passwd, tg=None, ds=None, mine=None):
	passwd = hash(passwd)
	data = {'token': token, 'nick': nick, 'passwd': passwd}
	if tg:
		data['tg'] = str(tg)
	if ds:
		data['ds'] = str(ds)
	if mine:
		data['mine'] = mine
	print(data)
	return call('api/user_add/', data)

def user_del(token, id):
	data = {'token': token, 'id': id}
	return call('api/user_del/', data)

def coins_add(token, id, amount):
	data = {'token': token, 'id': id, 'amount': amount}
	return call('api/coins_add/', data)

def coins_del(token, id, amount):
	data = {'token': token, 'id': id, 'amount': amount}
	return call('api/coins_del/', data)

def coins_transfer(token, src_id, dst_id, amount):
	data = {'token': token, 'src_id': src_id, 'dst_id': dst_id, 'amount': amount}
	return call('api/coins_transfer/', data)

def update_tg(token, id, tg):
	if tg != None:
		data = {'token': token, 'id': id, 'tg': str(tg)}
	else:
		data = {'token': token, 'id': id, 'tg': None}
	return call('api/update_tg/', data)

def update_ds(token, id, ds):
	data = {'token': token, 'id': id, 'ds': str(ds)}
	return call('api/update_ds/', data)

def update_mine(token, id, mine):
	data = {'token': token, 'id': id, 'mine': str(mine)}
	return call('api/update_mine/', data)

def update_nick(token, id, nick):
  data = {'token': token, 'id': id, 'nick': nick}
  return call('api/update_nick/', data)

def update_passwd(token, id, passwd):
  data = {'token': token, 'id': id, 'passwd': hash(passwd)}
  return call('api/update_passwd/', data)


def check_bal(token, id):
	data = {'token': token, 'id': id}
	return call('api/check_bal/', data)

def get_nick(token, id):
	data = {'token': token, 'id': id}
	return call('api/get_nick/', data)

def get_tg(token, id):
  data = {'token': token, 'id': id}
  return call('api/get_tg/', data)

def get_ds(token, id):
  data = {'token': token, 'id': id}
  return call('api/get_ds/', data)

def get_mine(token, id):
  data = {'token': token, 'id': id}
  return call('api/get_mine/', data)

def get_passwd(token, id):
  data = {'token': token, 'id': id}
  return call('api/get_passwd/', data)

def transfer_callbak(addr, token, src_id, amount):
	amount = str(amount)
	data = {'token': token, 'src_id': src_id, 'amount': amount}
	return call(addr + 'api/get_passwd/', data)

#print( user_in_db('ee77b9d8-44f3-4e01-a702-69d5524ee50b', '1234') )
