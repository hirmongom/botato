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
import asyncio
import random

import discord
from discord import app_commands
from discord.ext import commands

from utils.json import load_json, save_json
from utils.achievement import add_user_stat

from .local.blackjack import blackjack_game_handler
from .local.roulette import roulette_game_handler
from .local.race import race_game_handler


#***************************************************************************************************
class Casino(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


#***************************************************************************************************
  @app_commands.command(
    name = "blackjack",
    description = "Play a round of blackjack and try to win double your bet"
  )
  @app_commands.describe(
    bet = "Bet amount (€)"
  )
  async def blackjack(self, interaction: discord.Interaction, bet: float) -> None:
    self.bot.logger.info(f"(INTERACTION) |blackjack| from <{interaction.user.name}> with "
                         f"bet = <{bet}>")

    economy_data = load_json(interaction.user.name, "economy")
    bet = round(bet, 2)

    # Check if user has enough money
    if bet > economy_data["hand_balance"]:
      await interaction.response.send_message(f"<@{interaction.user.id}> You do not have enough "
                                              "money in hand", ephemeral = True)
      return

    await interaction.response.defer()
    
    economy_data["hand_balance"] -= bet
    save_json(economy_data, interaction.user.name, "economy")
    await add_user_stat("blackjack_hands_played", interaction)

    await blackjack_game_handler(bot = self.bot, interaction = interaction, bet = bet)


#***************************************************************************************************
  @app_commands.command(
    name = "roulette",
    description = "Spin the wheel and try your luck!"
  )
  @app_commands.describe(
    bet = "Bet amount (€)"
  )
  async def roulette(self, interaction: discord.Interaction, bet: float) -> None:
    self.bot.logger.info(f"(INTERACTION) |roulette| from <{interaction.user.name}> with "
                        f"bet = <{bet}>")

    economy_data = load_json(interaction.user.name, "economy")
    bet = round(bet, 2)

    # Check if user has enough money
    if bet > economy_data["hand_balance"]:
      await interaction.response.send_message(f"<@{interaction.user.id}> You do not have enough "
                                              "money in hand", ephemeral = True)
      return

    await interaction.response.defer()

    economy_data["hand_balance"] -= bet
    save_json(economy_data, interaction.user.name, "economy")
    await add_user_stat("roulettes_played", interaction)

    await roulette_game_handler(bot = self.bot, interaction = interaction, bet = bet)


#***************************************************************************************************
  @app_commands.command(
    name = "race",
    description = "Pick a racer, place your bet, and see if luck's on your side."
  )
  @app_commands.describe(
    bet = "Bet amount (€)"
  )
  async def race(self, interaction: discord.Interaction, bet: float) -> None:
    self.bot.logger.info(f"(INTERACTION) |race| from <{interaction.user.name}> with "
                         f"bet = <{bet}>")
    economy_data = load_json(interaction.user.name, "economy")
    bet = round(bet, 2)

    # Check if user has enough money
    if bet > economy_data["hand_balance"]:
      await interaction.response.send_message(f"<@{interaction.user.id}> You do not have enough "
                                              "money in hand", ephemeral = True)
      return

    await interaction.response.defer()

    economy_data["hand_balance"] -= bet
    save_json(economy_data, interaction.user.name, "economy")
    await add_user_stat("races_played", interaction)

    await race_game_handler(bot = self.bot, interaction = interaction, bet = bet)


#***************************************************************************************************
async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Casino(bot))