import os

import discord
from discord import app_commands
from discord.ext import commands

import random

from utils.json import load_json, save_json


class User(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


  async def daily_task(self) -> None:
    for file in os.listdir("data/user/"):
      if file != ".gitkeep":
        data = load_json(file[:-5], "user")
        data["daily_xp"] = 5
        data["xp_probabiliy"] = 5
        save_json(data, file[:-5], "user")


  @commands.Cog.listener()
  async def on_interaction(self, interaction: discord.Interaction) -> None:
    if type(interaction.command) == type(None) or interaction.command.name == "profile":
      # Shouldn't trigger after checking the current XP
      # Excluede certain interactions that are not commands
      return

    data = load_json(interaction.user.name, "user")
    level = data["level"]
    experience = data["experience"]
    xp_probabiliy = data["xp_probabiliy"]
    daily_xp = data["daily_xp"]
    
    if daily_xp > 0:
      if random.randint(1, 100) <= xp_probabiliy:
        increase = random.randint(10, 50)
        experience += increase
        await interaction.channel.send(f"(*) You received {increase} XP")

        if experience >= (level * 100 + (level - 1) * 50):
          level += 1
          data["level"] = level
          await interaction.channel.send(f"(*) You leveled up to level {level}!!")

        data["experience"] = experience
        data["xp_probabiliy"] = 5
        data["daily_xp"] = data["daily_xp"] - 1  
        self.bot.interaction_logger.info(f"Experience increase trigger succesful for {interaction.user.name} with {increase} XP")
        
      else:
        if xp_probabiliy < 75:
          xp_probabiliy += 5
          data["xp_probabiliy"] = xp_probabiliy
      
    save_json(data, interaction.user.name, "user")


  @app_commands.command(
    name = "profile",
    description = "Check your profile"
  )
  async def profile(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|profile| from {interaction.user.name}")

    if not os.path.isfile(f"data/user/{interaction.user.name}.json"):
      await interaction.response.send_message("It seems this is your first interaction with this " + 
                                              "bot, so I don't have any data, please check again")
      return
      
    data = load_json(interaction.user.name, "user")
    level = data["level"]
    experience = data["experience"]
    description = data["user_description"]

    embed = discord.Embed(title = interaction.user.display_name, description = str(description), color = discord.Color.pink())
    embed.add_field(name = "Level", value = level, inline = True)
    embed.add_field(name = "Experience", value = f"{experience} XP", inline = True)
    embed.add_field(name = "Next Level In", value = f"{level * 100 + (level - 1) * 50} XP")
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
      data = load_json(interaction.user.name, "user")
      data["user_description"] = description
      save_json(data, interaction.user.name, "user")
      await interaction.response.send_message("Description set!")

  @app_commands.command(
    name = "leaderboard",
    description = "Check the leaderboard"
  )
  @app_commands.choices(category = [
    app_commands.Choice(name = "Money", value = "economy"),
    app_commands.Choice(name = "Level", value = "user")
  ])
  async def leaderboard(self, interaction: discord.Interaction, category: str) -> None:
    self.bot.interaction_logger.info(f"|leaderboard| from {interaction.user.name}")
    await interaction.response.defer()

    rank_map = {
      1: "🏆 🥇",
      2: "🏆 🥈",
      3: "🏆 🥉",
      **{i: f"🏅  {i}  " for i in range(4, 100)} # Adjust based on max possible value
    }

    category_map = {
      "user": {"title": "Level", "field": "experience"},
      "economy": {"title": "Money", "field": "total"}
    }
    category_mapped = category_map[category]

    all_data = {}
    for file in os.listdir(f"data/{category}"):
      if file != ".gitkeep":
        user = file[:-5]
        user_data = load_json(user, category)
        user_data["user"] = user # @todo get user display name (use user_ids.json)
        if category == "economy":
          user_data["total"] = user_data["hand_balance"] + user_data["bank_balance"]
        all_data[user] = user_data
    sorted_data = dict(sorted(all_data.items(), key = lambda item: item[1][category_mapped["field"]], reverse=True))
    

    embed = discord.Embed(
      title = "🏆 Leaderboard 🏆",
      description = f"All the users ranked by {category_mapped['title']}",
      color = discord.Color.blue() if category == "user" else discord.Color.green())

    for i, key in enumerate(sorted_data.keys(), start = 1):
      if category == "economy":
        embed_value = f"➜ Total Money: {sorted_data[key]['total']}€"
      elif category == "user":
        embed_value = f"➜ Level {sorted_data[key]['level']} with {sorted_data[key]['experience']} XP"
      embed.add_field(name = f"{rank_map[i]}   ***{sorted_data[key]['user']}***",
                    value = embed_value, inline = False)

    embed.set_footer(text = "Precise Ranking | Botato Leaderboard", icon_url = self.bot.user.display_avatar.url)
  
    await interaction.followup.send(embed = embed)

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(User(bot))