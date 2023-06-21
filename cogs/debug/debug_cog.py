import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
import os
class Debug(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name = "ping",
        description = "Returns Pong!")
    async def ping(self, interaction: discord.Interaction):
        print(f">> |ping| from {interaction.user.name}")
        await interaction.response.send_message("Pong!")

    @app_commands.command(
        name = "echo",
        description = "Echoes a message")
    async def echo(self, interaction: discord.Interaction, message: str):
        print(f">> |echo| from {interaction.user.name} with message |{message}|")
        await interaction.response.send_message(message)       

    @app_commands.command(
        name = "reload",
        description = "Reload a specific cog")
    @app_commands.checks.has_permissions(administrator = True)
    async def reload(self, interaction: discord.Interaction, cog: str):
        print(f">> |reload| from {interaction.user.name} with cog |{cog}|")
        await self.bot.reload_extension(f"cogs.{cog}.{cog}_cog")
        await interaction.response.send_message(f"Reloaded {cog}")

    @app_commands.command(
        name = "resync",
        description = "Reloads all cogs and resyncs")
    @app_commands.checks.has_permissions(administrator = True)
    async def resync(self, interaction: discord.Interaction):
        print(f">> |resync| from {interaction.user.name}")

        await interaction.response.defer()

        for folder in os.listdir("./cogs"):
                await self.bot.reload_extension(f"cogs.{folder}.{folder}_cog")
                print(f"Reloaded {folder}")

        await self.bot.resync()

        await interaction.followup.send("Resynced commands")


async def setup(bot: commands.Bot):
    await bot.add_cog(Debug(bot))