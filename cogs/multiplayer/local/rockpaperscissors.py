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
import time
from typing import Callable

import discord
from discord.ext import commands

from utils.json import load_json, save_json
from utils.custom_ui import CoroButton


#***************************************************************************************************
move_name_map = ["Rock", "Paper", "Scissors"]
move_emoji_map = ["🪨", "📄", "✂️"]
num_emoji_map = ["0️⃣", "1️⃣", "2️⃣", "3️⃣"]


# @todo need some kind of timeout so that if the command has been running for a lot of time, 
# it gives the money back
#***************************************************************************************************
async def rockpaperscissors_handler(bot: commands.Bot, interaction: discord.Interaction, 
                                    message: discord.Message, players: list[discord.Member], 
                                    bet: float, bestof: int) -> None:
  if not await charge_users(interaction = interaction, players = players, bet = bet):
    return

  embed = get_embed(bot = bot, players = players, bet = bet, bestof = bestof)
  await message.edit(embed = embed)

  button_press = lambda interaction, button_id: (
      button_pressed(interaction, players, button_id)
  )
  # Add view
  future = [asyncio.Future()] # So that it is not mutable
  rounds = [[-1, -1]]
  view = discord.ui.View()
  rock_button = CoroButton(user_id = None, coro = make_button_coro(players, 0, rounds, future),
                          restricted = False, label = move_emoji_map[0])
  view.add_item(rock_button)
  paper_button = CoroButton(user_id = None, coro = make_button_coro(players, 1, rounds, future), 
                            restricted = False, label = move_emoji_map[1])
  view.add_item(paper_button)
  scissors_button = CoroButton(user_id = None, coro = make_button_coro(players, 2, rounds, future), 
                              restricted = False, label = move_emoji_map[2])
  view.add_item(scissors_button)
  
  await message.edit(embed = embed, view = view)

  winner = await game_loop(interaction = interaction, message = message, embed = embed, view = view, 
                          future = future, players = players, rounds = rounds, bestof = bestof)

  if winner == None:
    payout(players = players, bet = bet)
    await interaction.followup.send(f"<@{players[0].id}> <@{players[1].id}> It's a draw")
  else:
    payout(players = players, bet = bet, winner = winner)
    await interaction.followup.send(f"<@{winner.id}> Won")


#***************************************************************************************************
async def charge_users(interaction: discord.Interaction, players: list[discord.Member], 
                      bet: float) -> bool:
  users_data = {}
  for player in players:
    economy_data = load_json(player.name, "economy")
    if economy_data["hand_balance"] < bet:
      await interaction.followup.send(f"<@{player.id}> doesn't have enough money in hand")
      return False
    else:
      users_data[player.name] = economy_data
  
  for player in users_data.keys():
    users_data[player]["hand_balance"] -= bet
    save_json(users_data[player], player, "economy")
  return True


#***************************************************************************************************
def get_embed(bot: commands.Bot, players: list[discord.Member], bet: float, 
              bestof: int) -> discord.Embed:
  embed = discord.Embed(
    title = "🪨Rock 📄Paper ✂️Scissors",
    description = f"💰 Stake: {bet}€\n🏆 Format: Best of {bestof}",
    colour = discord.Colour.blue()
  )
  embed.add_field(name = "", value = "```🎮 Players ```", inline = False)
  embed.add_field(name = f"`{players[0].display_name}`", value = "", inline = True)
  embed.add_field(name = f"`{players[1].display_name}`", value = "", inline = True)
  embed.add_field(name = "", value = "```🔄 Rounds ```", inline = False)
  embed.add_field(name = "", value = "", inline = False) # Pre-footer separator
  embed.set_footer(text = "Botato Rock Paper Scissors | Botato Multiplayer Games", 
                  icon_url = bot.user.display_avatar.url)
  return embed


#***************************************************************************************************
def make_button_coro(players: list[discord.Member], button_id: int, rounds: list[list[int]], 
                    future: list[asyncio.Future]) -> Callable[..., None]:
  async def coro(interaction):
    await button_pressed(interaction, players, button_id, rounds, future)
  return coro


#***************************************************************************************************
async def button_pressed(interaction: discord.Interaction, players: list[discord.Member], 
                        button_id: int, rounds: list[list[int]], 
                        future: list[asyncio.Future]) -> None:
  if interaction.user not in players:
    await interaction.followup.send(f"<@{interaction.user.id}> Not allowed", ephemeral = True)
    return # User is not authorized

  if interaction.user == players[0]:
    if rounds[-1][0] == -1:
      rounds[-1][0] = button_id
    else:
      await interaction.followup.send(f"<@{interaction.user.id}> You already chose "
                                      f"{move_name_map[rounds[-1][0]]}", ephemeral = True)
      return
  else:
    if rounds[-1][1] == -1:
      rounds[-1][1] = button_id
    else:
      await interaction.followup.send(f"<@{interaction.user.id}> You already chose "
                                      f"{move_name_map[rounds[-1][1]]}", ephemeral = True)
      return

  future[0].set_result(interaction.user)
  future[0] = asyncio.Future()
  

#**************************************************************************************************
async def game_loop(interaction: discord.Interaction, message: discord.Message, 
                    embed: discord.Embed, view: discord.ui.View, future: asyncio.Future, 
                    players: list[discord.Member], rounds: list[list[int]], 
                    bestof: int) -> discord.Member:
  game_loop = True
  win_count = [0, 0]

  while game_loop:
    embed.add_field(name = "", value = "", inline = True) # Player 1 spot
    embed.add_field(name = "", value = "", inline = True) # Player 2 spot
    embed.add_field(name = "", value = "", inline = False) # Pre-footer separator
    await message.edit(embed = embed, view = view)

    while True: # Round
      try:
        user = await asyncio.wait_for(future[0], timeout = 60)
      except asyncio.TimeoutError:
        await message.edit(embed = embed, view = None)
        await interaction.followup.send(f"<@{players[0].id}> <@{players[1].id}> Game timed out")
        return None
      
      which_player = 0 if user == players[0] else 1
      player_confirm(embed = embed, players = players, player_id = which_player)
      await message.edit(embed = embed, view = view)

      if -1 not in rounds[-1]:
        if rounds[-1][0] == rounds[-1][1]: # Draw
          pass
        elif rounds[-1][0] == (rounds[-1][-1] + 1) % 3:
          which_player = 0
          win_count[0] += 1
        else:
          win_count[1] += 1
          which_player = 1

        update_score(embed = embed, players = players, score = win_count)
        show_choices(embed = embed, round_info = rounds[-1])

        if (win_count[which_player] > (bestof / 2)) or (len(rounds) == bestof):
          view.clear_items()
          game_loop = False
        rounds.append([-1, -1]) # New round
        await message.edit(embed = embed, view = view)
        break

  if win_count[0] == win_count[1]:
    winner = None
  elif win_count[0] > win_count[1]:
    winner = players[0]
  else:
    winner = players[1]

  return winner


#***************************************************************************************************
def player_confirm(embed: discord.Embed, players: list[discord.Member], player_id: int) -> None:
  embed.set_field_at(-3 + player_id, name = "✅", value = "")


#***************************************************************************************************
def show_choices(embed: discord.Embed, round_info = list[int]) -> None:
  embed.set_field_at(-3, name = move_emoji_map[round_info[0]], value = "")
  embed.set_field_at(-2, name = move_emoji_map[round_info[1]], value = "")


#***************************************************************************************************
def update_score(embed: discord.Embed, players: list[discord.Member], score: list[int]) -> None:
  embed.set_field_at(1, name = f"`{players[0].display_name}`", value = num_emoji_map[score[0]])
  embed.set_field_at(2, name = f"`{players[1].display_name}`", value = num_emoji_map[score[1]])
  
 
#***************************************************************************************************
def payout(players: list[discord.Member], bet: float, winner: discord.Member = None) -> None:
  if winner is None:
    for player in players:
      economy_data = load_json(player.name, "economy")
      economy_data["hand_balance"] += bet
      save_json(economy_data, player.name, "economy")
  else:
    economy_data = load_json(winner.name, "economy")
    economy_data["hand_balance"] += bet * 2
    save_json(economy_data, winner.name, "economy")