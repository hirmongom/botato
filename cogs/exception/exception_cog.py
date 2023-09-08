import traceback

import discord
from discord.ext import commands

from utils.json import load_json
from utils.funcs import make_data, save_user_id

class Exception(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot
    bot.tree.error(coro = self.__dispatch_to_app_command_handler)


  async def __dispatch_to_app_command_handler(self, interaction: discord.Interaction, 
                                              error: discord.app_commands.AppCommandError) -> None:
    self.bot.dispatch("app_command_error", interaction, error)


  @commands.Cog.listener("on_app_command_error")
  async def handle_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    # First interaction will break most commands which require data, since it is not created yet
    # If it coccurs, create data and notify user
    self.bot.logger.error("".join(traceback.format_exception(type(error), error, error.__traceback__)))
    if isinstance(error.original, KeyError):
      user_ids = load_json("user_ids", "other")
      if not interaction.user.name in user_ids.keys():
        make_data(interaction.user.name)
        save_user_id(interaction.user.name, interaction.user.id)
        await interaction.response.send_message("Data was created on your first interaction, try "
                                                "the command again.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Exception(bot))