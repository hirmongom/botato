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


  def get_next_f1_event(self) -> None:
    with open(f"data/bets/f1/f1_data.csv", mode = "r", newline = "") as file:
      race_data = {}
      reader = csv.reader(file)
      for row in reader:
        if row[3] == "":
          print(f"Next race: {row[0]}/{row[1]} {row[2]}")
          race_data["day"] = row[0]
          race_data["month"] = row[1]
          race_data["race"] = row[2]
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
    now = datetime.now()
    for sport in os.listdir("data/bets/"):
      data = load_json(f"{sport}/{sport}_bet", "bets")
      if int(data["day"]) == now.day and int(data["month"]) == now.month:
        pass


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Bets(bot))