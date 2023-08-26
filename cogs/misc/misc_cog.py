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

class Misc(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


  @app_commands.command(
    name = "git",
    description = "Check my code in my GitHub repository"
  )
  async def git(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|git| from {interaction.user.name}")
    await interaction.response.send_message("https://github.com/hmongom/Botato")


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
    self.bot.interaction_logger.info(f"|roll| from {interaction.user.name} with rolls = {rolls} and dice = {dice}")
    if rolls > 10 or rolls < 1:
      await interaction.response.send_message("u dum")
      return
    
    response = ""
    roll_result = 0
    for i in range(rolls):
      roll = random.randint(1, dice)
      response += f"\n\tRoll {i + 1} = {roll}"
      roll_result += roll
    response += f"\nTOTAL = {roll_result}"
    await interaction.response.send_message(f"You rolled {rolls}d{dice} and got:{response}")


  @app_command.command(
    name = "help",
    description = "Get help and information on the different functionalities provided by the bot"
  )
  async def help(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|help| from {interaction.user.name}")

    embed = main_embed

    help_categories = [
      discord.SelectOption(label = "User", value = 0),
      discord.SelectOption(label = "Economy", value = 1),
      discord.SelectOption(label = "Keys", value = 2),
      discord.SelectOption(label = "Bets", value = 3),
      discord.SelectOption(label = "Casino", value = 4)
    ]
    
    view = discord.ui.View()

    await interaction.response.send_message("@todo")


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Misc(bot))