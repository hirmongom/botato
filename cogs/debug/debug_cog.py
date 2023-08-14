import discord
from discord import app_commands
from discord.ext import commands

import os
from datetime import datetime

class Debug(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


  async def daily_trigger(self) -> None:
    time = datetime.now()
    self.bot.interaction_logger.info(f"Automatic cog daily trigger has started at "
          f"{str(time.hour).zfill(2)}:{str(time.minute).zfill(2)} " 
          f"{time.day}/{time.month}/{time.year}")


  @app_commands.command(
    name = "ping",
    description = "Checks bot latency")
  async def ping(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|ping| from {interaction.user.name}")
    await interaction.response.send_message(f"My latency is {format(self.bot.latency * 1000, '.2f')} milliseconds")     


  @app_commands.command(
    name = "time",
    description = "Displays the current local time of the bot")
  async def time(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|time| from {interaction.user.name}")
    time = datetime.now()
    await interaction.response.send_message(f"Bot's current local time and date is"
          f"\n{str(time.hour).zfill(2)}:{str(time.minute).zfill(2)}:{str(time.second).zfill(2)}"
          f"\n{time.day}/{time.month}/{time.year}")


  @app_commands.command(
    name = "reload",
    description = "Reload all cogs")
  async def reload(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|reload| from {interaction.user.name}")

    if not interaction.user.guild_permissions.administrator:
      await interaction.response.send_message("Missing Administrator permissions")
      return

    for folder in os.listdir("./cogs"):
      await self.bot.reload_extension(f"cogs.{folder}.{folder}_cog")
      self.bot.logger.info(f"Reloaded {folder}_cog")

    await interaction.response.send_message("Reloaded all cogs")


  @app_commands.command(
    name = "sync",
    description = "Syncs tree commands")
  async def sync(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|sync| from {interaction.user.name}")

    if not interaction.user.guild_permissions.administrator:
      await interaction.response.send_message("Missing Administrator permissions")
      return

    try:
      sync = await self.bot.tree.sync()
      self.bot.logger.info(f"Synced {len(sync)} commands")
    except Exception as e:
      self.bot.logger.error(f"Failed to sync commands: {e}")

    await interaction.response.send_message("Synced tree commands")


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Debug(bot))