import asyncio
import discord


class ChallengeSelect(discord.ui.Select):
  def __init__(self, user_id: int, challenges: list[dict], future: asyncio.Future, 
              *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    for i, challenge in enumerate(challenges):
      self.add_option(label = f"{i + 1}. {challenge['category']}", value = i)
    self.future = future

  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
      return # User not authorized
    await interaction.response.defer()
    choice = int(self.values[0])
    self.future.set_result(choice)


class FutureIdButton(discord.ui.Button):
  def __init__(self, user_id: int, future: asyncio.Future, id: int, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.future = future
    self.id = id

  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
      return # User not authorized
    await interaction.response.defer()
    self.future.set_result(self.id)


class FutureModalButton(discord.ui.Button):
  def __init__(self, future: asyncio.Future, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.future = future

  async def callback(self, interaction: discord.Interaction) -> None:
    future_response = asyncio.Future()
    option_modal = FutureModal(future = future_response, title = "Set an option for your problem", 
                              label = "Option", placeholder = "option")
    await interaction.response.send_modal(option_modal)
    response = await future_response
    self.future.set_result(response)


class FutureModal(discord.ui.Modal):
  def __init__(self, future: asyncio.Future, label: str, placeholder: str, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.add_item(discord.ui.TextInput(label = label, placeholder = placeholder))
    self.future = future

  async def on_submit(self, interaction: discord.Interaction) -> None:
    await interaction.response.defer()
    value = str(self.children[0])
    self.future.set_result(value)


class SolutionSelect(discord.ui.Select):
  def __init__(self, future: asyncio.Future, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.options = [
      discord.SelectOption(label = "Option 0", value = 0),
      discord.SelectOption(label = "Option 1", value = 1),
      discord.SelectOption(label = "Option 2", value = 2),
      discord.SelectOption(label = "Option 3", value = 3)
    ]
    self.placeholder = "Set Solution"
    self.future = future
  
  async def callback(self, interaction: discord.Interaction) -> None:
    await interaction.response.defer()
    result = int(self.values[0])
    self.future.set_result(result)