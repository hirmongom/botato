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

from .local.test_room import EntryButton, StartButton


class Test(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


#***************************************************************************************************
  @app_commands.command(
    name = "test_cpp",
    description = "Test execution of C++ script from python"
  )
  async def test_cpp(self, interaction: discord.Interaction) -> None:
    self.bot.logger.info(f"(INTERACTION) |test_cpp| from {interaction.user.name}")

    lib = ctypes.CDLL("./cpp/test/test.so") # Load shared library
    lib.hello_cpp.restype = ctypes.c_char_p # Set type of return

    await interaction.response.send_message(lib.hello_cpp().decode("utf-8"))


#***************************************************************************************************
  @app_commands.command(
    name = "test_room",
    description  = "Room creation for multiplayer commands"
  )
  async def test_room(self, interaction: discord.Interaction) -> None:
    self.bot.logger.info(f"(INTERACTION) |test_room| from {interaction.user.name}")
    await interaction.response.defer()

    host = interaction.user
    players = [host]

    embed = discord.Embed(
      title = "Test Room",
      description = "Room test",
      color = discord.Colour.red()
    )
    embed.add_field(name = "", value = "``` Players ```", inline = False)
    embed.add_field(name = f"⭐ {host.display_name}", value = "", inline = False)

    message = await interaction.followup.send(embed = embed)

    # button to join (everyone)
    join_button = EntryButton(players = players, embed = embed, message = message, 
                              label = "Join", style = discord.ButtonStyle.secondary)

    # button to start (host)
    start_future = asyncio.Future()
    start_button = StartButton(host_id = interaction.user.id, future = start_future, 
                               label = "Start", style = discord.ButtonStyle.success)

    view = discord.ui.View()
    view.add_item(join_button)
    view.add_item(start_button)
    await message.edit(embed = embed, view = view)

    start = await start_future  # Wait for start button press
    view.clear_items()
    await interaction.followup.send(embed = embed, view = view)


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Test(bot))