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


import asyncio

import discord
from discord import app_commands
from discord.ext import commands

import datetime

from utils.json import load_json, save_json
from utils.custom_ui import FutureSelectMenu
from utils.achievement import add_user_stat
from .local.keys_funcs import (
  store_game, get_game_list, remove_games, get_following_list_size, get_game_embed)


class Keys(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


  async def weekly_task(self) -> None:
    channel = self.bot.get_channel(int(self.bot.main_channel))
    data = load_json("autoupdate", "keys")
    user_ids = load_json("user_ids", "other")

    for user in data.keys():
      await channel.send(f"<@{user_ids[user]}> Your weekly update is ready!")
      games = load_json(user, "keys")
      for title in games.keys():
        try:
          embed = get_game_embed(bot = self.bot, title = title, link = games[title])
          await channel.send(embed = embed)
        except Exception as e:
          self.bot.logger.error(f"Error on Keys weekly trigger for {user}, title = <{title}>, "
                                f"link = {games[title]}\n{e}")


  @app_commands.command(
    name = "keys",
    description = "Queries for a game in clavecd.es and returns the first 5 prices"
  )
  @app_commands.describe(
    query = "The search query to find the game you are looking for"
  )
  async def keys(self, interaction: discord.Interaction, query: str) -> None:
    self.bot.logger.info(f"(INTERACTION) |keys| from {interaction.user.name} with query |{query}|")
    await interaction.response.defer()

    user_ids = load_json("user_ids", "other")
    await interaction.followup.send(f"<@{interaction.user.id}> Searching ...")

    await add_user_stat("gamekeys_searched", interaction)
    try:
      link = self.bot.web_scrapper.get_game_link(query)
      title = self.bot.web_scrapper.get_game_title(link)
      embed = get_game_embed(bot = self.bot, title = title, link = link)
    except Exception as e:
      self.bot.logger.error(f"Error on keys search: {e}")
      embed = get_game_embed(bot = self.bot, query = query)

    await interaction.followup.send(embed = embed)


  @app_commands.command(
    name = "follow",
    description = "Follow a game to easily check key prices (Maximum of 25 games)"
  )
  @app_commands.describe(
    game = "The game you want to follow"
  )
  async def follow(self, interaction: discord.Interaction, game : str) -> None:
    self.bot.logger.info(f"(INTERACTION) |follow| from {interaction.user.name} with game |{game}|")
    user_ids = load_json("user_ids", "other")

    if get_following_list_size(interaction.user.name) >= 25:
      await interaction.response.send_message(f"<@{interaction.user.id}> You have "
                                              "reached the maximum of following games")
      return

    await interaction.response.defer()
    
    try:
      link = self.bot.web_scrapper.get_game_link(game)
      title = self.bot.web_scrapper.get_game_title(link)
    except Exception as e:
      self.bot.logger.error(f"Error ocurred on follow() for {interaction.user.name} with game {game}\n{e}")
      await interaction.followup.send(f"<@{interaction.user.id}> No results found")
      return
  
    store_game(interaction.user.name, title, link)

    embed = discord.Embed(
      title = f"🎮➕ You are now following {title}",
      description = f"👤 <@{interaction.user.id}>\n{link}",
      colour = discord.Colour.blue()
    )
    image_link_title = title.replace(' ', '').replace('\'', '')
    image_link = f"https://www.clavecd.es/wp-content/uploads/{image_link_title}.jpg"
    print(image_link)
    embed.set_thumbnail(url = image_link)
    embed.add_field(name = "", value = "", inline = False)  # Pre-footer separator
    embed.set_footer(text = "Cheap Keys | Botato Game Keys", 
                    icon_url = self.bot.user.display_avatar.url)

    await interaction.followup.send(embed = embed)

  @app_commands.command(
    name = "list",
    description = "Lists all games you are following"
  )
  async def list(self, interaction: discord.Interaction) -> None:
    self.bot.logger.info(f"(INTERACTION) |list| from {interaction.user.name}")
    user_ids = load_json("user_ids", "other")
    games = get_game_list(interaction.user.name)

    if len(games) == 0:
      await interaction.response.send_message(f"<@{interaction.user.id}> You are not "
                                              "following any games")
      return
    
    embed = discord.Embed(
      title = "🧾 List 🕹️",
      description = f"👤 <@{interaction.user.id}>",
      colour = discord.Colour.blue()
    )
    embed.add_field(name = "", value = "``` Following Games ```", inline = False)

    for i, game in enumerate(games):
      embed.add_field(name = f"{i + 1}.\t {game}", value = "", inline = False)

    embed.add_field(name = "", value = "", inline = False) # Pre footer separator
    embed.set_footer(text = "Cheap Keys | Botato Game Keys", 
                    icon_url = self.bot.user.display_avatar.url)

    await interaction.response.send_message(embed = embed)


  @app_commands.command(
    name = "unfollow",
    description = "Remove one or multiple games from your following list"
  )
  async def unfollow(self, interaction: discord.Interaction) -> None:
    self.bot.logger.info(f"(INTERACTION) |unfollow| from {interaction.user.name}")
    await interaction.response.defer()
    games = get_game_list(interaction.user.name)

    if len(games) == 0:
      await interaction.followup.send(f"<@{interaction.user.id}> You are not following "
                                      "any games")
      return

    games_future = asyncio.Future()
    select_menu = FutureSelectMenu(
      min_values = 1,
      max_values = len(games),
      placeholder = "Choose games to unfollow", 
      user_id = interaction.user.id,
      future = games_future,
      options = games,
    )

    view = discord.ui.View()
    view.add_item(select_menu)
    message = await interaction.followup.send(view = view)

    games_ix = await games_future
    to_remove = [games[int(i)] for i in games_ix]
    remove_games(interaction.user.name, to_remove)

    response = ""
    for game in to_remove:
      response += "\n-\t" + game
    await message.edit(content = f"<@{interaction.user.id}> You unfollowed:"
                      f"{response}", view = None)


  @app_commands.command(
    name = "update",
    description = "Get the key prices for all the games on your following list"
    )
  async def update(self, interaction: discord.Interaction) -> None:
    self.bot.logger.info(f"(INTERACTION) |update| from {interaction.user.name}")
    await interaction.response.defer()
    user_ids = load_json("user_ids", "other")
    games = load_json(interaction.user.name, "keys")

    if len(games) == 0:
      await interaction.followup.send(f"<@{interaction.user.id}> You are not following "
                                      "any games")
      return

    await interaction.followup.send(f"<@{interaction.user.id}> Sit back and relax, "
                                    "this may take some time...")

    for title in games.keys():
      try:
        embed = get_game_embed(bot = self.bot, title = title, link = games[title])
        await interaction.followup.send(embed = embed)
      except Exception as e:
        self.bot.logger.error(f"Error on keys update() for {interaction.user.name}, title = <{title}>, "
                        f"link = {games[title]}\n{e}")


  @app_commands.command(
    name = "autoupdate_keys",
    description = "Enable or disable the weekly autoupdate keys function"
  )
  @app_commands.choices(option = [
    app_commands.Choice(name = "Enable", value = 1),
    app_commands.Choice(name = "Disable", value = 0)
  ])
  async def autoupdate_keys(self, interaction: discord.Interaction, option: app_commands.Choice[int]) -> None:
    self.bot.logger.info(f"(INTERACTION) |autoupdate_keys| from {interaction.user.name} and param {option}")

    games = load_json(interaction.user.name, "keys")
    if len(games) == 0:
      await interaction.response.send_message("You are not following any games")
      return
    
    data = load_json("autoupdate", "keys")
    data[interaction.user.name] = option.value

    save_json(data, "autoupdate", "keys")

    if option.value == 1:
      await interaction.response.send_message("You have opted in to receive weekly updates for your followed games")
    else:
      await interaction.response.send_message("You have opted out to receive weekly updates for your followed games")


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Keys(bot))