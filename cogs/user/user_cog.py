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
import asyncio

import discord
from discord import app_commands
from discord.ext import commands

import random

from utils.json import load_json, save_json
from utils.custom_ui import FutureModal
from .local.achievements_mapping import map_stat_name, map_tier


#***************************************************************************************************
class User(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


#***************************************************************************************************
  async def daily_task(self) -> None:
    # Reset daily XP
    for file in os.listdir("data/user/"):
      if file != ".gitkeep":
        data = load_json(file[:-5], "user")
        data["daily_xp"] = 10
        data["xp_probabiliy"] = 5
        save_json(data, file[:-5], "user")


#***************************************************************************************************
  @app_commands.command(
    name = "profile",
    description = "Review your own or others' profile"
  )
  @app_commands.describe(
    mention = "Mention a user to check its profile"
  )
  async def profile(self, interaction: discord.Interaction, mention: str = "") -> None:
    self.bot.logger.info(f"(INTERACTION) |profile| from <{interaction.user.name}>" +
                        (f" with |mention| = <{mention}>" if mention != "" else ""))

    # Mention check
    if mention != "":
      if mention.startswith("<@") and mention.endswith(">"):
        user_id = ''.join(filter(str.isdigit, mention))
        user = await interaction.guild.fetch_member(user_id)
      else:
        await interaction.response.send_message(f"<@{interaction.user.id}> Invalid mention "
                                                f"<{mention}>", ephemeral = True)
        return
    else:
      user = interaction.user

     # Check user exists
    if not os.path.isfile(f"data/user/{user.name}.json"):
      await interaction.response.send_message(f"<@{interaction.user.id}> It seems "
                    f"{user.display_name} hasn't interacted with me yet, so I don't have any data",
                    ephemeral = True)
      return


    user_data = load_json(user.name, "user")
    achievement_data = load_json(user.name, "achievement")

    level = user_data["level"]
    experience = user_data["experience"]
    description = user_data["user_description"]
    
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

    achievements = achievement_data["achievements"]
    if len(achievements) > 0:
      embed.add_field(name = "", value = "```🎯 Achievements 🎯```", inline = False)
      for achievement in achievements:
        keys = list(achievement.keys())
        embed.add_field(name = f"{map_tier[achievement[keys[1]]]} {achievement[keys[0]]} "
                               f"{map_stat_name[keys[0]]}", value = "", inline = False)

    await interaction.response.send_message(embed = embed)


#***************************************************************************************************
  @app_commands.command(
    name = "description",
    description = "Set a description to show in your profile"
  )
  @app_commands.describe(
    description = "The description you want to set (Max 64 characters)"
  )
  async def description(self, interaction: discord.Interaction, description: str) -> None:
    self.bot.logger.info(f"(INTERACTION)  |description| from <{interaction.user.name}> with "
                         f"description = <{description}>")

    if len(description) > 64:
      await interaction.response.send_message(f"<@{interaction.user.id}> Description too long",
                                              ephemeral = True)
    else:
      data = load_json(interaction.user.name, "user")
      data["user_description"] = description
      save_json(data, interaction.user.name, "user")
      await interaction.response.send_message(f"<@{interaction.user.id}> Description set!",
                                              ephemeral = True)


#***************************************************************************************************
  @app_commands.command(
    name = "leaderboard",
    description = "Check the leaderboard across different categories"
  )
  @app_commands.choices(category = [
    app_commands.Choice(name = "Level", value = "user"),
    app_commands.Choice(name = "Money", value = "economy")
  ])
  async def leaderboard(self, interaction: discord.Interaction, category: str) -> None:
    self.bot.logger.info(f"(INTERACTION) |leaderboard| from {interaction.user.name}")
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

    leaders = {}
    for file in os.listdir(f"data/{category}"):
      if file != ".gitkeep":
        user = file[:-5]
        user_data = load_json(user, category)

        user_info = await self.bot.fetch_user(user_ids[user])
        user_data["user"] = user_info.display_name

        if category == "economy":
          user_data["total"] = user_data["hand_balance"] + user_data["bank_balance"]

        leaders[user] = user_data

    sorted_data = dict(sorted(leaders.items(), key = lambda item: item[1][category_mapped["field"]],
                               reverse = True))

    embed = discord.Embed(
      title = "🏆 Leaderboard 🏆",
      description = f"All the users ranked by {category_mapped['title']}",
      color = discord.Color.blue() if category == "user" else discord.Color.green())
      
    embed.add_field(name = "", value = "```Global Ranking ```", inline = False)

    for i, key in enumerate(sorted_data.keys(), start = 1):

      if category == "economy":
        user_val = f"➜ Total Money: {round(float(sorted_data[key]['total']), 2)}€"

      elif category == "user":
        user_val = f"➜ Level {sorted_data[key]['level']} with {sorted_data[key]['experience']} XP"

      embed.add_field(name = f"{rank_map[i]}   ***{sorted_data[key]['user']}***",
                      value = user_val, inline = False)

    embed.add_field(name = "", value = "", inline = False) # pre-footer separator
    embed.set_footer(text = "Precise Ranking | Botato Leaderboard", 
                    icon_url = self.bot.user.display_avatar.url)
  
    await interaction.followup.send(embed = embed)


#***************************************************************************************************
  @app_commands.command(
    name = "wipe",
    description = "Erase all your data from the bot"
  )
  async def wipe(self, interaction: discord.Interaction) -> None:
    self.bot.logger.info(f"(INTERACTION) |wipe| from <{interaction.user.name}>")

    if not os.path.exists(f"data/user/{interaction.user.name}.json"):
      await interaction.response.send_message(f"<@{interaction.user.id}> There is no data to erase",
                                              ephemeral = True)
      return
      
    confirmation_future = asyncio.Future()
    confirmation_modal = FutureModal(future = confirmation_future, title = "Confirm Erease",
                                     label = f"Type <{interaction.user.name}> to confirm deletion", 
                                     placeholder = interaction.user.name)
    await interaction.response.send_modal(confirmation_modal)

    confirmation_response = await confirmation_future
    if not confirmation_response.lower() == interaction.user.name:
      await interaction.followup.send(f"<@{interaction.user.id}> You have to type your username to "
                                      "erase your data", ephemeral = True)
      return

    # Start deletion of user data
    for folder in os.listdir("data"):

      # Remove user from bettors in each bet
      if folder == "bets":  
        for bet in os.listdir("data/bets/"):
          bettors = load_json(f"{bet}/{bet}_bettors", "bets")
          if interaction.user.name in bettors:
            self.bot.logger.info(f"Removed {interaction.user.name} from {bet}/{bet}_bettors.json")
            del bettors[interaction.user.name]
            save_json(bettors, f"{bet}/{bet}_bettors", "bets")

      # Remove user from user_ids
      elif folder == "other": 
        user_ids = load_json("user_ids", "other")
        if interaction.user.name in user_ids:
          self.bot.logger.info(f"Removed {interaction.user.name} user_id from "
                               "data/other/user_ids.json")
          del user_ids[interaction.user.name]
          save_json(user_ids, "user_ids", "other")

      # Remove user data files
      else: 
        if os.path.exists(f"data/{folder}/{interaction.user.name}.json"):
          self.bot.logger.info(f"Removed {interaction.user.name}.json from data/{folder}/")
          os.remove(f"data/{folder}/{interaction.user.name}.json")

    await interaction.followup.send(f"<@{interaction.user.id}> All your data has been deleted",
                                    ephemeral = True)


#***************************************************************************************************
async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(User(bot))