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

class DailyChallenges(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


  async def daily_task(self) -> None:
    # @todo clear current (non-automated) challenges
    #       grab next automated challenges
    pass


  @app_commands.command(
    name = "daily_challenges",
    description = "Show daily challenges and try to solve them"
  )
  async def daily_challenges(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|daily_challenges| from {interaction.user.name}")
    await interaction.response.defer()

    # @todo Load challenges
    #       display them
    #       user chooses a challenge
    #       load options + solution
    #       display options (buttons) (2x2?)
    #       user chooses option -> win or lose = disable challenge for user

    await interaction.followup.send("@todo daily_challenges")

  
  @app_commands.command(
    name = "create_daily_challenge",
    description = "(ADMIN)"
  )
  async def create_daily_challenge(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|create_daily_challenge| from {interaction.user.name}")
    if not interaction.user.guild_permissions.administrator:
      await interaction.response.send_message("Missing Administrator permissions")
      return

    await interaction.response.defer()
    # data template: {challenge: "<name>", category: "<category>", 
    #                 options: [<A>, <B>, <C>, <D>], solution: <X>}
    # grap category
    # grab problem
    # grap options (4)
    # grab winner
    # store
    await interaction.followup.send("@todo create_daily_challenge")

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(DailyChallenges(bot))