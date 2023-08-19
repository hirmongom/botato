import discord
from discord import app_commands
from discord.ext import commands

import csv

# @todo Bets on real events (f1, lol)

class Bets(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot
    self.week_day = 0


  async def on_bot_run(self) -> None:
    # F1 Bets
    self.bot.logger.info("Fetching F1 data")
    self.bot.web_scrapper.get_f1_data()
    self.bot.logger.info("Fetched F1 data")
    with open("data/bets/f1/f1_data.csv", mode = "r", newline = "") as file:
      reader = csv.reader(file)
      for row in reader:
        if row[3] == "":
          print(f"Next race: {row[0]}/{row[1]} {row[2]}")
          break


  async def daily_trigger(self) -> None:
    pass


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Bets(bot))