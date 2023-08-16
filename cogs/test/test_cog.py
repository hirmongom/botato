import discord
from discord import app_commands
from discord.ext import commands

import ctypes

class Test(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


  @app_commands.command(
    name = "test_step",
    description = "Test for multiple-step (?) commands"
  )
  async def test_step(self, interaction: discord.Interaction) -> None:
    def check(message: str) -> bool:
      return message.author == interaction.user and message.channel == interaction.channel

    self.bot.interaction_logger.info(f"|test_step| from {interaction.user.name}")
    await interaction.response.defer()

    await interaction.followup.send("[y]es or [n]o?")
    response = await self.bot.wait_for("message", check = check, timeout = 5)

    if response.content.lower()[:1] == "y":
      await interaction.followup.send("Eres Kenny")
    elif response.content.lower()[:1] == "n":
      await interaction.followup.send("No mientas, si que eres Kenny")
    else:
      await interaction.followup.send("AAAAAAAAAAAAAAAAAAAAHHH, donde esta Kenny?")


  @app_commands.command(
    name = "test_cpp",
    description = "Test execution of C++ script from python"
  )
  async def test_cpp(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|test_cpp| from {interaction.user.name}")

    lib = ctypes.CDLL("./cpp/test/test.so")
    lib.hello_cpp.restype = ctypes.c_char_p

    await interaction.response.send_message(lib.hello_cpp().decode("utf-8"))
    

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Test(bot))