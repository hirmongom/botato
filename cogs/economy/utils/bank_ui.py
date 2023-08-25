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

from utils.json import load_json, save_json


class BankUpgradeButton(discord.ui.Button):
  def __init__(self, user_id: int, economy_data: dict, message: discord.Message, 
              embed: discord.Embed, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.economy_data = economy_data
    self.message = message
    self.embed = embed

  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
        return # User not authorized

    upgrade_cost = (self.economy_data["bank_upgrade"] + 1) * 5000
    if self.economy_data["hand_balance"] < upgrade_cost:
      await interaction.response.send_message("You do not have enough money in hand")
      await update_embed(message = self.message, embed = self.embed, 
                          economy_data = self.economy_data)
    else:
      self.economy_data["hand_balance"] = self.economy_data["hand_balance"] - upgrade_cost
      self.economy_data["bank_upgrade"] = self.economy_data["bank_upgrade"] + 1
      self.economy_data["max_withdrawal"] = upgrade_cost + 5000
      self.economy_data["interest_rate"] = self.economy_data["interest_rate"] + 0.01
      save_json(self.economy_data, interaction.user.name, "economy")
      
      max_withdrawal = self.economy_data["max_withdrawal"]
      interest_rate = self.economy_data["interest_rate"]
      await interaction.response.send_message(f"Upgrade completed!\nYou can now withdraw up to "
                                              f"{max_withdrawal}€ each week\nYour interest rate has "
                                              f"increased to {int((interest_rate - 1) * 100)}%")
      await update_embed(message = self.message, embed = self.embed, 
                        economy_data = self.economy_data, was_upgrade = True)
    

class BankOperationSelect(discord.ui.Select):
  def __init__(self, user_id: int, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.modals = {}

  def set_modal(self, value: str, modal: discord.ui.Modal) -> None:
    self.modals[value] = modal

  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
        return # User not authorized

    self.disabled = True
    await interaction.message.edit(view = self.view)
    await interaction.response.send_modal(self.modals[self.values[0]])


class BankOperationModal(discord.ui.Modal):
  def __init__(self, title: str, operation: int, economy_data: dict, 
              message: discord.Message, embed: discord.Embed) -> None:
    super().__init__(title = title)
    self.operation = operation
    self.economy_data = economy_data
    self.message = message
    self.embed = embed

  async def on_submit(self, interaction: discord.Interaction) -> None:
    form_value = str(self.children[0])

    try:
      form_value = round(float(form_value), 2)
      hand_balance = self.economy_data["hand_balance"]
      bank_balance = self.economy_data["bank_balance"]
      withdrawn_money = self.economy_data["withdrawn_money"]
      max_withdrawal = self.economy_data["max_withdrawal"]

      if self.operation == 1:
        if hand_balance < form_value:
          await interaction.response.send_message("You do not have enough money in hand")
        else:
          hand_balance -= form_value
          bank_balance += form_value
          await interaction.response.send_message(f"You deposited {form_value}€")

      elif self.operation == 2:
        if bank_balance < form_value:
          await interaction.response.send_message("You do not have that much money in the bank")
        elif withdrawn_money + form_value > max_withdrawal:
          await interaction.response.send_message("You cannot exceed the weekly maximum withdrawal limit")
        else:
          bank_balance -= form_value
          hand_balance += form_value
          withdrawn_money += form_value
          bank_balance = round(bank_balance, 2)
          await interaction.response.send_message(f"You withdrew {form_value}€")

      self.economy_data["hand_balance"] = hand_balance
      self.economy_data["bank_balance"] = bank_balance
      self.economy_data["withdrawn_money"] = withdrawn_money
      save_json(self.economy_data, interaction.user.name, "economy")
      
    except:
      await interaction.response.send_message(f"Must be a number")

    await update_embed(self.message, self.embed, self.economy_data)


async def update_embed(message: discord.Message, embed: discord.Embed, 
                      economy_data: dict, was_upgrade: bool = False) -> None:
  hand_balance = round(economy_data["hand_balance"], 2)
  bank_balance = round(economy_data["bank_balance"], 2)
  max_withdrawal = economy_data["max_withdrawal"]
  withdrawn_money = economy_data["withdrawn_money"]

  embed.set_field_at(0, name = "💰 Hand Balance", value = f"{hand_balance}€", inline = True)
  embed.set_field_at(1, name = "🏦 Bank Balance", value = f"{bank_balance}€", inline = True)
  embed.set_field_at(2, name = "📆🔽 Remaining Weekly Withdraw Limit", 
                          value = f"{max_withdrawal - withdrawn_money}€", inline = False)
  if was_upgrade:
    embed.remove_field(3)
  embed.add_field(name = "", value = "", inline = False) # pre-footer separator
  await message.edit(embed = embed, view = None)