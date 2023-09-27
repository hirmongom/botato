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
import time
import random
import copy

import discord
from discord.ext import commands

from utils.achievement import add_user_stat
from utils.json import load_json, save_json
from utils.custom_ui import FutureSelectMenu


#***************************************************************************************************
racers = ["🐎 Horse", "🐜 Ant", "🥬 Lettuce", "🥔 Potato"]

racer_name_map = [
  "Horse",
  "Ant",
  "Lettuce",
  "Potato"
]

racer_icon_map = ["🐎", "🐜", "🥬", "🥔"]

kTracks = [
  ["🐎", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_"],
  ["🐜", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_"],
  ["🥬", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_"],
  ["🥔", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_"]
]


#***************************************************************************************************
async def race_game_handler(bot: commands.Bot, interaction: discord.Interaction, 
                            bet: float) -> None:
  tracks = copy.deepcopy(kTracks)
  embed = get_embed(bot, tracks)

  racer_future = asyncio.Future()
  racer_select = FutureSelectMenu(user_id = interaction.user.id, future = racer_future,
                                  options = racers, placeholder = "Select a Racer")

  view = discord.ui.View()
  view.add_item(racer_select)

  message = await interaction.followup.send(embed = embed, view = view)
  racer = int(await racer_future)
  await message.edit(embed = embed, view = None) # Remove view

  winner = await race(message, embed, tracks)

  if winner == racer:
    await add_user_stat("races_won", interaction)
    economy_data = load_json(interaction.user.name, "economy")
    win_amount = bet * 4
    economy_data["hand_balance"] += win_amount
    save_json(economy_data, interaction.user.name, "economy")
    await interaction.followup.send(f"<@{interaction.user.id}> {racer_name_map[winner]} won the "
                                    f"race and you received {win_amount}€")

  else:
    await interaction.followup.send(f"<@{interaction.user.id}> {racer_name_map[winner]} won the "
                                    "race")


#***************************************************************************************************
def get_embed(bot: commands.Bot, tracks: list[list[str]]) -> discord.Embed:
  embed = discord.Embed(
    title="🏁 Race Track 🏁",
    description="Choose your favorite racer\n and place your bet!",
    colour=discord.Colour.light_gray()
  )

  embed.add_field(name = "", value = f"```{''.join(tracks[0])}  ```", inline = False)
  embed.add_field(name = "", value = f"```{''.join(tracks[1])}  ```", inline = False)
  embed.add_field(name = "", value = f"```{''.join(tracks[2])}  ```", inline = False)
  embed.add_field(name = "", value = f"```{''.join(tracks[3])}  ```", inline = False)

  embed.add_field(name = "", value = "", inline = False) # Pre-footer separator
  embed.set_footer(text = "Lucky Racing | Botato Casino", icon_url = bot.user.display_avatar.url)

  return embed


#***************************************************************************************************
async def race(message: discord.Message, embed: discord.Embed, tracks: list[list[str]]) -> int:
  track_size = len(tracks[0])
  racer_positions = [0, 0, 0, 0]

  while True:
    time.sleep(0.01)
    racer = random.randint(0, 3)
    tracks[racer][racer_positions[racer]] = "_"
    racer_positions[racer] += 1
    tracks[racer][racer_positions[racer]] = racer_icon_map[racer]
    update_embed(embed, tracks)
    await message.edit(embed = embed)

    if racer_positions[racer] == track_size - 1:
      return racer


#***************************************************************************************************
def update_embed(embed: discord.Embed, tracks: list[list[str]]):
  embed.clear_fields()
  embed.add_field(name = "", value = f"```{''.join(tracks[0])}  ```", inline = False)
  embed.add_field(name = "", value = f"```{''.join(tracks[1])}  ```", inline = False)
  embed.add_field(name = "", value = f"```{''.join(tracks[2])}  ```", inline = False)
  embed.add_field(name = "", value = f"```{''.join(tracks[3])}  ```", inline = False)
  embed.add_field(name = "", value = "", inline = False) # Pre-footer separator