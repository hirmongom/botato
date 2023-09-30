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
import calendar
from datetime import datetime

import discord
from discord.ext import commands

from utils.json import save_json
from utils.custom_ui import FutureModal, ModalButton, FutureConfirmationButton


#***************************************************************************************************
async def create_event_handler(interaction: discord.Interaction, day: int, month: int, 
                              year: int) -> None:
  embed = discord.Embed(
    title = "New event",
    description = "",
    color = discord.Color.blue())
  embed.add_field(name = f"📅 {day}/{month}", value = "", inline = True)
  message = await interaction.followup.send(embed = embed, ephemeral = True)

  view = discord.ui.View()

  # Get event name
  event_name = await get_event_name(interaction = interaction, view = view, message = message, 
                                    embed = embed)
  view.clear_items()
  embed.add_field(name = f"🎫 {event_name}", value = "", inline = False)

  # Get event pool
  event_pool = await get_event_pool(interaction = interaction, view = view, message = message, 
                                    embed = embed)
  if event_pool == -1:
    return

  view.clear_items()
  embed.add_field(name = f"💵 Pool of {event_pool}€", value = "", inline = False)

  # Get event choices and confirm event
  choices = await get_event_choices(interaction = interaction, view = view, message = message, 
                                    embed = embed)
  
  if len(choices) < 2:
    await interaction.followup.send(f"<@{interaction.user.id}> 2 Choices minimum", ephemeral = True)
    return

  # Store event
  now = datetime.now()
  bet_identifier = f"{now.month}{now.day}{now.minute}"

  os.mkdir(f"data/bets/{bet_identifier}")
  bet_data = {
    "ix": bet_identifier,
    "day": day,
    "month": month,
    "year": year,
    "event": event_name,
    "pool": event_pool,
    "status": "open"
  }
  save_json(bet_data, f"{bet_identifier}/{bet_identifier}_bet", "bets")

  bet_choices = {}
  for i, choice in enumerate(choices):
    bet_choices[i] = choice
  save_json(bet_choices, f"{bet_identifier}/{bet_identifier}_choices", "bets")

  await interaction.followup.send(f"<@{interaction.user.id}> Event created", ephemeral = True)


#***************************************************************************************************
async def get_event_name(interaction: discord.Interaction, view: discord.ui.View, 
                        message: discord.Message, embed: discord.Embed) -> str:
  name_future = asyncio.Future()

  name_modal = FutureModal(future = name_future, label = "Event name", placeholder = "", 
                          title = "Set event name")
  name_button = ModalButton(user_id = interaction.user.id, modal = name_modal, label = "Event Name")
  view.add_item(name_button)
  
  await message.edit(embed = embed, view = view)

  event_name = await name_future
  return event_name


#***************************************************************************************************
async def get_event_pool(interaction: discord.Interaction, view: discord.ui.View, 
                        message: discord.Message, embed: discord.Embed) -> float:
  pool_future = asyncio.Future()

  pool_modal = FutureModal(future = pool_future, label = "Event pool", placeholder = "€", 
                          title = "Set event pool")
  pool_button = ModalButton(user_id = interaction.user.id, modal = pool_modal, label = "Event Pool")
  view.add_item(pool_button)
  
  await message.edit(embed = embed, view = view)

  event_pool = await pool_future
  try:
    event_pool = round(float(event_pool), 2)
  except Exception:
    await message.edit(embed = embed, view = None)
    await interaction.followup.send(f"<@{interaction.user.id}> Pool must be a number", 
                                    ephemeral = True)
    return -1

  return event_pool


#***************************************************************************************************
async def get_event_choices(interaction: discord.Interaction, view: discord.ui.View, 
                            message: discord.Message, embed: discord.Embed) -> list[str]:

  event_future = asyncio.Event()
  event_confirmed_button = FutureConfirmationButton(user_id = interaction.user.id, 
                                                    label = "Confirm Event",
                                                    style = discord.ButtonStyle.primary, 
                                                    future = event_future)

  view.add_item(event_confirmed_button)
  embed.add_field(name = "📋 Choices:", value = "", inline = False)
  await message.edit(embed = embed, view = view)

  choices = []
  task = asyncio.create_task(choice_handler(interaction.user.id, choices, embed, message, view))

  while not event_future.is_set():
    await asyncio.sleep(0.5)

  task.cancel()
  await message.edit(embed = embed, view = None)
  
  return choices


#***************************************************************************************************
async def choice_handler(user_id: int, choices: list[str], embed: discord.Embed, 
                        message :discord.Message, view: discord.ui.View) -> None:
  while True:
    choice_future = asyncio.Future()
    choice_modal = FutureModal(future = choice_future, label = "Add choice", placeholder = "choice", 
                              title = "Add choice")
    choice_button = ModalButton(user_id  = user_id, modal = choice_modal, label = "Add Choice")
    view.add_item(choice_button)

    await message.edit(embed = embed, view = view)
    choice = await choice_future

    choices.append(choice)
    embed.add_field(name = choice, value = "", inline = False)

    view.remove_item(view.children[1])

    await message.edit(embed = embed, view = view)


#***************************************************************************************************
def get_possible_days(year: int, month: int) -> list[int]:
  max_day = calendar.monthrange(year, month)[1]
  possible_days = list(range(1, max_day + 1))
  return possible_days