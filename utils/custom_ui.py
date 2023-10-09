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
from typing import Callable

import discord


#***************************************************************************************************
class FutureSelectMenu(discord.ui.Select):
  def __init__(self, user_id: int, future: asyncio.Future, options: list[str], 
              values: list[str] = None, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.future = future
    self.option_values = values

    if not self.option_values:
      self.options = [
        discord.SelectOption(label = option, value = i) for i, option in enumerate(options)]
    else:
      self.options = [
        discord.SelectOption(label = option, value = values[i]) for i, option in enumerate(options)]

  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
      return # User not authorized
      
    self.disabled = True
    await interaction.response.defer()

    if not self.option_values:
      int_values = [int(i) for i in self.values]
      self.future.set_result(int_values if self.max_values > 1 else int_values[0])
    else:
      self.future.set_result(self.values if self.max_values > 1 else self.values[0])


#***************************************************************************************************
class ModalSelectMenu(discord.ui.Select):
  def __init__(self, user_id: int, future: asyncio.Future, options: list[str], 
              modals = list[discord.ui.Modal], *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.future = future
    self.modals = modals
    self.options = [
          discord.SelectOption(label = option, value = i) for i, option in enumerate(options)]
    
  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
      return # User not authorized
      
    self.disabled = True
    await interaction.response.send_modal(self.modals[int(self.values[0])])

    self.future.set_result(int(self.values[0]))


#***************************************************************************************************
class FutureModal(discord.ui.Modal):
  def __init__(self, future: asyncio.Future, label: str, placeholder: str, 
              *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.add_item(discord.ui.TextInput(label = label, placeholder = placeholder))
    self.future = future

  async def on_submit(self, interaction: discord.Interaction) -> None:
    await interaction.response.defer()
    form_value = str(self.children[0])
    self.future.set_result(form_value)


#***************************************************************************************************
class FutureButton(discord.ui.Button):
  def __init__(self, user_id: int, future: asyncio.Future, button_id: int = 1, 
              *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.future = future
    self.id = button_id

  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
      return # User not authorized

    await interaction.response.defer()
    self.future.set_result(self.id)


#***************************************************************************************************
class FutureConfirmationButton(discord.ui.Button):
  def __init__(self, user_id: int, future: asyncio.Future, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.future = future

  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
      return # User not authorized

    await interaction.response.defer()
    self.future.set()


#***************************************************************************************************
class ModalButton(discord.ui.Button):
  def __init__(self, user_id: int, modal: discord.ui.Modal, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.modal = modal

  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
      return # User not authorized
      
    self.disabled = True
    await interaction.response.send_modal(self.modal)


#***************************************************************************************************
class CoroButton(discord.ui.Button):
  def __init__(self, user_id: int, coro: Callable[..., None], restricted: bool = True, 
              *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.coro = coro
    self.restricted = restricted

  async def callback(self, interaction: discord.Interaction) -> None:
    if self.restricted and interaction.user.id != self.user_id:
      return # User not authorized
    
    await interaction.response.defer()
    if self.coro is not None and callable(self.coro):
            await self.coro(interaction)


#***************************************************************************************************
class MultiplayerRoom():
  def __init__(self, interaction: discord.Interaction, future: asyncio.Future, title: str, 
              description: str, players: list[discord.Member], min_players: int = None, 
              max_players: int = None) -> None:
    self.interaction = interaction
    self.future = future
    self.title = title
    self.description = description
    self.players = players
    self.min_players = min_players
    self.max_players = max_players
  
  async def start(self) -> None:
    await self.interaction.response.defer()

    host = self.interaction.user
    self.players.append(host)

    embed = discord.Embed(
      title = self.title,
      description = self.description,
      color = discord.Colour.red()
    )
    embed.add_field(name = "", value = "``` Players ```", inline = False)
    embed.add_field(name = f"⭐ {host.display_name}", value = "", inline = False)
    embed.add_field(name = "🔍 Waiting for player...", value = "", inline = False)

    self.message = await self.interaction.followup.send(embed = embed)

    # button to join (everyone)
    player_join = lambda interaction: (
      self.player_join_logic(interaction, self.players, self.message, embed)
    )
    join_button = CoroButton(user_id = None, coro = player_join, restricted = False, 
                            label = "Join", style = discord.ButtonStyle.secondary)

    # button to start (host)

    start = False
    view = discord.ui.View()
    while not start:
      start_future = asyncio.Future()
      start_button = FutureButton(user_id = self.interaction.user.id, future = start_future, 
                                  label = "Start", style = discord.ButtonStyle.success)
      view.add_item(join_button)
      view.add_item(start_button)
      await self.message.edit(embed = embed, view = view)

      await start_future  # Wait for start button press
      if self.min_players and len(self.players) < self.min_players:
        await self.interaction.followup.send(f"<@{self.interaction.user.id}> Not enough players "
                                             f"({len(self.players)}/{self.min_players})", 
                                             ephemeral = True)
      else:
        start = True

      view.clear_items()

    await self.message.edit(embed = embed, view = view)

    self.future.set_result(None)
  
  async def player_join_logic(self, interaction: discord.Interaction, players: list[discord.Member], 
                            message: discord.Message, embed: discord.Embed) -> None:
      if interaction.user not in players:
        if self.max_players:
          if len(players) > self.max_players:
            await interaction.followup.send(f"<@{interaction.user.id}> Players limit reached",
                                            ephemeral = True)
            return
        players.append(interaction.user)  
        embed.set_field_at(index = -1, name = f"{interaction.user.display_name}", value = ""),
        if self.max_players and len(players) < self.max_players:
          embed.add_field(name = "🔍 Waiting for player...", value = "", inline = False)
        await self.message.edit(embed = embed)
      else:
        await interaction.followup.send(f"<@{interaction.user.id}> You are already in the room",
                                          ephemeral = True)

  def get_message(self) -> discord.Message:
    return self.message