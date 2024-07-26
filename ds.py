import discord
from time import sleep

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

# API для отправки сообщения о переводе
# TG -> DS / DS -> Mine / ...
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
app = FastAPI()
# Для запуска API в потоке
from threading import Thread

from call2api import *
from db import *

API_TOKEN = read('conf.json')['api_token']
DS_TOKEN = read('conf.json')['ds_token']

from datetime import datetime
LCTIME = datetime.now()

# Обнуляем данные
db = read('conf.json')
db['push_src_nick'] = 0
db['push_id'] = 0
db['push_amount'] = 0
write(db, 'conf.json')

# Поток для приёма входящих переводов ТГ-ДС (костыль)
from discord.ext import tasks
@tasks.loop(seconds = 0.1)
async def push():
	db = read('conf.json')
	if db['push_id'] != 0:
		src_nick, id, amount = db['push_src_nick'], db['push_id'], db['push_amount']
		user = await bot.fetch_user(id)
		await user.send(f'''Вам перевели `{amount}` CDM.

Отправитель: `{src_nick}`''')
		db['push_src_nick'], db['push_id'], db['push_amount'] = 0, 0, 0
		write(db, 'conf.json')


@bot.event
async def on_ready():
	print(f'We have logged in as {bot.user}')
	await push.start()
	return 0

async def checkauth(message, reg = False):
	send = message.channel.send
	if user_in_db(API_TOKEN, ds=message.author.id) != 'false':
		return True
	elif reg:
		pass
	else:
		await send('''Пожалуйста, зарегистрируйтесь или войдите:
`!reg Nickname 1234567890`
`!login Nickname 1234567890`

Ник вводить желательно игровой.
Пароль любой.''')

def command(com, message):
	# Если не бот
	if message.author != bot.user:
		# Если не публичный чат
		if message.channel.type != discord.ChannelType.text:
			if message.content.startswith(f'!{com}'):
				return True

async def help(message):
	send = message.channel.send
	await send('''Исходный код: https://gitea.del.pw/justuser/CryptoDM

Доступные команды:
`/help             - Помощь
/reg ник          - Регистрация
/login ник пароль - Войти в аккаунт
/unreg            - Выйти из аккаунта
/passwd пароль    - Смена пароля
/bal              - Баланс
/pay ник сумма    - Перевод
`
''')

async def bal(message):
	send = message.channel.send
	if await checkauth(message):
		id = user_in_db(API_TOKEN, ds=message.author.id)
		coins = check_bal(API_TOKEN, id)
		nick = get_nick(API_TOKEN, id)
		await send(f'''Ваш баланс: `{coins}` CDM

Ник: `{nick}`''')

async def reg(message):
	send = message.channel.send
	if not await checkauth(message, reg=True):
		global LCTIME
		time_delta = datetime.now() - LCTIME
		if time_delta.seconds < 1:
			await send('Большая нагрузка, повторите запрос позже...')
			return 0
		if len(message.content.split()) == 3:
			com, nick, passwd = message.content.split()
			# Проверяем нет ли такого же ника
			if user_in_db(API_TOKEN, nick=nick) == 'false':
				if user_add(API_TOKEN, nick, passwd, ds=message.author.id) == 'OK':
					await send('Вы успешно зарегистрированны!')
				else:
					await send('Что-то пошло не так...')
			else:
				await send('Уже существует пользователь с таким ником')
		else:
			await send('/reg ник пароль')
	else:
		await send('Вы уже зарегистрированны')

async def login(message):
	send = message.channel.send
	if len(message.content.split()) == 3:
		global LCTIME
		time_delta = datetime.now() - LCTIME
		if time_delta.seconds < 1:
			await send('Большая нагрузка, повторите запрос позже...')
			return 0
		com, nick, passwd = message.content.split()
		id = user_in_db(API_TOKEN, nick=nick)
		if get_ds(API_TOKEN, id) != 'null':
			await send('Этот пользователь уже авторизован')
		elif get_passwd(API_TOKEN, id) == hash(passwd):
			if update_ds(API_TOKEN, id, ds=message.author.id) == 'OK':
				await send('Вы успешно авторизовались!')
			else:
				await send('Что-то пошло не так...')
		else:
			await send('Пароль не совпадает')
	else:
		await send('!login ник пароль')

async def unreg(message):
	send = message.channel.send
	id = user_in_db(API_TOKEN, ds=message.author.id)
	if update_ds(API_TOKEN, id, 'None') == 'OK':
		await send('Вы успешно вышли из аккаунта')

async def passwd(message):
	send = message.channel.send
	if await checkauth(message):
		if len(message.content.split()) == 2:
			com, passwd = message.content.split()
			id = user_in_db(API_TOKEN, ds=message.author.id)
			if update_passwd(API_TOKEN, id, passwd) == 'OK':
				await send('Пароль успешно изменён.')
			else:
				await send('Что-то пошло не так...')
		else:
			await send('!passwd пароль')

async def pay(message):
	send = message.channel.send
	if await checkauth(message):
		if len(message.content.split()) == 3:
			com, nick, amount = message.content.split()
			if float(amount) <= 0.0001:
				await send('Слишком малое или недопустимое значение.')
				return 0
			amount = str(float(amount)) # Защиты от 1000 нулей в начале
			src_id = user_in_db(API_TOKEN, ds=message.author.id)
			dst_id = user_in_db(API_TOKEN, nick=nick)
			if dst_id == 'false':
				await send('Не существует такого пользователя.')
			else:
				status = coins_transfer(API_TOKEN, src_id, dst_id, amount)
				if status == 'No_money':
					await send('Недостаточно средств.')
				elif status == 'OK':
					await send(f'''Успешно переведено `{amount}` CDM.
Адресат: `{nick}`''')
					ds_dst = get_ds(API_TOKEN, dst_id)
					tg_dst = get_tg(API_TOKEN, dst_id)
					src_nick = get_nick(API_TOKEN, src_id)
					if ds_dst != 'null':
						transfer_callback('http://127.0.0.1:3333/', API_TOKEN, src_nick, nick, amount)
					elif tg_dst != 'null':
						print(22222)
						transfer_callback('http://127.0.0.1:2222/', API_TOKEN, src_nick, nick, amount)
		else:
			await send('!pay ник количество')

@bot.event
async def on_message(message):
	send = message.channel.send
	if command('help', message):
		await help(message)
	elif command('reg', message):
		await reg(message)
	elif command('login', message):
		await login(message)
	elif command('unreg', message):
		await unreg(message)
	elif command('bal', message):
		await bal(message)
	elif command('passwd', message):
		await passwd(message)
	elif command('pay', message):
		await pay(message)


# API для переводов TG->DS / ...
class Transfer_callback_api(BaseModel):
	token: str
	src_nick: str
	dst_nick: str
	amount: str
@app.post('/api/transfer_callback/')
def transfer_callback_api(it: Transfer_callback_api):
	token, src_nick, dst_nick, amount = it.token, it.src_nick, it.dst_nick, it.amount
	db = read()
	if token in db['tokens']:
		dst_id = user_in_db(API_TOKEN, nick=dst_nick)
		ds_dst = int(get_ds(API_TOKEN, id=dst_id))
		# Передаём в поток данные (см начало скрипта)
		db = read('conf.json')
		db['push_src_nick'] = src_nick
		db['push_id'] = ds_dst
		db['push_amount'] = amount
		write(db, 'conf.json')
		return 200
	else:
		return 'Error'

def run_api():
	uvicorn.run(app, host='127.0.0.1', port=3333)

# Запускаем API для переводов
api = Thread(target=run_api)
api.Daemon = True
api.start()

# Запускаем бота
bot.run(DS_TOKEN)
