import os
from dotenv import load_dotenv

import asyncio

import discord
from discord.ext import commands
from discord import app_commands


class Botato(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix = "_not_designed_for_prefix_commands_", 
            intents = discord.Intents.all(),
            activity = discord.Activity(type = discord.ActivityType.watching, 
                                        name = "lo tonto que eres"))


    def run(self) -> None:
        load_dotenv()
        super().run(os.getenv("TOKEN"))


    async def setup_hook(self) -> None:
        for folder in os.listdir("./cogs"):
                await self.load_extension(f"cogs.{folder}.{folder}_cog")
                print(f"Loaded {folder}_cog")
        try:
            sync = await self.tree.sync()
            print(f"Synced {len(sync)} commands")
        except Exception as e:
            print(f"Failed to sync commands: {e}")


    async def on_ready(self) -> None:
        print(f'{bot.user} is connected\n')

    

if __name__ == "__main__":  
    bot = Botato()
    bot.run()