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

from utils.funcs import add_user_stat

# **************************************************************************************************
class BetTypeSelect(discord.ui.Select):
  def __init__(self, user_id: int, future: asyncio.Future, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.future = future
    self.placeholder = "Bet Type"
    self.options = [
      discord.SelectOption(label = "Straight", value = 0),
      discord.SelectOption(label = "Colour", value = 1),
      discord.SelectOption(label = "Even/Odd", value = 2),
      discord.SelectOption(label = "Low/High", value = 3),
    ]

  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
      return # User not authorized

    self.disabled = True
    result = int(self.values[0])

    # Bet on what? // num = button-modal, rest = select
    if result == 0: # Bet Type Straight
      future_num = asyncio.Future()
      num_select_modal = FutureModal(title = "Choose a number for your bet", future = future_num, 
                                    label = "Enter a number", placeholder = "Number (0-36)")
      await interaction.response.send_modal(num_select_modal)
      selected_num = await future_num
      self.future.set_result([0, selected_num])
    else:
      await interaction.response.defer()
      self.future.set_result([result, ""])


# **************************************************************************************************
class BetValueSelect(discord.ui.Select):
  def __init__(self, user_id: int, future: asyncio.Future, options: list[discord.SelectOption], *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.future = future
    self.options = options
    self.placeholder = "Bet Value"

  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
      return # User not authorized
    await interaction.response.defer()

    self.disabled = True
    result = int(self.values[0])
    self.future.set_result(result)



# **************************************************************************************************
class BetAmountButton(discord.ui.Button):
  def __init__(self, user_id: int, future: asyncio.Future, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.future = future


  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
      return # User not authorized

    self.disabled = True
    bet_amount_modal = FutureModal(title = "Enter bet amount", future = self.future, 
                                  label = "Bet amount", placeholder = "€")
    await interaction.response.send_modal(bet_amount_modal)


# **************************************************************************************************
class FutureModal(discord.ui.Modal):
  def __init__(self, future: asyncio.Future, label: str, placeholder: str, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.add_item(discord.ui.TextInput(label = label, placeholder = placeholder))
    self.future = future

  async def on_submit(self, interaction: discord.Interaction) -> None:
    await interaction.response.defer()
    self.future.set_result(str(self.children[0]))



# **************************************************************************************************
async def process_winnings(economy_data: dict, winnings: float, 
                          interaction: discord.Interaction) -> None:
  economy_data["bank_balance"] += winnings
  await add_user_stat("roulettes_won", interaction)