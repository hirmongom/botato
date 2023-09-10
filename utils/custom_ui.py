import asyncio
import discord

class FutureSelectMenu(discord.ui.Select):
  def __init__(self, user_id: int, future: asyncio.Future, options: list[str], 
              *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.future = future
    self.options = [
      discord.SelectOption(label = option, value = i) for i, option in enumerate(options)]

  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
      return # User not authorized
      
    self.disable = True
    await interaction.response.defer()
    self.future.set_result(self.values)