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
      data["daily_payments"] = 5
      data["probability"] = 5
      saveJson(data, file[:-5], "economy")


  @commands.Cog.listener()
  async def on_interaction(self, interaction: discord.Interaction) -> None:
    data = loadJson(interaction.user.name, "economy")
    try:
      money = data["money"]
      probability = data["probability"]
      daily_payments = data["daily_payments"]
    except Exception as e:  # First time run for user
      money = 100
      probability = 5
      daily_payments = 5
      data["money"] = money
      data["probability"] = probability
      data["daily_payments"] = daily_payments
      saveJson(data, interaction.user.name, "economy")
      data = loadJson(interaction.user.name, "economy")

    if daily_payments > 0:
      if random.randint(1, 100) <= probability:
        money = data.get("money")
        increase = random.randint(10, 50)
        money += increase
        data["money"] = money
        data["probability"] = 5
        data["daily_payments"] = data["daily_payments"] - 1
        saveJson(data, interaction.user.name, "economy")
        self.bot.interaction_logger.info(f"Money increase trigger succesful for {interaction.user.name}")
        await interaction.channel.send(f"You found {increase}€!")
      else:
        if probability < 75:
          probability += 5
          data["probability"] = probability
          saveJson(data, interaction.user.name, "economy")


  @app_commands.command(
    name = "balance",
    description = "Checks your economy balance"
  )
  async def balance(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|balance| from {interaction.user.name}")

    data = loadJson(interaction.user.name, "economy")
    money = data["money"]
    
    await interaction.response.send_message(f"Your account balance is {money}€")

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Economy(bot))