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

import os

import discord
from discord import app_commands
from discord.ext import commands

import random
import datetime

from utils.json import load_json, save_json
from .utils.bank_ui import BankOperationModal, BankOperationSelect, BankUpgradeButton
from .utils.shop_ui import ShopItemSelect
from .utils.shop_funcs import create_role


class Economy(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


  async def weekly_task(self) -> None:
    for file in os.listdir("data/economy/"):
      if file != ".gitkeep":
        economy_data = load_json(file[:-5], "economy")
        economy_data["withdrawn_money"] = 0
        economy_data["bank_balance"] = economy_data["bank_balance"] * economy_data["interest_rate"]
        save_json(economy_data, file[:-5], "economy")


  async def daily_task(self) -> None:
    for file in os.listdir("data/economy/"):
      if file != ".gitkeep":
        economy_data = load_json(file[:-5], "economy")
        if economy_data["daily_pay"] == 0:
          economy_data["streak"] = economy_data["streak"] + 1
          economy_data["daily_pay"] = 1
        else:
          economy_data["streak"] = 0        
        save_json(economy_data, file[:-5], "economy")


  @commands.Cog.listener()
  async def on_interaction(self, interaction: discord.Interaction) -> None:
    economy_data = load_json(interaction.user.name, "economy")
    user_data = load_json(interaction.user.name, "user")
    daily_pay = economy_data["daily_pay"]

    if daily_pay == 1:
      if economy_data["streak"] == 7:
        lower_bound = user_data["level"] * 100 + 500
        upper_bound = user_data["level"] * 100 + 1000
        economy_data["streak"] = 0
      else:
        lower_bound = user_data["level"] * 10 + 50
        upper_bound = user_data["level"] * 10 + 150
      increase = round(random.uniform(lower_bound, upper_bound), 2)
      economy_data["bank_balance"] = economy_data["bank_balance"] + increase
      economy_data["daily_pay"] = 0

      streak_msg = f" (Current streak = {economy_data['streak']} days)" if int(economy_data["streak"]) != 0 else ""
      await interaction.channel.send(f"(*) You received {increase}€ on your bank{streak_msg}")
      self.bot.interaction_logger.info(f"Money increase on first interaction for {interaction.user.name} with {increase}€")

    save_json(economy_data, interaction.user.name, "economy")


  @app_commands.command(
    name = "bank",
    description = "Check your account balance and perform opperations"
  )
  async def bank(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|bank| from {interaction.user.name}")
    if not os.path.isfile(f"data/economy/{interaction.user.name}.json"):
      await interaction.response.send_message("It seems this is your first interaction with this " + 
                                              "bot, so I don't have any data, please check again")
      return

    await interaction.response.defer()

    economy_data = load_json(interaction.user.name, "economy")
    hand_balance = round(economy_data["hand_balance"], 2)
    bank_balance = round(economy_data["bank_balance"], 2)
    max_withdrawal = economy_data["max_withdrawal"]
    withdrawn_money = economy_data["withdrawn_money"]
    interest_rate = economy_data["interest_rate"]
    user_data = load_json(interaction.user.name, "user")

    embed = discord.Embed(
      title = "🏦 Bank Account",
      description = f"Welcome to the bank, {interaction.user.display_name}! Choose an operation below.",
      color = discord.Color.gold()
    )
    embed.add_field(name = "💰 Hand Balance", value = f"{hand_balance}€", inline = True)
    embed.add_field(name = "🏦 Bank Balance", value = f"{bank_balance}€", inline = True)
    embed.add_field(name = f"📆🔽 Remaining Weekly Withdraw Limit", 
                    value = f"{max_withdrawal - withdrawn_money}€", 
                    inline = False)
    if user_data["level"] / 5 >= economy_data["bank_upgrade"] + 1:
      upgrade_cost = (economy_data["bank_upgrade"] + 1) * 5000
      embed.add_field(name = f"💰 You can upgrade your bank for {upgrade_cost}€", 
                      value = f"Withdrawal limit from {max_withdrawal}€ to {max_withdrawal + 5000}€\n"
                              f"Interest rate from {int((interest_rate - 1) * 100)}% to {int((interest_rate - 1) * 100 + 1)}%", 
                      inline = False)
    embed.add_field(name = "", value = "", inline = False) # pre-footer separator
    embed.set_footer(text = "Secure Banking | Botato Bank", icon_url = self.bot.user.display_avatar.url)
    
    message = await interaction.followup.send(embed = embed, ephemeral = True)

    deposit_modal = BankOperationModal(title = "Deposit", operation = 1, economy_data = economy_data,
                                message = message, embed = embed)
    deposit_modal.add_item(discord.ui.TextInput(label = "Amount"))
    withdraw_modal = BankOperationModal(title = "Withdraw", operation = 2, economy_data = economy_data,
                                 message = message, embed = embed)
    withdraw_modal.add_item(discord.ui.TextInput(label = "Amount"))

    menu_choice = [
      discord.SelectOption(label = "Deposit", value = 1),
      discord.SelectOption(label = "Withdraw", value = 2)]
    menu = BankOperationSelect(
      user_id = interaction.user.id,
      placeholder = "Choose an operation",
      options = menu_choice)
    menu.set_modal("1", deposit_modal)
    menu.set_modal("2", withdraw_modal)

    view = discord.ui.View()
    view.add_item(menu)
    if user_data["level"] / 5 >= economy_data["bank_upgrade"] + 1:
      button = BankUpgradeButton(user_id = interaction.user.id,
                                message = message,
                                embed = embed,
                                economy_data = economy_data,
                                label = "Upgrade Bank", 
                                style = discord.ButtonStyle.primary,)
      view.add_item(button)

    await message.edit(embed = embed, view = view)


  @app_commands.command(
    name = "shop",
    description = "Check all items available in the shop"
  )
  async def shop(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|shop| from {interaction.user.name}")
    await interaction.response.defer()
    
    user_data = load_json(interaction.user.name, "user")
    if user_data["role_name"] == "":
      await create_role(interaction) # First interaction with the shop will create the custom role

    shop_items = [ 
      # <id> refers to its position in the list
      {"emoji": "📛", "name": "Role Name", 
                    "description": "Create a personalized role with a name that sets you apart in the server.", 
                    "price": 149000.99, 
                    "id": 0},
      {"emoji": "🎨", "name": "Name Colour", 
                    "description": "Add a splash of colour to your name in the server.", 
                    "price": 99000.98, 
                    "id": 1}
    ]

    item_menu_choices = []

    embed = discord.Embed(
      title = "🏪 Botato Shop",
      description = "With the best prices for all products available in the server!",
      color = discord.Color.blue()
    )

    for item in shop_items:
      item_menu_choices.append(discord.SelectOption(label = item["name"], value = item["id"]))

      embed.add_field(name = "", value = f"```{item['emoji']} {item['name']}```")
      embed.add_field(name = f"💶 {item['price']}€", value = item["description"], inline = False)

    embed.add_field(name = "", value = "", inline = False) # Pre-footer separator
    embed.set_footer(text = "Cheap Shopping | Botato Shop", icon_url = self.bot.user.display_avatar.url)

    message = await interaction.followup.send(embed = embed)

    item_menu = ShopItemSelect(
      user_id = interaction.user.id,
      shop_items = shop_items,
      placeholder = "Purchase an item",
      options = item_menu_choices)

    view = discord.ui.View()
    view.add_item(item_menu)
    
    await message.edit(embed = embed, view = view)

  
  @app_commands.command(
    name = "deposit",
    description = "Deposit money into your bank"
  )
  @app_commands.describe(
    amount = "Amount of money to deposit into the bank"
  )
  async def deposit(self, interaction: discord.Interaction, amount: float) -> None:
    self.bot.interaction_logger.info(f"|deposit| from {interaction.user.name} with amount |{amount}|")
    amount = round(amount, 2)

    if not os.path.isfile(f"data/user/{interaction.user.name}.json"):
      await interaction.response.send_message("It seems this is your first interaction with this " + 
                                              "bot, so I don't have any data, please check again")
      return

    economy_data = load_json(interaction.user.name, "economy")
    if economy_data["hand_balance"] < amount:
      await interaction.response.send_message("You do not have enough money in hand")
    else:
      economy_data["hand_balance"] = round(economy_data["hand_balance"] - amount, 2)
      economy_data["bank_balance"] = round(economy_data["bank_balance"] + amount, 2)
      await interaction.response.send_message(f"You deposited {amount}€")
    save_json(economy_data, interaction.user.name, "economy")


  @app_commands.command(
    name = "withdraw",
    description = "Withdraw money from your bank"
  )
  @app_commands.describe(
    amount = "Amount of money to withdraw from the bank"
  )
  async def withdraw(self, interaction: discord.Interaction, amount: float) -> None:
    self.bot.interaction_logger.info(f"|withdraw| from {interaction.user.name} with amount |{amount}|")
    amount = round(amount, 2)

    if not os.path.isfile(f"data/user/{interaction.user.name}.json"):
      await interaction.response.send_message("It seems this is your first interaction with this " + 
                                              "bot, so I don't have any data, please check again")
      return

    economy_data = load_json(interaction.user.name, "economy")
    if economy_data["bank_balance"] < amount:
      await interaction.response.send_message("You do not have enough money in the bank")
    elif economy_data["max_withdrawal"] - economy_data["withdrawn_money"] < amount:
      await interaction.response.send_message("You cannot withdraw that much money")
    else:
      economy_data["hand_balance"] = round(economy_data["hand_balance"] + amount, 2)
      economy_data["bank_balance"] = round(economy_data["bank_balance"] - amount, 2)
      economy_data["withdrawn_money"] = round(economy_data["withdrawn_money"] + amount, 2)
      await interaction.response.send_message(f"You withdrew {amount}€")
      save_json(economy_data, interaction.user.name, "economy")


  @app_commands.command(
    name = "transfer",
    description = "Transfer money to another user's bank"
  )
  @app_commands.describe(
    amount = "Amount of money to transfer"
  )
  @app_commands.describe(
    mention = "Mention of the user who the transfer will go to"
  )
  async def transfer(self, interaction: discord.Interaction, amount: float, mention: str) -> None:
    self.bot.interaction_logger.info(f"|transfer| from {interaction.user.name} with amount "
                                    f" |{amount}| and mention |{mention}|")
    amount = round(amount, 2)
    if mention.startswith("<@") and mention.endswith(">"):
      user_id = ''.join(filter(str.isdigit, mention))
      recipient = await interaction.guild.fetch_member(user_id)
    else:
      await interaction.response.send_message(f"Invalid mention <{mention}>")
      return

    if not os.path.isfile(f"data/user/{interaction.user.name}.json"):
      await interaction.response.send_message("It seems this is your first interaction with this " + 
                                              "bot, so I don't have any data, please check again")
      return
    if not os.path.isfile(f"data/user/{recipient.name}.json"):
      await interaction.response.send_message(f"It seems {recipient.display_name} hasn't interacted "
                                                "with me yet, so I don't have any data")
      return

    user_economy_data = load_json(interaction.user.name, "economy")
    recipient_economy_data = load_json(recipient.name, "economy")

    if user_economy_data["bank_balance"] < amount:
      await interaction.response.send_message("You do not have enough money in the bank")
      return

    user_economy_data["bank_balance"] = round(user_economy_data["bank_balance"] - amount, 2)
    recipient_economy_data["bank_balance"] = round(recipient_economy_data["bank_balance"] + amount, 2)

    save_json(user_economy_data, interaction.user.name, "economy")
    save_json(recipient_economy_data, recipient.name, "economy")

    await interaction.response.send_message(f"You transfered {amount}€ to {recipient.display_name}")


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Economy(bot))