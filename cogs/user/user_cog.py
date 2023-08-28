#  * @copyright   This file is part of the "Botato" project.
#  * 
#  *              Every file is free software: you can redistribute it and/or modify
#  *              it under the terms of the GNU General Public License as published by
#  *              the Free Software Foundation, either version 3 of the License, or
#  *              (at your option) any later version.
#  * 
#  *              These files are distributed in the hope that they will be useful,
#  *              but WITHOUT ANY WARRANTY; without even the implied warranty of
#  *              MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  *              GNU General Public License for more details.
#  * 
#  *              You should have received a copy of the GNU General Public License
#  *              along with the "Botato" project. If not, see <http://www.gnu.org/licenses/>.

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
        data["daily_xp"] = 10
        data["xp_probabiliy"] = 5
        save_json(data, file[:-5], "user")


  @commands.Cog.listener()
  async def on_interaction(self, interaction: discord.Interaction) -> None:
    data = load_json(interaction.user.name, "user")
    level = data["level"]
    experience = data["experience"]
    xp_probabiliy = data["xp_probabiliy"]
    daily_xp = data["daily_xp"]
    
    if daily_xp > 0:
      if random.randint(1, 100) <= xp_probabiliy:
        increase = random.randint(20, 50)
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
          xp_probabiliy += 2
          data["xp_probabiliy"] = xp_probabiliy
      
    save_json(data, interaction.user.name, "user")


  @app_commands.command(
    name = "profile",
    description = "Review your own or others' profile"
  )
  @app_commands.describe(
    mention = "Mention a user to check its profile"
  )
  async def profile(self, interaction: discord.Interaction, mention: str = "") -> None:
    self.bot.interaction_logger.info(f"|profile| from {interaction.user.name}" + 
                                    (f" with |mention| {mention}" if mention != "" else ""))
    if mention != "":
      if mention.startswith("<@") and mention.endswith(">"):
        user_id = ''.join(filter(str.isdigit, mention))
        user = await interaction.guild.fetch_member(user_id)
      else:
        await interaction.response.send_message(f"Invalid mention <{mention}>")
        return
    else:
      user = interaction.user

    if not os.path.isfile(f"data/user/{user.name}.json"):
      if user.name == interaction.user.name:
        await interaction.response.send_message("It seems this is your first interaction with this " + 
                                                "bot, so I don't have any data, please check again")
      else:
        await interaction.response.send_message(f"It seems {user.display_name} hasn't interacted "
                                                "with me yet, so I don't have any data")
      return

    data = load_json(user.name, "user")
    level = data["level"]
    experience = data["experience"]
    description = data["user_description"]
    
    user_badges = ""
    if user.premium_since:
      user_badges += "  💎"

    embed = discord.Embed(title = f"{user.display_name}{user_badges}", color = discord.Color.pink())

    if description != "":
      embed.description = f"""```fix
{str(description)} ```""" # Use code formatting and fix syntax highlighting to customize description

    embed.add_field(name = "*Level*", value = level, inline = True)
    embed.add_field(name = "*Experience*", value = f"{experience} XP", inline = True)
    embed.add_field(name = "*Next Level In*", value = f"{level * 100 + (level - 1) * 50} XP")
    embed.set_thumbnail(url = user.display_avatar.url)
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
    description = "Check the leaderboard across different categories"
  )
  @app_commands.choices(category = [
    app_commands.Choice(name = "Level", value = "user"),
    app_commands.Choice(name = "Money", value = "economy")

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
    user_ids = load_json("user_ids", "other")
    all_data = {}
    for file in os.listdir(f"data/{category}"):
      if file != ".gitkeep":
        user = file[:-5]
        user_data = load_json(user, category)
        user_info = await self.bot.fetch_user(user_ids[user])
        user_data["user"] = user_info.display_name
        if category == "economy":
          user_data["total"] = user_data["hand_balance"] + user_data["bank_balance"]
        all_data[user] = user_data
    sorted_data = dict(sorted(all_data.items(), key = lambda item: item[1][category_mapped["field"]], reverse=True))

    embed = discord.Embed(
      title = "🏆 Leaderboard 🏆",
      description = f"All the users ranked by {category_mapped['title']}",
      color = discord.Color.blue() if category == "user" else discord.Color.green())
    embed.add_field(name = "", value = "", inline = False) # post-title separator
    for i, key in enumerate(sorted_data.keys(), start = 1):
      if category == "economy":
        embed_value = f"➜ Total Money: {round(float(sorted_data[key]['total']), 2)}€"
      elif category == "user":
        embed_value = f"➜ Level {sorted_data[key]['level']} with {sorted_data[key]['experience']} XP"
      embed.add_field(name = f"{rank_map[i]}   ***{sorted_data[key]['user']}***",
                    value = embed_value, inline = False)
    embed.add_field(name = "", value = "", inline = False) # pre-footer separator
    embed.set_footer(text = "Precise Ranking | Botato Leaderboard", icon_url = self.bot.user.display_avatar.url)
  
    await interaction.followup.send(embed = embed)


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(User(bot))