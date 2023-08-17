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
      def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.modals = {}
      def set_modal(self, value: str, modal: discord.ui.Modal) -> None:
        self.modals[value] = modal
      async def callback(self, interaction: discord.Interaction) -> None:
        self.disabled = True
        await interaction.message.edit(view=self.view)
        await interaction.response.send_modal(self.modals[self.values[0]])

    class CustomModal(discord.ui.Modal):
      def __init__(self, title: str) -> None:
        super().__init__(title = title)
      async def on_submit(self, interaction: discord.Interaction) -> None:
        form_value = str(self.children[0])
        if form_value.isdigit():
          await interaction.response.send_message(f"{self.title} modal submitted with form {self.children[0]}")
        else:
          await interaction.response.send_message(f"Must be a number")

    self.bot.interaction_logger.info(f"|test_menu| from {interaction.user.name}")
    # Initial checks
    try:
      economy_data = load_json(interaction.user.name, "economy")
      user_data = load_json(interaction.user.name, "user")
      hand_balance = economy_data["hand_balance"]
      bank_balance = economy_data["bank_balance"]
    except KeyError:
      await interaction.response.send_message("It seems this is your first interaction with this " + 
                                              "bot, so I don't have any data, please check again")
      return

    await interaction.response.defer()

    deposit_modal = CustomModal(title = "Deposit")
    deposit_modal.add_item(discord.ui.TextInput(label = "Amount"))
    withdraw_modal = CustomModal(title = "Withdraw")
    withdraw_modal.add_item(discord.ui.TextInput(label = "Amount"))

    menu_choice = [
      discord.SelectOption(label = "Deposit", value = 1),
      discord.SelectOption(label = "Withdraw", value = 2)]
    menu = CustomSelect(
      placeholder = "Choose an operation",
      options = menu_choice,)
    menu.set_modal("1", deposit_modal)
    menu.set_modal("2", withdraw_modal)

    view = discord.ui.View()
    view.add_item(menu)

    embed = discord.Embed(title = "Bank")
    await interaction.followup.send(embed = embed, view = view, ephemeral = True)


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Economy(bot))