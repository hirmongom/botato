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
from utils.json import load_json, save_json


#***************************************************************************************************
class EntryButton(discord.ui.Button):
  def __init__(self, players: list[discord.Member], embed: discord.Embed, 
               message: discord.Message, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.players = players
    self.embed = embed
    self.message = message

  async def callback(self, interaction: discord.Interaction) -> None:
    await interaction.response.defer()

    # Add user to room if not already in
    if interaction.user not in self.players:
      self.players.append(interaction.user)
      self.embed.add_field(name = f"{interaction.user.display_name}", value = "", inline = False)
      await self.message.edit(embed = self.embed)
    else:
      await interaction.followup.send("You are already in the room", ephemeral = True)


#***************************************************************************************************
class StartButton(discord.ui.Button):
  def __init__(self, host_id: int, future: asyncio.Future, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.host_id = host_id
    self.future = future

  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.host_id:
      return # User not authorized

    await interaction.response.defer()
    self.future.set_result(True)