import discord
from discord import app_commands
from discord.ext import commands

import ctypes
import datetime



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


  @app_commands.command(
     name = "test_embed",
     description = "Test embed creation and design"
  )
  async def test_embed(self, interaction: discord.Interaction) -> None:
    self.bot.interaction_logger.info(f"|test_embed| from {interaction.user.name}")

    embed = discord.Embed(
      title = "🚀 Galactic Explorer 🌌",
      description = "Your ultimate guide to the cosmos!",
      color = discord.Color.blue())

    # Thumbnail for the embed (replace with any image URL you like)
    embed.set_thumbnail(url = "https://astronomy.swin.edu.au/cms/cpg15x/albums/scaled_cache/spiralgalaxy1-145x120.jpg")

    # Author details
    embed.set_author(name = "Botato", 
                     icon_url = self.bot.user.display_avatar.url, 
                     url = "https://github.com/hmongom/Botato")

    # Fields for various sections
    embed.add_field(name = "🌟 Featured Star", value = "Alpha Centauri", inline=True)
    embed.add_field(name = "🪐 Featured Planet", value = "Kepler-22b", inline = True)
    embed.add_field(name = "🌌 Current Event", value = "Perseid Meteor Shower", inline = False)
    embed.add_field(name = "🔭 Latest Discovery", value = "A potential Earth-like planet in the Andromeda galaxy!", inline = False)

    # Image for the embed (replace with any image URL you like)
    embed.set_image(url = "https://img.freepik.com/free-vector/realistic-colorful-galaxy-background_23-2148965681.jpg")

    # Footer with some additional info
    embed.set_footer(text = "Last updated: 2023-08-03 | For more info, visit our website!", 
                     icon_url = "https://img.freepik.com/premium-vector/rocket-sketch-drawing-with-free-hand-vector-eps10_255544-1983.jpg?w=2000")

    # Timestamp for when the embed was created (optional)
    embed.timestamp = datetime.datetime.utcnow()

    await interaction.response.send_message(embed = embed)


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Test(bot))