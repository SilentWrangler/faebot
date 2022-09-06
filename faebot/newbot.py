import interactions

import os
import typing

from dotenv import load_dotenv
from random import randint



BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(BASEDIR+'/../.env', override= True)

TOKEN = os.getenv('DISCORD_TOKEN')
bot = interactions.Client(token=TOKEN)

@bot.command(
	name = "test",
	description = "testCommand"
)
async def test(ctx: interactions.CommandContext):
    await ctx.send("Test succesful")

bot.start()
