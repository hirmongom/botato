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
import random

import discord
from discord.ext import commands

from utils.json import load_json, save_json
from utils.achievement import add_user_stat
from utils.custom_ui import FutureButton, FutureSelectMenu, FutureModal, ModalButton


#***************************************************************************************************
bet_type_map = {
  0: "Straight",
  1: "Colour",
  2: "Even/Odd",
  3: "Low/High"
}

bet_value_map = [
  {**{i: f"🔢 {i}" for i in range(0, 36)}},
  {0: "🔴 Red", 1: "⚫ Black"},
  {0: "#️⃣ Even", 1: "*️⃣ Odd"},
  {0: "⏬ Low (1-18)", 1: "⏫ High (19-36)"}
]

colour_map = {
  0: [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36],  # Red numbers
  1: [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]  # Black numbers
}


# **************************************************************************************************
async def roulette_game_handler(bot: commands.Bot, interaction: discord.Interaction, 
                                bet: int) -> None:
  # Build interface
  embed = build_embed(bot)
  message = await interaction.followup.send(embed = embed)

  bet_type_future = asyncio.Future()
  view = discord.ui.View()
  bet_type_select = FutureSelectMenu(placeholder = "Bet Type", user_id = interaction.user.id, 
                                    future = bet_type_future, options = list(bet_type_map.values()))
  view.add_item(bet_type_select)
  await message.edit(embed = embed, view = view)


  # Get bet info
  bet_type = int(await bet_type_future)
  await message.edit(embed = embed, view = view) # Bet Type Select disabled

  bet_value = await get_bet_value(embed = embed, message = message, view = view, 
                                  interaction = interaction, bet_type = bet_type)
  await message.edit(embed = embed, view = view) # Bet Value Select disabled

  if bet_value == -1: # Invalid value
    return

  # Spin
  roulette_result = random.randint(0, 36)
  if roulette_result in colour_map[0]:
    roulette_result_colour = "🔴"
  elif roulette_result in colour_map[1]:
    roulette_result_colour = "⚫"
  else:
    roulette_result_colour = "🟢"

  embed.add_field(name = "", value = "```The roulette landed on```", inline = False)
  embed.add_field(name = f"{roulette_result_colour} {roulette_result}", value = "", inline = False)
  embed.add_field(name = "", value = "", inline = False) # Pre-footer separator
  await message.edit(embed = embed, view = view)

  # Handle result
  if bet_type == 0: # Bet Type Straight
    await handle_result_for_straight(interaction, roulette_result, bet, bet_value)
  elif bet_type == 1: # Bet Type Colour
    await handle_result_for_colour(interaction, roulette_result, bet, bet_value)
  elif bet_type == 2: # Bet Type Even/Odd
    await handle_result_for_evenodd(interaction, roulette_result, bet, bet_value)
  elif bet_type == 3: # Bet Type Low/High
    await handle_result_for_lowhigh(interaction, roulette_result, bet, bet_value)


# **************************************************************************************************
def build_embed(bot: commands.Bot) -> discord.Embed:
  embed = discord.Embed(
    title = "🎰 Roulette Wheel 🎰",
    description = "Place your bet and test your luck!",
    color = discord.Colour.red()
  )
  embed.add_field(
    name = "🔴 Red Numbers",
    value = "1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36",
    inline = True
  )
  embed.add_field(
    name = "⚫ Black Numbers",
    value = "2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35",
    inline = True
  )
  embed.add_field(
    name = "🟢 Zero",
    value = "0",
    inline = True
  )
  embed.add_field(
    name = "🎲 Bet Types",
    value = "Straight, Colour, Even/Odd, Low/High",
    inline = False
  )
  embed.add_field(name = "", value = "", inline = False) # Pre-footer separator
  embed.set_footer(text = "Lucky Roulette | Botato Casino", 
                  icon_url = bot.user.display_avatar.url)

  return embed


# **************************************************************************************************
async def get_bet_value(embed: discord.Embed, message: discord.Message, view: discord.ui.View,
                        interaction: discord.Interaction, bet_type: int) -> int:
  bet_value_future = asyncio.Future()
  if bet_type == 0: # Bet Type Straight
    bet_value_modal = FutureModal(title = "Select a Number", label = "Bet Value", 
                                  placeholder = "0-36", future = bet_value_future)
    modal_button = ModalButton(user_id = interaction.user.id, modal = bet_value_modal, 
                              label = "Bet Value")
    view.add_item(modal_button)
    await message.edit(embed = embed, view = view)
    bet_value = await bet_value_future
    await message.edit(embed = embed, view = view) # Modal Button disabled

    if not bet_value.isdigit():
      await interaction.followup.send(f"<@{interaction.user.id}> Value must be a number")
      return -1

    bet_value = int(bet_value)
    if bet_value < 0 or bet_value > 36:
      await interaction.followup.send(f"<@{interaction.user.id}> Value must be between 0 and 36")
      return -1

  else: # Show Select for bet value
    if bet_type == 1: # Bet Type Color
      bet_value_choices = ["Red", "Black"]
    elif bet_type == 2: # Bet Type Even/Odd
      bet_value_choices = ["Even", "Odd"]
    elif bet_type == 3: # Bet Type Low/High
      bet_value_choices = ["Low (1-18)", "High (19-36)"]
    
    bet_value_select = FutureSelectMenu(user_id = interaction.user.id, future = bet_value_future,
                                        options = bet_value_choices, placeholder = "Bet Value")
    view.add_item(bet_value_select)
    await message.edit(embed = embed, view = view)
    bet_value = await bet_value_future

  return int(bet_value)


# **************************************************************************************************
async def handle_result_for_straight(interaction: discord.Interaction, roulette_result: int, 
                                    bet: int, bet_value: int) -> None:
  if roulette_result == bet_value:
    if roulette_result == 0:
      win_amount = bet * 25
    else:
      win_amount = bet * 10
    await user_win(interaction, win_amount)
  else:
    await interaction.followup.send(f"<@{interaction.user.id}> You lost, better luck next time")


# **************************************************************************************************
async def handle_result_for_colour(interaction: discord.Interaction, roulette_result: int, 
                                    bet: int, bet_value: int) -> None:
  if roulette_result in colour_map[bet_value]:
    win_amount = bet * 2
    await user_win(interaction, win_amount)
  else:
    await interaction.followup.send(f"<@{interaction.user.id}> You lost, better luck next time")


# **************************************************************************************************
async def handle_result_for_evenodd(interaction: discord.Interaction, roulette_result: int, 
                                    bet: int, bet_value: int) -> None:
  if roulette_result == 0:
    await interaction.followup.send(f"<@{interaction.user.id}> You lost, better luck next time")
  else:
    if bet_value == 0: # Even
      if roulette_result % 2 != 0:
        await interaction.followup.send(f"<@{interaction.user.id}> You lost, better luck next time")
        return
    else: # Odd
      if roulette_result % 2 == 0:
        await interaction.followup.send(f"<@{interaction.user.id}> You lost, better luck next time")
        return
    win_amount = bet * 2
    await user_win(interaction, win_amount)


# **************************************************************************************************
async def handle_result_for_lowhigh(interaction: discord.Interaction, roulette_result: int, 
                                    bet: int, bet_value: int) -> None:
  if roulette_result == 0:
    await interaction.followup.send(f"<@{interaction.user.id}> You lost, better luck next time")
  else:
    if bet_value == 0: # Low
      if roulette_result >= 19:
        await interaction.followup.send(f"<@{interaction.user.id}> You lost, better luck next time")
        return
    else: # High
      if roulette_result <= 18:
        await interaction.followup.send(f"<@{interaction.user.id}> You lost, better luck next time")
        return
    win_amount = bet * 2
    await user_win(interaction, win_amount)


#***************************************************************************************************
async def user_win(interaction: discord.Interaction, amount: int) -> None:
  economy_data = load_json(interaction.user.name, "economy")
  economy_data["hand_balance"] += amount
  save_json(economy_data, interaction.user.name, "economy")
  await add_user_stat("roulettes_won", interaction)
  await interaction.followup.send(f"<@{interaction.user.id}> You've won {amount}€")