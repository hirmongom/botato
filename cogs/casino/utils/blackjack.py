import asyncio
import random
import discord


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


# **************************************************************************************************
def blackjack_start(deck) -> tuple[list[dict]]:
  player_hand = deal_player_hand(deck)
  dealer_hand = deal_dealer_hand(deck)

  return(player_hand, dealer_hand)


# **************************************************************************************************
def get_deck() -> dict:
  mapped_deck = [map_card(card) for card in kDeck]
  random.shuffle(mapped_deck)
  return mapped_deck


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


# **************************************************************************************************
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


# **************************************************************************************************
class BlackjackButton(discord.ui.Button):
  def __init__(self, user_id: int, future: asyncio.Future, button_id: int, *args, **kwargs)-> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.future = future
    self.id = button_id


  async def callback(self, interaction: discord.Interaction) -> None:
    await interaction.response.defer()
    self.future.set_result(self.id)


# **************************************************************************************************
def get_embed(player_hand: dict, player_total: int, 
              dealer_hand: dict, dealer_total: int) -> discord.Embed:
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
  for i in range(len(player_hand)):
    embed.add_field(name = f"{player_hand[i]['emote']}{player_hand[i]['name']}", 
                    value = "", inline = True)
  embed.add_field(name = f"TOTAL: {player_total}", value = "", inline = False)

  return embed