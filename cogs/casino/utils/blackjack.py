import asyncio
import random


deck = [
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


# **************************************************************************************************
def blackjack_start() -> tuple[list[dict]]:
  mapped_deck = [map_card(card) for card in deck]
  random.shuffle(mapped_deck)

  player_hand = deal_player_hand(mapped_deck)
  dealer_hand = deal_dealer_hand(mapped_deck)

  return(player_hand, dealer_hand)


# **************************************************************************************************
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


# **************************************************************************************************
def deal_player_hand(mapped_deck: dict) -> list[dict]:
  # Deal two cards to the player
  player_hand = random.sample(mapped_deck, 2)
  
  # Remove the dealt cards from the deck
  for card in player_hand:
    mapped_deck.remove(card)
  
  return player_hand


# **************************************************************************************************
def deal_dealer_hand(mapped_deck: dict) -> list[dict]:
  # Deal two cards to the dealer
  dealer_hand = random.sample(mapped_deck, 2)
  
  # Remove the dealt cards from the deck
  for card in dealer_hand:
    mapped_deck.remove(card)
  
  return dealer_hand