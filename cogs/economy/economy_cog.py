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
      data["daily_xp"] = 5
      data["xp_probabiliy"] = 5
      data["daily_money"] = 1
      saveJson(data, file[:-5], "economy")


  @commands.Cog.listener()
  async def on_interaction(self, interaction: discord.Interaction) -> None:
    data = loadJson(interaction.user.name, "economy")
    try:
      level = data["level"]
      experience = data["experience"]
      xp_probabiliy = data["xp_probabiliy"]
      daily_xp = data["daily_xp"]
      money = data["money"]
      daily_money = data["daily_money"]
    except Exception as e:  # First time run for user
      level = 1
      experience = 0
      xp_probabiliy = 5
      daily_xp = 5
      money = 100
      daily_money = 1

      data["level"] = level
      data["experience"] = experience
      data["xp_probabiliy"] = xp_probabiliy
      data["daily_xp"] = daily_xp
      data["money"] = money
      data["daily_money"] = daily_money

    if daily_money == 1:
      increase = random.randint(50, 150)
      data["money"] = data["money"] + increase
      data["daily_money"] = 0
      await interaction.channel.send(f"(*) You received {increase}€")
      self.bot.interaction_logger.info(f"Money increase on first interaction for {interaction.user.name} with {increase}€")

    if daily_xp > 0:
      if random.randint(1, 100) <= xp_probabiliy:
        increase = random.randint(10, 50)
        experience += increase
        await interaction.channel.send(f"(*) You received {increase} XP")

        if experience >= (level * 100):
          experience = experience - level * 100
          level += 1
          data["level"] = level
          await interaction.channel.send(f"(*) You leveled up to level {level}!!")

        data["experience"] = experience
        data["xp_probabiliy"] = 5
        data["daily_xp"] = data["daily_xp"] - 1  
        self.bot.interaction_logger.info(f"experience increase trigger succesful for {interaction.user.name} with {increase} XP")
        
      else:
        if xp_probabiliy < 75:
          xp_probabiliy += 5
          data["xp_probabiliy"] = xp_probabiliy
      
      saveJson(data, interaction.user.name, "economy")


  @app_commands.command(
    name = "balance",
    description = "Checks your economy balance"
  )
  async def balance(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|balance| from {interaction.user.name}")

    data = loadJson(interaction.user.name, "economy")
    level = data["level"]
    experience = data["experience"]
    money = data["money"]
    
    await interaction.response.send_message(f"Level = {level}\n" +
                                            f"Current XP = {experience}\n" +
                                            f"{level * 100 - experience} XP remaining for level {level + 1}\n"
                                            f"Money = {money}€"
                                            f"\n\n(I know i need to make this more visually appealing... will get to it someday)")

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Economy(bot))