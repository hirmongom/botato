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


import random
import discord
from utils.json import load_json, save_json
from utils.achievement import add_user_stat


#***************************************************************************************************
async def economy_on_interaction(interaction: discord.Interaction) -> None:
  # First user interaction yields money
  economy_data = load_json(interaction.user.name, "economy")
  user_data = load_json(interaction.user.name, "user")

  if economy_data["daily_pay"] == 1:
    await add_user_stat("days_interacted", interaction) # First interaction of the day
    if economy_data["streak"] == 7:
      lower_bound = user_data["level"] * 100 + 1000
      upper_bound = user_data["level"] * 100 + 1500
      economy_data["streak"] = 0
    else:
      lower_bound = user_data["level"] * 10 + 200
      upper_bound = user_data["level"] * 10 + 250
    increase = round(random.uniform(lower_bound, upper_bound), 2)
    economy_data["bank_balance"] += increase
    economy_data["daily_pay"] = 0

    streak_msg = ""
    if economy_data["streak"] != 0:
      streak_msg = f" (Current streak = {economy_data['streak']} days)" 
      
    await interaction.channel.send(f"(*) You received {increase}€ on your bank{streak_msg}")

  save_json(economy_data, interaction.user.name, "economy")


#***************************************************************************************************
async def user_on_interaction(interaction: discord.Interaction) -> None:
  user_data = load_json(interaction.user.name, "user")
  
  if user_data["daily_xp"] > 0:
    if random.randint(1, 100) <= user_data["xp_probabiliy"]:
      increase = random.randint(20, 50)
      user_data["experience"] += increase
      await interaction.channel.send(f"(*) You received {increase} XP")

      if user_data["experience"] >= (user_data["level"] * 100 + (user_data["level"] - 1) * 50):
        user_data["level"] += 1
        await interaction.channel.send(f"(*) You leveled up to level {user_data['level']}!!")

      user_data["xp_probabiliy"] = 5
      user_data["daily_xp"] -= 1  
      
    else:
      if user_data["xp_probabiliy"] < 75:
        user_data["xp_probabiliy"] += 5
    
  save_json(user_data, interaction.user.name, "user")