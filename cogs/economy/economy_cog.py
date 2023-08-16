import os

import discord
from discord import app_commands
from discord.ext import commands

import random

from util.json import loadJson, saveJson

class Economy(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


  async def daily_trigger(self) -> None:
    self.bot.interaction_logger.info("Economy daily trigger")
    for file in os.listdir("data/economy/"):
      data = loadJson(file[:-5], "economy")
      data["daily_money"] = 1
      saveJson(data, file[:-5], "economy")


  @commands.Cog.listener()
  async def on_interaction(self, interaction: discord.Interaction) -> None:
    data = loadJson(interaction.user.name, "economy")
    try:
      money = data["money"]
      daily_money = data["daily_money"]
    except Exception as e:  # First time run for user
      money = 100
      daily_money = 1

      data["money"] = money
      data["daily_money"] = daily_money

    if daily_money == 1:
      increase = random.randint(50, 150)
      data["money"] = data["money"] + increase
      data["daily_money"] = 0
      await interaction.channel.send(f"(*) You received {increase}€")
      self.bot.interaction_logger.info(f"Money increase on first interaction for {interaction.user.name} with {increase}€")

    saveJson(data, interaction.user.name, "economy")


  @app_commands.command(
    name = "bank",
    description = "Bank stuff"
  )
  async def bank(self, interaction: discord.Interaction) -> None:
    # @todo bank() command
    # First interaction you gotta sign up to bank
    # Check money
    # Change bank
    # Buy/manage stocks??
    pass


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Economy(bot))