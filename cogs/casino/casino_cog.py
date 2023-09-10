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
from discord import app_commands
from discord.ext import commands

import random


from utils.json import load_json, save_json
from utils.achievement import add_user_stat

from .local.blackjack import (
  blackjack_start, get_deck, draw_card, dealer_turn, blackjack_winnings, BlackjackButton, get_embed)
from .local.roulette import BetTypeSelect, BetValueSelect, BetAmountButton, process_winnings
from .local.horse_race import HorseSelect, race

class Casino(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


  @app_commands.command(
    name = "blackjack",
    description = "Play a round of blackjack and try to win double your bet"
  )
  @app_commands.describe(
    bet = "Bet amount (€)"
  )
  async def blackjack(self, interaction: discord.Interaction, bet: float) -> None:
    self.bot.logger.info(f"|blackjack| from {interaction.user.name} with bet |{bet}|")
    user_data = load_json(interaction.user.name, "user")
    economy_data = load_json(interaction.user.name, "economy")
    bet = round(bet, 2)

    if bet > economy_data["hand_balance"]:
      await interaction.response.send_message("You do not have enough money in hand")
      return

    await interaction.response.defer()
    
    economy_data["hand_balance"] -= bet
    save_json(economy_data, interaction.user.name, "economy")
    await add_user_stat("blackjack_hands_played", interaction)


    deck = get_deck()
    player_hand, dealer_hand = blackjack_start(deck)
    player_total = sum(card['value'] for card in player_hand)
    dealer_total = sum(card['value'] for card in dealer_hand)

    embed = get_embed(player_hand, player_total, dealer_hand, dealer_total)
    embed.add_field(name = "", value = "", inline = False) # pre-footer separator
    embed.set_footer(text = "Lucky Blackjack | Botato Casino", icon_url = self.bot.user.display_avatar.url)

    future_button = asyncio.Future()
    view = discord.ui.View()

    hit_button = BlackjackButton(style = discord.ButtonStyle.primary, 
                                 label = "Hit",
                                 user_id = interaction.user.id,
                                 future = future_button,
                                 button_id = 0)
    stand_button = BlackjackButton(style = discord.ButtonStyle.green, 
                                   label = "Stand",
                                   user_id = interaction.user.id,
                                   future = future_button,
                                   button_id = 1)
    double_button = BlackjackButton(style = discord.ButtonStyle.red, 
                                    label = "Double Down",
                                    user_id = interaction.user.id,
                                    future = future_button,
                                    button_id = 2)
    retire_button = BlackjackButton(style = discord.ButtonStyle.secondary, 
                                    label = "Retire",
                                    user_id = interaction.user.id,
                                    future = future_button,
                                    button_id = 3)
    
    view.add_item(hit_button)
    view.add_item(stand_button)
    view.add_item(double_button)
    view.add_item(retire_button)
    message = await interaction.followup.send(embed = embed, view = view)

    # Handle game
    while True:
      # Case of 2 ACES count as 22
      if player_total == 22:
        for card in player_hand:
          card['value'] = 1
          break
        player_total = sum(card['value'] for card in player_hand)
        embed = get_embed(player_hand, player_total, dealer_hand, dealer_total)
        embed.add_field(name = "", value = "", inline = False) # pre-footer separator
        embed.set_footer(text = "Lucky Blackjack | Botato Casino", icon_url = self.bot.user.display_avatar.url)
        await message.edit(embed = embed, view = view)

      if player_total == 21:
        dealer_total = dealer_turn(dealer_hand, deck, dealer_total)
        embed = get_embed(player_hand, player_total, dealer_hand, dealer_total, dealer_turn = True)
        embed.add_field(name = "", value = "", inline = False) # pre-footer separator
        embed.set_footer(text = "Lucky Blackjack | Botato Casino", icon_url = self.bot.user.display_avatar.url)
        await message.edit(embed = embed, view = None)
        if dealer_total == 21:
          await blackjack_winnings(bet, economy_data, interaction)
          await interaction.followup.send("It's a draw")
          return
        else:
          winnings = bet + bet * 1.5
          await blackjack_winnings(winnings, economy_data, interaction)
          await interaction.followup.send(f"You've won {winnings}€")
        return
  
      try:
        result = await asyncio.wait_for(future_button, timeout = 60)
      except asyncio.TimeoutError:
        await message.edit(embed = embed, view = None)
        await interaction.followup.send("Timeout: Blackjack game has been canceled")
        return    
      # Reset state
      future_button = asyncio.Future()
      hit_button.future = future_button
      stand_button.future = future_button
      double_button.future = future_button
      retire_button.future = future_button
      
      # Handle button press
      if result == 0: # Hit button
        player_total = draw_card(player_hand, deck)
        embed = get_embed(player_hand, player_total, dealer_hand, dealer_total)
        embed.add_field(name = "", value = "", inline = False) # pre-footer separator
        embed.set_footer(text = "Lucky Blackjack | Botato Casino", icon_url = self.bot.user.display_avatar.url)
        await message.edit(embed = embed, view = view)

        if player_total == 21:
          dealer_total = dealer_turn(dealer_hand, deck, dealer_total)
          embed = get_embed(player_hand, player_total, dealer_hand, dealer_total, dealer_turn = True)
          embed.add_field(name = "", value = "", inline = False) # pre-footer separator
          embed.set_footer(text = "Lucky Blackjack | Botato Casino", icon_url = self.bot.user.display_avatar.url)
          await message.edit(embed = embed, view = None)
          if dealer_total == 21:
            await blackjack_winnings(bet, economy_data, interaction)
            await interaction.followup.send("It's a draw")
          else:
            winnings = bet * 2
            await blackjack_winnings(winnings, economy_data, interaction)
            await interaction.followup.send(f"You've won {winnings}€")
          return
        elif player_total > 21:
          await message.edit(embed = embed, view = None)
          await interaction.followup.send("You went bust")
          return

      elif result == 1: # Stand button
        dealer_total = dealer_turn(dealer_hand, deck, dealer_total)
        embed = get_embed(player_hand, player_total, dealer_hand, dealer_total, dealer_turn = True)
        embed.add_field(name = "", value = "", inline = False) # pre-footer separator
        embed.set_footer(text = "Lucky Blackjack | Botato Casino", icon_url = self.bot.user.display_avatar.url)
        await message.edit(embed = embed, view = None)
        if dealer_total > 21 or dealer_total < player_total:
          winnings = bet * 2
          await blackjack_winnings(winnings, economy_data, interaction)
          await interaction.followup.send(f"You've won {winnings}€")
        elif dealer_total == player_total:
          await blackjack_winnings(bet, economy_data, interaction)
          await interaction.followup.send("It's a draw")
        else:
          await interaction.followup.send("You've lost")
        return

      elif result == 2: # Double down button
        if economy_data["hand_balance"] < bet:
          await interaction.followup.send("You do not have enough money in hand to Double Down")
        else:
          economy_data["hand_balance"] -= bet
          save_json(economy_data, interaction.user.name, "economy")

          bet += bet  
          player_total = draw_card(player_hand, deck)
          embed = get_embed(player_hand, player_total, dealer_hand, dealer_total)
          embed.add_field(name = "", value = "", inline = False) # pre-footer separator
          embed.set_footer(text = "Lucky Blackjack | Botato Casino", icon_url = self.bot.user.display_avatar.url)
          await message.edit(embed = embed, view = None)

          if player_total > 21:
            await message.edit(embed = embed, view = None)
            await interaction.followup.send("You went bust")
            return

          dealer_total = dealer_turn(dealer_hand, deck, dealer_total)
          embed = get_embed(player_hand, player_total, dealer_hand, dealer_total, dealer_turn = True)
          embed.add_field(name = "", value = "", inline = False) # pre-footer separator
          embed.set_footer(text = "Lucky Blackjack | Botato Casino", icon_url = self.bot.user.display_avatar.url)
          await message.edit(embed = embed, view = None)

          if dealer_total > 21 or dealer_total < player_total:
            winnings = bet * 2
            await blackjack_winnings(winnings, economy_data, interaction)
            await interaction.followup.send(f"You've won {winnings}€")
          elif dealer_total == player_total:
            await blackjack_winnings(bet, economy_data, interaction)
            await interaction.followup.send("It's a draw")
          else:
            await interaction.followup.send("You've lost")
          return
      elif result == 3:
        winnings = round(bet / 2, 2)
        await blackjack_winnings(winnings, economy_data, interaction)
        await message.edit(embed = embed, view = None)
        await interaction.followup.send(f"You retired, you've received half your bet: {winnings}€")
        return


  @app_commands.command(
    name = "roulette",
    description = "Spin the wheel and try your luck!"
  )
  async def roulette(self, interaction: discord.Interaction) -> None:
    self.bot.logger.info(f"|roulette| from {interaction.user.name}")
    await interaction.response.defer()

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
    embed.add_field(name = "", value = "", inline = False) # pre-footer separator
    embed.set_footer(text = "Lucky Roulette | Botato Casino", icon_url = self.bot.user.display_avatar.url)

    message = await interaction.followup.send(embed = embed)

    future = asyncio.Future()
    # Bet type  // Select
    view = discord.ui.View()
    bet_type_select = BetTypeSelect(user_id = interaction.user.id, future = future)
    view.add_item(bet_type_select)
    await message.edit(embed = embed, view = view)

    bet_info = await future
    embed.add_field(name = "```Bet Type```", value = f"🎲 {bet_type_map[bet_info[0]]}", inline = True)
    await message.edit(embed = embed, view = view) # Bet Type Select disabled

    # Handle Bet type:
    if bet_info[0] == 0: # Bet Type Straight
      if not bet_info[1].isdigit():
        await interaction.followup.send("Value must be a number")
        return
      bet_info[1] = int(bet_info[1])
      if bet_info[1] < 0 or bet_info[1] > 36:
        await interaction.followup.send("Value must be between 0 and 36")
        return
    else: # Show Select for bet value
      if bet_info[0] == 1: # Bet Type Color
        bet_value_choices = [discord.SelectOption(label = "Red", value = 0), 
                            discord.SelectOption(label = "Black", value = 1)]
      elif bet_info[0] == 2: # Bet Type Eveb/Odd
        bet_value_choices = [discord.SelectOption(label = "Even", value = 0), 
                            discord.SelectOption(label = "Odd", value = 1)]
      elif bet_info[0] == 3: # Bet Type Low/High
        bet_value_choices = [discord.SelectOption(label = "Low (1-18)", value = 0), 
                            discord.SelectOption(label = "High (19-36)", value = 1)]

      future = asyncio.Future()
      bet_value_select = BetValueSelect(user_id = interaction.user.id, future = future, 
                                        options = bet_value_choices)
      view.add_item(bet_value_select)
      await message.edit(embed = embed, view = view)
      
      bet_info[1] = await future

    embed.add_field(name = "```Bet Value```", value = bet_value_map[bet_info[0]][bet_info[1]], inline = True)
    await message.edit(embed = embed, view = view) # Bet Value Select disabled

    # How much? -  after selecting choice
    future = asyncio.Future()
    bet_amount_button = BetAmountButton(label = "Bet Amount", user_id = interaction.user.id, future = future)
    view.add_item(bet_amount_button)
    await message.edit(embed = embed, view = view)

    bet_amount = await future
    await message.edit(embed = embed, view = view) # Bet Amount Button disabled
    # Handle Bet type:
    try:
      bet_amount = round(float(bet_amount), 2)
    except:
        await interaction.followup.send("Value must be a number")
        return
    
    economy_data = load_json(interaction.user.name, "economy")
    if bet_amount > economy_data["hand_balance"]:
      await interaction.followup.send("You do not have enough money in hand")
      
    await add_user_stat("roulettes_played", interaction)
    economy_data["hand_balance"] -= bet_amount
    

    # Spin
    roulette_result = random.randint(0, 36)
    if roulette_result in colour_map[0]:
      roulette_result_colour = "🔴"
    elif roulette_result in colour_map[1]:
      roulette_result_colour = "⚫"
    else:
      roulette_result_colour = "🟢"

    embed.add_field(name = "```The roulette landed on```", 
                    value = f"{roulette_result_colour} {roulette_result}", inline = False)
    embed.add_field(name = "", value = "", inline = False) # pre-footer separator
    await message.edit(embed = embed, view = view)

    if bet_info[0] == 0: # Bet Type Straight
      if roulette_result == bet_info[1]:
        if roulette_result == 0:
          multiplier = 25
        else:
          multiplier = 10
        await process_winnings(economy_data, bet_amount * 2.5 * multiplier, interaction)
        await interaction.followup.send(f"You've won {bet_amount * 2.5 * multiplier}€")
      else:
        await interaction.followup.send("You lost, better luck next time")

    elif bet_info[0] == 1: # Bet Type Colour
      if roulette_result in colour_map[bet_info[1]]:
        await process_winnings(economy_data, bet_amount * 2.5, interaction)
        await interaction.followup.send(f"You've won {bet_amount * 2.5}€")
      else:
        await interaction.followup.send("You lost, better luck next time")

    elif bet_info[0] == 2: # Bet Type Even/Odd
      if bet_info[1] == 0:
        if roulette_result % 2 == 0 and roulette_result != 0:
          await process_winnings(economy_data, bet_amount * 2.5, interaction)
          await interaction.followup.send(f"You've won {bet_amount * 2.5}€")
        else:
          await interaction.followup.send("You lost, better luck next time")
      else:
        if roulette_result % 2 != 0 and roulette_result != 0:
          await process_winnings(economy_data, bet_amount * 2.5, interaction)
          await interaction.followup.send(f"You've won {bet_amount * 2.5}€")
        else:
          await interaction.followup.send("You lost, better luck next time")

    elif bet_info[0] == 3: # Bet Type Low/High
      if bet_info[1] == 0:
        if roulette_result >= 1 and roulette_result <= 18:
          await process_winnings(economy_data, bet_amount * 2.5, interaction)
          await interaction.followup.send(f"You've won {bet_amount * 2.5}€")
        else:
          await interaction.followup.send("You lost, better luck next time")
      else:
        if roulette_result >= 19 and roulette_result <= 36:
          await process_winnings(economy_data, bet_amount * 2.5, interaction)
          await interaction.followup.send(f"You've won {bet_amount * 2.5}€")
        else:
          await interaction.followup.send("You lost, better luck next time")

    save_json(economy_data, interaction.user.name, "economy")


  @app_commands.command(
    name = "horse_race",
    description = "Pick a racer, place your bet, and see if luck's on your side."
  )
  async def horse_race(self, interaction: discord.Interaction) -> None:
    self.bot.logger.info(f"|horse_race| from {interaction.user.name}")
    await interaction.response.defer()

    racer_name_map = [
      "Horse",
      "Ant",
      "Lettuce",
      "Potato"
    ]

    tracks = [
        ["🐎", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_"],
        ["🐜", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_"],
        ["🥬", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_"],
        ["🥔", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_", "_"]
    ]

    embed = discord.Embed(
        title="🏁 Race Track 🏁",
        description="Choose your favorite racer\n and place your bet!",
        colour=discord.Colour.light_gray()
    )
    embed.add_field(name = "", value = f"```{''.join(tracks[0])}  ```", inline = False)
    embed.add_field(name = "", value = f"```{''.join(tracks[1])}  ```", inline = False)
    embed.add_field(name = "", value = f"```{''.join(tracks[2])}  ```", inline = False)
    embed.add_field(name = "", value = f"```{''.join(tracks[3])}  ```", inline = False)
    embed.add_field(name = "", value = "", inline = False) # Pre-footer separator
    embed.set_footer(text = "Lucky Racing | Botato Casino", icon_url = self.bot.user.display_avatar.url)

    response_future = asyncio.Future()
    select_horse = HorseSelect(interaction.user.id, response_future)
    view = discord.ui.View()
    view.add_item(select_horse)

    message = await interaction.followup.send(embed = embed, view = view)
    horse_choice, bet_amount = await response_future
    horse_choice = int(horse_choice)
    await message.edit(embed = embed, view = None)

    try:
      bet_amount = round(float(bet_amount), 2)
    except ValueError:
      await interaction.followup.send("Bet amount must be a number")
      return

    economy_data = load_json(interaction.user.name, "economy")
    if economy_data["hand_balance"] < bet_amount:
      await interaction.followup.send("You do not have enough money in hand")
      return
    else:
      economy_data["hand_balance"] -= bet_amount
      save_json(economy_data, interaction.user.name, "economy")

    await add_user_stat("horse_races_played", interaction)


    winner = await race(message, embed, tracks)

    if winner == horse_choice:
      await add_user_stat("horse_races_won", interaction)
      increase = bet_amount * 4
      economy_data["bank_balance"] += increase
      save_json(economy_data, interaction.user.name, "economy")
      await interaction.followup.send(f"{racer_name_map[winner]} won the race and you received"
                                      f" {increase}€")
    else:
      await interaction.followup.send(f"{racer_name_map[winner]} won the race")


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Casino(bot))