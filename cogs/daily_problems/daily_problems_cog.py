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
from utils.funcs import add_user_stat
from .local.daily_problems_ui import ProblemSelect, FutureIdButton, FutureModalButton, FutureModal, SolutionSelect

class DailyProblems(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


  async def daily_task(self) -> None:
    for file in os.listdir("data/daily_problems"):
      if file.endswith(".json"):
        self.bot.interaction_logger.info(f"Removed problem data/daily_problems/{file}")
        os.remove(f"data/daily_poroblems/{file}")

    for file in os.listdir("data/daily_problems/problem_data"):
      if file.endswith(".json"):
        problem_data = load_json(f"problem_data/{file[:-5]}", "daily_problems")
        if problem_data["problems"]:
            problem = problem_data["problems"].pop(0)
            save_json(problem_data, f"problem_data/{file[:-5]}", "daily_problems")
            save_json(problem, problem["problem_id"], "daily_problems")
        else:
            self.bot.interaction_logger.info(f"No problems left for {file[-5]}")

    tried_problems = {}
    save_json(tried_problems, "tried_problems", "daily_problems")


  @app_commands.command(
    name = "daily_problems",
    description = "Show daily problems and try to solve them"
  )
  async def daily_problems(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|daily_problems| from {interaction.user.name}")
    await interaction.response.defer()

    problems = []
    for file in os.listdir("data/daily_problems/"):
      if file.endswith(".json") and file != "tried_problems.json":
        file = file[:-5]
        problem = load_json(file, "daily_problems")
        problem["filename"] = file
        problems.append(problem)

    embed = discord.Embed(
      title = "🌟 Current Problems 🌟",
      description = "💡 Sharpen your mind with Daily Problems! Solve math puzzles, conquer "
                    "coding problems, and unravel riddles. Test your skills and win rewards!",
      colour = discord.Colour.blue()
    )

    if len(problems) == 0:
      embed.add_field(name = "No available problems at the moment", value = "", inline = False)
      embed.add_field(name = "", value = "", inline = False) # Pre-footer separator
      embed.set_footer(text = "Skilled Problems | Botato Braintraining", icon_url = self.bot.user.display_avatar.url)
      await interaction.followup.send(embed = embed)
      return

    for i, problem in enumerate(problems):
      embed.add_field(name = "", value = f"```🔮 {i + 1} {problem['category']} 💶{problem['prize']}€ ```", 
                      inline = False)
      embed.add_field(name = "", value = problem["problem"], inline = False)
    embed.add_field(name = "", value = "", inline = False) # Pre-footer separator
    embed.set_footer(text = "Skilled Problems | Botato Braintraining", icon_url = self.bot.user.display_avatar.url)

    problem_future = asyncio.Future()
    select_menu = ProblemSelect(user_id = interaction.user.id, problems = problems, 
                                  future = problem_future)
    view = discord.ui.View()
    view.add_item(select_menu)
    message = await interaction.followup.send(embed = embed, view = view)

    problem = await problem_future
    problem = problems[problem]
    view.clear_items()
    
    # check if user has atempetd problem
    tried_problems = load_json("tried_problems", "daily_problems")
    if interaction.user.name in tried_problems:
      if problem["filename"] in tried_problems[interaction.user.name]:
        view.clear_items()
        await message.edit(embed = embed, view = view)
        await interaction.followup.send("You have already atempted this problem")
        return

    embed = discord.Embed(
      title = f"📚 {problem['category']} 📚",
      description = f"🔍 {problem['problem']}",
      colour = discord.Colour.blue()
    )
    embed.add_field(name = "", value = "``` 🔘 Possible Options ```", inline = False)
    selection_future = asyncio.Future()

    map_color = ["🔴", "🔵", "🟢", "🟡"]
    for i, option in enumerate(problem["options"]):
      if i == 2:
        embed.add_field(name = "", value = "", inline = False) # Separator
      embed.add_field(name = f"{map_color[i]} Option {i + 1}", value = option, inline = True)
      selection_button = FutureIdButton(user_id = interaction.user.id, future = selection_future, 
                                        id = i, label = f"{map_color[i]} Option {i + 1}")
      view.add_item(selection_button)
    embed.add_field(name = "", value = "", inline = False) # Pre-footer separator
    embed.set_footer(text = "Skilled Problems | Botato Braintraining", icon_url = self.bot.user.display_avatar.url)
  
    await message.edit(embed = embed, view = view)

    selection = await selection_future
    view.clear_items()
    await message.edit(embed = embed, view = view)

    if selection == problem["solution"]:
      economy_data = load_json(interaction.user.name, "economy")
      economy_data["bank_balance"] += problem["prize"]
      save_json(economy_data, interaction.user.name, "economy")
      await add_user_stat("completed_daily_problems", interaction)
      await interaction.followup.send(f"That was correct. You received {problem['prize']}€")
    else:
      await interaction.followup.send("Wrong answer, better luck next time!")

    if interaction.user.name not in tried_problems:
      tried_problems[interaction.user.name] = [problem["filename"]]
    else:  
      tried_problems[interaction.user.name].append(problem["filename"])
    save_json(tried_problems, "tried_problems", "daily_problems")

  @app_commands.command(
    name = "create_daily_problem",
    description = "Create a daily problem for users to solve"
  )
  @app_commands.describe(
    category = "Category of the problem"
  )
  @app_commands.describe(
    prize = "Economic reward for users who solve the problem correctly"
  )
  async def create_daily_problem(self, interaction: discord.Interaction, category: str, 
                                  prize: int) -> None:
    self.bot.interaction_logger.info(f"|create_daily_problem| from {interaction.user.name}")
    if not interaction.user.guild_permissions.administrator:
      await interaction.response.send_message("Missing Administrator permissions")
      return

    problem_future = asyncio.Future()
    future_modal = FutureModal(future = problem_future, title = "Problem", 
                              label = "Define the problem", placeholder = "problem")

    await interaction.response.send_modal(future_modal)
    problem = await problem_future

    embed = discord.Embed(
      title = category,
      description = problem,
      colour = discord.Colour.blue()
    )
    embed.add_field(name = "", value = "``` Options ```", inline = False)
    message = await interaction.followup.send(embed = embed, ephemeral = True)

    view = discord.ui.View()
    options = []
    for i in range(4):
      future_button = asyncio.Future()
      option_button = FutureModalButton(future = future_button, label = f"Option {i}", 
                                      style = discord.ButtonStyle.primary)
      view.add_item(option_button)
      await message.edit(embed = embed, view = view)
      option = await future_button
      options.append(option)
      embed.add_field(name = f"Option {i}", value = options[i], inline = False)
      view.clear_items()
    
    solution_future = asyncio.Future()
    solution_select = SolutionSelect(future = solution_future)
    view.add_item(solution_select)
    await message.edit(embed = embed, view = view)

    solution = await solution_future
    view.clear_items()
    embed.add_field(name = "", value = "``` Solution ```", inline = False)
    embed.add_field(name = f"Option {solution}", value = options[solution], inline = False)
    await message.edit(embed = embed, view = view)

    problem_data = {
      "category": category,
      "problem": problem,
      "options": options,
      "solution": solution,
      "prize": prize,
    }
    now = datetime.now()
    save_json(problem_data, f"{now.day}{now.hour}{now.minute}{now.second}", "daily_problems")
    

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(DailyProblems(bot))