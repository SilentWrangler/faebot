# faebot
Дикорд бот для модифицированной версии Fate Accelerated Edition

## Запуск

Для запуска потребуется:

 - База данных MySql
 - Токен Discord (см. [документацию discord.py](https://discordpy.readthedocs.io/en/stable/discord.html#discord-intro) )
 - Python версии 3.7 и выше
 - Библиотека poetry для установки требований
 
 Перед тем как запускать, необходимо в корне проекта создать файл .env с примерно следующим содержимым:
 
>DISCORD_TOKEN ="yourtokenhere"
>
>DB_PASS = password
>
>DB_USER = user
>
>DB_HOST = "localhost"
>
>DB_NAME = faebot

Перед первым запуском выполнить
 >poetry install 
 
Команды для запуска (предполагая консоль, открытую в корне проекта):
 >poetry run python faebot/bot.py

## Команды

TODO
