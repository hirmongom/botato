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
from discord.ext import commands
from utils.json import load_json, save_json


def store_game(user: str, title: str, link: str) -> None:
  data = load_json(user, "keys")
  data[title] = link
  save_json(data, user, "keys")


def get_game_list(user: str) -> list[str]:
  data = load_json(user, "keys")
  return list(data.keys())


def remove_games(user: str, games: list[str]) -> None:
  data = load_json(user, "keys")
  for game in games:
    del data[game]
  save_json(data, user, "keys")


def get_following_list_size(user: str) -> int:
  data = load_json(user, "keys")
  return len(data.keys())


def get_game_embed(bot: commands.Bot, query: str = "", link: str = "", title: str = "") -> discord.Embed:
  embed = discord.Embed(
    title = "🎮 Game Keys Search 🎮",
    description = f"Query: <{query}>",
    colour = discord.Colour.blue()
  )
  embed.set_footer(text = "Cheap Keys | Botato Game Keys", icon_url = bot.user.display_avatar.url)

  if query == "": # Keys were succesfully obtained

    image_link_title = title.replace(' ', '').replace('\'', '')
    image_link = f"https://www.clavecd.es/wp-content/uploads/{image_link_title}.jpg"
    embed.set_thumbnail(url = image_link)

    embed.description = f"{link}"
    embed.add_field(name = "", value = f"```🔑 {title} 🔑```", inline = False)

    while True:
      content = bot.web_scrapper.get_game_keys(link)
      if len(content) != 0:
          break
      bot.web_scrapper.restart_driver()
    
    for key in content:
      embed.add_field(name = key, value = "", inline = False)

    embed.add_field(name = "", value = "", inline = False) # Pre footer separator
  
  else: # Keys were not obtained
    embed.add_field(name = "No results found", value = "")
    embed.add_field(name = "", value = "", inline = False) # Pre footer separator

  return embed