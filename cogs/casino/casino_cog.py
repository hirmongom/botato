import os

import discord
from discord import app_commands
from discord.ext import commands

import random

# @idea Casino (blackjack, poker, roulette, coin flip)
#         * Limit gains: Based of amount of money earned in a span of time, there is an increasing
#           chance of an event happens with x options to choose from and 1 correct, the others have
#           varying degrees of negativity, and make you lose money.
#           The values of the choices are randomly based
#         * The higher the level of the user, the higher bets he can make


class Casino(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Casino(bot))