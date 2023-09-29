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
from utils.custom_ui import FutureSelectMenu, FutureModal, ModalButton


#***************************************************************************************************
async def bet_handler(bot: commands.Bot, interaction: discord.Interaction) -> None:
  # Get and send view
  embed = get_initial_embed(bot)
  message = await interaction.followup.send(embed = embed)

  event_ids, event_names = load_events(embed = embed)
  if len(event_ids) == 0:
    embed.add_field(name = "There are no current events", value = "", inline = False)
    await message.edit(embed = embed)
    return

  event_future = asyncio.Future()
  event_select = FutureSelectMenu(user_id = interaction.user.id, future = event_future, 
                                  options = event_names, placeholder = "Select an event")

  view = discord.ui.View()
  view.add_item(event_select)
  await message.edit(embed = embed, view = view)

  # Load event
  event = await event_future
  event_id = event_ids[event]

  event_data = load_json(f"{event_id}/{event_id}_bet", "bets")
  bettors = load_json(f"{event_id}/{event_id}_bettors", "bets")

  await message.edit(embed = embed, view = view)

  # Check if event is closed
  if event_data["status"] == "closed":
    await interaction.followup.send(f"<@{interaction.user.id}> Bets for {event_data['event']} are "
                                    "closed")
    return

  # Check if user has already placed a bet in {event_id} event
  for key in bettors.keys():
    if key == interaction.user.name:
      await interaction.followup.send(f"<@{interaction.user.id}> You have already placed a bet on "
                                      "this event")
      return

  # Get bet info
  user_bet = await get_user_bet(interaction = interaction, message = message, view = view, 
                                embed = embed, event_id = event_id, bettors = bettors)
  amount = user_bet[0]
  choice = user_bet[1]
  choice_name = user_bet[2]
  await message.edit(embed = embed, view = None)

  # Run checks
  try:
    amount = round(float(amount), 2)
  except Exception:
    await interaction.followup.send(f"<@{interaction.user.id}> Bet amount must be a number")
    return

  economy_data = load_json(interaction.user.name, "economy")
  if economy_data["hand_balance"] < amount:
    await interaction.followup.send(f"<@{interaction.user.id}> You do not have enough money")
    return

  # Process bet
  economy_data["hand_balance"] -= amount
  event_data["pool"] += amount
  bettors[interaction.user.name] = (choice, amount)
  save_json(economy_data, interaction.user.name, "economy")
  save_json(event_data, f"{event_id}/{event_id}_bet", "bets")
  save_json(bettors, f"{event_id}/{event_id}_bettors", "bets")

  await interaction.followup.send(f"<@{interaction.user.id}> You placed a bet of {amount}€ " 
                                  f"on {choice_name} in {event_names[event]}")
  await add_user_stat("bets_placed", interaction)


#***************************************************************************************************
def get_initial_embed(bot: commands.Bot) -> discord.Embed:
  embed = discord.Embed(
    title = "💰 Betting House",
    description = f"Check the next events and place bets on them!",
    color = discord.Colour.teal()
  )
  embed.set_footer(text = "Lucky Betting | Botato Bets", 
                  icon_url = bot.user.display_avatar.url)
  return embed


#***************************************************************************************************
def load_events(embed: discord.Embed) -> (list[str], list[str]):
  event_ids = []
  event_names = []
  for event_id in os.listdir("data/bets/"):
    if event_id != ".gitkeep":
      event_data = load_json(f"{event_id}/{event_id}_bet", "bets")
      embed.add_field(name = f"", value = f"```📅 {event_data['day']}/{event_data['month']}```", 
                      inline = False)
      embed.add_field(name = f"🎫 {event_data['event']}", value = f"💵 {event_data['pool']}€" , 
                      inline = False)

      event_ids.append(event_id)
      event_names.append(event_data["event"]) 
  embed.add_field(name = "", value = "", inline = False) # pre-footer separator

  return event_ids, event_names


#***************************************************************************************************
async def get_user_bet(interaction: discord.Interaction, message: discord.Message, 
                      view: discord.ui.View, embed: discord.Embed, event_id: str, 
                      bettors: dict) -> list[int, str, str]:
  bet_choices = load_json(f"{event_id}/{event_id}_choices", "bets")

  bet_choice_future = asyncio.Future()
  bet_choice_select = FutureSelectMenu(user_id = interaction.user.id, future = bet_choice_future,
                                        options = list(bet_choices.values()),
                                        placeholder = "Choose your bet")

  view.add_item(bet_choice_select)
  await message.edit(embed = embed, view = view)

  bet_choice = await bet_choice_future
  bet_choice_name = list(bet_choices.values())[bet_choice]

  bet_amount_future = asyncio.Future()
  bet_amount_modal = FutureModal(future = bet_amount_future, label = "Bet amount", 
                                placeholder = "€", title = "Enter how much you want to bet")
  bet_amount_button = ModalButton(user_id = interaction.user.id, modal = bet_amount_modal,
                                  label = "Bet amount")

  view.add_item(bet_amount_button)
  await message.edit(embed = embed, view = view)

  bet_amount = await bet_amount_future

  return [bet_amount, bet_choice, bet_choice_name]