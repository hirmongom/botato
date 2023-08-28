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

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View

import datetime

from .utils.game_data import store_game, get_game_list, remove_games, get_following_list_size
from utils.json import load_json, save_json
from utils.funcs import add_user_stat


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
      keys = ""
      try:
        for title in games.keys():
          while True:
            keys = self.bot.web_scrapper.get_game_keys(games[title])
            if len(keys) != 0:
              break
            self.bot.web_scrapper.restart_driver()
          await channel.send(
            f"**{title}**\n<{games[title]}>\n{keys}")
        await channel.send("------------------------------------------------------------")
      except Exception as e:
        self.bot.logger(f"Error on Keys weekly trigger for {user}\n{e}")
        await channel.send(content = "An error ocurred")
        return


  @app_commands.command(
    name = "keys",
    description = "Queries for a game in clavecd.es and returns the first 5 prices"
  )
  @app_commands.describe(
    query = "The search query to find the game you are looking for"
  )
  async def keys(self, interaction: discord.Interaction, query: str) -> None:
    self.bot.interaction_logger.info(f"|keys| from {interaction.user.name} with query |{query}|")

    await interaction.response.defer()
    await add_user_stat("gamekeys_searched", interaction)

    try:
      link = self.bot.web_scrapper.get_game_link(query)
      title = self.bot.web_scrapper.get_game_title(link)
      content = self.bot.web_scrapper.get_game_keys(link)
    except Exception as e:
      print(e)
      await interaction.followup.send(f"No results found")
      return

    await interaction.followup.send(f"{title}\n{link}\n{content}")


  @app_commands.command(
    name = "follow",
    description = "Follow a game to easily check key prices (Maximum of 25 games)"
  )
  @app_commands.describe(
    game = "The game you want to follow"
  )
  async def follow(self, interaction: discord.Interaction, game : str) -> None:
    self.bot.interaction_logger.info(f"|follow| from {interaction.user.name} with game |{game}|")

    if get_following_list_size(interaction.user.name) >= 25:
      await interaction.response.send_message("You have reached the maximum of following games")
      return

    await interaction.response.defer()
    
    try:
      link = self.bot.web_scrapper.get_game_link(game)
      title = self.bot.web_scrapper.get_game_title(link)
    except Exception as e:
      self.bot.logger.error(f"Error ocurred on follow() for {interaction.user.name} with game {game}\n{e}")
      await interaction.followup.send(f"No results found")
      return
  
    store_game(interaction.user.name, title, link)

    await interaction.followup.send(f"You are now following {title}\n{link}")


  @app_commands.command(
    name = "list",
    description = "Lists all games you are following"
  )
  async def list(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|list| from {interaction.user.name}")

    games = get_game_list(interaction.user.name)   

    if len(games) == 0:
      await interaction.response.send_message("You are not following any games")
      return

    output = ""
    for i, game in enumerate(games):
      output += f"\n-\t {game}"

    await interaction.response.send_message(f"Following games:{output}")


  @app_commands.command(
    name = "unfollow",
    description = "Remove one or multiple games from your following list"
  )
  async def unfollow(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|unfollow| from {interaction.user.name}")
    await interaction.response.defer()

    games = get_game_list(interaction.user.name)

    if len(games) == 0:
      await interaction.followup.send("You are not following any games")
      return

    game_choice = [discord.SelectOption(label = game, value = i) for i, game in enumerate(games)]

    menu = Select(
      min_values = 1,
      max_values = len(games),
      placeholder = "Choose games to unfollow", 
      options = game_choice,
    )

    async def menu_callback(interaction: discord.Interaction) -> None:
      to_remove = [games[int(i)] for i in menu.values]
      remove_games(interaction.user.name, to_remove)

      response = ""
      for game in to_remove:
        response += "\n-\t" + game
      await message.edit(content = f"You unfollowed:{response}", view = None)

    menu.callback = menu_callback
    view = View()
    view.add_item(menu)
    message = await interaction.followup.send(view = view, ephemeral = True)


  @app_commands.command(
    name = "update",
    description = "Get the key prices for all the games on your following list"
    )
  async def update(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|update| from {interaction.user.name}")
    await interaction.response.defer()
    games = load_json(interaction.user.name, "keys")

    if len(games) == 0:
      await interaction.followup.send("You are not following any games")
      return

    message = await interaction.followup.send("Sit back and relax, this may take some time...")

    keys = ""
    try:
      for title in games.keys():
        while True:
          keys = self.bot.web_scrapper.get_game_keys(games[title])
          if len(keys) != 0:
            break
          self.bot.web_scrapper.restart_driver()
        await interaction.followup.send(
          f"**{title}**\n<{games[title]}>\n{keys}")
    except Exception as e:
      self.bot.logger.error(f"Error on update() for {interaction.user.name}\n{e}")
      await message.edit(content = "An error ocurred")
      return
    await message.delete()


  @app_commands.command(
    name = "autoupdate_keys",
    description = "Enable or disable the weekly autoupdate keys function"
  )
  @app_commands.choices(option = [
    app_commands.Choice(name = "Enable", value = 1),
    app_commands.Choice(name = "Disable", value = 0)
  ])
  async def autoupdate_keys(self, interaction: discord.Interaction, option: app_commands.Choice[int]) -> None:
    self.bot.interaction_logger.info(f"|autoupdate_keys| from {interaction.user.name} and param {option}")

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