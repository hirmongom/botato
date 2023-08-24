import os
import asyncio

import discord
from discord import app_commands
from discord.ext import commands

import random


from utils.json import load_json, save_json
from .utils.blackjack import blackjack_start, get_deck, draw_card, BlackjackButton, get_embed


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
    self.bot.interaction_logger.info(f"|blackjack| from {interaction.user.name}")
    economy_data = load_json(interaction.user.name, "economy")

    if bet > economy_data["hand_balance"]:
      await interaction.response.send_message("You do not have enough money in hand")
      return

    await interaction.response.defer()

    economy_data["hand_balance"] -= bet
    save_json(economy_data, interaction.user.name, "economy")

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
      if player_total != 21:
        try:
          result = await asyncio.wait_for(future_button, timeout = 60)
          await interaction.followup.send(f"Pressed {result}")
        except asyncio.TimeoutError:
          await interaction.followup.send("Stop loop")
          return
        # Reset state
        future_button = asyncio.Future()
        hit_button.future = future_button
        stand_button.future = future_button
        double_button.future = future_button
      else:
        result = 0

      # Handle button press
      if result == 0: # Hit button
        player_total = draw_card(player_hand, deck)
        embed = get_embed(player_hand, player_total, dealer_hand, dealer_total)
        await message.edit(embed = embed, view = view)

        if player_total == 21:
          pass # auto stand
        elif player_total > 21:
          await message.edit(embed = embed, view = None)
          await interaction.followup.send("You went bust!")
          return

      elif result == 1: # Stand button
        pass

      elif result == 2: # Double down button
        pass


  @app_commands.command(
    name = "roulette",
    description = "@todo"
  )
  async def roulette(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|roulette| from {interaction.user.name}")
    await interaction.response.send_message("Unimplemented")


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Casino(bot))