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

async def create_role(interaction: discord.Interaction) -> None:
  new_role = await interaction.guild.create_role(
      name = interaction.user.name,
      colour = discord.Colour.default(),
      hoist = False,
      reason = f"Role created by Botato for user: {interaction.user.name}"
  )

  user_data = load_json(interaction.user.name, "user")
  user_data["role_name"] = interaction.user.name
  save_json(user_data, interaction.user.name, "user")

  await interaction.user.add_roles(new_role)


async def fetch_role(role_id: int, interaction: discord.Interaction) -> discord.Role:
  return interaction.guild.get_role(role_id)


async def edit_role_name(user_data: dict, role_id: int, name: str, interaction: discord.Interaction) -> None:
  role = await fetch_role(role_id, interaction)
  await role.edit(name = name, hoist = True)
  
  user_data["role_name"] = name
  save_json(user_data, interaction.user.name, "user")


async def edit_role_colour(role_id: int, r: int, g: int, b: int, 
                          interaction: discord.Interaction) -> None:
  role = await fetch_role(role_id, interaction)
  await role.edit(colour = discord.Colour.from_rgb(r, g, b))


async def process_purchase(user_data: dict, economy_data: dict, item: dict, form_value: str, 
                          interaction: discord.Interaction) -> None:
  user_role_name = user_data["role_name"]
  all_roles = await interaction.guild.fetch_roles()
  user_role_id = next((role.id for role in all_roles if role.name == user_role_name), None)

  # Role Name purchase *****************************************************************************
  if item["id"] == 0:
    await edit_role_name(user_data, user_role_id, form_value, interaction)

  elif item["id"] == 1: # Name Colour purchase *****************************************************
    colour = []

    # Parse colour from form_value
    number = ""
    for char in form_value:
      if char.isdigit():
        number += char
      elif number:
        if int(number) > 255:
          await interaction.response.send_message("Invalid number, must be between 0 and 255")
          return
        colour.append(int(number))
        number = ""
    if number:
        colour.append(int(number))

    if len(colour) != 3:
      await interaction.response.send_message(f"An RGB colour is defined by 3 values, not {len(colour)}")
      return

    await edit_role_colour(user_role_id, colour[0], colour[1], colour[2], interaction)

  economy_data["hand_balance"] -= item["price"]
  save_json(economy_data, interaction.user.name, "economy")

  await interaction.response.send_message("Purchase completed")