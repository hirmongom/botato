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


#***************************************************************************************************
class FutureSelectMenu(discord.ui.Select):
  def __init__(self, user_id: int, future: asyncio.Future, options: list[str], 
              *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.future = future
    self.options = [
      discord.SelectOption(label = option, value = i) for i, option in enumerate(options)]

  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
      return # User not authorized
      
    self.disable = True
    await interaction.response.defer()
    self.future.set_result(self.values)


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