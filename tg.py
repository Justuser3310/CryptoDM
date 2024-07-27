import telebot
from telebot.formatting import hcode
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime

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
TG_TOKEN = read('conf.json')['tg_token']
bot = telebot.TeleBot(TG_TOKEN)

LCTIME = datetime.now()

def checkauth(message, reg = False):
	if user_in_db(API_TOKEN, tg=message.chat.id) != 'false':
		return True
	else:
		if not reg:
			markup = ReplyKeyboardMarkup(resize_keyboard=True)
			markup.add('Баланс')
			#markup.add('Перевод')
			markup.add('Помощь')
			bot.reply_to(message, '''Пожалуйста, зарегистрируйтесь или войдите:
/reg Nickname 1234567890
/login Nickname 1234567890

Ник вводить желательно игровой.
Пароль любой.''', reply_markup=markup)
		return False

@bot.message_handler(commands=['start'])
def start(message):
	markup = ReplyKeyboardMarkup(resize_keyboard=True)

	markup.add('Баланс')
	markup.add('Помощь')

	if not checkauth(message):
		pass
	else:
		bot.reply_to(message, 'Всё работает', reply_markup=markup)

@bot.message_handler(commands=['help'])
def help(message):
	bot.reply_to(message, f'''Исходный код: https://gitea.del.pw/justuser/CryptoDM

Доступные команды:
{hcode("""/help             - Помощь
/reg ник          - Регистрация
/login ник пароль - Войти в аккаунт
/unreg            - Выйти из аккаунта
/passwd пароль    - Смена пароля
/nick ник         - Смена ника
/bal              - Баланс
/pay ник сумма    - Перевод
""")}
''', parse_mode='HTML')

@bot.message_handler(commands=['reg'])
def reg(message):
	if not checkauth(message, reg=True):
		global LCTIME
		time_delta = datetime.now() - LCTIME
		if time_delta.seconds < 1:
			bot.reply_to(message, 'Большая нагрузка, повторите запрос позже...')
			return 0
		if len(message.text.split()) == 3:
			com, nick, passwd = message.text.split()
			# Проверяем нет ли такого же ника
			if user_in_db(API_TOKEN, nick=nick) == 'false':
				if user_add(API_TOKEN, nick, passwd, tg=message.chat.id) == 'OK':
					bot.reply_to(message, 'Вы успешно зарегистрированны!')
				else:
					bot.reply_to(message, 'Что-то пошло не так...')
			else:
				bot.reply_to(message, 'Уже существует пользователь с таким ником')
		else:
			bot.reply_to(message, '/reg ник пароль')
	else:
		bot.reply_to(message, 'Вы уже зарегистрированны')

@bot.message_handler(commands=['login'])
def login(message):
	if len(message.text.split()) == 3:
		global LCTIME
		time_delta = datetime.now() - LCTIME
		if time_delta.seconds < 1:
			bot.reply_to(message, 'Большая нагрузка, повторите запрос позже...')
			return 0
		com, nick, passwd = message.text.split()
		id = user_in_db(API_TOKEN, nick=nick)
		print('!!!!', get_tg(API_TOKEN, id))
		if get_tg(API_TOKEN, id) != 'null':
			bot.reply_to(message, 'Этот пользователь уже авторизован')
		elif get_passwd(API_TOKEN, id) == hash(passwd):
			if update_tg(API_TOKEN, id, message.chat.id) == 'OK':
				bot.reply_to(message, 'Вы успешно авторизовались!')
			else:
				bot.reply_to(message, 'Что-то пошло не так...')
		else:
			bot.reply_to(message, 'Пароль не совпадает')
	else:
		bot.reply_to(message, '/login пароль')

@bot.message_handler(commands=['unreg'])
def unreg(message):
  id = user_in_db(API_TOKEN, tg=message.chat.id)
  if update_tg(API_TOKEN, id, 'None') == 'OK':
    bot.reply_to(message, 'Вы успешно вышли из аккаунта')

'''
@bot.message_handler(commands=['unreg'])
def unreg(message):
	id = user_in_db(API_TOKEN, tg=message.chat.id)
	print(int(id))
	print("1")
	if user_del(API_TOKEN, id) == 'OK':
		bot.reply_to(message, 'OK')
'''

@bot.message_handler(commands=['passwd'])
def passwd(message):
	if checkauth(message):
		if len(message.text.split()) == 2:
			com, passwd = message.text.split()
			id = user_in_db(API_TOKEN, tg=message.chat.id)
			if update_passwd(API_TOKEN, id, passwd) == 'OK':
				bot.reply_to(message, 'Пароль успешно изменён.')
			else:
				bot.reply_to(message, 'Что-то пошло не так...')
		else:
			bot.reply_to(message, '/passwd новый_пароль')


@bot.message_handler(commands=['nick'])
def nick(message):
	if checkauth(message):
		if len(message.text.split()) == 2:
			com, new_nick = message.text.split()
			id = user_in_db(API_TOKEN, tg=message.chat.id)
			if update_nick(API_TOKEN, id, new_nick) == 'OK':
				bot.reply_to(message, 'Ник успешно изменён')
			else:
				bot.reply_to(message, 'Что-то пошло не так...')
		else:
			bot.reply_to(message, '/nick новый_ник')

@bot.message_handler(commands=['bal'])
def bal(message):
	if checkauth(message):
		id = user_in_db(API_TOKEN, tg=message.chat.id)
		coins = check_bal(API_TOKEN, id)
		nick = get_nick(API_TOKEN, id)
		bot.reply_to(message, f'''Ваш баланс: {hcode(coins)} CDM

Ник: {hcode(nick)}''', parse_mode='HTML')

@bot.message_handler(commands=['pay'])
def pay(message):
	if checkauth(message):
		if len(message.text.split()) == 3:
			com, nick, amount = message.text.split()
			if float(amount) <= 0.0001:
				bot.reply_to(message, 'Слишком малое или недопустимое значение.')
				return 0
			amount = str(float(amount)) # Защиты от 1000 нулей в начале
			src_id = user_in_db(API_TOKEN, tg=message.chat.id)
			dst_id = user_in_db(API_TOKEN, nick=nick)
			if dst_id == 'false':
				bot.reply_to(message, 'Не существует такого пользователя.')
			else:
				status = coins_transfer(API_TOKEN, src_id, dst_id, amount)
				if status == 'No_money':
					bot.reply_to(message, 'Недостаточно средств.')
				elif status == 'OK':
					bot.reply_to(message, f'''Успешно переведено {hcode(amount)} CDM.
Адресат: {hcode(nick)}''', parse_mode='HTML')

					tg_dst = get_tg(API_TOKEN, dst_id)
					ds_dst = get_ds(API_TOKEN, dst_id)
					src_nick = get_nick(API_TOKEN, src_id)
					if tg_dst != 'null':
						transfer_callback('http://127.0.0.1:2222/', API_TOKEN, src_nick, nick, amount)
					elif ds_dst != 'null':
						transfer_callback('http://127.0.0.1:3333/', API_TOKEN, src_nick, nick, amount)
		else:
			bot.reply_to(message, '/pay ник количество')

@bot.message_handler(func=lambda message: True)
def checks(message):
	if message.text == 'Баланс':
		bal(message)
	elif message.text == 'Помощь':
		help(message)

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
		tg_dst = int(get_tg(API_TOKEN, id=dst_id))
		print(tg_dst)
		bot.send_message(tg_dst, f'''Вам перевели {hcode(amount)} CDM.

Отправитель: {hcode(src_nick)}''', parse_mode='HTML')
		return 200
	else:
		return 'Error'

def run_api():
	uvicorn.run(app, host='127.0.0.1', port=2222)

# Запускаем API для переводов
api = Thread(target=run_api)
api.Daemon = True
api.start()

# Запускаем бота
bot.infinity_polling()
