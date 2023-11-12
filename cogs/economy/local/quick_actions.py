#  * @copyright   This file is part of the "Botato" project.
#  * 
#  *              Every file is free software: you can redistribute it and/or modify
#  *              it under the terms of the GNU General Public License as published by
#  *              the Free Software Foundation, either version 3 of the License, or
#  *              (at your option) any later version.
#  * 
#  *              These files are distributed in the hope that they will be useful,
#  *              but WITHOUT ANY WARRANTY; without even the implied warranty of
#  *              MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  *              GNU General Public License for more details.
#  * 
#  *              You should have received a copy of the GNU General Public License
#  *              along with the "Botato" project. If not, see <http://www.gnu.org/licenses/>.


import discord

from utils.json import load_json, save_json


#***************************************************************************************************
async def deposit(interaction: discord.Interaction, amount: float) -> None:
  amount = round(amount, 2)

  economy_data = load_json(interaction.user.name, "economy")
  if economy_data["hand_balance"] < amount:
    await interaction.followup.send(f"<@{interaction.user.id}> You do not have enough money in "
                                    "hand", ephemeral = True)
  else:
    economy_data["hand_balance"] = round(economy_data["hand_balance"] - amount, 2)
    economy_data["bank_balance"] = round(economy_data["bank_balance"] + amount, 2)
    save_json(economy_data, interaction.user.name, "economy")
    await interaction.followup.send(f"<@{interaction.user.id}> You deposited {amount}€",
                                    ephemeral = True)


#***************************************************************************************************
async def withdraw(interaction: discord.Interaction, amount: float) -> None:
    amount = round(amount, 2)

    economy_data = load_json(interaction.user.name, "economy")
    if economy_data["bank_balance"] < amount:
      await interaction.followup.send(f"<@{interaction.user.id}> You do not have enough money in "
                                    "the bank", ephemeral = True)

    elif economy_data["max_withdrawal"] - economy_data["withdrawn_money"] < amount:
      await interaction.followup.send(f"<@{interaction.user.id}> You cannot withdraw that much "
                                      "money", ephemeral = True)
    else:
      economy_data["hand_balance"] = round(economy_data["hand_balance"] + amount, 2)
      economy_data["bank_balance"] = round(economy_data["bank_balance"] - amount, 2)
      economy_data["withdrawn_money"] = round(economy_data["withdrawn_money"] + amount, 2)
      save_json(economy_data, interaction.user.name, "economy")
      await interaction.followup.send(f"<@{interaction.user.id}> You withdrew {amount}€",
                                      ephemeral = True)


#***************************************************************************************************
async def transfer(interaction: discord.Interaction, amount: float, 
                  recipient: discord.member.Member) -> None:
  user_economy_data = load_json(interaction.user.name, "economy")
  recipient_economy_data = load_json(recipient.name, "economy")

  if user_economy_data["bank_balance"] < amount:
    await interaction.followup.send(f"<@{interaction.user.id}> You do not have enough money in the "
                                    "bank", ephemeral = True)
    return

  user_economy_data["bank_balance"] = round(user_economy_data["bank_balance"] - amount, 2)
  recipient_economy_data["bank_balance"] = round(recipient_economy_data["bank_balance"] + amount, 2)

  save_json(user_economy_data, interaction.user.name, "economy")
  save_json(recipient_economy_data, recipient.name, "economy")

  await interaction.followup.send(f"<@{interaction.user.id}> transferred {amount}€ to "
                                          f"<@{recipient.id}>")


#***************************************************************************************************
async def upgrade_bank(interaction: discord.Interaction) -> None:
  economy_data = load_json(interaction.user.name, "economy")
  upgrade_cost = (economy_data["bank_upgrade"] + 1) * 10000

  if economy_data["hand_balance"] < upgrade_cost:
    await interaction.followup.send(f"<@{interaction.user.id}> You do not have enough money in "
                                    "hand", ephemeral = True)
  else:
    economy_data["hand_balance"] -= upgrade_cost
    economy_data["bank_upgrade"] += 1
    economy_data["max_withdrawal"] += 25000
    economy_data["interest_rate"] += 0.02
    economy_data["withdrawn_money"] = 0
    save_json(economy_data, interaction.user.name, "economy")
    await interaction.followup.send(f"<@{interaction.user.id}> Upgrade completed!\nYou can now "
                                    f"withdraw up to {economy_data['max_withdrawal']}€ each week\n"
                                    "Your interest rate has increased to "
                                    f"{int((economy_data['interest_rate'] - 1) * 100)}%", 
                                    ephemeral = True)