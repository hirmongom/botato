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
from .local.horse_race import HorseSelect, race


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
    name = "horse_race",
    description = "Pick a racer, place your bet, and see if luck's on your side."
  )
  async def horse_race(self, interaction: discord.Interaction) -> None:
    self.bot.logger.info(f"|horse_race| from {interaction.user.name}")
    await interaction.response.defer()

    racer_name_map = [
      "Horse",
      "Ant",
      "Lettuce",
      "Potato"
    ]

    tracks = [
        ["🐎", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_"],
        ["🐜", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_"],
        ["🥬", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_"],
        ["🥔", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_"]
    ]

    embed = discord.Embed(
        title="🏁 Race Track 🏁",
        description="Choose your favorite racer\n and place your bet!",
        colour=discord.Colour.light_gray()
    )
    embed.add_field(name = "", value = f"```{''.join(tracks[0])}  ```", inline = False)
    embed.add_field(name = "", value = f"```{''.join(tracks[1])}  ```", inline = False)
    embed.add_field(name = "", value = f"```{''.join(tracks[2])}  ```", inline = False)
    embed.add_field(name = "", value = f"```{''.join(tracks[3])}  ```", inline = False)
    embed.add_field(name = "", value = "", inline = False) # Pre-footer separator
    embed.set_footer(text = "Lucky Racing | Botato Casino", icon_url = self.bot.user.display_avatar.url)

    response_future = asyncio.Future()
    select_horse = HorseSelect(interaction.user.id, response_future)
    view = discord.ui.View()
    view.add_item(select_horse)

    message = await interaction.followup.send(embed = embed, view = view)
    horse_choice, bet_amount = await response_future
    horse_choice = int(horse_choice)
    await message.edit(embed = embed, view = None)

    try:
      bet_amount = round(float(bet_amount), 2)
    except ValueError:
      await interaction.followup.send("Bet amount must be a number")
      return

    economy_data = load_json(interaction.user.name, "economy")
    if economy_data["hand_balance"] < bet_amount:
      await interaction.followup.send("You do not have enough money in hand")
      return
    else:
      economy_data["hand_balance"] -= bet_amount
      save_json(economy_data, interaction.user.name, "economy")

    await add_user_stat("horse_races_played", interaction)


    winner = await race(message, embed, tracks)

    if winner == horse_choice:
      await add_user_stat("horse_races_won", interaction)
      increase = bet_amount * 4
      economy_data["bank_balance"] += increase
      save_json(economy_data, interaction.user.name, "economy")
      await interaction.followup.send(f"{racer_name_map[winner]} won the race and you received"
                                      f" {increase}€")
    else:
      await interaction.followup.send(f"{racer_name_map[winner]} won the race")


#***************************************************************************************************
async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Casino(bot))