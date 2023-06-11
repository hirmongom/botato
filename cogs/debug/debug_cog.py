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
        description = "Pong!")
    async def ping(self, interaction: discord.Interaction):
        print(f">> |ping| from {interaction.user.name}#{interaction.user.discriminator}")
        await interaction.response.send_message("Pong")

    @app_commands.command(
        name = "echo",
        description = "Echoes a message")
    async def echo(self, interaction: discord.Interaction, message: str):
        print(f">> |echo| from {interaction.user.name}#{interaction.user.discriminator} with message |{message}|")
        await interaction.response.send_message(message)

    @app_commands.command(
        name = "test",
        description = "Test command")
    @app_commands.describe(number = "Choice test")
    @app_commands.choices(number = [
        Choice(name = "one", value = 1),
        Choice(name = "two", value = 2),
        Choice(name = "three", value = 3)
    ])
    async def test(self, interaction: discord.Interaction, number: int):
        print(f">> |test| from {interaction.user.name}#{interaction.user.discriminator} with number |{number}|")
        await interaction.response.send_message(f"Number: {number}")

    @app_commands.command(
        name = "reloadall",
        description = "Reloads all cogs")
    async def reloadall(self, interaction: discord.Interaction):
        print(f">> |reloadall| from {interaction.user.name}#{interaction.user.discriminator}")
        if interaction.user.name != self.bot.admin:
            await interaction.response.send_message("No permission")
            return
        for folder in os.listdir("./cogs"):
                await self.bot.reload_extension(f"cogs.{folder}.{folder}_cog")
                print(f"Reloaded {folder}")
        await interaction.response.send_message("Reloaded all cogs")
        

    @app_commands.command(
        name = "reload",
        description = "Reloads a cog")
    async def reload(self, interaction: discord.Interaction, cog: str):
        print(f">> |reload| from {interaction.user.name}#{interaction.user.discriminator} with cog |{cog}|")
        if interaction.user.name != self.bot.admin:
            await interaction.response.send_message("No permission")
            return
        await self.bot.reload_extension(f"cogs.{cog}.{cog}_cog")
        await interaction.response.send_message(f"Reloaded {cog}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Debug(bot))