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
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from utils.json import load_json, save_json
from utils.achievement import add_user_stat

from .local.daily_problems import daily_problems_handler
from .local.create_daily_problem import create_daily_problem_handler


#***************************************************************************************************
class DailyProblems(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


#***************************************************************************************************
  async def daily_task(self) -> None:
    for file in os.listdir("data/daily_problems"):
      if file.endswith(".json"):
        self.bot.logger.info(f"Removed problem data/daily_problems/{file}")
        os.remove(f"data/daily_problems/{file}")

    for file in os.listdir("data/daily_problems/problem_data"):
      if file.endswith(".json"):
        problem_data = load_json(f"problem_data/{file[:-5]}", "daily_problems")
        if problem_data["problems"]:
            problem = problem_data["problems"].pop(0)
            save_json(problem_data, f"problem_data/{file[:-5]}", "daily_problems")
            save_json(problem, problem["problem_id"], "daily_problems")
        else:
            self.bot.logger.info(f"No problems left for {file[-5]}")

    tried_problems = {}
    save_json(tried_problems, "tried_problems", "daily_problems")


#***************************************************************************************************
  @app_commands.command(
    name = "daily_problems",
    description = "Show daily problems and try to solve them"
  )
  async def daily_problems(self, interaction: discord.Interaction) -> None:
    self.bot.logger.info(f"(INTERACTION) |daily_problems| from <{interaction.user.name}>")
    await interaction.response.defer()

    await daily_problems_handler(bot = self.bot, interaction = interaction)


#***************************************************************************************************
  @app_commands.command(
    name = "create_daily_problem",
    description = "(ADMIN) Create a daily problem for users to solve"
  )
  @app_commands.describe(
    category = "Category of the problem"
  )
  @app_commands.describe(
    prize = "Economic reward for users who solve the problem correctly"
  )
  async def create_daily_problem(self, interaction: discord.Interaction, category: str, 
                                  prize: int) -> None:
    self.bot.logger.info(f"(INTERACTION) |create_daily_problem| from <{interaction.user.name}>")

    if not interaction.user.guild_permissions.administrator:
      await interaction.response.send_message(f"<@{interaction.user.id}> Missing Administrator "
                                              "permissions")
      return

    await create_daily_problem_handler(interaction = interaction, category = category, 
                                      prize = prize)
    

#***************************************************************************************************
async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(DailyProblems(bot))