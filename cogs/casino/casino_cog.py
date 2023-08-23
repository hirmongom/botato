import os
import asyncio

import discord
from discord import app_commands
from discord.ext import commands

import random


from utils.json import load_json, save_json
from .utils.blackjack import blackjack_start

# @idea Casino (blackjack, poker, roulette, coin flip)
# @idea Daily roulette

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

    economy_data["hand_balance"] -= bet
    save_json(economy_data, interaction.user.name, "economy")

    player_hand, dealer_hand = blackjack_start()
    player_total = sum(card['value'] for card in player_hand)
    dealer_total = sum(card['value'] for card in dealer_hand)

    embed = discord.Embed(
      title = "♠️♥️ Blackjack ♦️♣️",
      description = "",
      color = discord.Color.red()
    )

    embed.add_field(name = "", value = f"```Dealer's hand```", inline = False)
    embed.add_field(name = f"{dealer_hand[0]['emote']}{dealer_hand[0]['name']}",
                    value = "", inline = True)
    embed.add_field(name = f"🂠", value = "", inline = True)
    embed.add_field(name = f"TOTAL: {dealer_hand[0]['value']}", value = "", inline = False)

    embed.add_field(name = "", value = f"```Your hand```", inline = False)
    embed.add_field(name = f"{player_hand[0]['emote']}{player_hand[0]['name']}", 
                    value = "", inline = True)
    embed.add_field(name = f"{player_hand[1]['emote']}{player_hand[1]['name']}",
                    value = "", inline = True)
    embed.add_field(name = f"TOTAL: {player_total}", value = "", inline = False)

    view = discord.ui.View()

    hit_button = discord.ui.Button(style = discord.ButtonStyle.primary, label = "Hit")
    stand_button = discord.ui.Button(style = discord.ButtonStyle.secondary, label = "Stand")
    double_button = discord.ui.Button(style = discord.ButtonStyle.red, label = "Double Down")
    
    view.add_item(hit_button)
    view.add_item(stand_button)
    view.add_item(double_button)

    await interaction.response.send_message(embed = embed, view = view)
    await interaction.followup.send("@todo - Work in Progress")


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Casino(bot))