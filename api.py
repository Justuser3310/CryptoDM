from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db import *

app = FastAPI()

def token_check(token):
	db = read()
	if token in db['tokens']:
		return True
	else:
		return False

class User_in_db(BaseModel):
	token: str
	id: str = None
	tg: str = None
	ds: str = None
	mine: str = None
	nick: str = None
@app.post('/api/user_in_db/')
def user_in_db(it: User_in_db):
	token, id, tg, ds, mine, nick = it.token, it.id, it.tg, it.ds, it.mine, it.nick
	if token_check(token):
		db = read()
		try:
			if id and id in db['id']:
				return id
			elif tg and tg in db['tg']:
				return db['tg'][tg]
			elif ds and ds in db['ds']:
				return db['ds'][ds]
			elif mine and mine in db['mine']:
				return db['mine'][mine]
			elif nick and nick in db['nick']:
				return db['nick'][nick]
			else:
				return False
		except:
			return False
	else:
		return 'Error'


def gen_id():
	db = read()
	for i in range(1,100000):
		check = str(i)
		print(db)
		if check not in db['id']:
			return str(i)
	return 'Full?'

class User_add(BaseModel):
	token: str
	id: str = None
	tg: str = None
	ds: str = None
	mine: str = None
	nick: str
	passwd: str
@app.post('/api/user_add/')
def user_add(it: User_add):
	token, id, tg, ds, mine, nick, passwd = it.token, it.id, it.tg, it.ds, it.mine, it.nick, it.passwd
	id = gen_id()
	print(id)
	if token_check(token):
		db = read()
		db['id'][id] = {'tg': tg, 'ds': ds, 'mine': mine, 'nick': nick, 'passwd': passwd, 'bal': 0.0}
		db['nick'][nick] = id
		if tg:
			db['tg'][tg] = id
		if ds:
			db['ds'][ds] = id
		if mine:
			db['mine'][mine] = id
		write(db)
		return 'OK'
	else:
		return 'Error'

class User_del(BaseModel):
	token: str
	id: str
@app.post('/api/user_del/')
def user_del(it: User_del):
	token, id = it.token, it.id
	if token_check(token):
		db = read()
		tg, ds, mine, nick = db['id'][id]['tg'], db['id'][id]['ds'], db['id'][id]['mine'], db['id'][id]['nick']
		del db['nick'][nick]
		if tg:
			del db['tg'][tg]
		if ds:
			del db['ds'][ds]
		if mine:
			del db['mine'][mine]
		del db['id'][id]
		write(db)
		return 'OK'
	else:
		return 'Error'

class Coins_add(BaseModel):
	token: str
	id: str
	amount: str
@app.post('/api/coins_add/')
def coins_add(it: Coins_add):
	token, id, amount = it.token, it.id, float(it.amount)
	if token_check(token):
		db = read()
		db['id'][id]['bal'] += amount
		write(db)
		return 'OK'
	else:
		return 'Error'

class Coins_del(BaseModel):
	token: str
	id: str
	amount: str
@app.post('/api/coins_del/')
def coins_del(it: Coins_del):
	token, id, amount = it.token, it.id, float(it.amount)
	if token_check(token):
		db = read()
		db['id'][id]['bal'] -= amount
		write(db)
		return 'OK'
	else:
		return 'Error'

class Coins_transfer(BaseModel):
	token: str
	src_id: str
	dst_id: str
	amount: str
@app.post('/api/coins_transfer/')
def coins_transfer(it: Coins_transfer):
	token, src_id, dst_id, amount = it.token, it.src_id, it.dst_id, float(it.amount)
	if token_check(token):
		db = read()
		amount = abs(amount) # Защита от отриц. чисел
		src_bal = db['id'][src_id]['bal']
		if src_bal > amount and amount > 0.0001:
			db['id'][src_id]['bal'] -= amount
			db['id'][dst_id]['bal'] += amount
			write(db)
			return 'OK'
		else:
			return 'No_money'
	else:
		return 'Error'

class Update_tg(BaseModel):
	token: str
	id: str
	tg: str
@app.post('/api/update_tg/')
def update_tg(it: Update_tg):
	token, id, tg = it.token, it.id, it.tg
	if token_check(token):
		db = read()
		cur_tg = db['id'][id]['tg']
		try:
			del db['tg'][cur_tg]
		except:
			pass
		if tg == 'None':
			db['id'][id]['tg'] = None
		else:
			db['id'][id]['tg'] = tg
			db['tg'][tg] = id
		write(db)
		return 'OK'
	else:
		return 'Error'

class Update_ds(BaseModel):
	token: str
	id: str
	ds: str
@app.post('/api/update_ds/')
def update_ds(it: Update_ds):
	token, id, ds = it.token, it.id, it.ds
	if token_check(token):
		db = read()
		cur_ds = db['id'][id]['ds']
		try:
			del db['ds'][cur_ds]
		except:
			pass
		if ds == 'None':
			db['id'][id]['ds'] = None
		else:
			db['id'][id]['ds'] = ds
			db['ds'][ds] = id
		write(db)
		return 'OK'
	else:
		return 'Error'

class Update_mine(BaseModel):
	token: str
	id: str
	mine: str
@app.post('/api/update_mine/')
def update_mine(it: Update_mine):
	token, id, mine = it.token, it.id, it.mine
	if token_check(token):
		db = read()
		cur_mine = db['id'][id]['mine']
		del db['mine'][cur_mine]
		db['id'][id]['mine'] = mine
		db['mine'][mine] = id
		write(db)
		return 'OK'
	else:
		return 'Error'

class Update_nick(BaseModel):
	token: str
	id: str
	nick: str
@app.post('/api/update_nick/')
def update_nick(it: Update_nick):
	token, id, nick = it.token, it.id, it.nick
	if token_check(token):
		db = read()
		cur_nick = db['id'][id]['nick']
		del db['nick'][cur_nick]
		db['id'][id]['nick'] = nick
		db['nick'][nick] = id
		write(db)
		return 'OK'
	else:
		return 'Error'

class Update_passwd(BaseModel):
	token: str
	id: str
	passwd: str
@app.post('/api/update_passwd/')
def update_tg(it: Update_passwd):
	token, id, passwd = it.token, it.id, it.passwd
	if token_check(token):
		db = read()
		db['id'][id]['passwd'] = passwd
		write(db)
		return 'OK'
	else:
		return 'Error'


class Check_bal(BaseModel):
  token: str
  id: str
@app.post('/api/check_bal/')
def check_bal(it: Check_bal):
	token, id = it.token, it.id
	if token_check(token):
		db = read()
		return db['id'][id]['bal']
	else:
		return 'Error'

class Get_nick(BaseModel):
  token: str
  id: str
@app.post('/api/get_nick/')
def get_nick(it: Get_nick):
	token, id = it.token, it.id
	if token_check(token):
		db = read()
		return db['id'][id]['nick']
	else:
		return 'Error'

class Get_tg(BaseModel):
  token: str
  id: str
@app.post('/api/get_tg/')
def get_tg(it: Get_tg):
  token, id = it.token, it.id
  if token_check(token):
    db = read()
    return db['id'][id]['tg']
  else:
    return 'Error'

class Get_ds(BaseModel):
  token: str
  id: str
@app.post('/api/get_ds/')
def get_ds(it: Get_ds):
  token, id = it.token, it.id
  if token_check(token):
    db = read()
    return db['id'][id]['ds']
  else:
    return 'Error'

class Get_mine(BaseModel):
  token: str
  id: str
@app.post('/api/get_mine/')
def get_mine(it: Get_mine):
  token, id = it.token, it.id
  if token_check(token):
    db = read()
    return db['id'][id]['mine']
  else:
    return 'Error'

class Get_passwd(BaseModel):
	token: str
	id: str
@app.post('/api/get_passwd/')
def get_passwd(it: Get_passwd):
	token, id = it.token, it.id
	if token_check(token):
		db = read()
		return db['id'][id]['passwd']
	else:
		return 'Error'

# TODO: unauth from account

if __name__ == '__main__':
	import uvicorn
	uvicorn.run(app, host='127.0.0.1', port=1111)
