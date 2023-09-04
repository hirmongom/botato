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
from .local.daily_challenges_ui import ChallengeSelect, FutureIdButton, FutureModalButton, FutureModal, SolutionSelect

class DailyChallenges(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


  async def daily_task(self) -> None:
    for file in os.listdir("data/daily_challenges"):
      if file.endswith(".json"):
        self.bot.interaction_logger.info(f"Removed challenge data/daily_challenges/{file}")
        os.remove(f"data/daily_challenges/{file}")

    for file in os.listdir("data/daily_challenges/problem_data"):
      if file.endswith(".json"):
        problem_data = load_json(f"problem_data/{file[:-5]}", "daily_challenges")
        if problem_data["problems"]:
            problem = problem_data["problems"].pop(0)
            save_json(problem_data, f"problem_data/{file[:-5]}", "daily_challenges")
            save_json(problem, problem["problem_id"], "daily_challenges")
        else:
            self.bot.interaction_logger.info(f"No problems left for {file[-5]}")

    tried_challenges = {}
    save_json(tried_challenges, "tried_challenges", "daily_challenges")


  @app_commands.command(
    name = "daily_challenges",
    description = "Show daily challenges and try to solve them"
  )
  async def daily_challenges(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|daily_challenges| from {interaction.user.name}")
    await interaction.response.defer()

    challenges = []
    for file in os.listdir("data/daily_challenges/"):
      if file.endswith(".json") and file != "tried_challenges.json":
        file = file[:-5]
        challenge = load_json(file, "daily_challenges")
        challenge["filename"] = file
        challenges.append(challenge)

    embed = discord.Embed(
      title = "🌟 Current Challenges 🌟",
      description = "💡 Sharpen your mind with Daily Challenges! Solve math puzzles, conquer "
                    "coding problems, and unravel riddles. Test your skills and win rewards!",
      colour = discord.Colour.blue()
    )

    if len(challenges) == 0:
      embed.add_field(name = "No available challenges at the moment", value = "", inline = False)
      embed.add_field(name = "", value = "", inline = False) # Pre-footer separator
      embed.set_footer(text = "Skilled Problems | Botato Braintraining", icon_url = self.bot.user.display_avatar.url)
      await interaction.followup.send(embed = embed)
      return

    for i, challenge in enumerate(challenges):
      embed.add_field(name = "", value = f"```🔮 {i + 1} {challenge['category']} 💶{challenge['prize']}€ ```", 
                      inline = False)
      embed.add_field(name = "", value = challenge["problem"], inline = False)
    embed.add_field(name = "", value = "", inline = False) # Pre-footer separator
    embed.set_footer(text = "Skilled Problems | Botato Braintraining", icon_url = self.bot.user.display_avatar.url)

    challenge_future = asyncio.Future()
    select_menu = ChallengeSelect(user_id = interaction.user.id, challenges = challenges, 
                                  future = challenge_future)
    view = discord.ui.View()
    view.add_item(select_menu)
    message = await interaction.followup.send(embed = embed, view = view)

    challenge = await challenge_future
    challenge = challenges[challenge]
    view.clear_items()
    
    # check if user has atempetd challenge
    tried_challenges = load_json("tried_challenges", "daily_challenges")
    if interaction.user.name in tried_challenges:
      if challenge["filename"] in tried_challenges[interaction.user.name]:
        view.clear_items()
        await message.edit(embed = embed, view = view)
        await interaction.followup.send("You have already atempted this challenge")
        return

    embed = discord.Embed(
      title = f"📚{challenge['category']}📚",
      description = f"🔍 {challenge['problem']}",
      colour = discord.Colour.blue()
    )
    embed.add_field(name = "", value = "``` 🔘 Possible Options ```", inline = False)
    selection_future = asyncio.Future()

    map_color = ["🔴", "🔵", "🟢", "🟡"]
    for i, option in enumerate(challenge["options"]):
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

    if selection == challenge["solution"]:
      economy_data = load_json(interaction.user.name, "economy")
      economy_data["bank_balance"] += challenge["prize"]
      save_json(economy_data, interaction.user.name, "economy")
      await add_user_stat("completed_daily_challenges", interaction)
      await interaction.followup.send(f"That was correct. You received {challenge['prize']}€")
    else:
      await interaction.followup.send("Wrong answer, better luck next time!")

    if interaction.user.name not in tried_challenges:
      tried_challenges[interaction.user.name] = [challenge["filename"]]
    else:  
      tried_challenges[interaction.user.name].append(challenge["filename"])
    save_json(tried_challenges, "tried_challenges", "daily_challenges")

  @app_commands.command(
    name = "create_daily_challenge",
    description = "Create a daily challenge for users to solve"
  )
  @app_commands.describe(
    category = "Category of the problem"
  )
  @app_commands.describe(
    prize = "Economic reward for users who solve the problem correctly"
  )
  async def create_daily_challenge(self, interaction: discord.Interaction, category: str, 
                                  prize: int) -> None:
    self.bot.interaction_logger.info(f"|create_daily_challenge| from {interaction.user.name}")
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

    challenge_data = {
      "category": category,
      "problem": problem,
      "options": options,
      "solution": solution,
      "prize": prize,
    }
    now = datetime.now()
    save_json(challenge_data, f"{now.day}{now.hour}{now.minute}{now.second}", "daily_challenges")
    

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(DailyChallenges(bot))