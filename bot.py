import os
import typing

from dotenv import load_dotenv
from discord.ext import commands
from random import randint

from db import HeroCreator, Adventurer, session_scope


load_dotenv(override= True)
TOKEN = os.getenv('DISCORD_TOKEN')


PREFIX = '-'
bot = commands.Bot(command_prefix=PREFIX)


class State:
    test_msg = None
    creators = dict()
    characters = dict()



class Stat(commands.Converter):
    async def convert(self, ctx, argument):
        stats = {
            'careful':'careful',
            'flashy': 'flashy',
            'quick':'quick',
            'strong':'strong',
            'clever':'clever',
            'sneaky':'sneaky',
            'rich':'rich',
            'аккуратность':'careful',
            'эффектность': 'flashy',
            'проворность':'quick',
            'сила':'strong',
            'ум':'clever',
            'хитрость':'sneaky',
            'достаток':'rich',
            }
        if argument.lower() not in stats:
            try:
                ars = argument.lower().split('d')
                if len(ars)!=2:
                    raise commands.BadArgument()
                iters = int(ars[0])
                sides = int(ars[1])
                return f'dice:{iters}d{sides}'
            except:
                raise commands.BadArgument()
        return stats[argument.lower()]


@bot.command()
async def test(ctx):
    State.test_msg = await ctx.send('reaction number: - ')


@bot.group()
async def char(ctx):
    """Группа для управления персонажами.
    """
    print('char command')
    pass

@char.command()
async def make(ctx):
    """Начинает создание персонажа"""
    chan = ctx.channel.id
    if chan in State.creators:
        if not State.creators[chan].done:
            await ctx.send('Этот канал занят! Создайте персонажа в другом канале.')
            return
    State.creators[chan] = HeroCreator(ctx.author, ctx.channel)
    await State.creators[chan].start()

@char.command()
async def look(ctx, name: str):
    """Просматривает профиль героя"""
    with session_scope() as session:
        heroes = Adventurer.name_search(session,name)
        if len(heroes)==0:
            await ctx.send('Герой не найден!')
        elif len(heroes)==1:
            for it in heroes[0].profile_russian():
                await ctx.send(f'{it}')
        else:
            msg = 'Найдено несколько, уточните:\n'
            for hero in heroes:
                user = await bot.fetch_user(hero.owner_id)
                msg += f'{hero.name} ({user.display_name})\n'
            await ctx.send(msg)

@char.command()
async def switch(ctx, name: str):
    """переключается на героя"""
    with session_scope() as session:
        heroes = Adventurer.name_owner_search(session,name,ctx.author.id)
        if len(heroes)==0:
            await ctx.send('Герой не найден!')
        elif len(heroes)==1:
            for it in heroes[0].profile_russian():
                await ctx.send(f'{it}')

            State.characters[ctx.author.id] = heroes[0].id
        else:
            msg = 'Найдено несколько, уточните:\n'
            for hero in heroes:
                msg += f'{hero.name}\n'
            await ctx.send(msg)

@char.command()
async def cancel(ctx):
    """Отменяет создание персонажа"""
    chan = ctx.channel.id
    if chan in State.creators:
        if State.creators[chan].done:
              await ctx.send('Здесь не создаётся персонаж.')
              return
        if State.creators[chan].user == ctx.author:
            State.creators.pop(chan, None)
            await ctx.send('Создание отменено.')
        else:
            await ctx.send('Отмена может быть произведена только создающим.')
    else:
        await ctx.send('Здесь не создаётся персонаж.')


@bot.command()
async def roll(ctx, stat: Stat, name : typing.Optional[str]):
    """Делает бросок на определённый подход"""
    if stat.startswith('dice'):
        _, exp = stat.split(':')
        iters_str, sides_str = exp.split('d')
        iters, sides = int(iters_str), int(sides_str)
        rolls = []
        for i in range(iters):
            rolls.append(randint(1,sides))
        await ctx.send(f'{ctx.author.mention} : {sum(rolls)} {rolls}')
        return
    with session_scope() as session:
        char = None
        if name is None:
            if ctx.author.id not in State.characters:
                await ctx.send("Укажите имя персонажа или используйте команду char switch для выбора персонажа по умолчанию")
                return
            charid = State.characters[ctx.author.id]
            char = Adventurer.get_by_id(session,charid)
        else:
            heroes = Adventurer.name_owner_search(session,name,ctx.author.id)
            if len(heroes)==0:
                await ctx.send('Герой не найден!')
                return
            elif len(heroes)==1:
                char = heroes[0]
            else:
                msg = 'Найдено несколько, уточните:\n'
                for hero in heroes:
                    msg += f'{hero.name}\n'
                await ctx.send(msg)
                return
        roll = char.make_check(stat)
        await ctx.send(f'{ctx.author.mention} : {roll[0]} {roll[1]}')

@bot.event
async def on_reaction_add(reaction, user):
    if State.test_msg is not None:
        if reaction.message.id == State.test_msg.id:
            await State.test_msg.edit(content = f'reaction number: {HeroCreator.em_to_num(reaction.emoji)}')
    chan = reaction.message.channel.id
    if chan in State.creators:
        if State.creators[chan].message is not None:
            if reaction.message.id == State.creators[chan].message.id and user.id == State.creators[chan].user.id:
                number  = HeroCreator.em_to_num(reaction.emoji)
                if number is not None:

                    await State.creators[chan].add_number(number)
@bot.group()
async def fate(ctx):
    pass

@fate.command()
async def use(ctx, name : typing.Optional[str]):
    char = None
    with session_scope() as session:
        if name is None:
            if ctx.author.id not in State.characters:
                await ctx.send("Укажите имя персонажа или используйте команду char switch для выбора персонажа по умолчанию")
                return
            charid = State.characters[ctx.author.id]
            char = Adventurer.get_by_id(session,charid)
        else:
            heroes = Adventurer.name_owner_search(session,name,ctx.author.id)
            if len(heroes)==0:
                await ctx.send('Герой не найден!')
                return
            elif len(heroes)==1:
                char = heroes[0]
            else:
                msg = 'Найдено несколько, уточните:\n'
                for hero in heroes:
                    msg += f'{hero.name}\n'
                await ctx.send(msg)
                return
        if char.fate>0:
            char.fate-=1
            await ctx.send(f"Использовано очко судьбы. Осталось {char.fate}")
            char.save(session)
        else:
            await ctx.send(f"Нет очков судьбы!")

@fate.command()
@commands.has_role("Повелитель бота")
async def give(ctx, name : str, amount : int):
    with session_scope() as session:
        heroes = Adventurer.name_search(session,name)
        if len(heroes)==0:
            await ctx.send('Герой не найден!')
        elif len(heroes)==1:
            heroes[0].fate+=amount
            heroes[0].save(session)
            await ctx.send(f'{heroes[0].name} теперь имеет {heroes[0].fate} очков судьбы')
        else:
            msg = 'Найдено несколько, уточните:\n'
            for hero in heroes:
                user = await bot.fetch_user(hero.owner_id)
                msg += f'{hero.name} ({user.display_name})\n'
            await ctx.send(msg)


@bot.command()
@commands.has_role("Повелитель бота")
async def stress(ctx,name : str, amount : int):
    with session_scope() as session:
        heroes = Adventurer.name_search(session,name)
        if len(heroes)==0:
            await ctx.send('Герой не найден!')
        elif len(heroes)==1:
            heroes[0].stress+=amount
            heroes[0].save(session)
            await ctx.send(f'{heroes[0].name} теперь имеет {heroes[0].stress} стресса')
        else:
            msg = 'Найдено несколько, уточните:\n'
            for hero in heroes:
                user = await bot.fetch_user(hero.owner_id)
                msg += f'{hero.name} ({user.display_name})\n'
            await ctx.send(msg)


@bot.event
async def on_message(message):
    chan = message.channel.id
    if chan in State.creators:
        if message.author == State.creators[chan].user:
            await State.creators[chan].add_text(message.content)
    await bot.process_commands(message)


bot.run(TOKEN)