import discord
from discord import app_commands
from discord.ext import commands

import os


class Debug(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


  @app_commands.command(
    name = "ping",
    description = "Checks bot latency")
  async def ping(self, interaction: discord.Interaction) -> None:
    print(f">> |ping| from {interaction.user.name}")
    await interaction.response.send_message(f"My latency is {format(self.bot.latency * 1000, '.2f')} milliseconds")     


  @app_commands.command(
    name = "reload",
    description = "Reload all cogs")
  async def reload(self, interaction: discord.Interaction) -> None:
    print(f">> |reload| from {interaction.user.name}")

    if not interaction.user.guild_permissions.administrator:
      await interaction.response.send_message("Missing Administrator permissions")
      return

    for folder in os.listdir("./cogs"):
      await self.bot.reload_extension(f"cogs.{folder}.{folder}_cog")
      print(f"Reloaded {folder}")

    await interaction.response.send_message("Reloaded all cogs")


  @app_commands.command(
    name = "sync",
    description = "Syncs tree commands")
  async def sync(self, interaction: discord.Interaction) -> None:
    print(f">> |sync| from {interaction.user.name}")

    if not interaction.user.guild_permissions.administrator:
      await interaction.response.send_message("Missing Administrator permissions")
      return

    try:
      sync = await self.bot.tree.sync()
      print(f"Synced {len(sync)} commands")
    except Exception as e:
      print(f"Failed to sync commands: {e}")

    await interaction.response.send_message("Synced tree commands")


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Debug(bot))