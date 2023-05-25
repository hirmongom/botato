import os
from dotenv import load_dotenv

import discord
from discord.ext import commands
from discord import app_commands

load_dotenv()
token = os.getenv('TOKEN')
bot = commands.Bot(command_prefix = "_not_designed_for_prefix_commands_", intents = discord.Intents.all())

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="lo tonto que eres"))
    try:
        sync = await bot.tree.sync()
        print(f"Synced {len(sync)} commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    print(f'{bot.user} is connected\n')

@bot.tree.command(name = "ping")
async def ping(interaction: discord.Interaction):
        print(f">> |ping| from {interaction.user.name}#{interaction.user.discriminator}")
        await interaction.response.send_message("Pong")

@bot.tree.command(name = "echo")
@app_commands.describe(message = "The message to echo")
async def echo(interaction: discord.Interaction, message: str):
    print(f">> |echo| from {interaction.user.name}#{interaction.user.discriminator}")
    await interaction.response.send_message(message)


bot.run(token)