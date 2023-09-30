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
from datetime import datetime

import discord
from discord.ext import commands

from utils.custom_ui import FutureSelectMenu, FutureModal, ModalButton
from utils.json import save_json


#***************************************************************************************************
async def create_daily_problem_handler(interaction: discord.Interaction,
                                      category: str, prize: float) -> None:
  problem = await get_problem_definition(interaction)
  embed = get_embed(category, problem)

  message = await interaction.followup.send(embed = embed, ephemeral = True)

  options = await get_options(interaction = interaction, message = message, embed = embed)
  
  solution = await get_solution(interaction = interaction, message = message, embed = embed, 
                                options = options)

  problem_data = {
    "category": category,
    "problem": problem,
    "options": options,
    "solution": solution,
    "prize": prize,
  }

  now = datetime.now()
  save_json(problem_data, f"{now.day}{now.hour}{now.minute}{now.second}", "daily_problems")

  await interaction.followup.send(f"<@{interaction.user.id}> Daily Problem created", 
                                  ephemeral = True)


#***************************************************************************************************
async def get_problem_definition(interaction: discord.Interaction) -> str:
  problem_future = asyncio.Future()
  future_modal = FutureModal(future = problem_future, title = "Problem", 
                            label = "Define the problem", placeholder = "problem")

  await interaction.response.send_modal(future_modal)
  problem = await problem_future
  return problem


#***************************************************************************************************
def get_embed(category: str, problem: str) -> discord.Embed:
  embed = discord.Embed(
    title = category,
    description = problem,
    colour = discord.Colour.blue()
  )
  embed.add_field(name = "", value = "``` Options ```", inline = False)
  return embed


#***************************************************************************************************
async def get_options(interaction: discord.Interaction, message: discord.Message, 
                      embed: discord.Embed) -> list[str]:
  view = discord.ui.View()

  options = []
  for i in range(4):
    option_future = asyncio.Future()
    option_modal = FutureModal(future = option_future, label = "Option", placeholder = "option", 
                              title = "Add an Option")
    option_button = ModalButton(user_id = interaction.user.id, modal = option_modal, 
                                label = f"Option {i}", style = discord.ButtonStyle.primary)
    view.add_item(option_button)

    await message.edit(embed = embed, view = view)
    option = await option_future

    options.append(option)
    embed.add_field(name = f"Option {i}", value = options[i], inline = False)
    view.clear_items()

  return options


#***************************************************************************************************
async def get_solution(interaction: discord.Interaction, message: discord.Message, 
                      embed: discord.Embed, options: list[str]) -> int:
  solution_future = asyncio.Future()
  solution_select = FutureSelectMenu(user_id = interaction.user.id, future = solution_future, 
                                     options = options, placeholder = "Select Solution")
  view = discord.ui.View()
  view.add_item(solution_select)
  await message.edit(embed = embed, view = view)

  solution = await solution_future
  view.clear_items()
  embed.add_field(name = "", value = "``` Solution ```", inline = False)
  embed.add_field(name = f"Option {solution}", value = options[solution], inline = False)
  await message.edit(embed = embed, view = view)

  return solution