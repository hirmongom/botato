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
import ctypes

import discord

from utils.json import load_json, save_json


# ************************** bet() command **************************


class EventBetSelect(discord.ui.Select):
  def __init__(self, user_id: int, message: discord.Message, embed: discord.Embed, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.message = message
    self.embed = embed


  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
        return # User not authorized

    await interaction.response.defer()

    self.disabled = True
    await self.message.edit(view = self.view)

    choice = self.values[0]
    bet_data = load_json(f"{choice}/{choice}_bet", "bets")
    bettors = load_json(f"{choice}/{choice}_bettors", "bets")

    # Check if bet is closed
    if bet_data["status"] == "closed":
      await interaction.followup.send(f"Bets for {bet_data['event']} are closed")
      return

    # Check if user has already placed a bet in {choice} event
    for key in bettors.keys():
      if key == interaction.user.name:
        await interaction.followup.send("You have already placed a bet on this event")
        return

    choice_bet_select = ChoiceBetSelect(user_id = self.user_id, message = self.message, 
                                      embed = self.embed, sport = choice)
    await choice_bet_select.setup(self.view)


class ChoiceBetSelect(discord.ui.Select):
  def __init__(self, user_id: int, message: discord.Message, embed: discord.Embed, 
              sport: str,  *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.message = message
    self.embed = embed
    self.sport = sport

    self.menu_choices = []
    self.bet_choices = load_json(f"{sport}/{sport}_choices", "bets")

    for key in self.bet_choices.keys():
      self.menu_choices.append(discord.SelectOption(label = self.bet_choices[key], value = key))
    
    self.options = self.menu_choices


  async def setup(self, view: discord.ui.View):
    view.add_item(self)
    await self.message.edit(view = view)


  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
        return # User not authorized

    self.disabled = True
    await interaction.message.edit(view = self.view)

    modal = PlaceBetModal(message = self.message, embed = self.embed, sport = self.sport, 
                          bet_choice = self.values[0], bet_choices = self.bet_choices)
    await interaction.response.send_modal(modal)


class PlaceBetModal(discord.ui.Modal):
  def __init__(self, message: discord.Message, embed: discord.Embed, 
              sport: str, bet_choice: int, bet_choices: dict[int, str]) -> None:
    super().__init__(title = "Bet amount")
    self.message = message
    self.embed = embed
    self.sport = sport
    self.bet_choice = bet_choice
    self.bet_choices = bet_choices
    self.add_item(discord.ui.TextInput(label = "Amount"))

  async def on_submit(self, interaction: discord.Interaction) -> None:
    economy_data = load_json(interaction.user.name, "economy")
    form_value = str(self.children[0])

    try:
      form_value = round(float(form_value), 2)
      if form_value > economy_data["hand_balance"]:
        await interaction.response.send_message("You do not have enough money in hand")
      else:
        bet = load_json(f"{self.sport}/{self.sport}_bet", "bets")
        bettors = load_json(f"{self.sport}/{self.sport}_bettors", "bets")

        bet["pool"] = float(bet["pool"]) + form_value
        bettors[interaction.user.name] = (self.bet_choice, form_value)
        economy_data["hand_balance"] -= form_value
        save_json(bet, f"{self.sport}/{self.sport}_bet", "bets")
        save_json(bettors, f"{self.sport}/{self.sport}_bettors", "bets")
        save_json(economy_data, interaction.user.name, "economy")
        await interaction.response.send_message(f"You placed a bet of {form_value}€ " 
                                                f"on {self.bet_choices[self.bet_choice]} "
                                                f"in {bet['event']}")
        await add_user_stat("bets_placed", interaction)
    except:
      await interaction.response.send_message(f"Must be a number")
    await update_embed(message = self.message, embed = self.embed)


async def update_embed(message: discord.Message, embed: discord.Embed) -> None:
  embed.clear_fields()
  for i, sport in enumerate(os.listdir("data/bets/")):
    data = load_json(f"{sport}/{sport}_bet", "bets")
    embed.add_field(name = f"", value = f"```📅 {data['day']}/{data['month']}```", inline = False)
    embed.add_field(name = f"🎫{data['event']}", value = f"💵 Pool: {data['pool']}€" , inline = False)
  embed.add_field(name = "", value = "", inline = False) # pre-footer separator
  await message.edit(embed = embed, view = None)


# ************************** create_event() command **************************


def create_choice_button(user_id: int, future: asyncio.Future) -> None:
  return FutureModalCallbackButton(user_id = user_id,
                                  label = "Add choice",
                                  style = discord.ButtonStyle.primary,
                                  future = future,
                                  modal_title = "Add a choice for the event bet",
                                  modal_label = "Choice")

class FutureModalCallbackButton(discord.ui.Button):
  def __init__(self, user_id: int, future: asyncio.Future, modal_title: str, 
              modal_label: str, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.future = future
    self.modal_title = modal_title
    self.modal_label = modal_label


  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
        return # User not authorized

    modal = FutureCallbackModal(title = self.modal_title, label = self.modal_label, 
                                future = self.future)
    await interaction.response.send_modal(modal)


class FutureCallbackModal(discord.ui.Modal):
  def __init__(self, title: str, label: str, future: asyncio.Future) -> None:
    super().__init__(title = title)
    self.future = future
    self.add_item(discord.ui.TextInput(label = label))

  async def on_submit(self, interaction: discord.Interaction) -> None:
    await interaction.response.defer()
    form_value = str(self.children[0])
    self.future.set_result(form_value)


class FutureSimpleButton(discord.ui.Button):
  def __init__(self, user_id: int, future: asyncio.Event,  *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.future = future


  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
        return # User not authorized
    await interaction.response.defer()
    self.future.set()


async def choice_handler(user_id: int, choices: list[str], embed: discord.Embed, 
                          message :discord.Message, view: discord.ui.View) -> None:
  while True:
    choice_future = asyncio.Future()
    choice_button = create_choice_button(user_id = user_id, future = choice_future)
    view.add_item(choice_button)
    await message.edit(embed = embed, view = view)

    choice = await choice_future

    choices.append(choice)
    embed.add_field(name = choice, value = "", inline = False)

    choice_future = asyncio.Future()
    view.remove_item(view.children[1])

    choice_button = create_choice_button(user_id = user_id, future = choice_future)

    await message.edit(embed = embed, view = view)


# ************************** close_event() command **************************


class CustomFutureSelect(discord.ui.Select):
  def __init__(self, user_id: int, future: asyncio.Event, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.future = future

  async def callback(self, interaction: discord.Interaction) -> None:
    await interaction.response.defer()
    self.disabled = True
    self.future.set_result(self.values[0])