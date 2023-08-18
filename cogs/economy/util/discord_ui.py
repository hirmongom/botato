import discord

from util.json import load_json, save_json


class BankUpgradeButton(discord.ui.Button):
  def __init__(self, user_id: int, economy_data: dict, message: discord.Message, 
              embed: discord.Embed, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.economy_data = economy_data
    self.message = message
    self.embed = embed

  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
        return # User not authorized

    upgrade_cost = (self.economy_data["bank_upgrade"] + 1) * 5000
    if self.economy_data["hand_balance"] < upgrade_cost:
      await interaction.response.send_message("You do not have enough money in hand")
      await update_embed(message = self.message, embed = self.embed, 
                          economy_data = self.economy_data)
    else:
      self.economy_data["hand_balance"] = self.economy_data["hand_balance"] - upgrade_cost
      self.economy_data["bank_upgrade"] = self.economy_data["bank_upgrade"] + 1
      self.economy_data["max_withdrawal"] = self.economy_data["max_withdrawal"] + 500
      save_json(self.economy_data, interaction.user.name, "economy")
      
      max_withdrawal = self.economy_data["max_withdrawal"]
      await interaction.response.send_message(f"Upgrade completed!\nYou can now withdraw up to "
                                              f"{max_withdrawal} each week")
      await update_embed(message = self.message, embed = self.embed, 
                        economy_data = self.economy_data, was_upgrade = True)
    

class BankOperationSelect(discord.ui.Select):
  def __init__(self, user_id: int, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.modals = {}

  def set_modal(self, value: str, modal: discord.ui.Modal) -> None:
    self.modals[value] = modal

  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
        return # User not authorized

    self.disabled = True
    await interaction.message.edit(view = self.view)
    await interaction.response.send_modal(self.modals[self.values[0]])


class BankOperationModal(discord.ui.Modal):
  def __init__(self, title: str, operation: int, economy_data: dict, 
              message: discord.Message, embed: discord.Embed) -> None:
    super().__init__(title = title)
    self.operation = operation
    self.economy_data = economy_data
    self.message = message
    self.embed = embed

  async def on_submit(self, interaction: discord.Interaction) -> None:
    form_value = str(self.children[0])

    if form_value.isdigit():
      form_value = int(form_value)
      hand_balance = self.economy_data["hand_balance"]
      bank_balance = self.economy_data["bank_balance"]
      withdrawn_money = self.economy_data["withdrawn_money"]
      max_withdrawal = self.economy_data["max_withdrawal"]

      if self.operation == 1:
        if hand_balance < form_value:
          await interaction.response.send_message("You do not have enough money in hand")
        else:
          hand_balance -= form_value
          bank_balance += form_value
          await interaction.response.send_message(f"You deposited {form_value}€")

      elif self.operation == 2:
        if bank_balance < form_value:
          await interaction.response.send_message("You do not have that much money in the bank")
        elif withdrawn_money + form_value > max_withdrawal:
          await interaction.response.send_message("You cannot exceed the weekly maximum withdrawal limit")
        else:
          bank_balance -= form_value
          hand_balance += form_value
          withdrawn_money += form_value
          await interaction.response.send_message(f"You withdrew {form_value}€")

      self.economy_data["hand_balance"] = hand_balance
      self.economy_data["bank_balance"] = bank_balance
      self.economy_data["withdrawn_money"] = withdrawn_money
      save_json(self.economy_data, interaction.user.name, "economy")
      
    else:
      await interaction.response.send_message(f"Must be a number")

    await update_embed(self.message, self.embed, self.economy_data)


async def update_embed(message: discord.Message, embed: discord.Embed, 
                      economy_data: dict, was_upgrade: bool = False) -> None:
  hand_balance = economy_data["hand_balance"]
  bank_balance = economy_data["bank_balance"]
  max_withdrawal = economy_data["max_withdrawal"]
  withdrawn_money = economy_data["withdrawn_money"]

  embed.set_field_at(0, name = "💰 Hand Balance", value = f"{hand_balance}€", inline = True)
  embed.set_field_at(1, name = "🏦 Bank Balance", value = f"{bank_balance}€", inline = True)
  embed.set_field_at(2, name = "📆🔽 Remaining Weekly Withdraw Limit", 
                          value = f"{max_withdrawal - withdrawn_money}€", inline = False)
  if was_upgrade:
    embed.remove_field(3)

  await message.edit(embed = embed, view = None)