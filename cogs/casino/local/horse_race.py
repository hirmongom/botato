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


import time
import asyncio
import random
import discord


class HorseSelect(discord.ui.Select):
  def __init__(self, user_id: int, future: asyncio.Future, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.options = [
      discord.SelectOption(label = "🐎 Horse", value = 0),
      discord.SelectOption(label = "🐜 Ant", value = 1),
      discord.SelectOption(label = "🥬 Lettuce", value = 2),
      discord.SelectOption(label = "🥔 Potato", value = 3),
    ]
    self.user_id = user_id
    self.future = future

  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
      return # User not authorized

    selected_horse = self.values[0]
    future_value = asyncio.Future()
    bet_value_modal = BetModal(future = future_value, title = "Choose how much you want to bet")
    await interaction.response.send_modal(bet_value_modal)

    bet_amount = await future_value
    self.future.set_result((selected_horse, bet_amount))


class BetModal(discord.ui.Modal):
  def __init__(self, future: asyncio.Future, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.add_item(discord.ui.TextInput(label = "Bet amount", placeholder = "€"))
    self.future = future

  async def on_submit(self, interaction: discord.Interaction) -> None:
    await interaction.response.defer()
    value = str(self.children[0])
    self.future.set_result(value)


async def race(message: discord.Message, embed: discord.Embed, tracks: list[list[str]]) -> int:
  racer_icon_map = ["🐎", "🐜", "🥬", "🥔"]
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


def update_embed(embed: discord.Embed, tracks: list[list[str]]):
  embed.clear_fields()
  embed.add_field(name = "", value = f"```{''.join(tracks[0])}  ```", inline = False)
  embed.add_field(name = "", value = f"```{''.join(tracks[1])}  ```", inline = False)
  embed.add_field(name = "", value = f"```{''.join(tracks[2])}  ```", inline = False)
  embed.add_field(name = "", value = f"```{''.join(tracks[3])}  ```", inline = False)
  embed.add_field(name = "", value = "", inline = False) # Pre-footer separator