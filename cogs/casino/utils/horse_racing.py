import asyncio
import discord
from utils.json import load_json, save_json

class EntryButton(discord.ui.Button):
  def __init__(self, players: list[discord.Member], entry: int, embed = discord.Embed, 
               message = discord.Message, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.players = players
    self.entry = entry
    self.embed = embed
    self.message = message

  async def callback(self, interaction: discord.Interaction) -> None:
    self.disabled = True
    economy_data = load_json(interaction.user.name, "economy")
    if economy_data["hand_balance"] < self.entry:
      await interaction.response.send_message("You do not have enough money in hand")
      return

    await interaction.response.defer()

    economy_data["hand_balance"] -= self.entry
    save_json(economy_data, interaction.user.name, "economy")

    self.players.append(interaction.user)
    self.embed.add_field(name = f"{interaction.user.display_name}", value = "", inline = False)
    await self.message.edit(embed = self.embed)


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