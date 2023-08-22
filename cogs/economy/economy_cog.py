import os

import discord
from discord import app_commands
from discord.ext import commands

import random

from utils.json import load_json, save_json
from .utils.custom_ui import BankOperationModal, BankOperationSelect, BankUpgradeButton

# @idea Weekly lottery, minimum of players (or not, just max of tickets)
# @idea Purchasable itmes:
#        * Custom name color
#        * Custom rol


class Economy(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot
    self.week_day = 0


  async def daily_task(self) -> None:
    for file in os.listdir("data/economy/"):
      if file != ".gitkeep":
        data = load_json(file[:-5], "economy")
        if data["daily_pay"] == 0:
          data["streak"] = data["streak"] + 1
          data["daily_pay"] = 1
        else:
          data["streak"] = 0
        if self.week_day == 0:
          data["withdrawn_money"] = 0
          data["bank_balance"] = data["bank_balance"] * data["interest_rate"]
        save_json(data, file[:-5], "economy")


  @commands.Cog.listener()
  async def on_interaction(self, interaction: discord.Interaction) -> None:
    if type(interaction.command) == type(None) or interaction.command.name == "bank":
      # Shouldn't trigger after checking the current XP
      # Excludee certain interactions that are not commands
      return

    data = load_json(interaction.user.name, "economy")
    daily_pay = data["daily_pay"]

    if daily_pay == 1:
      if data["streak"] == 7:
        increase = random.randint(750, 1000)
        data["streak"] = 0
      else:
        increase = random.randint(50, 150)
      data["bank_balance"] = data["bank_balance"] + increase
      data["daily_pay"] = 0

      streak_msg = f" (Current streak = {data['streak']} days)" if int(data["streak"]) != 0 else ""
      await interaction.channel.send(f"(*) You received {increase}€ on your bank{streak_msg}")
      self.bot.interaction_logger.info(f"Money increase on first interaction for {interaction.user.name} with {increase}€")

    save_json(data, interaction.user.name, "economy")


  @app_commands.command(
    name = "bank",
    description = "Check your account balance and perform opperations"
  )
  async def bank(self, interaction: discord.Interaction) -> None:
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
    interest_rate = economy_data["interest_rate"]
    user_data = load_json(interaction.user.name, "user")

    embed = discord.Embed(
      title = "🏦 Bank Account",
      description = f"Welcome to the bank, {interaction.user.display_name}! Choose an operation below.",
      color = discord.Color.gold()
    )
    embed.add_field(name = "💰 Hand Balance", value = f"{hand_balance}€", inline = True)
    embed.add_field(name = "🏦 Bank Balance", value = f"{bank_balance}€", inline = True)
    embed.add_field(name = "📆🔽 Remaining Weekly Withdraw Limit", 
                    value = f"{max_withdrawal - withdrawn_money}€", inline = False)
    if user_data["level"] / 5 >= economy_data["bank_upgrade"] + 1:
      upgrade_cost = (economy_data["bank_upgrade"] + 1) * 5000
      embed.add_field(name = f"💰 You can upgrade your bank for {upgrade_cost}€", 
                      value = f"Withdrawal limit from {max_withdrawal}€ to {max_withdrawal + 500}€\n"
                              f"Interest rate from {int((interest_rate - 1) * 100)}% to {int((interest_rate - 1) * 100 + 1)}%", 
                      inline = False)

    embed.set_footer(text = "Secure Banking | Botato Bank", icon_url = self.bot.user.display_avatar.url)
    
    message = await interaction.followup.send(embed = embed, ephemeral = True)

    deposit_modal = BankOperationModal(title = "Deposit", operation = 1, economy_data = economy_data,
                                message = message, embed = embed)
    deposit_modal.add_item(discord.ui.TextInput(label = "Amount"))
    withdraw_modal = BankOperationModal(title = "Withdraw", operation = 2, economy_data = economy_data,
                                 message = message, embed = embed)
    withdraw_modal.add_item(discord.ui.TextInput(label = "Amount"))

    menu_choice = [
      discord.SelectOption(label = "Deposit", value = 1),
      discord.SelectOption(label = "Withdraw", value = 2)]
    menu = BankOperationSelect(
      user_id = interaction.user.id,
      placeholder = "Choose an operation",
      options = menu_choice,)
    menu.set_modal("1", deposit_modal)
    menu.set_modal("2", withdraw_modal)

    view = discord.ui.View()
    view.add_item(menu)
    if user_data["level"] / 5 >= economy_data["bank_upgrade"] + 1:
      button = BankUpgradeButton(user_id = interaction.user.id,
                                message = message,
                                embed = embed,
                                economy_data = economy_data,
                                label = "Upgrade Bank", 
                                style = discord.ButtonStyle.primary,)
      view.add_item(button)

    await message.edit(embed = embed, view = view)


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Economy(bot))