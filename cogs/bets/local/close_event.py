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
import shutil

import discord
from discord.ext import commands

from utils.json import load_json, save_json
from utils.custom_ui import FutureSelectMenu


#***************************************************************************************************
async def close_event_handler(bot: commands.Bot, interaction: discord.Interaction) -> None:
  # Get available events
  event_names = []
  event_ids = []
  for event in os.listdir("data/bets"):
    if event != ".gitkeep":
      event_data = load_json(f"{event}/{event}_bet", "bets")
      event_names.append(event_data["event"])
      event_ids.append(event)

  if len(event_ids) == 0:
    await interaction.followup.send(f"<@{interaction.user.id}> There are no events going on", 
                                    ephemeral = True)
    return

  # Instantiate message and view
  message = await interaction.followup.send("Loading events..", ephemeral = True)
  view = discord.ui.View()

  # Get event to close
  event = await get_event(interaction = interaction, message = message, view = view, 
                          choices = event_names, values = event_ids)

  # Get event winner
  winner = await get_winner(interaction = interaction, message = message, view = view, 
                            event_id = event)

  # Send rewards
  await process_winners(bot = bot, event_id = event, event_winner = winner)

  # Remove event
  folder_path = f"data/bets/{event}"
  try:
    shutil.rmtree(folder_path)
    bot.logger.info(f"Folder '{folder_path}' and its contents deleted successfully.")
  except OSError as e:
    bot.logger.error(f"Error deleting folder '{folder_path}: {e}")


#***************************************************************************************************
async def get_event(interaction: discord.Interaction, message: discord.Message, 
                    view: discord.ui.View, choices: list[str], values: list[str]) -> str:
  event_select_future = asyncio.Future()
  event_select = FutureSelectMenu(user_id = interaction.user.id, future = event_select_future,
                                  options = choices, values = values, placeholder = "Select Event")

  view.add_item(event_select)
  await message.edit(content = None, view = view)

  event_select_result = await event_select_future
  return event_select_result


#***************************************************************************************************
async def get_winner(interaction: discord.Interaction, message: discord.Message, 
                    view: discord.ui.View, event_id: int) -> str:
  winner_future = asyncio.Future()
  winner_choices = []
  event_choices = load_json(f"{event_id}/{event_id}_choices", "bets")

  choice_names = []
  choice_values = []
  for key in event_choices:
    choice_names.append(event_choices[key])
    choice_values.append(key)
  choice_names.append("Cancel")
  choice_values.append(-1)

  winner_select = FutureSelectMenu(user_id = interaction.user.id, future = winner_future, 
                                  options = choice_names, values = choice_values,
                                  placeholder = "Select Winner")
 
  view.add_item(winner_select)
  await message.edit(view = view)

  winner_select_result = await winner_future
  await message.edit(view = view) # Select menu disabled

  return int(winner_select_result)


#***************************************************************************************************
async def process_winners(bot: commands.Bot, event_id: int, event_winner: int) -> None:
  channel = bot.get_channel(int(bot.main_channel))

  event_data = load_json(f"{event_id}/{event_id}_bet", "bets")
  bettors = load_json(f"{event_id}/{event_id}_bettors", "bets")
  event_choices = load_json(f"{event_id}/{event_id}_choices", "bets")

  if event_winner == -1: # Return money to user
    for bettor in bettors.keys():
      economy_data = load_json(bettor, "economy")
      economy_data["bank_balance"] += bettors[bettor][1]
      save_json(economy_data, bettor, "economy")
    await channel.send(f"Event {event_data['event']} has been cancelled")
  
  else:
    await channel.send(f"{event_choices[str(event_winner)]} won {event_data['event']}")
    user_ids = load_json("user_ids", "other")
    winner_bettors = []
    winner_bettors_amount = 0

    for key in bettors.keys():
      if bettors[key][0] == event_winner:
        winner_bettors_amount += bettors[key][1]
        winner_bettors.append(key)
        
    for bettor in winner_bettors:
      economy_data = load_json(bettor, "economy")
      percentage = bettors[bettor][1] / winner_bettors_amount
      increase = round(event_data["pool"] * percentage, 2)
      economy_data["bank_balance"] += increase
      await channel.send(f"<@{user_ids[bettor]}> You've won {increase}€ from the pool of "
                        f"{event_data['pool']}€")
      save_json(economy_data, bettor, "economy")