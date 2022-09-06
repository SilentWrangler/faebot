import interactions

import os
import typing

from dotenv import load_dotenv
from random import randint

from db import HeroCreatorV2, Adventurer, session_scope


BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(BASEDIR+'/../.env', override= True)

TOKEN = os.getenv('DISCORD_TOKEN')
bot = interactions.Client(token=TOKEN)

class State:
	creators = dict()

@bot.command(
	name = "test",
	description = "testCommand"
)
async def test(ctx: interactions.CommandContext):
    await ctx.send("Test succesful")
	
	

@bot.command()
async def char(ctx: interactions.CommandContext):
	"""Группа команд для персонажей"""
	pass

# START CHARACTER CREATION SECTION
# =================================

creation_modal = interactions.Modal(
	title="Создание персонажа",
	custom_id="create_char_form",
	components=[
		interactions.TextInput(
			style=interactions.TextStyleType.SHORT,
			label="Имя персонажа",
			custom_id="text_input_char_name",
			min_length=2,
			max_length=50,
		),
			interactions.TextInput(
			style=interactions.TextStyleType.PARAGRAPH,
			label="Описание персонажа, аспекты и трюки",
			custom_id="text_input_char_desc",
			min_length=10,
			max_length=2000,
		)
	],
)

retry_creation_button = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Заново",
    custom_id="creation_retry_button"
)

@char.subcommand()
async def make(ctx: interactions.CommandContext):
	"""Начать создание персонажа"""
	
	await ctx.popup(creation_modal)

@bot.component("creation_retry_button")
async def retry_making(ctx):
	await ctx.popup(creation_modal)


stat_up_button = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="↑",
    custom_id="stat_up_button"
)

stat_down_button = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="↓",
    custom_id="stat_down_button"
)

pick0 = interactions.Button(
    style=interactions.ButtonStyle.SECONDARY,
    label="0",
    custom_id="pick0"
)

pick1 = interactions.Button(
    style=interactions.ButtonStyle.SECONDARY,
    label="1",
    custom_id="pick1"
)

pick2 = interactions.Button(
    style=interactions.ButtonStyle.SECONDARY,
    label="2",
    custom_id="pick2"
)

pick3 = interactions.Button(
    style=interactions.ButtonStyle.SECONDARY,
    label="3",
    custom_id="pick3"
)

creation_done_button = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Готово!",
    custom_id="creation_done_button"
)

pick_row = interactions.ActionRow.new(stat_up_button, stat_down_button)
stat_rows = interactions.ActionRow.new( pick0, pick1, pick2, pick3)
creation_rows = [pick_row,stat_rows]

done_row = interactions.ActionRow.new(creation_done_button)

@bot.modal("create_char_form")
async def proceed_with_making(ctx, char_name: str, char_desc: str):
	with session_scope() as session:
		if Adventurer.name_exists(session,char_name):
			await ctx.send("Герой с таким именем уже существует. Попробовать заново?", components=retry_creation_button , ephemeral=True)
		else:
			creator = HeroCreatorV2(ctx, char_name, char_desc)
			msg = await ctx.send(creator.message, components=creation_rows)
			State.creators[msg.id] = creator

async def update_creator(ctx, creator):
	if creator.stats_left > 0:
		await ctx.edit(creator.message, components = creation_rows)
	else:
		await ctx.edit(creator.message, components =[pick_row, stat_rows,done_row ])

@bot.component("stat_up_button")
async def stat_up(ctx):
	creator = State.creators[ctx.message.id]
	if creator.ctx.user.id == ctx.user.id:
		creator.change_selected_stat(-1)
		await update_creator(ctx,creator)

@bot.component("stat_down_button")
async def stat_down(ctx):
	creator = State.creators[ctx.message.id]
	if creator.ctx.user.id == ctx.user.id:
		creator.change_selected_stat(1)
		await update_creator(ctx,creator)

@bot.component("pick0")
async def pick0_f(ctx):
	creator = State.creators[ctx.message.id]
	if creator.ctx.user.id == ctx.user.id:
		creator.pick_selected_stat(0)
		await update_creator(ctx,creator)

@bot.component("pick1")
async def pick1_f(ctx):
	creator = State.creators[ctx.message.id]
	if creator.ctx.user.id == ctx.user.id:
		creator.pick_selected_stat(1)
		await update_creator(ctx,creator)

@bot.component("pick2")
async def pick2_f(ctx):
	creator = State.creators[ctx.message.id]
	if creator.ctx.user.id == ctx.user.id:
		creator.pick_selected_stat(2)
		await update_creator(ctx,creator)
		
@bot.component("pick3")
async def pick3_f(ctx):
	creator = State.creators[ctx.message.id]
	if creator.ctx.user.id == ctx.user.id:
		creator.pick_selected_stat(3)
		await update_creator(ctx,creator)


@bot.component("creation_done_button")
async def creation_done(ctx):
	creator = State.creators[ctx.message.id]
	if creator.ctx.user.id == ctx.user.id:
		creator.finish()
		await ctx.send("Герой создан.")
		
		

# =================================
# END CHARACTER CREATION SECTION


@char.subcommand()
@interactions.option()
async def look(ctx: interactions.CommandContext, name: str):
	with session_scope() as session:
		heroes = Adventurer.name_search(session,name)
		print(heroes)
		if len(heroes)==0:
			await ctx.send('Герой не найден!')
		elif len(heroes)==1:
			try:
				embed = interactions.Embed(title = heroes[0].name)
				embed.add_field("Ресрурсы",f'**Жетоны:** {heroes[0].fate} **Стресс:** {heroes[0].stress} **Опыт:** {heroes[0].exp}')
				embed.add_field("Подходы", heroes[0].stats_message)
				print(embed)
				description_embed = interactions.Embed(
					title = heroes[0].name,
					description = heroes[0].description
				)
				msg = await ctx.send("Найденный герой:", embeds = [embed, description_embed])
			except Exception as ex:
				print(f"Error: {e}")
			#for it in heroes[0].profile_russian():
			#	await ctx.send(f'{it}')
		else:
			msg = 'Найдено несколько, уточните:\n'
			for hero in heroes:
				user = await bot.fetch_user(hero.owner_id)
				msg += f'{hero.name} ({user.display_name})\n'
			await ctx.send(msg)

bot.start()
