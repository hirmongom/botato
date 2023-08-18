import os, sys
import argparse
from dotenv import load_dotenv

import asyncio
from datetime import datetime, timedelta
import logging

import discord
from discord.ext import commands
from discord.ext import tasks

from util.funcs import make_data
from util.web_scrapper import WebScrapper
    

class Botato(commands.Bot):
  main_channel = 0
  def __init__(self) -> None:
    super().__init__(
      command_prefix = "~", 
      intents = discord.Intents.all(),
      activity = discord.Activity(type = discord.ActivityType.watching, 
                                  name = "lo tonto que eres"))
    self.set_up_loggers()
    self.logger.info("********************** RUN **********************")
    self.web_scrapper = None

  def set_up_loggers(self) -> None: 
    # Configure and set loggers
    logger_formatter_stream = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger_formatter_file = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    logger_stream_handler = logging.StreamHandler()
    logger_stream_handler.setFormatter(logger_formatter_stream)

    # Set up main logger
    self.logger = logging.getLogger("MainLogger")
    self.logger.setLevel(logging.INFO)
    self.logger.addHandler(logger_stream_handler)
    main_file_handler = logging.FileHandler("logs/main.log")
    main_file_handler.setFormatter(logger_formatter_file)
    self.logger.addHandler(main_file_handler)

    # Set up interaction logger
    self.interaction_logger = logging.getLogger("InteractionLogger")
    self.interaction_logger.setLevel(logging.DEBUG)
    self.interaction_logger.addHandler(logger_stream_handler)
    interaction_file_handler = logging.FileHandler("logs/interaction.log")
    interaction_file_handler.setFormatter(logger_formatter_file)
    self.interaction_logger.addHandler(interaction_file_handler)
    self.interaction_logger.propagate = False


  def cog_unload(self) -> None:
    self.daily_cog_trigger.cancel()


  @tasks.loop(hours = 1)
  async def hourly_loop(self) -> None:
    daily_task_hour = 0

    # Run daily cog tasks
    now = datetime.now()
    if now.hour == daily_task_hour:
      for cog in self.cogs.values():
        if hasattr(cog, "daily_task"):
          await cog.daily_task()

    # Run hourly cog tasks
    for cog in self.cogs.values():
      if hasattr(cog, "hourly_task"):
        await cog.hourly_task()


  @hourly_loop.before_loop
  async def before_hourly_loop(self):
    await self.wait_until_next_hour()


  async def wait_until_next_hour(self):
    now = datetime.now()
    future = datetime(now.year, now.month, now.day, (now.hour + 1) % 24 , 0)
    await discord.utils.sleep_until(future)


  def run(self) -> None:
    load_dotenv()
    self.main_channel = os.getenv("MAIN_CHANNEL")
    self.web_scrapper = WebScrapper(self.logger, os.getenv("BROWSER_PATH"))
    super().run(os.getenv("TOKEN"))


  async def setup_hook(self) -> None:
    self.logger.info("Started setup_hook()")
    for folder in os.listdir("./cogs"):
      await self.load_extension(f"cogs.{folder}.{folder}_cog")
      self.logger.info(f"Loaded cog {folder}_cog")

    await self.argument_parsing()
    self.logger.info("Finished setup_hook()")


  async def argument_parsing(self) -> None:
    if len(sys.argv) == 1:
      return

    self.logger.info("Started argument parsing")

    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", action = "store_true", help = "Run setup_hook on startup")
    parser.add_argument("--wipe", action = "store_true", help = "Wipe all data")
    args = parser.parse_args()

    if args.setup:
      self.logger.info("--setup")
      try:
        sync = await self.tree.sync()
        self.logger.info(f"Synced {len(sync)} commands")
      except Exception as e:
        self.logger.error(f"Failed to sync commands: \n{e}")

    if args.wipe:
      self.logger.info("--wipe")
      for category in os.listdir("data/"):
        for data_file in os.listdir(f"data/{category}/"):
          if data_file != ".gitkeep":
            os.remove(f"data/{category}/{data_file}")
      self.logger.info("Data wipe completed")

    self.logger.info("Finished argument parsing")


  async def on_ready(self) -> None:
    self.hourly_loop.start()
    self.logger.info(f"{bot.user} is ready")

  @commands.Cog.listener()
  async def on_interaction(self, interaction: discord.Interaction) -> None:
    if not os.path.isfile(f"data/user/{interaction.user.name}.json"):
      self.interaction_logger.info(f"First interaction of |{interaction.user.name}|")
      # First interaction for user -> create data
      make_data(interaction.user.name)
      

if __name__ == "__main__":  
  bot = Botato()
  bot.run()