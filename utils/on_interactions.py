import random
import discord
from utils.json import load_json, save_json
from utils.funcs import add_user_stat

async def economy_on_interaction(interaction: discord.Interaction) -> None:
  economy_data = load_json(interaction.user.name, "economy")
  user_data = load_json(interaction.user.name, "user")
  daily_pay = economy_data["daily_pay"]

  if daily_pay == 1:
    await add_user_stat("days_interacted", interaction)
    if economy_data["streak"] == 7:
      lower_bound = user_data["level"] * 100 + 1000
      upper_bound = user_data["level"] * 100 + 1500
      economy_data["streak"] = 0
    else:
      lower_bound = user_data["level"] * 10 + 200
      upper_bound = user_data["level"] * 10 + 250
    increase = round(random.uniform(lower_bound, upper_bound), 2)
    economy_data["bank_balance"] = economy_data["bank_balance"] + increase
    economy_data["daily_pay"] = 0

    streak_msg = f" (Current streak = {economy_data['streak']} days)" if int(economy_data["streak"]) != 0 else ""
    await interaction.channel.send(f"(*) You received {increase}€ on your bank{streak_msg}")

  save_json(economy_data, interaction.user.name, "economy")


async def user_on_interaction(interaction: discord.Interaction) -> None:
  data = load_json(interaction.user.name, "user")
  level = data["level"]
  experience = data["experience"]
  xp_probabiliy = data["xp_probabiliy"]
  daily_xp = data["daily_xp"]
  
  if daily_xp > 0:
    if random.randint(1, 100) <= xp_probabiliy:
      increase = random.randint(20, 50)
      experience += increase
      await interaction.channel.send(f"(*) You received {increase} XP")

      if experience >= (level * 100 + (level - 1) * 50):
        level += 1
        data["level"] = level
        await interaction.channel.send(f"(*) You leveled up to level {level}!!")

      data["experience"] = experience
      data["xp_probabiliy"] = 5
      data["daily_xp"] = data["daily_xp"] - 1  
      
    else:
      if xp_probabiliy < 75:
        xp_probabiliy += 2
        data["xp_probabiliy"] = xp_probabiliy
    
  save_json(data, interaction.user.name, "user")