import os
import asyncio

import discord
from discord import app_commands
from discord.ext import commands

import random


from utils.json import load_json, save_json
from utils.funcs import make_casino_data
from .utils.blackjack import (
  blackjack_start, get_deck, draw_card, dealer_turn, blackjack_winnings, BlackjackButton, get_embed)


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
  async def blackjack(self, interaction: discord.Interaction, bet: int) -> None:
    self.bot.interaction_logger.info(f"|blackjack| from {interaction.user.name} with bet |{bet}|")
    economy_data = load_json(interaction.user.name, "economy")
    casino_data = load_json(interaction.user.name, "casino")
    try:
      casino_data["total_casino_winnings"]
    except:
      make_casino_data(interaction.user.name)
      casino_data = load_json(interaction.user.name, "casino")

    if bet > economy_data["hand_balance"]:
      await interaction.response.send_message("You do not have enough money in hand")
      return

    await interaction.response.defer()

    economy_data["hand_balance"] -= bet
    save_json(economy_data, interaction.user.name, "economy")
    casino_data["blackjack_hands_played"] += 1
    casino_data["total_blackjack_winnings"] -= bet
    casino_data["total_casino_winnings"] -= bet
    save_json(casino_data, interaction.user.name, "casino")

    deck = get_deck()
    player_hand, dealer_hand = blackjack_start(deck)
    player_total = sum(card['value'] for card in player_hand)
    dealer_total = sum(card['value'] for card in dealer_hand)

    embed = get_embed(player_hand, player_total, dealer_hand, dealer_total)

    future_button = asyncio.Future()
    view = discord.ui.View()

    hit_button = BlackjackButton(style = discord.ButtonStyle.primary, 
                                 label = "Hit",
                                 user_id = interaction.user.id,
                                 future = future_button,
                                 button_id = 0)
    stand_button = BlackjackButton(style = discord.ButtonStyle.secondary, 
                                   label = "Stand",
                                   user_id = interaction.user.id,
                                   future = future_button,
                                   button_id = 1)
    double_button = BlackjackButton(style = discord.ButtonStyle.red, 
                                    label = "Double Down",
                                    user_id = interaction.user.id,
                                    future = future_button,
                                    button_id = 2)
    
    view.add_item(hit_button)
    view.add_item(stand_button)
    view.add_item(double_button)
    message = await interaction.followup.send(embed = embed, view = view)

    # Handle game
    while True:
      # Case of 2 ACES count as 22
      if player_total == 22:
        while total > 21 and any(card['name'] == 'Ace' and card['value'] == 11 for card in hand):
          # Find the first Ace with value 11 and change its value to 1
          for card in hand:
            if card['name'] == 'Ace' and card['value'] == 11:
              card['value'] = 1
              break
          player_total = sum(card['value'] for card in hand)

      if player_total == 21:
        dealer_total = dealer_turn(dealer_hand, deck, dealer_total)
        embed = get_embed(player_hand, player_total, dealer_hand, dealer_total, dealer_turn = True)
        await message.edit(embed = embed, view = None)
        if dealer_total == 21:
          blackjack_winnings(bet, economy_data, casino_data, interaction)
          await interaction.followup.send("It's a draw")
          return
        else:
          winnings = bet + bet * 1.5
          blackjack_winnings(winnings, economy_data, casino_data, interaction)
          await interaction.followup.send(f"You've won {winnings}€")
        return
  
      try:
        result = await asyncio.wait_for(future_button, timeout = 60)
      except asyncio.TimeoutError:
        await interaction.followup.send("Timeout: Blackjack game has been canceled")
        return    
      # Reset state
      future_button = asyncio.Future()
      hit_button.future = future_button
      stand_button.future = future_button
      double_button.future = future_button

      # Handle button press
      if result == 0: # Hit button
        player_total = draw_card(player_hand, deck)
        embed = get_embed(player_hand, player_total, dealer_hand, dealer_total)
        await message.edit(embed = embed, view = view)

        if player_total == 21:
          dealer_total = dealer_turn(dealer_hand, deck, dealer_total)
          embed = get_embed(player_hand, player_total, dealer_hand, dealer_total, dealer_turn = True)
          await message.edit(embed = embed, view = None)
          if dealer_total == 21:
            blackjack_winnings(bet, economy_data, casino_data, interaction)
            await interaction.followup.send("It's a draw")
          else:
            winnings = bet * 2
            blackjack_winnings(winnings, economy_data, casino_data, interaction)
            await interaction.followup.send(f"You've won {winnings}€")
          return
        elif player_total > 21:
          await message.edit(embed = embed, view = None)
          await interaction.followup.send("You went bust")
          return

      elif result == 1: # Stand button
        dealer_total = dealer_turn(dealer_hand, deck, dealer_total)
        embed = get_embed(player_hand, player_total, dealer_hand, dealer_total, dealer_turn = True)
        await message.edit(embed = embed, view = None)
        if dealer_total > 21 or dealer_total < player_total:
          winnings = bet * 2
          blackjack_winnings(winnings, economy_data, casino_data, interaction)
          await interaction.followup.send(f"You've won {winnings}€")
        elif dealer_total == player_total:
          blackjack_winnings(bet, economy_data, casino_data, interaction)
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
          casino_data["total_blackjack_winnings"] -= bet
          casino_data["total_casino_winnings"] -= bet
          save_json(casino_data, interaction.user.name, "casino")

          bet += bet  
          player_total = draw_card(player_hand, deck)
          embed = get_embed(player_hand, player_total, dealer_hand, dealer_total)
          await message.edit(embed = embed, view = None)

          if player_total > 21:
            await message.edit(embed = embed, view = None)
            await interaction.followup.send("You went bust")
            return

          dealer_total = dealer_turn(dealer_hand, deck, dealer_total)
          embed = get_embed(player_hand, player_total, dealer_hand, dealer_total, dealer_turn = True)
          await message.edit(embed = embed, view = None)

          if dealer_total > 21 or dealer_total < player_total:
            winnings = bet * 2
            blackjack_winnings(winnings, economy_data, casino_data, interaction)
            await interaction.followup.send(f"You've won {winnings}€")
          elif dealer_total == player_total:
            blackjack_winnings(bet, economy_data, casino_data, interaction)
            await interaction.followup.send("It's a draw")
          else:
            await interaction.followup.send("You've lost")
          return


  @app_commands.command(
    name = "roulette",
    description = "@todo"
  )
  async def roulette(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|roulette| from {interaction.user.name}")
    await interaction.response.send_message("Unimplemented")


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Casino(bot))