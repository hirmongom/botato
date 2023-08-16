import discord
from discord import app_commands
from discord.ext import commands

import random

class Misc(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


  @app_commands.command(
    name = "roll",
    description = "Roll a specific dice"
  )
  @app_commands.describe(
    rolls = "The number of rolls you want to perform with your dice (10 maximum)",
  )
  @app_commands.describe(
    dice = "The type of dice you want to use for your roll",
  )
  @app_commands.choices(
    dice = [
      app_commands.Choice(name = "d6", value = 6),
      app_commands.Choice(name = "d20", value = 20)
    ]
  )
  async def roll(self, interaction: discord.Interaction, rolls: int, dice: int):
    self.bot.interaction_logger.info(f"|roll| from {interaction.user.name} with rolls = {rolls} and dice = {dice}")
    if rolls > 10 or rolls < 1:
      await interaction.response.send_message("u dum")
      return
    
    response = ""
    roll_result = 0
    for i in range(rolls):
      roll = random.randint(1, dice)
      response += f"\n\tRoll {i + 1} = {roll}"
      roll_result += roll
    response += f"\nTOTAL = {roll_result}"
    await interaction.response.send_message(f"You rolled {rolls}d{dice} and got:{response}")

  @app_commands.command(
    name = "test",
    description = "Test for progressive (?) commands"
  )
  async def test(self, interaction: discord.Interaction) -> None:
    def check(message: str) -> bool:
      return message.author == interaction.user and message.channel == interaction.channel

    self.bot.interaction_logger.info(f"|test| from {interaction.user.name}")
    await interaction.response.defer()

    await interaction.followup.send("[y]es or [n]o?")
    response = await self.bot.wait_for("message", check = check, timeout = 5)

    if response.content.lower()[:1] == "y":
      await interaction.followup.send("Eres Kenny")
    elif response.content.lower()[:1] == "n":
      await interaction.followup.send("No mientas, si que eres Kenny")
    else:
      await interaction.followup.send("AAAAAAAAAAAAAAAAAAAAHHH, donde esta Kenny?")


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Misc(bot))