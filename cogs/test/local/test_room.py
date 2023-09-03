import asyncio
import discord
from utils.json import load_json, save_json

class EntryButton(discord.ui.Button):
  def __init__(self, players: list[discord.Member], embed: discord.Embed, 
               message: discord.Message, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.players = players
    self.embed = embed
    self.message = message

  async def callback(self, interaction: discord.Interaction) -> None:
    await interaction.response.defer()

    if interaction.user not in self.players:
      self.players.append(interaction.user)
      self.embed.add_field(name = f"{interaction.user.display_name}", value = "", inline = False)
      await self.message.edit(embed = self.embed)
    else:
      await interaction.followup.send("You are already in the room", ephemeral = True)


class StartButton(discord.ui.Button):
  def __init__(self, host_id: int, future: asyncio.Future, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.host_id = host_id
    self.future = future

  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.host_id:
      return # User not authorized

    await interaction.response.defer()
    self.future.set_result(True)
    # remove buttons