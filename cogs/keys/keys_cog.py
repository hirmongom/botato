import discord
from discord import app_commands
from discord.ext import commands

from util.scrap_keys import scrapKeys

class Util(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name = "keys",
        description = "Queries for a game in clavecd.es and returns the first 5 prices")
    async def keys(self, interaction: discord.Interaction, query: str):
        print(f">> |keys| from {interaction.user.name} with query |{query}|")
        query = query.replace(" ", "+")
        query = f"https://clavecd.es/catalog/search-{query}"

        await interaction.response.defer()

        try:
            title, content = scrapKeys(query)
        except Exception as e:
            print(e)
            await interaction.followup.send(f"No results found")
            return

        await interaction.followup.send(f"{title}\n{query}\n{content}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Util(bot))