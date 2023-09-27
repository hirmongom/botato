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


lock = asyncio.Lock()


#***************************************************************************************************
async def update_achievement(interaction: discord.Interaction, achievement_data: dict, 
                            user_data: dict, stat: str, value: int, tier: int) -> None:
  map_stat_name = {
    "days_interacted": "Days Engaged",
    "command_count": "Commands Executed",
    "gamekeys_searched": "Game Key Queries",
    "blackjack_hands_played": "Blackjack Rounds Played",
    "blackjack_hands_won": "Blackjack Rounds Victorious",
    "roulettes_played": "Roulette Rounds Played",
    "roulettes_won": "Roulette Rounds Victorious",
    "races_played": "Race Bets Made",
    "races_won": "Successful Race Bets",
    "bets_placed": "Total Bets Made",
    "completed_daily_problems": "Total Daily Problems Solved"
  }

  if tier == 1:
    achievement_data["achievements"].append({stat: value, "tier": tier})
  else:
    for achievement in achievement_data["achievements"]:
      if stat in achievement:
        achievement[stat] = value
        achievement["tier"] = tier
        break

  xp_increase = tier * 100
  user_data["experience"] += xp_increase

  await interaction.followup.send(f"You unlocked the achievement {value} {map_stat_name[stat]} "
                                  f"and received {xp_increase} XP!")
  if user_data["experience"] >= (user_data["level"] * 100 + (user_data["level"] - 1) * 50):
    user_data["level"] += 1
    await interaction.followup.send(f"(*) You leveled up to level {user_data['level']}!!")


#***************************************************************************************************
async def add_user_stat(stat: str, interaction: discord.Interaction) -> None:
  async with lock:
    achievement_data = load_json(interaction.user.name, "achievement")
    user_data = load_json(interaction.user.name, "user")
    achievement_data[stat] += 1

    if stat == "days_interacted":
      if achievement_data[stat] == 10:
        await update_achievement(interaction, achievement_data, user_data, stat, 10, 1)
      if achievement_data[stat] == 25:
        await update_achievement(interaction, achievement_data, user_data, stat, 25, 2)
      if achievement_data[stat] == 50:
        await update_achievement(interaction, achievement_data, user_data, stat, 50, 3)
      if achievement_data[stat] == 100:
        await update_achievement(interaction, achievement_data, user_data, stat, 100, 4)

    if stat == "command_count":
      if achievement_data[stat] == 100:
        await update_achievement(interaction, achievement_data, user_data, stat, 100, 1)
      if achievement_data[stat] == 250:
        await update_achievement(interaction, achievement_data, user_data, stat, 250, 2)
      if achievement_data[stat] == 500:
        await update_achievement(interaction, achievement_data, user_data, stat, 500, 3)
      if achievement_data[stat] == 1000:
        await update_achievement(interaction, achievement_data, user_data, stat, 1000, 4)

    elif stat == "gamekeys_searched":
      if achievement_data[stat] == 10:
        await update_achievement(interaction, achievement_data, user_data, stat, 10, 1)
      if achievement_data[stat] == 25:
        await update_achievement(interaction, achievement_data, user_data, stat, 25, 2)
      if achievement_data[stat] == 50:
        await update_achievement(interaction, achievement_data, user_data, stat, 50, 3)
      if achievement_data[stat] == 100:
        await update_achievement(interaction, achievement_data, user_data, stat, 100, 4)
    
    elif stat == "blackjack_hands_played":
      if achievement_data[stat] == 50:
        await update_achievement(interaction, achievement_data, user_data, stat, 50, 1)
      if achievement_data[stat] == 100:
        await update_achievement(interaction, achievement_data, user_data, stat, 100, 2)
      if achievement_data[stat] == 250:
        await update_achievement(interaction, achievement_data, user_data, stat, 250, 3)
      if achievement_data[stat] == 500:
        await update_achievement(interaction, achievement_data, user_data, stat, 500, 4)

    elif stat == "blackjack_hands_won":
      if achievement_data[stat] == 50:
        await update_achievement(interaction, achievement_data, user_data, stat, 50, 1)
      if achievement_data[stat] == 100:
        await update_achievement(interaction, achievement_data, user_data, stat, 100, 2)
      if achievement_data[stat] == 250:
        await update_achievement(interaction, achievement_data, user_data, stat, 250, 3)
      if achievement_data[stat] == 500:
        await update_achievement(interaction, achievement_data, user_data, stat, 500, 4)

    elif stat == "roulettes_played":
      if achievement_data[stat] == 50:
        await update_achievement(interaction, achievement_data, user_data, stat, 50, 1)
      if achievement_data[stat] == 100:
        await update_achievement(interaction, achievement_data, user_data, stat, 100, 2)
      if achievement_data[stat] == 250:
        await update_achievement(interaction, achievement_data, user_data, stat, 250, 3)
      if achievement_data[stat] == 500:
        await update_achievement(interaction, achievement_data, user_data, stat, 500, 4)

    elif stat == "roulettes_won":
      if achievement_data[stat] == 50:
        await update_achievement(interaction, achievement_data, user_data, stat, 50, 1)
      if achievement_data[stat] == 100:
        await update_achievement(interaction, achievement_data, user_data, stat, 100, 2)
      if achievement_data[stat] == 250:
        await update_achievement(interaction, achievement_data, user_data, stat, 250, 3)
      if achievement_data[stat] == 500:
        await update_achievement(interaction, achievement_data, user_data, stat, 500, 4)

    elif stat == "races_played":
      if achievement_data[stat] == 50:
        await update_achievement(interaction, achievement_data, user_data, stat, 50, 1)
      if achievement_data[stat] == 100:
        await update_achievement(interaction, achievement_data, user_data, stat, 100, 2)
      if achievement_data[stat] == 250:
        await update_achievement(interaction, achievement_data, user_data, stat, 250, 3)
      if achievement_data[stat] == 500:
        await update_achievement(interaction, achievement_data, user_data, stat, 500, 4)

    elif stat == "races_won":
      if achievement_data[stat] == 50:
        await update_achievement(interaction, achievement_data, user_data, stat, 50, 1)
      if achievement_data[stat] == 100:
        await update_achievement(interaction, achievement_data, user_data, stat, 100, 2)
      if achievement_data[stat] == 250:
        await update_achievement(interaction, achievement_data, user_data, stat, 250, 3)
      if achievement_data[stat] == 500:
        await update_achievement(interaction, achievement_data, user_data, stat, 500, 4)

    elif stat == "bets_placed":
      if achievement_data[stat] == 5:
        await update_achievement(interaction, achievement_data, user_data, stat, 5, 1)
      if achievement_data[stat] == 15:
        await update_achievement(interaction, achievement_data, user_data, stat, 15, 2)
      if achievement_data[stat] == 25:
        await update_achievement(interaction, achievement_data, user_data, stat, 25, 3)
      if achievement_data[stat] == 50:
        await update_achievement(interaction, achievement_data, user_data, stat, 50, 4)

    elif stat == "completed_daily_problems":
      if achievement_data[stat] == 5:
        await update_achievement(interaction, achievement_data, user_data, stat, 5, 1)
      if achievement_data[stat] == 15:
        await update_achievement(interaction, achievement_data, user_data, stat, 15, 2)
      if achievement_data[stat] == 25:
        await update_achievement(interaction, achievement_data, user_data, stat, 25, 3)
      if achievement_data[stat] == 50:
        await update_achievement(interaction, achievement_data, user_data, stat, 50, 4)

    save_json(achievement_data, interaction.user.name, "achievement")
    save_json(user_data, interaction.user.name, "user")