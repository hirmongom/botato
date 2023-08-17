import os

import discord
from discord import app_commands
from discord.ext import commands

import random

from util.json import load_json, save_json


class Economy(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot
    self.week_day = 0


  async def daily_trigger(self) -> None:
    self.bot.interaction_logger.info("Economy daily trigger")
    self.week_day = (self.week_day + 1) % 8

    for file in os.listdir("data/economy/"):
      data = load_json(file[:-5], "economy")
      data["daily_pay"] = 1
      if self.week_day == 0:
        data["withdrawn_money"] = 0
      save_json(data, file[:-5], "economy")


  @commands.Cog.listener()
  async def on_interaction(self, interaction: discord.Interaction) -> None:
    if type(interaction.command) == type(None) or interaction.command.name == "bank":
      # Shouldn't trigger after checking the current XP
      # Excluede certain interactions that are not commands
      return

    data = load_json(interaction.user.name, "economy")
    daily_pay = data["daily_pay"]

    if daily_pay == 1:
      increase = random.randint(50, 150)
      data["bank_balance"] = data["bank_balance"] + increase
      data["daily_pay"] = 0
      await interaction.channel.send(f"(*) You received {increase}€ on your bank")
      self.bot.interaction_logger.info(f"Money increase on first interaction for {interaction.user.name} with {increase}€")

    save_json(data, interaction.user.name, "economy")


  @app_commands.command(
    name = "bank",
    description = "Bank stuff"
  )
  async def bank(self, interaction: discord.Interaction) -> None:
    class CustomSelect(discord.ui.Select):
      def __init__(self, user_id: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.modals = {}
        self.user_id = user_id

      def set_modal(self, value: str, modal: discord.ui.Modal) -> None:
        self.modals[value] = modal

      async def callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.user_id:
            #await interaction.response.send_message("You are not authorized to interact with this menu.", ephemeral=True)
            return
        self.disabled = True
        await interaction.message.edit(view = self.view)
        await interaction.response.send_modal(self.modals[self.values[0]])

    class CustomModal(discord.ui.Modal):
      def __init__(self, title: str, operation: int, economy_data: dict, message: discord.Message, embed: discord.Embed) -> None:
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

          self.embed.set_field_at(0, name = "💰 Hand Balance", value = f"{hand_balance}€", inline = True)
          self.embed.set_field_at(1, name = "🏦 Bank Balance", value = f"{bank_balance}€", inline = True)
          self.embed.set_field_at(2, name = "📆🔽 Remaining Weekly Withdraw Limit", 
                                  value = f"{max_withdrawal - withdrawn_money}€", inline = False)
          await self.message.edit(embed = self.embed)
        else:
          await interaction.response.send_message(f"Must be a number")

    self.bot.interaction_logger.info(f"|bank| from {interaction.user.name}")

    if not os.path.isfile(f"data/economy/{interaction.user.name}.json"):
      await interaction.response.send_message("It seems this is your first interaction with this " + 
                                              "bot, so I don't have any data, please check again")
      return

    await interaction.response.defer()

    economy_data = load_json(interaction.user.name, "economy")
    hand_balance = economy_data["hand_balance"]
    bank_balance = economy_data["bank_balance"]
    max_withdrawal = economy_data["max_withdrawal"]
    withdrawn_money = economy_data["withdrawn_money"]
    user_data = load_json(interaction.user.name, "user")

    embed = discord.Embed(
      title = "🏦 Bank Operations",
      description = f"Welcome to the bank, {interaction.user.display_name}! Choose an operation below.",
      color = discord.Color.gold()
    )
    embed.add_field(name = "💰 Hand Balance", value = f"{hand_balance}€", inline = True)
    embed.add_field(name = "🏦 Bank Balance", value = f"{bank_balance}€", inline = True)
    embed.add_field(name = "📆🔽 Remaining Weekly Withdraw Limit", 
                    value = f"{max_withdrawal - withdrawn_money}€", inline = False)
    if user_data["level"] / 5 >= economy_data["bank_upgrade"] + 1:
      print(user_data["level"] / 5)
      upgrade_cost = (economy_data["bank_upgrade"] + 1) * 5000
      embed.add_field(name = f"💰 You can upgrade your bank for {upgrade_cost}€", 
                      value = f"Withdrawal limit from {max_withdrawal}€ to {max_withdrawal + 500}€", inline = False)
    embed.set_footer(text = "Secure Banking | Botato Bank", icon_url = self.bot.user.display_avatar.url)
    
    message = await interaction.followup.send(embed = embed, ephemeral = True)

    deposit_modal = CustomModal(title = "Deposit", operation = 1, economy_data = economy_data,
                                message = message, embed = embed)
    deposit_modal.add_item(discord.ui.TextInput(label = "Amount"))
    withdraw_modal = CustomModal(title = "Withdraw", operation = 2, economy_data = economy_data,
                                 message = message, embed = embed)
    withdraw_modal.add_item(discord.ui.TextInput(label = "Amount"))

    menu_choice = [
      discord.SelectOption(label = "Deposit", value = 1),
      discord.SelectOption(label = "Withdraw", value = 2)]
    menu = CustomSelect(
      user_id = interaction.user.id,
      placeholder = "Choose an operation",
      options = menu_choice,)
    menu.set_modal("1", deposit_modal)
    menu.set_modal("2", withdraw_modal)

    view = discord.ui.View()
    view.add_item(menu)

    await message.edit(embed = embed, view = view)


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Economy(bot))