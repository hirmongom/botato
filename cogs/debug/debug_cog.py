import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

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
        print(f">> |echo| from {interaction.user.name}#{interaction.user.discriminator}")
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
        print(f">> |test| from {interaction.user.name}#{interaction.user.discriminator}")
        await interaction.response.send_message(f"Number: {number}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Debug(bot))