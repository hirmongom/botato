# Running on replit
# @Author: Hiram Montejano Gómez

from keep_alive import keep_alive

import os
import discord
from discord.ext import commands


# ********************** STARTUP ********************** #
intents = discord.Intents().all()
bot = commands.Bot(command_prefix = '.', intents = intents)
token = os.environ['token']

@bot.event
async def on_ready():
    print(f'{bot.user} is connected\n')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="lo tonto que eres"))
# ****************************************************** #


@bot.command(name = "ping", help= "Returns Pong")
async def ping(ctx):
        await ctx.send("Pong")


# ********************** RUN *************************** #
keep_alive()
bot.run(token)
# ****************************************************** #