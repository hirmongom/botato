import argparse
import os
from dotenv import load_dotenv

import asyncio
from datetime import datetime, timedelta

import discord
from discord.ext import commands
from discord import app_commands
from discord.ext import tasks


class Botato(commands.Bot):
  def __init__(self) -> None:
    super().__init__(
      command_prefix = "_not_designed_for_prefix_commands_", 
      intents = discord.Intents.all(),
      activity = discord.Activity(type = discord.ActivityType.watching, 
                                  name = "lo tonto que eres"))


  def cog_unload(self) -> None:
    self.daily_cog_trigger.cancel()


  @tasks.loop(hours=24)
  async def daily_cog_trigger(self) -> None:
    now = datetime.now()
    if now.hour == 10 and now.minute == 42:
      for cog in self.cogs.values():
        if hasattr(cog, "daily_trigger"):
          await cog.daily_trigger()


  @daily_cog_trigger.before_loop
  async def before_daily_cog_trigger(self):
    await self.wait_until(10, 42)


  async def wait_until(self, hour, minute):
    now = datetime.now()
    future = datetime(now.year, now.month, now.day, hour, minute)
    if now.time() > future.time():
      future += timedelta(days=1)
    await discord.utils.sleep_until(future)


  def run(self) -> None:
    load_dotenv()
    super().run(os.getenv("TOKEN"))


  async def setup_hook(self) -> None:
    for folder in os.listdir("./cogs"):
      await self.load_extension(f"cogs.{folder}.{folder}_cog")
      print(f"(!) Loaded {folder}_cog")

    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", action="store_true", help="Run setup_hook on startup")
    args = parser.parse_args()

    if args.setup:
      try:
        sync = await self.tree.sync()
        print(f"(!) Synced {len(sync)} commands")
      except Exception as e:
        print(f"(!) Failed to sync commands: {e}")


  async def on_ready(self) -> None:
    self.daily_cog_trigger.start()
    print(f'(!) {bot.user} is ready\n')


if __name__ == "__main__":  
  bot = Botato()
  bot.run()