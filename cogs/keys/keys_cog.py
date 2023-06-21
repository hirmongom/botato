import discord
from discord import app_commands
from discord.ext import commands

from util.scrap_keys import scrapKeys, getLink, getTitle
from util.key_data import storeKey

class Util(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name = "keys",
        description = "Queries for a game in clavecd.es and returns the first 5 prices")
    async def keys(self, interaction: discord.Interaction, query: str) -> None:
        print(f">> |keys| from {interaction.user.name} with query |{query}|")

        await interaction.response.defer()

        try:
            link = getLink(query)
            title, content = scrapKeys(link)
        except Exception as e:
            print(e)
            await interaction.followup.send(f"No results found")
            return

        await interaction.followup.send(f"{title}\n{link}\n{content}")

    @app_commands.command(
        name = "follow",
        description = "Follow a game to easily check key prices"
    )
    async def follow(self, interaction: discord.Interaction, game : str) -> None:
        print(f">> |follow| from {interaction.user.name} with game |{game}|")

        await interaction.response.defer()
        
        try:
            link = getLink(game)
            title = getTitle(link)
        except Exception as e:
            print(e)
            await interaction.followup.send(f"No results found")
            return
     
        storeKey(interaction.user.name, title, link)

        await interaction.followup.send(f"You are now following {title}")

    # TODO list following games
    # TODO unfollow game (should bring a choice selection)
    # TODO ask for manual update of all following
    # TODO set remind hours?

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Util(bot))