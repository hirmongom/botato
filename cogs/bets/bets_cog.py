import os
import asyncio

import discord
from discord import app_commands
from discord.ext import commands

import csv
from datetime import datetime
import calendar

from utils.json import save_json, load_json
from .utils.custom_ui import (
  emoji_mapping, 
  EventBetSelect, 
  FutureModalCallbackButton, 
  FutureSimpleButton, 
  create_choice_button
)


class Bets(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot
    self.week_day = 0
    self.ready_bets = []


  def update_data(self, sport: str) -> None:
    if sport == "f1":
      self.bot.logger.info("Fetching F1 data")

      self.bot.web_scrapper.get_f1_data()
      self.bot.logger.info("Fetched events")
      self.bot.web_scrapper.get_f1_pilots()
      self.bot.logger.info("Fetched pilots")

      self.bot.logger.info("Finished fetching F1 data")


  def get_next_event(self, sport: str) -> None:
    if sport == "f1":
      with open(f"data/bets/f1/f1_data.csv", mode = "r", newline = "") as file:
        race_data = {}
        reader = csv.reader(file)
        for row in reader:
          if row[4] == "":
            race_data["ix"] = row[0]
            race_data["day"] = row[1]
            race_data["month"] = row[2]
            race_data["event"] = row[3]
            race_data["pool"] = 500
            race_data["status"] = "open"
            save_json(race_data, "f1/f1_bet", "bets")
            break


  def get_possible_days(self, year: int, month: int) -> list[int]:
    max_day = calendar.monthrange(year, month)[1]
    possible_days = list(range(1, max_day + 1))
    return possible_days

  async def fetch_data(self) -> None:
    # F1 Data
    self.update_data("f1")


  async def on_bot_run(self) -> None:
    for sport in os.listdir("data/bets"):
      self.bot.interaction_logger.info(f"Loaded event {sport}")
      self.get_next_event(sport)


  async def daily_task(self) -> None:
    # @todo extract into functions for the close_bet command
    if len(self.ready_bets) > 0:
      for sport in self.ready_bets:
        self.update_data(sport) # To get the winner
        bet_data = load_json(f"{sport}/{sport}_bet", "bets")
        bettors = load_json(f"{sport}/{sport}_bettors", "bets")
        bet_choices = load_json(f"{sport}/{sport}_chioces", "bets")
        winner_bettors = []
        winner_bettors_amount = 0  
        event_winner = ""
        user_ids = load_json("user_ids", "other")
        with open(f"data/bets/{sport}/{sport}_data.csv", mode = "r", newline = "") as file:
          reader = csv.reader(file)
          for row in reader:
            if row[0] == bet_data["ix"]:
              event_winner = row[4]

              # Notify
              channel = self.bot.get_channel(int(self.bot.main_channel))
              await channel.send(f"{event_winner} won {sport.upper()} {bet_data['event']}")

              for key in bettors.keys():
                if bet_chioces[bettors[key][0]] == event_winner:
                  winner_bettors_amount += bettors[key][1]
                  winner_bettors.append(key)
              for bettor in winner_bettors:
                economy_data = load_json(bettor, "economy")
                percentage = bettors[bettor][1] / winner_bettors_amount
                increase = int(bet_data["pool"] * percentage)
                economy_data["bank_balance"] += increase
                await channel.send(f"<@{user_ids[bettor]}> You've won {increase}€ from" 
                                  f" the pool of {bet_data['pool']}€")
                save_json(economy_data, bettor, "economy")
              break
        self.get_next_event(sport)
        
      self.ready_bets = []
        
    # If an event happens today, mark it to process it tomorrow
    now = datetime.now()
    for sport in os.listdir("data/bets/"):
      data = load_json(f"{sport}/{sport}_bet", "bets")
      if int(data["day"]) == now.day and int(data["month"]) == now.month:
        data["status"] = "closed"
        self.ready_bets.append("f1")


  @app_commands.command(
    name = "bet",
    description = "Check ongoing bets and try your luck!"
  )
  async def bet(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|bet| from {interaction.user.name}")
    await interaction.response.defer()

    select_choices = []
    embed = discord.Embed(
      title = "💰 Betting House",
      description = f"Check the next events and place bets on them!",
      color = discord.Colour.teal()
    )
    embed.set_footer(text = "Lucky Betting | Botato Bets", 
                    icon_url = self.bot.user.display_avatar.url)
    message = await interaction.followup.send(embed = embed)

    for i, sport in enumerate(os.listdir("data/bets/")):
      data = load_json(f"{sport}/{sport}_bet", "bets")
      emoji = emoji_mapping[sport]
      embed.add_field(name = "", value = "", inline = False) # Separator
      embed.add_field(name = f"📅 {data['day']}/{data['month']}", value = "", inline = False),
      embed.add_field(name = f"{emoji} {sport.upper()}", value =  f"{data['event']}", inline = True)
      embed.add_field(name = f"💵 Pool", value = f"{data['pool']}€", inline = True)
      select_choices.append(discord.SelectOption(label = data["event"], value = sport)) 
    embed.add_field(name = "", value = "", inline = False) # Separator

    select_menu = EventBetSelect(
      user_id = interaction.user.id,
      placeholder = "Select an event",
      options = select_choices,
      message = message,
      embed = embed)

    view = discord.ui.View()
    view.add_item(select_menu)

    await message.edit(embed = embed, view = view)

  
  @app_commands.command(
    name = "create_event",
    description = "(ADMIN) Create a custom event for users to bet on"
  )
  @app_commands.describe(
    day = "The day when the event takes place"
  )
  @app_commands.describe(
    month = "The month when the event takes place"
  )
  @app_commands.describe(
    year = "The year when the event takes place"
  )
  async def create_event(self, interaction: discord.Interaction, day: int, month: int, 
                      year: int = datetime.now().year) -> None:
    self.bot.interaction_logger.info(f"|create_event| from {interaction.user.name} with day |{day}|" 
                                      f" month |{month}| and year |{year}|")

    if not interaction.user.guild_permissions.administrator:
      await interaction.response.send_message("Missing Administrator permissions")
      return 

    now = datetime.now()
    if year < now.year:
      await interaction.response.send_message(f"Year ({year}) cannot be lower than the current"
                                              f" year ({now.year})")
      return

    if month < 1 or month > 12:
      await interaction.response.send_message(f"Month ({month}) does not exist")
      return

    if year == now.year and month < now.month:
      await interaction.response.send_message(f"Month ({month}) is lower than current month" 
                                              f" ({now.month}) for this year ({now.year})")
      return

    if month == now.month and day <= now.day:
      await interaction.response.send_message(f"Day ({day}) must be greater than today ({now.day})"
                                              f" for this month ({now.month})")
      return

    possible_days = self.get_possible_days(year, month)
    if day not in possible_days:
      await interaction.response.send_message(f"Invalid day {day} for month {month} and" 
                                              f" year {year}")
      return

    await interaction.response.defer()

    embed = discord.Embed(
      title = "New event",
      description = "",
      color = discord.Color.blue())

    embed.add_field(name = f"📅 {day}/{month}", value = "", inline = True)
    # @todo I need:
    # bet.json and selections.json

    future = asyncio.Future()

    message = await interaction.followup.send(embed = embed)

    # Get event name
    view = discord.ui.View()
    event_button = FutureModalCallbackButton(user_id = interaction.user.id,
                                            label = "Event Name", 
                                            style = discord.ButtonStyle.primary,
                                            future = future,
                                            modal_title = "Set Event Name",
                                            modal_label = "Event Name")
    view.add_item(event_button)
    
    await message.edit(embed = embed, view = view)
    event_name = await future
    view.clear_items()
    embed.add_field(name = f"🎫 {event_name}", value = "", inline = True)


    # LOOP
    # Get event selections
    choice_future = asyncio.Future()
    event_confirmed = asyncio.Event()

    event_confirmed_button =FutureSimpleButton(user_id = interaction.user.id,
                                                label = "Confirm Event",
                                                style = discord.ButtonStyle.primary,
                                                future = event_confirmed)
    choice_button = create_choice_button(user_id = interaction.user.id, future = choice_future)

    view.add_item(event_confirmed_button)
    view.add_item(choice_button)
    embed.add_field(name = "", value = "", inline = False) # Separator
    embed.add_field(name = "📋 Choices:", value = "", inline = False)
    await message.edit(embed = embed, view = view)

    choices = []
    while not event_confirmed.is_set():
      choice = await choice_future
      choices.append(choice)
      embed.add_field(name = choice, value = "", inline = False)

      choice_future = asyncio.Future()
      view.remove_item(choice_button)
      choice_button = create_choice_button(user_id = interaction.user.id, future = choice_future)
      view.add_item(choice_button)
      await message.edit(embed = embed, view = view)

    await interaction.followup.send("Event created!")
    

  @app_commands.command(
    name = "close_event",
    description = "(ADMIN) Set the winner and close a custom made bet"
  )
  async def close_event(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger(f"|close_event| from {interaction.user.name}")
    if not interaction.user.guild_permissions.administrator:
      await interaction.response.send_message("Missing Administrator permissions")
      return

    await interaction.response.send_message("@todo")


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Bets(bot))