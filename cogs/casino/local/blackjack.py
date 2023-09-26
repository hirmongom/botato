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

from utils.json import save_json, load_json
from utils.achievement import add_user_stat
from utils.custom_ui import FutureButton


#***************************************************************************************************
kDeck = [
  "Ace of Hearts", "2 of Hearts", "3 of Hearts", "4 of Hearts", "5 of Hearts",
  "6 of Hearts", "7 of Hearts", "8 of Hearts", "9 of Hearts", "10 of Hearts",
  "Jack of Hearts", "Queen of Hearts", "King of Hearts",
  
  "Ace of Diamonds", "2 of Diamonds", "3 of Diamonds", "4 of Diamonds", "5 of Diamonds",
  "6 of Diamonds", "7 of Diamonds", "8 of Diamonds", "9 of Diamonds", "10 of Diamonds",
  "Jack of Diamonds", "Queen of Diamonds", "King of Diamonds",
  
  "Ace of Clubs", "2 of Clubs", "3 of Clubs", "4 of Clubs", "5 of Clubs",
  "6 of Clubs", "7 of Clubs", "8 of Clubs", "9 of Clubs", "10 of Clubs",
  "Jack of Clubs", "Queen of Clubs", "King of Clubs",
  
  "Ace of Spades", "2 of Spades", "3 of Spades", "4 of Spades", "5 of Spades",
  "6 of Spades", "7 of Spades", "8 of Spades", "9 of Spades", "10 of Spades",
  "Jack of Spades", "Queen of Spades", "King of Spades"
]


#***************************************************************************************************
async def blackjack_game_handler(bot: commands.Bot, interaction: discord.Interaction, 
                                bet: int) -> None:
  economy_data = load_json(interaction.user.name, "economy")

  deck = get_deck()
  player_hand, dealer_hand = blackjack_start(deck)

  dealer_total = sum(card['value'] for card in dealer_hand)
  player_total = sum(card['value'] for card in player_hand)
  
  if player_total == 22: # Case of 2 ACES count as 22
    for card in player_hand:
      card['value'] = 1
      break
    player_total = sum(card['value'] for card in player_hand)

  embed = get_embed(bot, player_hand, player_total, dealer_hand, dealer_total)

  future_button = asyncio.Future()
  view, hit_button, stand_button, double_button, retire_button = get_view(future = future_button, 
                                                                          interaction = interaction)

  message = await interaction.followup.send(embed = embed, view = view)

  # Handle game
  while True:
    if player_total == 21:
      bet *= 1.5
      await player_turn_end(interaction, deck, dealer_hand, dealer_total, player_total, economy_data, bet)
      break
    elif player_total > 21:
      await message.edit(embed = embed, view = None)
      await interaction.followup.send(f"<@{interaction.user.id}> You went bust")
      break

    try:
      result = await asyncio.wait_for(future_button, timeout = 60)
    except asyncio.TimeoutError:
      await message.edit(embed = embed, view = None)
      await interaction.followup.send(f"<@{interaction.user.id}> Timeout: Blackjack game has been "
                                      "canceled")
      break   

    # Reset state
    future_button = asyncio.Future()
    hit_button.future = future_button
    stand_button.future = future_button
    double_button.future = future_button
    retire_button.future = future_button
    
    # Handle button press

    if result == 0: # Hit button
      player_total = draw_card(player_hand, deck)
      embed = get_embed(bot, player_hand, player_total, dealer_hand, dealer_total)
      await message.edit(embed = embed, view = view)

    elif result == 1: # Stand button
      await player_turn_end(interaction, deck, dealer_hand, dealer_total, player_total, economy_data, bet)
      break

    elif result == 2: # Double down button
      if economy_data["hand_balance"] < bet:
        await interaction.followup.send(f"<@{interaction.user.id}> You do not have enough money in "
                                        "hand to Double Down")
      else:
        economy_data["hand_balance"] -= bet
        bet += bet  
        player_total = draw_card(player_hand, deck)
        await player_turn_end(interaction, deck, dealer_hand, dealer_total, player_total, 
                        economy_data, bet)
        break

    elif result == 3: # Retire button
      recovers = round(bet / 2, 2)
      economy_data["hand_balance"] += recovers
      
      await message.edit(embed = embed, view = None)
      await interaction.followup.send(f"<@{interaction.user.id}> You retired, you've received half "
                                      f"your bet: {recovers}€")
      break

  embed = get_embed(bot, player_hand, player_total, dealer_hand, dealer_total, dealer_turn = True)
  await message.edit(embed = embed, view = None)
  save_json(economy_data, interaction.user.name, "economy")


#***************************************************************************************************
def blackjack_start(deck) -> tuple[list[dict]]:
  player_hand = deal_player_hand(deck)
  dealer_hand = deal_dealer_hand(deck)

  return(player_hand, dealer_hand)


#***************************************************************************************************
def get_deck() -> dict:
  mapped_deck = [map_card(card) for card in kDeck]
  random.shuffle(mapped_deck)
  return mapped_deck


#***************************************************************************************************
def map_card(card: str) -> dict:
  # Mapping card names to their blackjack values
  card_values = {
    "Ace": 11, "2": 2, "3": 3, "4": 4, "5": 5,
    "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
    "Jack": 10, "Queen": 10, "King": 10
  }

  # Mapping card suits to their emotes
  suit_emotes = {
    "Hearts": "♥️", "Diamonds": "♦️", "Clubs": "♣️", "Spades": "♠️"
  }

  # Split the card string into value and suit
  parts = card.split(" of ")
  value_name = parts[0]
  suit = parts[1]
  
  # Get the blackjack value and emote using the dictionaries
  value = card_values[value_name]
  emote = suit_emotes[suit]
  
  # Return the mapped data
  return {
    "name": value_name,
    "emote": emote,
    "value": value
  }


#***************************************************************************************************
def deal_player_hand(mapped_deck: dict) -> list[dict]:
  # Deal two cards to the player
  player_hand = random.sample(mapped_deck, 2)
  
  # Remove the dealt cards from the deck
  for card in player_hand:
    mapped_deck.remove(card)
  
  return player_hand


#***************************************************************************************************
def deal_dealer_hand(mapped_deck: dict) -> list[dict]:
  # Deal two cards to the dealer
  dealer_hand = random.sample(mapped_deck, 2)
  
  # Remove the dealt cards from the deck
  for card in dealer_hand:
    mapped_deck.remove(card)
  
  return dealer_hand


#***************************************************************************************************
def draw_card(hand, deck) -> int:
  card = random.choice(deck)
  hand.append(card)
  deck.remove(card)
  total = sum(card['value'] for card in hand)

  # Check if total is over 21 and there's an Ace in the hand
  while total > 21 and any(card['name'] == 'Ace' and card['value'] == 11 for card in hand):
    # Find the first Ace with value 11 and change its value to 1
    for card in hand:
      if card['name'] == 'Ace' and card['value'] == 11:
        card['value'] = 1
        break
    total = sum(card['value'] for card in hand)

  return total


#***************************************************************************************************
def dealer_turn(hand: dict, deck: dict, dealer_total) -> int:
  total = dealer_total
  while total < 17:
    total = draw_card(hand, deck)
  return total


#***************************************************************************************************
def get_embed(bot: commands.Bot, player_hand: dict, player_total: int, 
              dealer_hand: dict, dealer_total: int,
              dealer_turn: bool = False) -> discord.Embed:
  embed = discord.Embed(
    title = "♠️♥️ Blackjack ♦️♣️",
    description = "",
    color = discord.Color.red()
  )

  embed.add_field(name = "", value = f"```Dealer's hand```", inline = False)
  if not dealer_turn:
    embed.add_field(name = f"{dealer_hand[0]['emote']}{dealer_hand[0]['name']}",
                    value = "", inline = True)
    embed.add_field(name = f"🂠", value = "", inline = True)
    embed.add_field(name = f"TOTAL: {dealer_hand[0]['value']}", value = "", inline = False)
  else:
    for i in range(len(dealer_hand)):
      embed.add_field(name = f"{dealer_hand[i]['emote']}{dealer_hand[i]['name']}", 
                      value = "", inline = True)
    embed.add_field(name = f"TOTAL: {dealer_total}", value = "", inline = False)

  embed.add_field(name = "", value = f"```Your hand```", inline = False)
  for i in range(len(player_hand)):
    embed.add_field(name = f"{player_hand[i]['emote']}{player_hand[i]['name']}", 
                    value = "", inline = True)
  embed.add_field(name = f"TOTAL: {player_total}", value = "", inline = False)

  embed.add_field(name = "", value = "", inline = False) # Pre-footer separator
  embed.set_footer(text = "Lucky Blackjack | Botato Casino", 
                  icon_url = bot.user.display_avatar.url)

  return embed


#***************************************************************************************************
def get_view(future: asyncio.Future, interaction: discord.Interaction) -> tuple:
  view = discord.ui.View()

  hit_button = FutureButton(style = discord.ButtonStyle.primary, 
                            label = "Hit",
                            user_id = interaction.user.id,
                            future = future,
                            button_id = 0)
  stand_button = FutureButton(style = discord.ButtonStyle.green, 
                              label = "Stand",
                              user_id = interaction.user.id,
                              future = future,
                              button_id = 1)
  double_button = FutureButton(style = discord.ButtonStyle.red, 
                               label = "Double Down",
                               user_id = interaction.user.id,
                               future = future,
                               button_id = 2)
  retire_button = FutureButton(style = discord.ButtonStyle.secondary, 
                               label = "Retire",
                               user_id = interaction.user.id,
                               future = future,
                               button_id = 3)
  
  view.add_item(hit_button)
  view.add_item(stand_button)
  view.add_item(double_button)
  view.add_item(retire_button)

  return (view, hit_button, stand_button, double_button, retire_button)


#***************************************************************************************************
async def player_turn_end(interaction: discord.Interaction, deck: dict, dealer_hand: list[dict], 
                          dealer_total: int, player_total: int, economy_data: dict, 
                          bet: int) -> None:
  dealer_total = dealer_turn(dealer_hand, deck, dealer_total)

  if dealer_total > 21 or dealer_total < player_total:
    winnings = bet * 2
    economy_data["hand_balance"] += winnings
    add_user_stat("blackjack_hands_won", interaction)
    await interaction.followup.send(f"<@{interaction.user.id}> You've won {winnings}€")

  elif dealer_total == player_total:
    economy_data["hand_balance"] += bet
    await interaction.followup.send(f"<@{interaction.user.id}> It's a draw")

  else:
    await interaction.followup.send(f"<@{interaction.user.id}> You've lost")