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
from discord import app_commands
from discord.ext import commands

import random

from .local.help_handler import HelpHandlerSelect


class Misc(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


#***************************************************************************************************
  @app_commands.command(
    name = "git",
    description = "Check my code in my GitHub repository"
  )
  async def git(self, interaction: discord.Interaction) -> None:
    self.bot.logger.info(f"(INTERACTION) |git| from {interaction.user.name}")
    await interaction.response.send_message("https://github.com/hmongom/Botato")


#***************************************************************************************************
  @app_commands.command(
    name = "roll",
    description = "Roll a specific dice"
  )
  @app_commands.describe(
    rolls = "The number of rolls you want to perform with your dice (10 maximum)",
  )
  @app_commands.describe(
    dice = "The type of dice you want to use for your roll",
  )
  @app_commands.choices(
    dice = [
      app_commands.Choice(name = "d6", value = 6),
      app_commands.Choice(name = "d20", value = 20)
    ]
  )
  async def roll(self, interaction: discord.Interaction, rolls: int, dice: int):
    # @todo embed
    self.bot.logger.info(f"(INTERACTION) |roll| from {interaction.user.name} with rolls = {rolls} " 
                         f"and dice = {dice}")

    # Check if rolls is within the limits
    if rolls > 10 or rolls < 1:
      await interaction.response.send_message(f"<@{interaction.user.id}>That amount of rolls is "
                                              f"not within the limits")
      return
    
    # Perform the rolls and add to result and response
    roll_result = 0
    response = ""
    for i in range(rolls):
      roll = random.randint(1, dice)
      roll_result += roll
      response += f"\n\tRoll {i + 1} = {roll}"

    # Form and send response
    response += f"\nTOTAL = {roll_result}"
    await interaction.response.send_message(f"<@{interaction.user.id}> You rolled {rolls}d{dice} " 
                                            f"and got:{response}")


#***************************************************************************************************
  @app_commands.command(
    name = "help",
    description = "Get help and information on the different functionalities provided by the bot"
  )
  async def help(self, interaction: discord.Interaction) -> None:
    self.bot.logger.info(f"(INTERACTION) |help| from {interaction.user.name}")
    await interaction.response.defer()
    
    message = await interaction.followup.send("Loading..") # To keep the message as variable

    # Load and start the help handler
    help_handler_select = HelpHandlerSelect(interaction.user.id, self.bot, message)
    await help_handler_select.start()


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Misc(bot))