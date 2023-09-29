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


import os, sys
import argparse
import asyncio
import logging

from dotenv import load_dotenv
from datetime import datetime, timedelta, date

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks

from utils.data import make_data, save_user_id
from utils.achievement import add_user_stat
from utils.on_interactions import economy_on_interaction, user_on_interaction
from utils.web_scrapper import WebScrapper
    

#***************************************************************************************************
class Botato(commands.Bot):
  def __init__(self) -> None:
    super().__init__(
      command_prefix = "~", 
      intents = discord.Intents.all(),
      activity = discord.Activity(type = discord.ActivityType.playing, 
                                  name = "The loading game (I'm loading)"))
    self.set_up_logger()
    self.logger.info("********************** RUN **********************")

    self.main_channel = 0     # Loads on run()
    self.web_scrapper = None  # Loads on run()
    self.start_scrapper = True


#***************************************************************************************************
  def set_up_logger(self) -> None: 
    now = datetime.now()

    # Configure and set loggers
    logger_formatter_stream = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    logger_formatter_file = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    logger_stream_handler = logging.StreamHandler()
    logger_stream_handler.setFormatter(logger_formatter_stream)

    # Set up main logger
    self.logger = logging.getLogger("Logger")
    self.logger.setLevel(logging.INFO)
    self.logger.addHandler(logger_stream_handler)
    main_file_handler = logging.FileHandler(f"logs/{now.day}_{now.month}_{now.year}.log")
    main_file_handler.setFormatter(logger_formatter_file)
    self.logger.addHandler(main_file_handler)


#***************************************************************************************************
  @tasks.loop(hours = 1)
  async def hourly_loop(self) -> None:
    daily_task_hour = 0
    current_date = date.today()
    day_name = current_date.strftime('%A')
    now = datetime.now()

    # Run weekly cog tasks
    if day_name == "Monday" and now.hour == daily_task_hour:
      for cog in self.cogs.values():
        if hasattr(cog, "weekly_task"):
          self.logger.info(f"{cog.qualified_name} weekly_task")
          await cog.weekly_task()

    # Run daily cog tasks and set up new logger 
    if now.hour == daily_task_hour:
      self.set_up_logger()
      for cog in self.cogs.values():
        if hasattr(cog, "daily_task"):
          self.logger.info(f"{cog.qualified_name} daily_task")
          await cog.daily_task()

    # Run hourly cog tasks
    for cog in self.cogs.values():
      if hasattr(cog, "hourly_task"):
        self.logger.info(f"{cog.qualified_name} hourly_task")
        await cog.hourly_task()


#***************************************************************************************************
  @hourly_loop.before_loop
  async def before_hourly_loop(self):
    await self.wait_until_next_hour()


#***************************************************************************************************
  async def wait_until_next_hour(self):
    now = datetime.now()
    future = datetime(now.year, now.month, now.day, (now.hour + 1) % 24 , 0)
    await discord.utils.sleep_until(future)


#***************************************************************************************************
  def run(self) -> None:
    load_dotenv()
    self.main_channel = os.getenv("MAIN_CHANNEL")
    super().run(os.getenv("TOKEN"))


#***************************************************************************************************
  async def setup_hook(self) -> None:
    self.logger.info("(!) Started setup_hook")

    # Load cogs
    for folder in os.listdir("./cogs"):
      await self.load_extension(f"cogs.{folder}.{folder}_cog")
      self.logger.info(f"Loaded cog {folder}_cog")
    
    # Execute run options
    await self.argument_parsing()

    self.logger.info("(!) Finished setup_hook")


#***************************************************************************************************
  async def argument_parsing(self) -> None:
    if len(sys.argv) == 1:
      return  # No arguments

    self.logger.info("(!) Started argument parsing")

    parser = argparse.ArgumentParser()
    parser.add_argument("--sync", action = "store_true", help = "Run setup_hook on startup to sync "
                        "commands")
    parser.add_argument("--wipe", action = "store_true", help = "Wipe all json data (only)")
    parser.add_argument("--noweb", action = "store_true", help = "Disable the WebScrapper, for "
                                                                  "debugging purposes only")
    args = parser.parse_args()

    if args.sync:
      # Sync tree commands
      self.logger.info("--sync")
      try:
        sync = await self.tree.sync()
        self.logger.info(f"Synced {len(sync)} commands")
      except Exception as e:
        self.logger.error(f"Failed to sync commands: \n{e}")

    if args.wipe:
      # Delete al .json data
      self.logger.info("--wipe")
      for category in os.listdir("data/"):
        for data_file in os.listdir(f"data/{category}/"):
          if os.path.isdir(f"data/{category}/{data_file}"):
            for sub_data_file in os.listdir(f"data/{category}/{data_file}"):
              if sub_data_file.endswith(".json"):
                self.logger.info(f"Removed data/{category}/{data_file}/{sub_data_file}")
                os.remove(f"data/{category}/{data_file}/{sub_data_file}")
          elif data_file.endswith(".json"):
            self.logger.info(f"Removed data/{category}/{data_file}")
            os.remove(f"data/{category}/{data_file}")
      self.logger.info("Json data wipe completed")

    if args.noweb:
      self.start_scrapper = False

    self.logger.info("(!) Finished argument parsing")


#***************************************************************************************************
  async def on_ready(self) -> None:
    if self.start_scrapper:
      self.logger.info("(!) Starting web scrapper")
      self.web_scrapper = WebScrapper(self.logger, os.getenv("BROWSER_PATH"))
    self.hourly_loop.start()

    for cog in self.cogs.values():
      if hasattr(cog, "on_bot_run"):
        self.logger.info(f"{cog.qualified_name} on_bot_run")
        await cog.on_bot_run()

    self.logger.info(f"(*******) {bot.user} is ready")
    activity = discord.Activity(type = discord.ActivityType.watching, 
                                name = "lo tonto que eres")
    await self.change_presence(activity = activity)


#***************************************************************************************************
  @commands.Cog.listener()
  async def on_interaction(self, interaction: discord.Interaction) -> None:
    if interaction.type == discord.InteractionType.application_command:
      await add_user_stat("command_count", interaction)
      if interaction.data["name"] == "wipe":
        return
      try: # Run on_interaction functions
        await economy_on_interaction(interaction)
        await user_on_interaction(interaction)
      except KeyError: # First user interaction
        make_data(interaction.user.name)
        save_user_id(interaction.user.name, interaction.user.id)


#***************************************************************************************************
if __name__ == "__main__":  
  bot = Botato()
  bot.run()