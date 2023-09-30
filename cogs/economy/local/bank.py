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
from discord.ext import commands

from utils.custom_ui import FutureModal, ModalSelectMenu, FutureButton
from utils.json import load_json

from .quick_actions import deposit, withdraw, upgrade_bank


#***************************************************************************************************
async def bank_handler(bot: commands.Bot, interaction: discord.Interaction) -> None:
  # Load data
  economy_data = load_json(interaction.user.name, "economy")
  user_data = load_json(interaction.user.name, "user")

  embed = get_embed(bot = bot, interaction = interaction, economy_data = economy_data, 
                    user_data = user_data)
  
  message = await interaction.followup.send(embed = embed, ephemeral = True)
  operation, amount = await get_operation(interaction = interaction, message = message, 
                                  embed = embed, economy_data = economy_data, user_data = user_data)
  try:
    amount = round(float(amount), 2)
  except Exception:
    await message.edit(embed = embed, view = None)
    await interaction.followup.send(f"<@{interaction.user.id}> Amount must be a number")
    return
  
  if operation == 0:
    await deposit(interaction = interaction, amount = amount)
  elif operation == 1:
    await withdraw(interaction = interaction, amount = amount)
  elif operation == 2:
    await upgrade_bank(interaction = interaction)

  economy_data = load_json(interaction.user.name, "economy")
  user_data = load_json(interaction.user.name, "user")
  embed = get_embed(bot = bot, interaction = interaction, economy_data = economy_data, 
                    user_data = user_data)

  await message.edit(embed = embed, view = None)


#***************************************************************************************************
def get_embed(bot: commands.Bot, interaction: discord.Interaction, economy_data: dict, 
              user_data: dict) -> discord.Embed:
  embed = discord.Embed(
    title = "🏦 Bank Account",
    description = f"Welcome to the bank {interaction.user.display_name}! Choose an operation below",
    color = discord.Color.gold()
  )

  embed.add_field(name = "💰 Hand Balance", value = f"{round(economy_data['hand_balance'], 2)}€", 
                  inline = True)
  embed.add_field(name = "🏦 Bank Balance", value = f"{round(economy_data['bank_balance'], 2)}€", 
                  inline = True)
  embed.add_field(name = f"📆🔽 Remaining Weekly Withdraw Limit", 
          value = f"{round(economy_data['max_withdrawal'] - economy_data['withdrawn_money'], 2)}€", 
          inline = False)

  if user_data["level"] / 10 >= economy_data["bank_upgrade"] + 1:
    upgrade_cost = (economy_data["bank_upgrade"] + 1) * 10000
    embed.add_field(name = f"💰 You can upgrade your bank for {upgrade_cost}€", 
                    value = f"Withdrawal limit from {economy_data['max_withdrawal']}€ "
                            f"to {economy_data['max_withdrawal'] + 25000}€\n"
                            f"Interest rate from {int((economy_data['interest_rate'] - 1) * 100)}% "
                            f"to {int((economy_data['interest_rate'] - 1) * 100 + 2)}%", 
                    inline = False)

  embed.add_field(name = "", value = "", inline = False) # Pre-footer separator
  embed.set_footer(text = "Secure Banking | Botato Bank", icon_url = bot.user.display_avatar.url)

  return embed


#***************************************************************************************************
async def get_operation(interaction: discord.Interaction, message: discord.Message, 
                        embed: discord.Embed, economy_data: dict, user_data: dict) -> (int, int):
  amount_future = asyncio.Future()
  operation_future = asyncio.Future()

  deposit_modal = FutureModal(future = amount_future, label = "Amount", placeholder = "€", 
                              title = "Enter deposit amount")
  withdraw_modal = FutureModal(future = amount_future, label = "Amount", placeholder = "€", 
                              title = "Enter withdrawal amount")

  operation_select = ModalSelectMenu(user_id = interaction.user.id, future = operation_future, 
                        options = ["Deposit", "Withdraw"], modals = [deposit_modal, withdraw_modal],
                        placeholder = "Select an operation")

  view = discord.ui.View()
  view.add_item(operation_select)

  if user_data["level"] / 10 >= economy_data["bank_upgrade"] + 1:
    upgrade_button = FutureButton(user_id = interaction.user.id, future = operation_future, 
                                  button_id = 2, label = "Upgrade Bank")
    view.add_item(upgrade_button)

  await message.edit(embed = embed, view = view)


  operation = await operation_future

  amount = 0
  if operation != 2:
    amount = await amount_future

  return (operation, amount)