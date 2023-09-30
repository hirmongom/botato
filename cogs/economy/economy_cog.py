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
import random
import datetime

import discord
from discord import app_commands
from discord.ext import commands

from utils.json import load_json, save_json

from .local.bank import bank_handler
from .local.quick_actions import deposit, withdraw, transfer
from .local.shop import shop_handler


#***************************************************************************************************
class Economy(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


#***************************************************************************************************
  async def weekly_task(self) -> None:
    # Reset withdrawal limit and give interests
    for file in os.listdir("data/economy/"):
      if file != ".gitkeep":
        economy_data = load_json(file[:-5], "economy")
        economy_data["withdrawn_money"] = 0
        economy_data["bank_balance"] = economy_data["bank_balance"] * economy_data["interest_rate"]
        save_json(economy_data, file[:-5], "economy")


#***************************************************************************************************
  async def daily_task(self) -> None:
    # Reset daily money reward and check streak
    for file in os.listdir("data/economy/"):
      if file != ".gitkeep":
        economy_data = load_json(file[:-5], "economy")
        if economy_data["daily_pay"] == 0:
          economy_data["streak"] = economy_data["streak"] + 1
          economy_data["daily_pay"] = 1
        else:
          economy_data["streak"] = 0        
        save_json(economy_data, file[:-5], "economy")


#***************************************************************************************************
  @app_commands.command(
    name = "bank",
    description = "Check your account balance and perform opperations"
  )
  async def bank(self, interaction: discord.Interaction) -> None:
    self.bot.logger.info(f"(INTERACTION) |bank| from <{interaction.user.name}>")

    await interaction.response.defer()
    await bank_handler(bot = self.bot, interaction = interaction)


#***************************************************************************************************
  @app_commands.command(
    name = "shop",
    description = "Check all items available in the shop"
  )
  async def shop(self, interaction: discord.Interaction) -> None:
    self.bot.logger.info(f"(INTERACTION) |shop| from <{interaction.user.name}>")
    await interaction.response.defer()
    
    await shop_handler(bot = self.bot, interaction = interaction)

  
#***************************************************************************************************
  @app_commands.command(
    name = "deposit",
    description = "Deposit money into your bank"
  )
  @app_commands.describe(
    amount = "Amount of money to deposit into the bank"
  )
  async def deposit(self, interaction: discord.Interaction, amount: float) -> None:
    self.bot.logger.info(f"(INTRERACTION) |deposit| from <{interaction.user.name}> with amount = "
                        f"<{amount}>")
    
    await interaction.response.defer()
    await deposit(interaction = interaction, amount = amount)


#***************************************************************************************************
  @app_commands.command(
    name = "withdraw",
    description = "Withdraw money from your bank"
  )
  @app_commands.describe(
    amount = "Amount of money to withdraw from the bank"
  )
  async def withdraw(self, interaction: discord.Interaction, amount: float) -> None:
    self.bot.logger.info(f"(INTRERACTION) |withdraw| from <{interaction.user.name}> with amount = "
                        f"<{amount}>")
    
    await interaction.response.defer()
    await withdraw(interaction = interaction, amount = amount)


#***************************************************************************************************
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
    self.bot.logger.info(f"(INTERACTION) |transfer| from <{interaction.user.name}> with amount = "
                                    f"<{amount}> and mention = <{mention}>")
    amount = round(amount, 2)

    if mention.startswith("<@") and mention.endswith(">"):
      user_id = ''.join(filter(str.isdigit, mention))
      recipient = await interaction.guild.fetch_member(user_id)
    else:
      await interaction.response.send_message(f"<@{interaction.user.id}> Invalid mention "
                                              f"<{mention}>", ephemeral = True)
      return

    if not os.path.isfile(f"data/user/{recipient.name}.json"):
      await interaction.response.send_message(f"<@{interaction.user.id}> It seems "
                                              f"{recipient.display_name} hasn't interacted "
                                              "with me yet, so I don't have any data",
                                              ephemeral = True)
      return

    await interaction.response.defer()
    await transfer(interaction = interaction, amount = amount, recipient = recipient)


#***************************************************************************************************
async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Economy(bot))