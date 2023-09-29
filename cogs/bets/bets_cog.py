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
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from utils.json import save_json, load_json

from .local.bet import bet_handler
from .local.create_event import create_event_handler, get_possible_days
from .local.close_event import close_event_handler


#***************************************************************************************************
class Bets(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


#***************************************************************************************************
  async def daily_task(self) -> None:
    now = datetime.now()
    try:
      for event in os.listdir("data/bets/"):
        data = load_json(f"{event}/{event}_bet", "bets")
        if int(data["day"]) == now.day and int(data["month"]) == now.month:
          data["status"] = "closed"
          save_json(data, f"{event}/{event}_bet", "bets")
          self.bot.logger.info(f"(bet_cog) Event <{sport.upper()}> <{data['event']}> closed")
    except Exception as e:
      self.bot.logger.error(f"Folder not found <./data/bets/>\n{e}")


#***************************************************************************************************
  @app_commands.command(
    name = "bet",
    description = "Check ongoing bets and try your luck!"
  )
  async def bet(self, interaction: discord.Interaction) -> None:
    self.bot.logger.info(f"(INTERACTION) |bet| from <{interaction.user.name}>")
    await interaction.response.defer()

    await bet_handler(bot = self.bot, interaction = interaction)

  
#***************************************************************************************************
  @app_commands.command(
    name = "create_event",
    description = "(ADMIN) Create a custom event for users to bet on"
  )
  @app_commands.describe(
    day = "The day when the event takes place"
  )
  @app_commands.describe(
    month = "The month when the event takes place"
  )
  @app_commands.describe(
    year = "The year when the event takes place"
  )
  async def create_event(self, interaction: discord.Interaction, day: int, month: int, 
                      year: int = datetime.now().year) -> None:
    self.bot.logger.info(f"(INTERACTION) |create_event| from <{interaction.user.name}> with day = "
                        f"<{day}>, month = <{month}> and year = <{year}>")

    # Check if user has permissions
    if not interaction.user.guild_permissions.administrator:
      await interaction.response.send_message(f"<@{interaction.user.id}> Missing Administrator "
                                              "permissions", ephemeral = True)
      return

    # Check viable date
    now = datetime.now()
    if year < now.year:
      await interaction.response.send_message(f"<@{interaction.user.id}> Year ({year}) cannot be "
                                              f"lower than the current year ({now.year})", 
                                              ephemeral = True)
      return

    if month < 1 or month > 12:
      await interaction.response.send_message(f"<@{interaction.user.id}> Month ({month}) does not "
                                              "exist", ephemeral = True)
      return

    if year == now.year and month < now.month:
      await interaction.response.send_message(f"<@{interaction.user.id}> Month ({month}) is lower "
                                              f"than current month ({now.month}) for this year "
                                              f"({now.year})", ephemeral = True)
      return

    if month == now.month and day < now.day:
      await interaction.response.send_message(f"<@{interaction.user.id}> Day ({day}) cannot be "
                                              f"lower than today ({now.day}) for this month "
                                              f"({now.month})", ephemeral = True)
      return

    possible_days = get_possible_days(year, month)
    if day not in possible_days:
      await interaction.response.send_message(f"<@{interaction.user.id}> Invalid day {day} for "
                                              f"month {month} and year {year}", ephemeral = True)
      return

    await interaction.response.defer()

    # Start handler
    await create_event_handler(interaction = interaction, day = day, month = month, year = year)


#***************************************************************************************************
  @app_commands.command(
    name = "close_event",
    description = "(ADMIN) Set the winner and close a custom made bet"
  )
  async def close_event(self, interaction: discord.Interaction) -> None:
    self.bot.logger.info(f"(INTERACTION) |close_event| from <{interaction.user.name}>")

    if not interaction.user.guild_permissions.administrator:
      await interaction.response.send_message(f"<@{interaction.user.id}> Missing Administrator "
                                              "permissions", ephemeral = True)
      return

    await interaction.response.defer()

    await close_event_handler(bot = self.bot, interaction = interaction)
    

#***************************************************************************************************
async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Bets(bot))