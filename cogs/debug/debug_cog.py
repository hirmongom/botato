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

import discord
from discord import app_commands
from discord.ext import commands

import os
from datetime import datetime

class Debug(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


  async def on_bot_run(self) -> None:
    pass

  async def weekly_task(self) -> None:
    pass

  async def daily_task(self) -> None:
    pass

  async def hourly_task(self) -> None:
    pass


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
    description = "(ADMIN) Reload all cogs")
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
    description = "(ADMIN) Syncs tree commands")
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


  @app_commands.command(
    name = "run_weekly_task",
    description = "(ADMIN) Executes weekly_task() for all cogs")
  async def run_weekly_task(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|run_weekly_task| from {interaction.user.name}")
    await interaction.response.defer()

    if not interaction.user.guild_permissions.administrator:
      await interaction.response.send_message("Missing Administrator permissions")
      return

    for cog in self.bot.cogs.values():
      if hasattr(cog, "weekly_task"):
        await cog.weekly_task()
    
    await interaction.followup.send("weekly_task() triggered for all cogs") 


  @app_commands.command(
    name = "run_daily_task",
    description = "(ADMIN) Executes daily_task() for all cogs")
  async def run_daily_task(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|run_daily_task| from {interaction.user.name}")
    await interaction.response.defer()

    if not interaction.user.guild_permissions.administrator:
      await interaction.response.send_message("Missing Administrator permissions")
      return

    for cog in self.bot.cogs.values():
      if hasattr(cog, "daily_task"):
        await cog.daily_task()
    
    await interaction.followup.send("daily_task() triggered for all cogs") 


  @app_commands.command(
    name = "run_hourly_task",
    description = "(ADMIN) Executes hourly_task() for all cogs")
  async def run_hourly_task(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|run_hourly_task| from {interaction.user.name}")
    await interaction.response.defer()

    if not interaction.user.guild_permissions.administrator:
      await interaction.response.send_message("Missing Administrator permissions")
      return

    for cog in self.bot.cogs.values():
      if hasattr(cog, "hourly_task"):
        await cog.hourly_task()
    
    await interaction.followup.send("hourly_task() triggered for all cogs") 


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Debug(bot))