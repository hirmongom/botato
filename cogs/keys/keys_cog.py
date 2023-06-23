import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View

from .util.scrap_keys import scrapKeys, getLink, getTitle
from .util.game_follow import storeGame, getGameList, removeGames, loadJson

# TODO ask for manual update of all following
# TODO set remind hours?
# TODO max 25 following games

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
            title = getTitle(link)
            content = scrapKeys(link)
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
     
        storeGame(interaction.user.name, title, link)

        await interaction.followup.send(f"You are now following {title}\n{link}")


    @app_commands.command(
        name = "list",
        description = "Lists all games you are following"
    )
    async def list(self, interaction: discord.Interaction) -> None:
        print(f">> |list| from {interaction.user.name}")
    
        games = getGameList(interaction.user.name)   

        if len(games) == 0:
            await interaction.response.send_message("You are not following any games")
            return

        output = ""
        for i, game in enumerate(games):
            output += f"\n-\t {game}"

        await interaction.response.send_message(f"Following games:{output}")


    @app_commands.command(
        name = "unfollow",
        description = "Remove one or multiple games from your following list"
    )
    async def unfollow(self, interaction: discord.Interaction) -> None:
        print(f">> |unfollow| from {interaction.user.name}")
        await interaction.response.defer()

        games = getGameList(interaction.user.name)

        if len(games) == 0:
            await interaction.followup.send("You are not following any games")
            return

        game_choice = [discord.SelectOption(label = game, value = i) for i, game in enumerate(games)]

        menu = Select(
            min_values = 1,
            max_values = len(games),
            placeholder = "Choose games to unfollow", 
            options = game_choice,
        )

        async def menu_callback(interaction: discord.Interaction) -> None:
            to_remove = [games[int(i)] for i in menu.values]
            removeGames(interaction.user.name, to_remove)

            response = ""
            for game in to_remove:
                response += "\n-\t" + game
            await message.edit(content = f"You unfollowed:{response}", view = None, ephemeral = False)

        menu.callback = menu_callback
        view = View()
        view.add_item(menu)
        message = await interaction.followup.send(view = view, ephemeral = True)


    @app_commands.command(
        name = "update",
        description = "Get the key prices for all the games or your following list"
    )
    async def update(self, interaction: discord.Interaction) -> None:
        print(f">> |update| from {interaction.user.name}")
        await interaction.response.defer()
        games = loadJson(interaction.user.name)

        message = await interaction.followup.send("Sit back and relax, this is going to take some time...")

        response = f"{40 * '='}\n\n"
        for title in games.keys():
            response += f"**{title}**\n<{games[title]}>\n{scrapKeys(games[title])}\n\n{40 * '='}\n\n"

        print(response)
        await message.edit(content = response)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Util(bot))