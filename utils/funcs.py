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

import asyncio
import discord
from utils.json import load_json, save_json

def make_data(user: str) -> None:
  user_data = {}
  user_data["level"] = 1
  user_data["experience"] = 0
  user_data["xp_probabiliy"] = 5
  user_data["daily_xp"] = 10
  user_data["days_interacted"] = 0
  user_data["gamekeys_searched"] = 0
  user_data["bets_placed"] = 0
  user_data["blackjack_hands_played"] = 0
  user_data["blackjack_hands_won"] = 0
  user_data["roulettes_played"] = 0
  user_data["roulettes_won"] = 0
  user_data["achievments"] = []
  user_data["user_description"] = ""
  user_data["role_name"] = ""
  save_json(user_data, user, "user")

  economy_data = {}
  economy_data["hand_balance"] = 0
  economy_data["bank_balance"] = 500 
  economy_data["daily_pay"] = 1
  economy_data["max_withdrawal"] = 5000
  economy_data["withdrawn_money"] = 0
  economy_data["bank_upgrade"] = 0
  economy_data["interest_rate"] = 1
  economy_data["streak"] = 0
  save_json(economy_data, user, "economy")


def save_user_id(user_name: str, user_id: int) -> None:
  user_ids = load_json("user_ids", "other")
  user_ids[user_name] = user_id
  save_json(user_ids, "user_ids", "other")


# ********** ACHIEVMENTS **********
lock = asyncio.Lock()

async def update_achievment(interaction: discord.Interaction, user_data: dict, stat: str, value: int, tier: int) -> None:
  map_stat_name = {
    "days_interacted": "Days Interacted",
    "gamekeys_searched": "Game Keys Searched",
    "blackjack_hands_played": "Blackjack Hands Played",
    "blackjack_hands_won": "Blackjack Hands Won",
    "roulettes_played": "Roulette Games Played",
    "roulettes_won": "Roulette Games Won",
    "bets_placed": "Bets Placed"
  }

  if tier == 1:
    user_data["achievments"].append({stat: value, "tier": tier})
  else:
    for achievment in user_data["achievments"]:
      if stat in achievment:
        achievment[stat] = value
        achievment["tier"] = tier
        break

  xp_increase = tier * 100
  user_data["experience"] += xp_increase

  await interaction.followup.send(f"You unlocked the achievment {value} {map_stat_name[stat]} "
                                  f"and received {xp_increase} XP!")
  if user_data["experience"] >= (user_data["level"] * 100 + (user_data["level"] - 1) * 50):
    user_data["level"] += 1
    await interaction.followup.send(f"(*) You leveled up to level {user_data['level']}!!")


async def add_user_stat(stat: str, interaction: discord.Interaction) -> None:
  async with lock:
    user_data = load_json(interaction.user.name, "user")
    if stat == "days_interacted":
      user_data[stat] += 1
      if user_data[stat] == 10:
        await update_achievment(interaction, user_data, stat, 10, 1)
      if user_data[stat] == 25:
        await update_achievment(interaction, user_data, stat, 25, 2)
      if user_data[stat] == 50:
        await update_achievment(interaction, user_data, stat, 50, 3)
      if user_data[stat] == 100:
        await update_achievment(interaction, user_data, stat, 100, 4)

    elif stat == "gamekeys_searched":
      user_data[stat] += 1
      if user_data[stat] == 10:
        await update_achievment(interaction, user_data, stat, 10, 1)
      if user_data[stat] == 25:
        await update_achievment(interaction, user_data, stat, 25, 2)
      if user_data[stat] == 50:
        await update_achievment(interaction, user_data, stat, 50, 3)
      if user_data[stat] == 100:
        await update_achievment(interaction, user_data, stat, 100, 4)
    
    elif stat == "blackjack_hands_played":
      user_data[stat] += 1
      if user_data[stat] == 50:
        await update_achievment(interaction, user_data, stat, 50, 1)
      if user_data[stat] == 100:
        await update_achievment(interaction, user_data, stat, 100, 2)
      if user_data[stat] == 250:
        await update_achievment(interaction, user_data, stat, 250, 3)
      if user_data[stat] == 500:
        await update_achievment(interaction, user_data, stat, 500, 4)

    elif stat == "blackjack_hands_won":
      user_data[stat] += 1
      if user_data[stat] == 50:
        await update_achievment(interaction, user_data, stat, 50, 1)
      if user_data[stat] == 100:
        await update_achievment(interaction, user_data, stat, 100, 2)
      if user_data[stat] == 250:
        await update_achievment(interaction, user_data, stat, 250, 3)
      if user_data[stat] == 500:
        await update_achievment(interaction, user_data, stat, 500, 4)

    elif stat == "roulettes_played":
      user_data[stat] += 1
      if user_data[stat] == 50:
        await update_achievment(interaction, user_data, stat, 50, 1)
      if user_data[stat] == 100:
        await update_achievment(interaction, user_data, stat, 100, 2)
      if user_data[stat] == 250:
        await update_achievment(interaction, user_data, stat, 250, 3)
      if user_data[stat] == 500:
        await update_achievment(interaction, user_data, stat, 500, 4)

    elif stat == "roulettes_won":
      user_data[stat] += 1
      if user_data[stat] == 50:
        await update_achievment(interaction, user_data, stat, 50, 1)
      if user_data[stat] == 100:
        await update_achievment(interaction, user_data, stat, 100, 2)
      if user_data[stat] == 250:
        await update_achievment(interaction, user_data, stat, 250, 3)
      if user_data[stat] == 500:
        await update_achievment(interaction, user_data, stat, 500, 4)

    elif stat == "bets_placed":
      user_data[stat] += 1
      if user_data[stat] == 5:
        await update_achievment(interaction, user_data, stat, 5, 1)
      if user_data[stat] == 15:
        await update_achievment(interaction, user_data, stat, 15, 2)
      if user_data[stat] == 25:
        await update_achievment(interaction, user_data, stat, 25, 3)
      if user_data[stat] == 50:
        await update_achievment(interaction, user_data, stat, 50, 4)

    save_json(user_data, interaction.user.name, "user")