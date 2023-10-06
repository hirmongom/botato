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
import ctypes
import datetime

import discord
from discord import app_commands
from discord.ext import commands

from utils.custom_ui import MultiplayerRoom


#***************************************************************************************************
class Test(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


#***************************************************************************************************
  @app_commands.command(
    name = "test_cpp",
    description = "Test execution of C++ script from python"
  )
  async def test_cpp(self, interaction: discord.Interaction) -> None:
    self.bot.logger.info(f"(INTERACTION) |test_cpp| from <{interaction.user.name}>")

    lib = ctypes.CDLL("./cpp/test/test.so") # Load shared library
    lib.hello_cpp.restype = ctypes.c_char_p # Set type of return

    await interaction.response.send_message(lib.hello_cpp().decode("utf-8"))


#***************************************************************************************************
  @app_commands.command(
    name = "test_room",
    description  = "Room creation for multiplayer commands"
  )
  async def test_room(self, interaction: discord.Interaction) -> None:
    self.bot.logger.info(f"(INTERACTION) |test_room| from <{interaction.user.name}>")

    halt_future = asyncio.Future()
    players = []
    room = MultiplayerRoom(interaction = interaction, future = halt_future, title = "Test Room", 
                          description = "This is a description", players = players)
    await room.start()
    await halt_future

    response = "Game Started with players:"
    for player in players:
      response += "\n" + player.display_name

    await interaction.followup.send(response)


#***************************************************************************************************
async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Test(bot))