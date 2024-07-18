import os
import json

if not os.path.exists('db.json'):
	db = {'tokens': [],
				'id': {},
				'tg': {},
				'ds': {},
				'mine': {},
				'nick': {}}
	js = json.dumps(db, indent=2)
	with open("db.json", "w") as outfile:
		outfile.write(js)
	print('Created new db.json')

if not os.path.exists('conf.json'):
	db = {'api_token': 'None',
				'tg_token': 'None',
				'ds_token': 'None'}
	js = json.dumps(db, indent=2)
	with open("conf.json", "w") as outfile:
		outfile.write(js)
	print('Created new conf.json')

def read(file = 'db.json'):
	with open(file, "r", encoding="utf-8") as openfile:
		db = json.load(openfile)
	return db

def write(db, file = 'db.json'):
	js = json.dumps(db, indent=2, ensure_ascii=False)
	with open(file, "w", encoding="utf-8") as outfile:
		outfile.write(js)
