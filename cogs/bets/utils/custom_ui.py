import os

import discord

from utils.json import load_json, save_json


emoji_mapping = {
  "test": "🛝",
  "f1": "🏎️"
}


class EventBetSelect(discord.ui.Select):
  def __init__(self, user_id: int, message: discord.Message, embed: discord.Embed, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.message = message
    self.embed = embed


  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
        return # User not authorized

    self.disabled = True
    await self.message.edit(view = self.view)

    new_view = discord.ui.View()
    value_bet_select = ValueBetSelect(user_id = self.user_id, message = self.message, 
                                      embed = self.embed, sport = self.values[0]) 
    new_view.add_item(value_bet_select)
    await interaction.response.send_message(view = new_view)


class ValueBetSelect(discord.ui.Select):
  def __init__(self, user_id: int, message: discord.Message, embed: discord.Embed, 
              sport: str,  *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.message = message
    self.embed = embed
    self.sport = sport

    self.menu_choices = []
    self.selections = load_json(f"{sport}/{sport}_selections", "bets")

    for key in self.selections.keys():
      self.menu_choices.append(discord.SelectOption(label = self.selections[key], value = key))

    self.options = self.menu_choices


  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
        return # User not authorized

    self.disabled = True
    await interaction.message.edit(view = self.view)

    modal = PlaceBetModal(message = self.message, embed = self.embed, sport = self.sport, 
                          bet_selection = self.values[0], selections = self.selections)
    await interaction.response.send_modal(modal)


class PlaceBetModal(discord.ui.Modal):
  def __init__(self, message: discord.Message, embed: discord.Embed, 
              sport: str, bet_selection: int, selections: dict[int, str]) -> None:
    super().__init__(title = "Bet amount")
    self.message = message
    self.embed = embed
    self.sport = sport
    self.bet_selection = bet_selection
    self.selections = selections
    self.add_item(discord.ui.TextInput(label = "Amount"))

  async def on_submit(self, interaction: discord.Interaction) -> None:
    economy_data = load_json(interaction.user.name, "economy")
    form_value = str(self.children[0])

    if form_value.isdigit():
      form_value = int(form_value)
      if form_value > economy_data["hand_balance"]:
        await interaction.response.send_message("You do not have enough money in hand")
      else:
        bet = load_json(f"{self.sport}/{self.sport}_bet", "bets")
        bettors = load_json(f"{self.sport}/{self.sport}_bettors", "bets")

        bet["pool"] += form_value
        bettors[interaction.user.name] = (self.bet_selection, form_value)
        economy_data["hand_balance"] -= form_value
        # add the user and its placed bet and the player
        #   {user: "user", bet: "123", bet_on: "player"}
        # withdraw amount to user
        save_json(bet, f"{self.sport}/{self.sport}_bet", "bets")
        save_json(bettors, f"{self.sport}/{self.sport}_bettors", "bets")
        save_json(economy_data, interaction.user.name, "economy")
        await interaction.response.send_message(f"You placed a bet of {form_value}€ " 
                                                f"on {self.selections[self.bet_selection]} "
                                                f"in {self.sport.upper()}")
    else:
      await interaction.response.send_message(f"Must be a number")
    await update_embed(message = self.message, embed = self.embed)


async def update_embed(message: discord.Message, embed: discord.Embed) -> None:
  embed.clear_fields()
  for i, sport in enumerate(os.listdir("data/bets/")):
      data = load_json(f"{sport}/{sport}_bet", "bets")
      emoji = emoji_mapping[sport]
      embed.add_field(name = "", value = "", inline = False) # Separator
      embed.add_field(name = f"📅 {data['day']}/{data['month']}", value = "", inline = False),
      embed.add_field(name = f"{emoji} {sport.upper()}", value =  f"{data['event']}", inline = True)
      embed.add_field(name = f"💵 Pool", value = f"{data['pool']}€", inline = True)
  embed.add_field(name = "", value = "", inline = False) # Separator
  await message.edit(embed = embed, view = None)