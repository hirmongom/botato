import os

import discord
from discord import app_commands
from discord.ext import commands

import random

from util.json import loadJson, saveJson


class User(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


  async def daily_trigger(self) -> None:
    self.bot.interaction_logger.info("User daily trigger")
    for file in os.listdir("data/user/"):
      data = loadJson(file[:-5], "user")
      data["daily_xp"] = 5
      data["xp_probabiliy"] = 5
      saveJson(data, file[:-5], "user")


  @commands.Cog.listener()
  async def on_interaction(self, interaction: discord.Interaction) -> None:
    data = loadJson(interaction.user.name, "user")
    try:
      level = data["level"]
      experience = data["experience"]
      xp_probabiliy = data["xp_probabiliy"]
      daily_xp = data["daily_xp"]
    except Exception as e:  # First time run for user
      level = 1
      experience = 0
      xp_probabiliy = 5
      daily_xp = 5
      user_description = ""

      data["level"] = level
      data["experience"] = experience
      data["xp_probabiliy"] = xp_probabiliy
      data["daily_xp"] = daily_xp
      data["user_description"] = user_description

    if interaction.command.name != "profile":
      # Shouldn't trigger after checking the current XP   
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
      
    saveJson(data, interaction.user.name, "user")


  @app_commands.command(
    name = "profile",
    description = "Check your profile"
  )
  async def profile(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|profile| from {interaction.user.name}")

    try:
      data = loadJson(interaction.user.name, "user")
      level = data["level"]
      experience = data["experience"]
      description = data["user_description"]
    except KeyError:
      await interaction.response.send_message("It seems this is your first interaction with this " + 
                                              "bot, so I don't have any data, please check again")
      return

    embed = discord.Embed(title = interaction.user.display_name, description = str(description), color = discord.Color.pink())
    embed.add_field(name = "Level", value = level, inline = True)
    embed.add_field(name = "Experience", value = f"{experience} XP", inline = True)
    embed.add_field(name = "To Next Level", value = f"{level * 100 - experience} XP")
    embed.set_thumbnail(url = interaction.user.display_avatar.url)
    #embed.set_image(url = self.bot.user.display_avatar.url)

    await interaction.response.send_message(embed = embed)


  @app_commands.command(
    name = "description",
    description = "Set a description to show in your profile"
  )
  @app_commands.describe(
    description = "The description you want to set (Max 64 characters)"
  )
  async def description(self, interaction: discord.Interaction, description: str) -> None:
    self.bot.interaction_logger.info(f"|description| from {interaction.user.name} with description |{description}|")

    if not os.path.isfile(f"data/user/{interaction.user.name}.json"):
      await interaction.response.send_message("You cannot set your description on your first " +
                                              "interaction, please try again")
    elif len(description) > 64:
      await interaction.response.send_message("Description too long")
    else:
      data = loadJson(interaction.user.name, "user")
      data["user_description"] = description
      saveJson(data, interaction.user.name, "user")
      await interaction.response.send_message("Description set!") 
  
async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(User(bot))