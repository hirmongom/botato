import os
import asyncio
import shutil

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
  create_choice_button,
  choice_handler,
  CustomFutureSelect
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


  async def bet_winner_process(self, bet_data: dict[str, str], bettors: dict[str, list[str, int]], 
                              bet_choices: dict[str, str], event_winner: str) -> None:
    channel = self.bot.get_channel(int(self.bot.main_channel))
    await channel.send(f"{event_winner} won {bet_data['event']}")

    user_ids = load_json("user_ids", "other")
    winner_bettors_amount = 0
    winner_bettors = []

    for key in bettors.keys():
      if bet_choices[bettors[key][0]] == event_winner:
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


  async def on_bot_run(self) -> None:
    for sport in os.listdir("data/bets"):
      self.bot.interaction_logger.info(f"Loaded event {sport}")
      if not os.path.exists(f"data/bets/{sport}/{sport}_bet.json"):
        self.get_next_event(sport)


  async def daily_task(self) -> None:
    if len(self.ready_bets) > 0:
      for sport in self.ready_bets:
        # @todo self.update_data(sport) # To get the winner
        bet_data = load_json(f"{sport}/{sport}_bet", "bets")
        bettors = load_json(f"{sport}/{sport}_bettors", "bets")
        bet_choices = load_json(f"{sport}/{sport}_choices", "bets") 
        event_winner = ""
        with open(f"data/bets/{sport}/{sport}_data.csv", mode = "r", newline = "") as file:
          reader = csv.reader(file)
          for row in reader:
            if row[0] == bet_data["ix"]:
              event_winner = row[4]

              await self.bet_winner_process(bet_data, bettors, bet_choices, event_winner)
              break

        bettors = {}
        save_json(bettors, f"{sport}/{sport}_bettors", "bets")
        self.get_next_event(sport)
        
      self.ready_bets = []
        
    # If an event happens today, mark it to process it tomorrow
    now = datetime.now()
    for sport in os.listdir("data/bets/"):
      data = load_json(f"{sport}/{sport}_bet", "bets")
      if int(data["day"]) == now.day and int(data["month"]) == now.month:
        data["status"] = "closed"
      if not sport.startswith("custom"):
        self.ready_bets.append(sport)


  @app_commands.command(
    name = "bet",
    description = "Check ongoing bets and try your luck!"
  )
  async def bet(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|bet| from {interaction.user.name}")
    await interaction.response.defer()

    embed = discord.Embed(
      title = "💰 Betting House",
      description = f"Check the next events and place bets on them!",
      color = discord.Colour.teal()
    )
    embed.set_footer(text = "Lucky Betting | Botato Bets", 
                    icon_url = self.bot.user.display_avatar.url)
    message = await interaction.followup.send(embed = embed)

    select_choices = []
    for i, sport in enumerate(os.listdir("data/bets/")):
      data = load_json(f"{sport}/{sport}_bet", "bets")
      try:
        emoji = emoji_mapping[sport]
      except Exception:
        emoji = "🎫"
      embed.add_field(name = f"📅 {data['day']}/{data['month']}", value = "", inline = False),
      if sport.startswith("custom"):
        embed.add_field(name = f"{emoji} CUSTOM", value =  f"{data['event']}", inline = True)
      else:
        embed.add_field(name = f"{emoji} {sport.upper()}", value =  f"{data['event']}", inline = True)
      embed.add_field(name = f"💵 Pool", value = f"{data['pool']}€", inline = True)
      select_choices.append(discord.SelectOption(label = data["event"], value = sport)) 

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

    if month == now.month and day < now.day:
      await interaction.response.send_message(f"Day ({day}) cannot be lower than today ({now.day})"
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
    message = await interaction.followup.send(embed = embed)

    future = asyncio.Future()
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
    embed.add_field(name = f"🎫 {event_name}", value = "", inline = False)

    pool_future = asyncio.Future()
    pool_button = FutureModalCallbackButton(user_id = interaction.user.id,
                                            label = "Event pool", 
                                            style = discord.ButtonStyle.primary,
                                            future = pool_future,
                                            modal_title = "Set Event Pool",
                                            modal_label = "€")
    view.add_item(pool_button)
    await message.edit(embed = embed, view = view)
    pool = await pool_future
    view.clear_items()
    if not pool.isdigit():
      await message.edit(embed = embed, view = view)
      await interaction.followup.send("Pool must be a number")
      return
    embed.add_field(name = f"💵 Pool of {pool}€", value = "", inline = False)


    event_confirmed = asyncio.Event()
    event_confirmed_button =FutureSimpleButton(user_id = interaction.user.id,
                                                label = "Confirm Event",
                                                style = discord.ButtonStyle.primary,
                                                future = event_confirmed)
    view.add_item(event_confirmed_button)
    embed.add_field(name = "📋 Choices:", value = "", inline = False)
    await message.edit(embed = embed, view = view)

    choices = []
    task = asyncio.create_task(choice_handler(interaction.user.id, choices, embed, message, view))

    while not event_confirmed.is_set():
      await asyncio.sleep(0.5)

    task.cancel()
    await message.edit(embed = embed, view = None)
    
    if len(choices) < 2:
      await interaction.followup.send("The bet needs a minimum of 2 choices")
      return

    bet_identifier = f"{now.month}{now.day}{now.minute}"

    os.mkdir(f"data/bets/custom{bet_identifier}")
    bet_data = {
      "ix": bet_identifier,
      "day": day,
      "month": month,
      "year": year,
      "event": event_name,
      "pool": pool,
      "status": "open"
    }
    save_json(bet_data, f"custom{bet_identifier}/custom{bet_identifier}_bet", "bets")

    bet_choices = {}
    for i, choice in enumerate(choices):
      bet_choices[i] = choice
    save_json(bet_choices, f"custom{bet_identifier}/custom{bet_identifier}_choices", "bets")

    await interaction.followup.send("Event created!")


  @app_commands.command(
    name = "close_event",
    description = "(ADMIN) Set the winner and close a custom made bet"
  )
  async def close_event(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|close_event| from {interaction.user.name}")
    if not interaction.user.guild_permissions.administrator:
      await interaction.response.send_message("Missing Administrator permissions")
      return

    await interaction.response.defer()

    event_select_choices = []
    for bet in os.listdir("data/bets"):
      if bet.startswith("custom"):
        bet_data = load_json(f"{bet}/{bet}_bet", "bets")
        event_select_choices.append(discord.SelectOption(label = bet_data["event"], value = bet))

    if len(event_select_choices) == 0:
      await interaction.followup.send("There are no events going on")
      return

    event_select_future = asyncio.Future()
    event_select = CustomFutureSelect(
      placeholder = "Select an event",
      options = event_select_choices,
      user_id = interaction.user.id,
      future = event_select_future
    )

    view = discord.ui.View()
    view.add_item(event_select)
    message = await interaction.followup.send(view = view)

    event_select_result = await event_select_future

    # choose winner
    winner_select_future = asyncio.Future()
    winner_select_choices = []
    bet_choices = load_json(f"{event_select_result}/{event_select_result}_choices", "bets")

    for key in bet_choices:
      winner_select_choices.append(discord.SelectOption(label = bet_choices[key], value = key))

    winner_select = CustomFutureSelect(
      placeholder = "Select a winner",
      options = winner_select_choices,
      user_id = interaction.user.id,
      future = winner_select_future
    )
    view.add_item(winner_select)
    await message.edit(view = view)

    winner_select_result = await winner_select_future

    await message.edit(view = view) # Select menu disabled

    bet_data = load_json(f"{event_select_result}/{event_select_result}_bet", "bets")
    bettors = load_json(f"{event_select_result}/{event_select_result}_bettors", "bets")
    bet_choices = load_json(f"{event_select_result}/{event_select_result}_choices", "bets")
    winner = bet_choices[winner_select_result]
    await self.bet_winner_process(bet_data, bettors, bet_choices, winner)

    folder_path = f"data/bets/{event_select_result}"
    try:
      shutil.rmtree(folder_path)
      self.bot.interaction_logger.info(f"Folder '{folder_path}' and its contents deleted successfully.")
    except OSError as e:
      self.bot.interaction_logger.error(f"Error deleting folder '{folder_path}: {e}")


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Bets(bot))