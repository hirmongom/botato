import os

import discord
from discord import app_commands
from discord.ext import commands

import csv
from datetime import datetime

from utils.json import save_json, load_json

class Bets(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot
    self.week_day = 0
    self.ready_bets = []


  def update_data(self, sport: str) -> None:
    if sport == "f1":
      self.bot.logger.info("Fetching F1 data")
      self.bot.web_scrapper.get_f1_data()
      self.bot.logger.info("Fetched F1 data")


  def get_next_f1_event(self) -> None:
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


  async def on_bot_run(self) -> None:
    # @todo F1 Bets
    self.bot.logger.info("Fetching F1 data")
    self.bot.web_scrapper.get_f1_data()
    self.bot.logger.info("Fetched F1 data")
    self.get_next_f1_event()

    # @todo debug
    await self.daily_task()


  async def daily_task(self) -> None:
    self.bot.interaction_logger.info("Bets daily task")

    # If an event was completed yesterday process the bet
    if len(self.ready_bets) > 0:
      for sport in self.ready_bets:
        self.bot.interaction_logger.info(f"Processing bet for {sport}")
        self.update_data(sport)
      self.ready_bets = []
        

    # If an event happens today, mark it to process it tomorrow
    now = datetime.now()
    for sport in os.listdir("data/bets/"):
      data = load_json(f"{sport}/{sport}_bet", "bets")
      if int(data["day"]) == now.day and int(data["month"]) == now.month:
        self.ready_bets.append("f1")


  @app_commands.command(
    name = "bet",
    description = "Check ongoing bets and try your luck!"
  )
  async def bet(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|bet| from {interaction.user.name}")
    await interaction.response.defer()

    emoji_mapping = {
      "f1": "🏎️"
    }

    embed = discord.Embed(
      title = "💰 Betting House",
      description = f"Check the next events and place bets on them!",
      color = discord.Colour.teal()
    )
    for sport in os.listdir("data/bets/"):
      data = load_json(f"{sport}/{sport}_bet", "bets")
      emoji = emoji_mapping[sport]
      embed.add_field(name = f"📅 {data['day']}/{data['month']} {sport.upper()}",
                      value = f"{emoji} {data['event']} ➡️ Current pool = {data['pool']}€",
                      inline = False)
    embed.set_footer(text = "Lucky Betting | Botato Bets", icon_url = self.bot.user.display_avatar.url)

    await interaction.followup.send(embed = embed)
    

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Bets(bot))