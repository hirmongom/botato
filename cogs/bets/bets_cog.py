import os

import discord
from discord import app_commands
from discord.ext import commands

import csv
from datetime import datetime

from utils.json import save_json, load_json
from .utils.custom_ui import EventBetSelect, emoji_mapping


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


  async def fetch_data(self) -> None:
    # F1 Data
    self.update_data("f1")


  async def on_bot_run(self) -> None:
    for sport in os.listdir("data/bets"):
      self.bot.interaction_logger.info(f"Loaded event {sport}")
      self.get_next_event(sport)


  async def daily_task(self) -> None:
    self.bot.interaction_logger.info("Bets daily task")

    if len(self.ready_bets) > 0:
      for sport in self.ready_bets:
        self.update_data(sport) # To get the winner
        bet_data = load_json(f"{sport}/{sport}_bet", "bets")
        bettors = load_json(f"{sport}/{sport}_bettors", "bets")
        bet_selections = load_json(f"{sport}/{sport}_selections", "bets")
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
                if bet_selections[bettors[key][0]] == event_winner:
                  winner_bettors_amount += bettors[key][1]
                  winner_bettors.append(key)
              for bettor in winner_bettors:
                economy_data = load_json(bettor, "economy")
                percentage = bettors[bettor][1] / winner_bettors_amount
                increase = int(bet_data["pool"] * percentage)
                economy_data["bank_balance"] += increase
                await channel.send(f"<@{user_ids[bettor]}> You've won {increase}€ from the pool of {bet_data['pool']}€")
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
    embed.set_footer(text = "Lucky Betting | Botato Bets", icon_url = self.bot.user.display_avatar.url)
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
    

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Bets(bot))