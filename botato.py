import os
from dotenv import load_dotenv

import discord
from discord.ext import commands
from discord import app_commands

class Botato(commands.Bot):
    def __init__(self, appId: int) -> None:
        super().__init__(
            command_prefix = "_not_designed_for_prefix_commands_", 
            intents = discord.Intents.all(),
            application_id = appId)

    async def setup_hook(self) -> None:
        for folder in os.listdir("./cogs"):
                await self.load_extension(f"cogs.{folder}.{folder}_cog")
                print(f"Loaded {folder}_cog")
        try:
            sync = await bot.tree.sync()
            print(f"Synced {len(sync)} commands")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

    async def on_ready(self) -> None:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="lo tonto que eres"))
        print(f'{bot.user} is connected\n')

    async def resync(self) -> None:
        try: 
            sync = await bot.tree.sync()
            print(f"Synced {len(sync)} commands")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

if __name__ == "__main__":
    load_dotenv()
    bot = Botato(appId=os.getenv('APPID'))
    bot.run(os.getenv('TOKEN'))