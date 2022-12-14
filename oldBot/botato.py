import os
import discord
from dotenv import load_dotenv
from discord.ext import commands


def main():
    intents = discord.Intents().all()
    client = commands.Bot(command_prefix = '.', intents = intents)

    load_dotenv()

    @client.event
    async def on_ready():
        print(f'{client.user} is connected\n')
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="lo tonto que eres"))

    for folder in os.listdir("./modules"):
        if os.path.exists(os.path.join("modules", folder, "cog.py")):
            client.load_extension(f"modules.{folder}.cog")

    client.run(os.getenv('DISCORD_TOKEN'))


if __name__ == "__main__":
    main()