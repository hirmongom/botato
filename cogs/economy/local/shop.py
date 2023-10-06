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
from discord.ext import commands

from utils.json import load_json, save_json
from utils.custom_ui import ModalSelectMenu, FutureModal


#***************************************************************************************************
shop_items = [ 
  { "emoji": "📛", 
    "name": "Role Name", 
    "description": "Create a personalized role with a name that sets you apart in the server.", 
    "price": 75900.00},
  { "emoji": "🎨", 
    "name": "Name Colour", 
    "description": "Add a splash of colour to your name in the server.", 
    "price": 49899.95}
]


#***************************************************************************************************
async def shop_handler(bot: commands.Bot, interaction: discord.Interaction) -> None:
  user_data = load_json(interaction.user.name, "user")
  if user_data["role_name"] == "":
    await create_role(interaction = interaction) # First interaction with the shop will create the custom role

  item_menu_choices = []

  embed = get_embed(bot = bot, choices = item_menu_choices)
  message = await interaction.followup.send(embed = embed)
  item, form_value = await get_purchase(interaction = interaction, message = message, embed = embed, 
                                        options = item_menu_choices)

  await process_purchase(interaction = interaction, item_id = item, form_value = form_value)
  await message.edit(embed = embed, view = None)


#***************************************************************************************************
def get_embed(bot: commands.Bot, choices: list[dict]) -> discord.Embed:
  embed = discord.Embed(
    title = "🏪 Botato Shop",
    description = "With the best prices for all products available in the server!",
    color = discord.Color.blue()
  )

  for item in shop_items:
    choices.append(item["name"])

    embed.add_field(name = "", value = f"```{item['emoji']} {item['name']}```")
    embed.add_field(name = f"💶 {item['price']}€", value = item["description"], inline = False)

  embed.add_field(name = "", value = "", inline = False) # Pre-footer separator
  embed.set_footer(text = "Cheap Shopping | Botato Shop", icon_url = bot.user.display_avatar.url)

  return embed


#***************************************************************************************************
async def get_purchase(interaction: discord.Interaction, message: discord.Message, 
                      embed: discord.Embed, options: list[str]) -> (int, str):
  view = discord.ui.View()
  form_value_future = asyncio.Future()
  item_future = asyncio.Future()

  role_name_modal = FutureModal(future = form_value_future, label = "Role Name", 
                              placeholder = "role", title = "Enter your Role Name")
  role_colour_modal = FutureModal(future = form_value_future, label = "Role Colour", 
                              placeholder = "3 numbers (0-255) separated by non-digit character(s)", 
                              title = "Enter your Role Colour")

  item_menu = ModalSelectMenu(user_id = interaction.user.id, future = item_future, 
                              options = options, modals = [role_name_modal, role_colour_modal], 
                              placeholder = "Purchase an Item")

  view.add_item(item_menu)
  await message.edit(embed = embed, view = view)

  item = await item_future
  form_value = await form_value_future

  return (item, form_value)


#***************************************************************************************************
async def process_purchase(interaction: discord.Interaction, item_id: int, form_value: str) -> None:
  user_data = load_json(interaction.user.name, "user")
  economy_data = load_json(interaction.user.name, "economy")
  item = shop_items[item_id]

  user_role_name = user_data["role_name"]
  all_roles = await interaction.guild.fetch_roles()
  user_role_id = next((role.id for role in all_roles if role.name == user_role_name), None)

  # Role Name purchase
  if item_id == 0:
    await edit_role_name(interaction = interaction, user_data = user_data, 
                          role_id = user_role_id, name = form_value)

  # Name Colour purchase
  elif item_id == 1: 
    colour = []

    # Parse colour from form_value
    rgb = parse_colour(colour_str = form_value)
    if len(rgb) != 3:
      await interaction.followup.send("An RGB colour is defined by 3 values, "
                                              f"not {len(rgb)}", ephemeral = True)
      return

    if -1 in rgb:
      await interaction.followup.send(f"<@{interaction.user.id}> Invalid number, must be "
                                      "between 0 and 255", ephemeral = True)
      return

    await edit_role_colour(interaction = interaction, role_id = user_role_id, 
                            r = rgb[0], g = rgb[1], b = rgb[2])

  economy_data["hand_balance"] -= item["price"]
  save_json(economy_data, interaction.user.name, "economy")

  await interaction.followup.send(f"<@{interaction.user.id}> Purchase completed")


#***************************************************************************************************
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


#***************************************************************************************************
async def fetch_role(interaction: discord.Interaction, role_id: int) -> discord.Role:
  return interaction.guild.get_role(role_id)


#***************************************************************************************************
async def edit_role_name(interaction: discord.Interaction, user_data: dict, role_id: int, 
                        name: str) -> None:
  role = await fetch_role(interaction = interaction, role_id = role_id)
  await role.edit(name = name, hoist = True)
  
  user_data["role_name"] = name
  save_json(user_data, interaction.user.name, "user")


#***************************************************************************************************
async def edit_role_colour(interaction: discord.Interaction, role_id: int, 
                          r: int, g: int, b: int) -> None:
  role = await fetch_role(interaction = interaction, role_id = role_id)
  await role.edit(colour = discord.Colour.from_rgb(r, g, b))


#***************************************************************************************************
def parse_colour(colour_str: str) -> list[int]:
  number = ""
  colour = []

  for char in colour_str:
    if char.isdigit():
      number += char
    elif number:
      if int(number) > 255:
        return [-1, -1, -1]
      colour.append(int(number))
      number = ""
  if number:
      colour.append(int(number))
  print(colour)
  return colour