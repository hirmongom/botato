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
from discord import app_commands
from discord.ext import commands

from utils.custom_ui import MultiplayerRoom

from .local.rockpaperscissors import rockpaperscissors_handler


#***************************************************************************************************
class Multiplayer(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


#***************************************************************************************************
  @app_commands.command(
    name = "rockpaperscissors",
    description = "Play Rock Paper Scissors with another player"
  )
  @app_commands.describe(
    bet = "Bet amount"
  )
  @app_commands.describe(
    bestof = "Number of rounds to play"
  )
  @app_commands.choices(
    bestof = [
      app_commands.Choice(name = "BO1", value = 1),
      app_commands.Choice(name = "BO3", value = 3),
      app_commands.Choice(name = "BO5", value = 5),
    ]
  )
  async def rockpaperscissors(self, interaction: discord.Interaction, 
                              bet: float, bestof: int) -> None:
    self.bot.logger.info(f"(INTERACTION) |rockpaperscissors| from <{interaction.user.name}> with "
                         f"bet = <{bet}> and bestof = <{bestof}>")
    bet = round(bet, 2)
    wait_future = asyncio.Future()
    players = []
    room = MultiplayerRoom(interaction = interaction, future = wait_future, 
                          title = "🎲 Rock Paper Scissors Duel Room 🎲", 
                          description = "Stake your bet and challenge others in this classic game "
                                        "of strategy and luck!"
                                        f"\n\n💰 Bet: {bet}€ | 🏆 Format: BO{bestof}",
                          players = players, min_players = 2, max_players = 2)
    await room.start()
    await wait_future

    message = room.get_message()
    await rockpaperscissors_handler(bot = self.bot, interaction = interaction, message = message, 
                                    players = players, bet = bet, bestof = bestof)
    

#***************************************************************************************************
async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Multiplayer(bot))