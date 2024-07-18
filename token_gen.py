from db import *
from uuid import uuid4

db = read()
token = str(uuid4())

db['tokens'].append(token)
write(db)

print(f'Сгенерирован новый токен: {token}')

