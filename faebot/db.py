import os
from contextlib import contextmanager
from random import randint, choice

from sqlalchemy import create_engine, Column, Integer, String, Sequence, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(BASEDIR+'/../.env')

USER = os.getenv('DB_USER')
PASS = os.getenv('DB_PASS')
HOST = os.getenv('DB_HOST')
NAME = os.getenv('DB_NAME')

#engine = create_engine(f'mysql://{USER}:{PASS}@{HOST}/{NAME}?charset=utf8', encoding='utf8')
engine = create_engine('sqlite:///testbase.db?charset=utf8', echo=True)
Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()

Base = declarative_base()

class Adventurer(Base):
    __tablename__ = 'adventurers'
    session = Session()
    id = Column(Integer, Sequence('adv_id_seq'), primary_key=True)
    owner_id = Column(BigInteger)
    name = Column(String(50))
    description = Column(String(2000))

    #Stats
    careful = Column(Integer)
    flashy = Column(Integer)
    quick = Column(Integer)
    strong = Column(Integer)
    clever = Column(Integer)
    sneaky = Column(Integer)
    rich = Column(Integer)
    #--------------------
    #Variables
    stress = Column(Integer)
    fate = Column(Integer)
    exp = Column(Integer)
    #--------------
    def get_stat(self, stat):
        stats = {
            'careful':self.careful,
            'flashy': self.flashy,
            'quick':self.quick,
            'strong':self.strong,
            'clever':self.clever,
            'sneaky':self.sneaky,
            'rich':self.rich

            }
        return stats[stat]
    def set_stat(self, stat, value):
        if stat=='careful':
            self.careful=value
            return
        if stat=='flashy':
            self.flashy=value
            return
        if stat=='quick':
            self.quick=value
            return
        if stat=='strong':
            self.strong=value
            return
        if stat=='clever':
            self.clever=value
            return
        if stat=='sneaky':
            self.sneaky=value
            return
        if stat=='rich':
            self.rich=value
            return
    def make_check(self, stat):
        base  = self.get_stat(stat)
        rolls = []
        for i in range(4):
            roll = randint(1,6)
            rolls.append(roll)
            if roll>4:
                base+=1
            if roll<3:
                base-=1
        return (base,tuple(rolls))

    def profile_russian(self):
        return [
            (
            f'Имя: {self.name}\n'
            f'Очки судьбы: {self.fate} Стресс:{self.stress} Очки опыта:{self.exp}\n'
            f'============ОПИСАНИЕ И АСПЕКТЫ=============\n'),
            f'{self.description}\n',
            (
            f'=================ПОДХОДЫ===================\n'
            f'Аккуратность: {self.careful}\n'
            f'Эффектность: {self.flashy}\n'
            f'Проворность: {self.quick}\n'
            f'Сила: {self.strong}\n'
            f'Ум: {self.clever}\n'
            f'Хитрость: {self.sneaky}\n'
            f'Достаток: {self.rich}'
            )
            ]
    @property
    def stats_message(self):
        return (
		    f'Аккуратность: {self.careful}\n'
		    f'Эффектность: {self.flashy}\n'
		    f'Проворность: {self.quick}\n'
	        f'Сила: {self.strong}\n'
	        f'Ум: {self.clever}\n'
	        f'Хитрость: {self.sneaky}\n'
	        f'Достаток: {self.rich}'
        )
	
    def save(self, session):
        session.add(self)
        session.commit()



    @classmethod
    def get(cls,session, **kwargs):
        query = session.query(cls)
        for key in kwargs:
            query = query.filter(cls.__dict__[key]==kwargs[key])
        return query.all()


    @classmethod
    def name_exists(cls,session, name):
        query = session.query(cls)
        query = query.filter(cls.name.ilike(name))
        cnt = query.count()
        return cnt>0



    @classmethod
    def name_search(cls,session, name):
        query = session.query(cls)
        query = query.filter(cls.name.ilike(f'%{name}%'))
        return query.all()

    @classmethod
    def name_owner_search(cls,session, name, ownerid):
        query = session.query(cls)
        query = query.filter(cls.name.ilike(f'%{name}%'))
        query = query.filter(cls.owner_id == ownerid)
        return query.all()

    @classmethod
    def get_by_id(cls,session, id):
        query = session.query(cls)
        query = query.filter(cls.id == id)
        return query.first()


class HeroCreator:

    number_to_emoji = {
        0:'0️⃣',
        1:'1️⃣',
        2:'2️⃣',
        3:'3️⃣',
        4:'4️⃣',
        5:'5️⃣',
        6:'6️⃣',
        7:'7️⃣',
        8:'8️⃣',
        9:'9️⃣'
    }

    emoji_to_number = {
        '0️⃣':0,
        '1️⃣':1,
        '2️⃣':2,
        '3️⃣':3 ,
        '4️⃣':4 ,
        '5️⃣':5 ,
        '6️⃣':6 ,
        '7️⃣':7 ,
        '8️⃣':8,
        '9️⃣':9
    }
    @classmethod
    def em_to_num(cls, em):
        return cls.emoji_to_number.get(em, None)

    def __init__(self, user, hook):
        self.user = user
        self.hook = hook
        self.done = False
    async def start(self):
        self.hero = Adventurer(
            fate=3, stress = 0,
            owner_id = self.user.id
            )
        self.stage = 'name'
        self.stats = [3,2,2,1,1,1,0]
        await self.hook.send('Как зовут персонажа?')
        self.message = None

    async def add_numbers(self,message):
        for i in set(self.stats):
            await message.add_reaction(HeroCreator.number_to_emoji[i])

    async def send_stat_message(self,stat):
        msg = (
            f'Осталось: {self.stats}\n'
            f'{stat}'
            )
        self.message = await self.hook.send(msg)
        await self.add_numbers(self.message)

    async def add_text(self, text):
        print("function fired")
        if self.stage == 'name':
            print("Name stage recognized")
            with session_scope() as session:
                if not Adventurer.name_exists(session,text):
                    self.hero.name = text
                    self.stage = 'desc'
                    await self.hook.send('Короткое описание персонажа и аспекты:')
                else:
                    await self.hook.send('Имя занято!')
        elif self.stage == 'desc':
            print("Description stage recognized")
            self.hero.description = text
            self.stage = 'stats-careful'
            await self.send_stat_message('Аккуратность')
        else:
            pass

    async def add_number(self, number):
        if self.stage == 'stats-careful':
            if number in self.stats:
                self.hero.careful = number
                self.stats.remove(number)
                self.stage = 'stats-flashy'
                await self.send_stat_message('Эффектность')
        elif self.stage == 'stats-flashy':
            if number in self.stats:
                self.hero.flashy = number
                self.stats.remove(number)
                self.stage = 'stats-quick'
                await self.send_stat_message('Проворность')
        elif self.stage == 'stats-quick':
            if number in self.stats:
                self.hero.quick = number
                self.stats.remove(number)
                self.stage = 'stats-strong'
                await self.send_stat_message('Сила')
        elif self.stage == 'stats-strong':
            if number in self.stats:
                self.hero.strong = number
                self.stats.remove(number)
                self.stage = 'stats-clever'
                await self.send_stat_message('Ум')
        elif self.stage == 'stats-clever':
            if number in self.stats:
                self.hero.clever = number
                self.stats.remove(number)
                self.stage = 'stats-sneaky'
                await self.send_stat_message('Хитрость')
        elif self.stage == 'stats-sneaky':
            if number in self.stats:
                self.hero.sneaky = number
                self.stats.remove(number)
                self.hero.rich = self.stats[0]
                await self.hook.send(f'Достаток {self.hero.rich}')
                await self.finish()

    async def finish(self):
        with session_scope() as s:
            s.add(self.hero)
            s.commit()
            s.close()
            self.message  = None
            self.done = True
            await self.hook.send('Готово!')






class HeroCreatorV2:
	def __init__(self,ctx, name, description):
		self.ctx = ctx
		self.hero = Adventurer(
			fate = 3, stress = 0, exp = 0,
			owner_id = int(ctx.user.id),
			name = name, description = description
		)
		self.stats = [3,2,2,1,1,1,0]
		self.stat_picks = [-1,-1,-1,-1,-1,-1,-1]
		self.stat_names = ['Аккуратность','Эффектность','Проворность','Сила','Ум','Хитрость','Достаток']
		self.selected_stat = 0
		self.done = True
		
	@property
	def message(self):
			msg = f"**{self.hero.name}**\n\n"
			dsc = self.hero.description
			if len(dsc)>200:
				dsc = dsc[0:200] + "(...)"
			msg += dsc
			
			msg += f'\n Подходы: {self.stats}\n'
			stat = ''
			for i in range(len(self.stat_picks)):
				stat += "> " if i==self.selected_stat else "+ "
				stat += self.stat_names[i]
				stat += " -" if self.stat_picks[i] == -1 else f" {self.stat_picks[i]}"
				stat += "\n"
			msg += stat
			return msg
		
	@property
	def stats_left(self):
		return len(self.stats)
		
	def change_selected_stat(self, direction):
		self.selected_stat += direction
		if self.selected_stat < 0:
			self.selected_stat = 0
		if self.selected_stat >= len(self.stat_picks):
			self.selected_stat = len(self.stat_picks) - 1
	
	def pick_selected_stat(self, stat):
		if stat in self.stats:
			self.stat_picks[self.selected_stat] = stat
			self.stats.remove(stat)
		elif stat in self.stat_picks:
			idx = self.stat_picks.index(stat)
			self.stat_picks[idx], self.stat_picks[self.selected_stat] = self.stat_picks[self.selected_stat], self.stat_picks[idx]
	
	def finish(self):
		self.hero.careful = self.stat_picks[0]
		self.hero.flashy  = self.stat_picks[1]
		self.hero.quick   = self.stat_picks[2]
		self.hero.strong  = self.stat_picks[3]
		self.hero.clever  = self.stat_picks[4]
		self.hero.sneaky  = self.stat_picks[5]
		self.hero.rich    = self.stat_picks[6]
		
		with session_scope() as s:
			s.add(self.hero)
			s.commit()
			s.close()
			self.message  = None
			self.done = True
			
	