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

import discord
from discord.ext import commands

from utils.json import load_json, save_json
from utils.custom_ui import FutureSelectMenu, FutureButton
from utils.achievement import add_user_stat


#***************************************************************************************************
async def daily_problems_handler(bot: commands.Bot, interaction: discord.Interaction) -> None:
  problems = load_problems()
  embed, available_problems = make_initial_embed(bot = bot, problems = problems)

  message = await interaction.followup.send(embed = embed)
  if not available_problems:
    return

  problem = await get_problem(interaction = interaction, message = message, embed = embed, 
                              problems = problems)
  
  # check if user has atempted problem
  tried_problems = load_json("tried_problems", "daily_problems")
  if interaction.user.name in tried_problems:
    if problem["filename"] in tried_problems[interaction.user.name]:
      await interaction.followup.send(f"<@{interaction.user.id}> You have already atempted this "
                                      "problem")
      return

  embed, selection_future = await show_problem_menu(bot = bot, interaction = interaction, 
                                                    message = message, problem = problem)

  selection = await selection_future
  await message.edit(embed = embed, view = None)

  await process_solution(interaction = interaction, selection = selection, problem = problem)


#***************************************************************************************************
def load_problems() -> list[dict]:
  problems = []
  for file in os.listdir("data/daily_problems/"):
    if file.endswith(".json") and file != "tried_problems.json":
      file = file[:-5]
      problem = load_json(file, "daily_problems")
      problem["filename"] = file
      problems.append(problem)
  return problems


#***************************************************************************************************
def make_initial_embed(bot: commands.Bot, problems: list[dict]) -> (discord.Embed, bool):
  available_problems = True

  embed = discord.Embed(
    title = "🌟 Current Problems 🌟",
    description = "💡 Sharpen your mind with Daily Problems! Solve math puzzles, conquer "
                  "coding problems, and unravel riddles. Test your skills and win rewards!",
    colour = discord.Colour.blue()
  )

  if len(problems) == 0:
    embed.add_field(name = "No available problems at the moment", value = "", inline = False)
    available_problems = False
  else:
    for i, problem in enumerate(problems):
      embed.add_field(name = "", 
                      value = f"```🔮 {i + 1} {problem['category']} 💶{problem['prize']}€ ```", 
                      inline = False)
      embed.add_field(name = "", value = problem["problem"], inline = False)

  embed.add_field(name = "", value = "", inline = False) # Pre-footer separator
  embed.set_footer(text = "Skilled Problems | Botato Braintraining", 
                  icon_url = bot.user.display_avatar.url)

  return embed, available_problems


#***************************************************************************************************
async def get_problem(interaction: discord.Interaction, message: discord.message, 
                      embed: discord.Embed, problems: list[dict]) -> dict:
  choices = []
  for problem in problems:
    choices.append(problem["category"])

  problem_future = asyncio.Future()
  problem_select = FutureSelectMenu(user_id = interaction.user.id, future = problem_future, 
                                    options = choices)

  view = discord.ui.View()
  view.add_item(problem_select)
  await message.edit(embed = embed, view = view)

  problem = await problem_future
  await message.edit(embed = embed, view = None) 

  return problems[problem]


#***************************************************************************************************
async def show_problem_menu(bot: commands.Bot, interaction: discord.Interaction, 
                        message: discord.Message, problem: dict) -> (discord.Embed, asyncio.Future):
  embed = discord.Embed(
    title = f"📚 {problem['category']} 📚",
    description = f"🔍 {problem['problem']}",
    colour = discord.Colour.blue()
  )
  embed.add_field(name = "", value = "``` 🔘 Possible Options ```", inline = False)

  selection_future = asyncio.Future()
  map_color = ["🔴", "🔵", "🟢", "🟡"]

  view = discord.ui.View()
  row = 0
  for i, option in enumerate(problem["options"]):
    if i == 2:
      embed.add_field(name = "", value = "", inline = False) # Separator
      row = 1
    embed.add_field(name = f"{map_color[i]} Option {i + 1}", value = option, inline = True)
    selection_button = FutureButton(user_id = interaction.user.id, future = selection_future, 
                                    button_id = i, label = f"{map_color[i]} Option {i + 1}", 
                                    row = row)
    view.add_item(selection_button)

  embed.add_field(name = "", value = "", inline = False) # Pre-footer separator
  embed.set_footer(text = "Skilled Problems | Botato Braintraining", 
                  icon_url = bot.user.display_avatar.url)

  await message.edit(embed = embed, view = view)
  return embed, selection_future


#***************************************************************************************************
async def process_solution(interaction: discord.Interaction, selection: int, problem: dict) -> None:
  if selection == problem["solution"]:
    economy_data = load_json(interaction.user.name, "economy")
    economy_data["bank_balance"] += problem["prize"]
    save_json(economy_data, interaction.user.name, "economy")
    await add_user_stat("completed_daily_problems", interaction)
    await interaction.followup.send(f"<@{interaction.user.id}> That was correct. You received "
                                    f"{problem['prize']}€")
  else:
    await interaction.followup.send(f"<@{interaction.user.id}> Wrong answer, better luck next time")

  tried_problems = load_json("tried_problems", "daily_problems")
  if interaction.user.name not in tried_problems:
    tried_problems[interaction.user.name] = [problem["filename"]]
  else:  
    tried_problems[interaction.user.name].append(problem["filename"])
  save_json(tried_problems, "tried_problems", "daily_problems")