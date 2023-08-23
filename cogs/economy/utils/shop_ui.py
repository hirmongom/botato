import discord

from utils.json import load_json, save_json
from .shop_funcs import process_purchase

shop_item_fields = [
  {"label": "Role name to display", "placeholder": "role name"},
  {"label": "Colour RGB values", "placeholder": "3 numbers (0-255) separated by non-digit character(s)"}
]

class ShopItemSelect(discord.ui.Select):
  def __init__(self, user_id: int, shop_items: list[dict], *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_id = user_id
    self.shop_items = shop_items

  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
        return # User not authorized

    item_id = int(self.values[0])
    economy_data = load_json(interaction.user.name, "economy")
       
    self.disabled = True
    await interaction.message.edit(view = None)

    if self.shop_items[item_id]["price"] > economy_data["hand_balance"]:
      await interaction.response.send_message("You do not have enough money in hand")
      return
    else:
      modal = FutureFormModal(title = f"{self.shop_items[item_id]['name']}",
                              economy_data = economy_data,
                              item = self.shop_items[item_id])
      modal.add_item(discord.ui.TextInput(label = shop_item_fields[item_id]["label"], 
                                          max_length = 64, 
                                          placeholder = shop_item_fields[item_id]["placeholder"]))
      await interaction.response.send_modal(modal)


class FutureFormModal(discord.ui.Modal):
  def __init__(self, title: str, economy_data: dict, item: dict) -> None:
    super().__init__(title = title)
    self.economy_data = economy_data
    self.item = item


  async def on_submit(self, interaction: discord.Interaction) -> None:
    form_value = str(self.children[0])

    user_data = load_json(interaction.user.name, "user")
    await process_purchase(user_data = user_data,
                          economy_data = self.economy_data,
                          item = self.item,
                          form_value = form_value,
                          interaction = interaction)