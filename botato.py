import os
import discord
from dotenv import load_dotenv
from discord.ext import commands


# ********************** STARTUP ********************** #
intents = discord.Intents().all()
bot = commands.Bot(command_prefix = '.', intents = intents)

@bot.event
async def on_ready():
    print(f'{bot.user} is connected\n')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="lo tonto que eres"))
# ****************************************************** #

@bot.command(name = "ping", help= "Returns Pong")
async def ping(ctx):
        await ctx.send("Pong")


# ********************** RUN *************************** #
load_dotenv()
bot.run(os.getenv('TOKEN'))
# ****************************************************** #