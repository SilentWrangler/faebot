import interactions

import os
import typing

from dotenv import load_dotenv
from random import randint

from db import HeroCreatorV2, Adventurer, session_scope, HeroLvlUp


BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(BASEDIR+'/../.env', override= True)

TOKEN = os.getenv('DISCORD_TOKEN')
bot = interactions.Client(token=TOKEN)

stat_to_russian = {
    'careful':'аккуратность',
    'flashy': 'эффектность',
    'quick':'проворность',
    'strong':'сила',
    'clever':'ум',
    'sneaky':'хитрость',
    'rich':'достаток'
}

class State:
	creators = dict()
	characters = dict()
	updated_characters = dict()
	damaged_characters = dict()
	roll_approaches = dict()

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
	if isinstance(creator, HeroLvlUp):
		await ctx.edit(creator.message, components = upgrade_rows)
	else:
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
	else:
		await ctx.send("Этот персонаж создаётся другим игроком",ephemeral = True)

@bot.component("stat_down_button")
async def stat_down(ctx):
	creator = State.creators[ctx.message.id]
	if creator.ctx.user.id == ctx.user.id:
		creator.change_selected_stat(1)
		await update_creator(ctx,creator)
	else:
		await ctx.send("Этот персонаж создаётся другим игроком",ephemeral = True)

@bot.component("pick0")
async def pick0_f(ctx):
	creator = State.creators[ctx.message.id]
	if creator.ctx.user.id == ctx.user.id:
		creator.pick_selected_stat(0)
		await update_creator(ctx,creator)
	else:
		await ctx.send("Этот персонаж создаётся другим игроком",ephemeral = True)

@bot.component("pick1")
async def pick1_f(ctx):
	creator = State.creators[ctx.message.id]
	if creator.ctx.user.id == ctx.user.id:
		creator.pick_selected_stat(1)
		await update_creator(ctx,creator)
	else:
		await ctx.send("Этот персонаж создаётся другим игроком",ephemeral = True)
	
@bot.component("pick2")
async def pick2_f(ctx):
	creator = State.creators[ctx.message.id]
	if creator.ctx.user.id == ctx.user.id:
		creator.pick_selected_stat(2)
		await update_creator(ctx,creator)
	else:
		await ctx.send("Этот персонаж создаётся другим игроком",ephemeral = True)
	
@bot.component("pick3")
async def pick3_f(ctx):
	creator = State.creators[ctx.message.id]
	if creator.ctx.user.id == ctx.user.id:
		creator.pick_selected_stat(3)
		await update_creator(ctx,creator)
	else:
		await ctx.send("Этот персонаж создаётся другим игроком",ephemeral = True)


@bot.component("creation_done_button")
async def creation_done(ctx):
	creator = State.creators.get(ctx.message.id)
	if creator is None:
		await ctx.send("Этот персонаж больше не создаётся/изменяется", ephemeral = True)
	elif creator.done:
		await ctx.send("Этот персонаж больше не создаётся/изменяется", ephemeral = True)
	else:
		if creator.ctx.user.id == ctx.user.id:
			creator.finish()
			State.creators.pop(ctx.message.id)
			await ctx.send("Герой создан.")
		else:
			await ctx.send("Этот персонаж создаётся/изменяется другим игроком",ephemeral = True)
		
		

# =================================
# END CHARACTER CREATION SECTION

# START CHARACTER UPGRADE SECTION
#======================================

 
plus_one = interactions.Button(
    style=interactions.ButtonStyle.SECONDARY,
    label="+",
    custom_id="plus_one"
)

minus_one = interactions.Button(
    style=interactions.ButtonStyle.SECONDARY,
    label="-",
    custom_id="minus_one"
)

pm_row = interactions.ActionRow.new(minus_one, plus_one)

upgrade_rows = [pick_row, pm_row, done_row]

@char.subcommand()
@interactions.option(description = "Имя героя для изменения")
async def upgrade(ctx, name: str):
	"""Использовать опыт для улучшения подходов"""
	with session_scope() as session:
		heroes = Adventurer.name_owner_search(session,name,int(ctx.author.id))
		target = None
		if len(heroes)==0:
			await ctx.send('Герой не найден!', ephemeral = True)
			return interactions.StopCommand
		elif len(heroes)==1:
			target = heroes[0]
		else:
			msg = 'Найдено несколько, уточните:\n'
			for hero in heroes:
				if hero.name == name:
					target = hero
					break
				msg += f'{hero.name}\n'
			if target is None:
				await ctx.send(msg, ephemeral = True)
				return interactions.StopCommand
		creator = HeroLvlUp(ctx,target)
		msg = await ctx.send(creator.message, components = upgrade_rows)
		State.creators[msg.id] = creator

@bot.component("plus_one")
async def plus_one_f(ctx):
	creator = State.creators[ctx.message.id]
	if creator.ctx.user.id == ctx.user.id:
		creator.pick_selected_stat(1)
		await update_creator(ctx,creator)
	else:
		await ctx.send("Этот персонаж изменяется другим игроком",ephemeral = True)

@bot.component("minus_one")
async def minus_one_f(ctx):
	creator = State.creators[ctx.message.id]
	if creator.ctx.user.id == ctx.user.id:
		creator.pick_selected_stat(-1)
		await update_creator(ctx,creator)
	else:
		await ctx.send("Этот персонаж изменяется другим игроком",ephemeral = True)
	
#======================================
# END CHARACTER UPGRADE SECTION



@char.subcommand()
@interactions.option(description = "Имя персонажа. Оставить пустым, чтобы просмотреть всех.", required = False)
async def look(ctx: interactions.CommandContext, name: str = ""):
	"""Просмотреть профиль героя"""
	with session_scope() as session:
		heroes = Adventurer.name_search(session,name)
		print(heroes)
		if len(heroes)==0:
			await ctx.send('Герой не найден!')
		elif len(heroes)==1:
			try:
				embed = interactions.Embed(title = heroes[0].name)
				embed.add_field("Ресурсы",f'**Жетоны:** {heroes[0].fate} **Стресс:** {heroes[0].stress} **Опыт:** {heroes[0].exp}')
				embed.add_field("Подходы", heroes[0].stats_message)
				
				description_embed = interactions.Embed(
					title = heroes[0].name,
					description = heroes[0].description
				)
				msg = await ctx.send("Найденный герой:", embeds = [description_embed, embed, ])
			except Exception as ex:
				print(f"Error: {e}")
			#for it in heroes[0].profile_russian():
			#	await ctx.send(f'{it}')
		else:
			msg = 'Найдено несколько, уточните:\n'
			for hero in heroes:
				if hero.name == name: #Exact name match
					try:
						embed = interactions.Embed(title = hero.name)
						embed.add_field("Ресурсы",f'**Жетоны:** {hero.fate} **Стресс:** {hero.stress} **Опыт:** {hero.exp}')
						embed.add_field("Подходы", hero.stats_message)
						
						description_embed = interactions.Embed(
							title = hero.name,
							description = hero.description
						)
						msg = await ctx.send("Найденный герой:", embeds = [description_embed, embed, ])
						return interactions.StopCommand
					except Exception as ex:
						print(f"Error: {e}")
				user = await interactions.get(bot, interactions.User, object_id=hero.owner_id)
				msg += f'{hero.name} ({user.username}#{user.discriminator})\n'
			await ctx.send(msg)


@char.subcommand()
@interactions.option(description = "Имя персонажа, на которого надо переключиться.")
async def switch(ctx, name: str):
	"""Переключиться на героя"""
	with session_scope() as session:
		heroes = Adventurer.name_owner_search(session,name,ctx.author.id)
		if len(heroes)==0:
			await ctx.send('Герой не найден!')
		elif len(heroes)==1:
			embed = interactions.Embed(title = heroes[0].name)
			embed.add_field("Ресурсы",f'**Жетоны:** {heroes[0].fate} **Стресс:** {heroes[0].stress} **Опыт:** {heroes[0].exp}')
			embed.add_field("Подходы", heroes[0].stats_message)
			print(embed)
			description_embed = interactions.Embed(
				title = heroes[0].name,
				description = heroes[0].description
			)
			msg = await ctx.send("Найденный герой:", embeds = [embed, description_embed])
			State.characters[ctx.author.id] = heroes[0].id
		else:
			msg = 'Найдено несколько, уточните:\n'
			for hero in heroes:
				if hero.name == name:
					try:
						embed = interactions.Embed(title = hero.name)
						embed.add_field("Ресурсы",f'**Жетоны:** {hero.fate} **Стресс:** {hero.stress} **Опыт:** {hero.exp}')
						embed.add_field("Подходы", hero.stats_message)
						print(embed)
						description_embed = interactions.Embed(
							title = hero.name,
							description = hero.description
						)
						msg = await ctx.send("Найденный герой:", embeds = [description_embed, embed, ])
						State.characters[ctx.author.id] = hero.id
						return interactions.StopCommand
					except Exception as ex:
						print(f"Error: {e}")
				msg += f'{hero.name}\n'
			await ctx.send(msg)

# START CHARACTER CHANGE SECTION
#======================================
@char.subcommand()
@interactions.option(description = "Имя героя для изменения")
async def change(ctx, name: str):
	"""Изменить имя и описание персонажа"""
	with session_scope() as session:
		heroes = Adventurer.name_owner_search(session,name,int(ctx.author.id))
		target = None
		if len(heroes)==0:
			await ctx.send('Герой не найден!', ephemeral = True)
		elif len(heroes)==1:
			target = heroes[0]
		else:
			msg = 'Найдено несколько, уточните:\n'
			for hero in heroes:
				if hero.name == name:
					target = hero
					break
				msg += f'{hero.name}\n'
			if target is None:
				await ctx.send(msg, ephemeral = True)
				return interactions.StopCommand
		update_modal = interactions.Modal(
			title="Создание персонажа",
			custom_id="update_char_form",
			components=[
				interactions.TextInput(
					style=interactions.TextStyleType.SHORT,
					label="Имя персонажа",
					custom_id="text_input_char_name",
					min_length=2,
					max_length=50,
					value = target.name
				),
					interactions.TextInput(
					style=interactions.TextStyleType.PARAGRAPH,
					label="Описание персонажа, аспекты и трюки",
					custom_id="text_input_char_desc",
					min_length=10,
					max_length=2000,
					value = target.description
				)
			],
		)
		State.updated_characters[ctx.user.id] = target.id
		await ctx.popup(update_modal)
		
@bot.modal("update_char_form")
async def proceed_with_change(ctx, char_name: str, char_desc: str):
	with session_scope() as session:
		hero = Adventurer.get_by_id(session, State.updated_characters.pop(ctx.user.id))
		hero.name = char_name
		hero.description = char_desc
		hero.save(session)
		embed = interactions.Embed(title = hero.name)
		embed.add_field("Ресурсы",f'**Жетоны:** {hero.fate} **Стресс:** {hero.stress} **Опыт:** {hero.exp}')
		embed.add_field("Подходы", hero.stats_message)
		
		description_embed = interactions.Embed(
			title = hero.name,
			description = hero.description
		)
		msg = await ctx.send("Изменение успешно!", embeds = [description_embed, embed, ])

#======================================
# END CHARACTER CHANGE SECTION



@bot.command()
async def roll(ctx):
	"""Бросок костей"""
	pass

@roll.error
async def roll_error(ctx,error):
	await ctx.send(str(error), ephemeral=True)

@roll.subcommand(name = "dice", description = "Бросок костей в формате XdY")
@interactions.option(description = "Бросок формата XdY, где X - количество костей, а Y - количество граней")
async def roll_dice(ctx, dice: str):
	result = []
	rolls = 0
	sides = 0
	if dice.lower().startswith('d'):
		try:
			rolls = 1
			sides = int(dice[1:])
		except ValueError:
			raise ValueError("Неверный формат броска")
	else:
		try:
			rolls_s, sides_s = dice.lower().split('d')
			rolls = int(rolls_s)
			sides = int(sides_s)
		except Exception:
			raise Exception("Неверный формат броска")
	for i in range(rolls):
		result.append(randint(1,sides))
		
	await ctx.send(f"{dice}: {sum(result)} {result}")
# START FATE ROLL SECTION
#======================================
@roll.subcommand(name = "fate", description = "Бросок по системе FATE")
async def roll_fate(ctx):

	await ctx.send(
		"Выберите подход:",
		components =[
			interactions.SelectMenu(
				placeholder = "Выберите подход...",
				custom_id = "menu_component_approach",
				options = [
					interactions.SelectOption( value = "careful", label = "Аккуратность"),
					interactions.SelectOption( value = "flashy", label = "Эффектность"),
					interactions.SelectOption( value = "quick", label = "Проворность"),
					interactions.SelectOption( value = "strong", label = "Сила"),
					interactions.SelectOption( value = "clever", label = "Ум"),
					interactions.SelectOption( value = "sneaky", label = "Хитрость"),
					interactions.SelectOption( value = "rich", label = "Достаток"),
					interactions.SelectOption( value = "minion_0", label = "Миньон: нет модификатора (0)"),
					interactions.SelectOption( value = "minion_+2", label = "Миньон: хорошо умеет (+2)"),
					interactions.SelectOption( value = "minion_-2", label = "Миньон: плохо умеет (-2)"),
				]
			),
		],
		
	)

@bot.component("menu_component_approach")
async def select_approach(ctx, approach: str):
	char_id = State.characters.get(ctx.author.id)
	char_name = ""
	if char_id is not None:
		with session_scope() as session:
			char_name = Adventurer.get_by_id(session,char_id).name
	State.roll_approaches[ctx.message.id] = approach
	
	stat_select_modal = interactions.Modal(
		title = "FATE Roll",
		custom_id="fate_roll_form",
		components = [
			interactions.TextInput(
				style=interactions.TextStyleType.SHORT,
				label="Имя персонажа",
				custom_id="text_input_char_name",
				min_length=2,
				max_length=50,
				value = char_name
			),
			interactions.TextInput(
				style=interactions.TextStyleType.SHORT,
				label="Иллюстрация действия",
				custom_id="text_input_pic_url",
				min_length=2,
				max_length=1000,
				required = False
			),
			interactions.TextInput(
				style=interactions.TextStyleType.PARAGRAPH,
				label="Действие",
				custom_id="text_input_rp_description",
				min_length=0,
				max_length=2000,
				required = False
			),
			
		]
	)
	await ctx.popup(stat_select_modal)

@bot.modal("fate_roll_form")
async def proceed_with_fate_roll(ctx, char_name: str, pic_url: typing.Optional[str], rp_description: typing.Optional[str]):
	total = 0
	title = ""
	result = []
	approach = State.roll_approaches.pop(ctx.message.id)[0]
	print(approach)
	if approach.startswith("minion_"):
		mod = int( approach[7:])
		result = []
		total = mod
		for i in range(4):
			roll = randint(1,6)
			result.append(roll)
			if roll>4:
				total+=1
			if roll<3:
				total-=1
		title = f"{char_name} делает бросок ({'+' if mod>0 else ''}{mod})"
		
	else:
		with session_scope() as session:
			heroes = Adventurer.name_owner_search(session,char_name,int(ctx.user.id))
			if len(heroes)==0:
				await ctx.send('Герой не найден!', ephemeral = True)
				return interactions.StopCommand
			elif len(heroes)==1:
				State.characters[ctx.author.id] = heroes[0].id
				mod = heroes[0].get_stat(approach)
				title = f"{heroes[0].name} делает проверку на {stat_to_russian[approach]} ({'+' if mod>0 else ''}{mod})"
				total, result = heroes[0].make_check(approach)
			else:
				msg = 'Найдено несколько, уточните:\n'
				notFound = True
				for hero in heroes:
					if hero.name == name: #Exact name match
						State.characters[ctx.author.id] = hero.id
						mod = hero.get_stat(approach)
						title = f"{hero.name} делает проверку на {stat_to_russian[approach]} ({'+' if mod>0 else ''}{mod})"
						total, result = hero.make_check(approach)
						notFound = False
						break
					msg += f'{hero.name}\n'
				if notFound:
					await ctx.send(msg, ephemeral = True)
					return interactions.StopCommand
	embeds = []
	mech_embed = interactions.Embed(
		title = title,
		description = f"Результат: {total} {result}"
	)
	
	
	if pic_url!="" or rp_description!="":
		rp_embed = interactions.Embed(
			title = title,
			description = "~~~" if rp_description=="" else rp_description,
			image = interactions.EmbedImageStruct(url = pic_url) if pic_url!="" else None
		)
		embeds.append(rp_embed)
	embeds.append(mech_embed)
	await ctx.send(embeds = embeds)
	
#======================================
# END FATE ROLL SECTION

# START GM RESOURCE CONTROL SECTION
#======================================
@bot.command()
async def gm(ctx):
	"""Команды для гейммастера, должны ограничиваться разрешением"""
	pass

@gm.group(name = "fate", description = "Управление жетонами судьбы")
async def gm_fate(ctx):
    pass
	
@gm_fate.subcommand(name = "give", description = "Выдать/отобрать жетоны судьбы")
@interactions.option(description = "Имя персонажа, которому выдаются жетоны")
@interactions.option(description = "Количество жетонов. Отрицательное, если надо отобрать")
async def gm_fate_give(ctx, char_name: str, amount: int):
	print("gm_fate_give")
	with session_scope() as session:
		print("	session open")
		heroes = Adventurer.name_search(session,char_name)
		print("	search performed")
		old_fate, new_fate = 0, 0
		full_name = char_name
		print(heroes)
		if len(heroes)==0:
			await ctx.send('Герой не найден!', ephemeral = True)
			return interactions.StopCommand
		elif len(heroes)==1:
			old_fate = heroes[0].fate
			heroes[0].fate += amount
			new_fate = heroes[0].fate
			heroes[0].save(session)
			full_name = heroes[0].name
		else:
			msg = 'Найдено несколько, уточните:\n'
			notFound = True
			for hero in heroes:
				if hero.name == char_name: #Exact name match
					old_fate = hero.fate
					hero.fate += amount
					new_fate = hero.fate
					hero.save(session)
					full_name = hero.name
					notFound = False
					break
				user = await interactions.get(bot, interactions.User, object_id=hero.owner_id)
				msg += f'{hero.name} ({user.username}#{user.discriminator})\n'
			if notFound:
				await ctx.send(msg, ephemeral = True)
				return interactions.StopCommand
		await ctx.send(f'{full_name}: жетоны судьбы {old_fate} → {new_fate}')


@gm_fate.subcommand(name = "set", description = "Установить количество жетонов судьбы")
@interactions.option(description = "Имя персонажа, которому выдаются жетоны")
@interactions.option(description = "Количество жетонов.")
async def gm_fate_set(ctx, char_name: str, amount: int):
	with session_scope() as session:
		heroes = Adventurer.name_search(session,char_name)
		old_fate, new_fate = 0, 0
		full_name = char_name
		print(heroes)
		if len(heroes)==0:
			await ctx.send('Герой не найден!', ephemeral = True)
			return interactions.StopCommand
		elif len(heroes)==1:
			old_fate = heroes[0].fate
			heroes[0].fate = amount
			new_fate = heroes[0].fate
			heroes[0].save(session)
			full_name = heroes[0].name
		else:
			msg = 'Найдено несколько, уточните:\n'
			notFound = True
			for hero in heroes:
				if hero.name == char_name: #Exact name match
					old_fate = hero.fate
					hero.fate = amount
					new_fate = hero.fate
					hero.save(session)
					full_name = hero.name
					notFound = False
					break
				user = await interactions.get(bot, interactions.User, object_id=hero.owner_id)
				msg += f'{hero.name} ({user.username}#{user.discriminator})\n'
			if notFound:
				await ctx.send(msg, ephemeral = True)
				return interactions.StopCommand
		await ctx.send(f'{full_name}: жетоны судьбы {old_fate} → {new_fate}')

@gm.group(name = "stress", description = "Управление стрессом")
async def gm_stress(ctx):
	pass

@gm_stress.subcommand(name = "give", description = "Нанести/вылечить урон")
@interactions.option(description = "Имя персонажа")
@interactions.option(description = "Количество урона. Отрицательное для лечения.")
async def gm_stress_give(ctx, char_name: str, amount: int):
	with session_scope() as session:
		heroes = Adventurer.name_search(session,char_name)
		old_stress, new_stress = 0, 0
		full_name = char_name
		print(heroes)
		if len(heroes)==0:
			await ctx.send('Герой не найден!', ephemeral = True)
			return interactions.StopCommand
		elif len(heroes)==1:
			old_stress = heroes[0].stress
			heroes[0].stress = amount
			new_stress = heroes[0].stress
			heroes[0].save(session)
			full_name = heroes[0].name
		else:
			msg = 'Найдено несколько, уточните:\n'
			notFound = True
			for hero in heroes:
				if hero.name == char_name: #Exact name match
					old_stress = hero.stress
					hero.stress += amount
					new_stress = hero.stress
					hero.save(session)
					full_name = hero.name
					notFound = False
					break
				user = await interactions.get(bot, interactions.User, object_id=hero.owner_id)
				msg += f'{hero.name} ({user.username}#{user.discriminator})\n'
			if notFound:
				await ctx.send(msg, ephemeral = True)
				return interactions.StopCommand
		await ctx.send(f'{full_name}: стресс {old_stress} → {new_stress}')


@gm_stress.subcommand(name = "set", description = "Установить стресс")
@interactions.option(description = "Имя персонажа")
@interactions.option(description = "Значение стресса.")
async def gm_stress_set(ctx, char_name: str, amount: int):
	with session_scope() as session:
		heroes = Adventurer.name_search(session,char_name)
		old_stress, new_stress = 0, 0
		full_name = char_name
		print(heroes)
		if len(heroes)==0:
			await ctx.send('Герой не найден!', ephemeral = True)
			return interactions.StopCommand
		elif len(heroes)==1:
			old_stress = heroes[0].stress
			heroes[0].stress = amount
			new_stress = heroes[0].stress
			heroes[0].save(session)
			full_name = heroes[0].name
		else:
			msg = 'Найдено несколько, уточните:\n'
			notFound = True
			for hero in heroes:
				if hero.name == char_name: #Exact name match
					old_stress = hero.stress
					hero.stress = amount
					new_stress = hero.stress
					hero.save(session)
					full_name = hero.name
					notFound = False
					break
				user = await interactions.get(bot, interactions.User, object_id=hero.owner_id)
				msg += f'{hero.name} ({user.username}#{user.discriminator})\n'
			if notFound:
				await ctx.send(msg, ephemeral = True)
				return interactions.StopCommand
		await ctx.send(f'{full_name}: стресс {old_stress} → {new_stress}')

@gm.group(name = "exp", description = "Управление опытом")
async def gm_exp(ctx):
    pass


@gm_exp.subcommand(name = "give", description = "Выдать/отобрать опыт")
@interactions.option(description = "Имя персонажа, которому выдаётся опыт")
@interactions.option(description = "Количество опыта. Отрицательное, если надо отобрать")
async def gm_exp_give(ctx, char_name: str, amount: int):
	print("gm_exp_give")
	with session_scope() as session:
		print("	session open")
		heroes = Adventurer.name_search(session,char_name)
		print("	search performed")
		old_exp, new_exp = 0, 0
		full_name = char_name
		print(heroes)
		if len(heroes)==0:
			await ctx.send('Герой не найден!', ephemeral = True)
			return interactions.StopCommand
		elif len(heroes)==1:
			old_exp = heroes[0].exp
			heroes[0].exp += amount
			new_exp = heroes[0].exp
			heroes[0].save(session)
			full_name = heroes[0].name
		else:
			msg = 'Найдено несколько, уточните:\n'
			notFound = True
			for hero in heroes:
				if hero.name == char_name: #Exact name match
					old_exp = hero.exp
					hero.exp += amount
					new_exp = hero.exp
					hero.save(session)
					full_name = hero.name
					notFound = False
					break
				user = await interactions.get(bot, interactions.User, object_id=hero.owner_id)
				msg += f'{hero.name} ({user.username}#{user.discriminator})\n'
			if notFound:
				await ctx.send(msg, ephemeral = True)
				return interactions.StopCommand
		await ctx.send(f'{full_name}: опыт {old_exp} → {new_exp}')



@gm_exp.subcommand(name = "set", description = "Установить количество опыта")
@interactions.option(description = "Имя персонажа, которому выдаётся опыт")
@interactions.option(description = "Количество опыта.")
async def gm_exp_set(ctx, char_name: str, amount: int):
	with session_scope() as session:
		heroes = Adventurer.name_search(session,char_name)
		old_exp, new_exp = 0, 0
		full_name = char_name
		print(heroes)
		if len(heroes)==0:
			await ctx.send('Герой не найден!', ephemeral = True)
			return interactions.StopCommand
		elif len(heroes)==1:
			old_exp = heroes[0].exp
			heroes[0].exp = amount
			new_exp = heroes[0].exp
			heroes[0].save(session)
			full_name = heroes[0].name
		else:
			msg = 'Найдено несколько, уточните:\n'
			notFound = True
			for hero in heroes:
				if hero.name == char_name: #Exact name match
					old_exp = hero.exp
					hero.exp = amount
					new_exp = hero.exp
					hero.save(session)
					full_name = hero.name
					notFound = False
					break
				user = await interactions.get(bot, interactions.User, object_id=hero.owner_id)
				msg += f'{hero.name} ({user.username}#{user.discriminator})\n'
			if notFound:
				await ctx.send(msg, ephemeral = True)
				return interactions.StopCommand
		await ctx.send(f'{full_name}: опыт {old_exp} → {new_exp}')

#======================================
# END GM RESOURCE CONTROL SECTION


bot.start()
