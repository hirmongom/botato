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
from discord.ext import commands

from .help_embeds import *


#***************************************************************************************************
class HelpHandlerSelect(discord.ui.Select):
	def __init__(self, user_id: int, bot_instance: commands.Bot, message = discord.Webhook, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		self.options = [
			discord.SelectOption(label = "👤 User", value = 0),
			discord.SelectOption(label = "💰 Economy", value = 1),
			discord.SelectOption(label = "🔑 Game Keys", value = 2),
			discord.SelectOption(label = "🎲 Bets", value = 3),
			discord.SelectOption(label = "🎰 Casino", value = 4),
			discord.SelectOption(label = "📚 Daily Problems", value = 5),
			discord.SelectOption(label = "👥 Multiplayer", value = 6),
			discord.SelectOption(label = "📦 Miscellaneous", value = 7)
		]
		self.placeholder = "Choose a category"

		self.user_id = user_id
		self.bot = bot_instance
		self.message = message
		self._view = discord.ui.View()


#***************************************************************************************************
	async def start(self) -> None:
		# Show main help embed
		embed = main_help_embed(self.bot)
		self._view.add_item(self)

		await self.message.edit(content = None, embed = embed, view = self._view)


#***************************************************************************************************
	async def callback(self, interaction: discord.Interaction) -> None:
		if interaction.user.id != self.user_id:
				return # User not authorized

		await interaction.response.defer()
		choice = int(self.values[0])

		# Show help embed based on choice
		if choice == 0:
			self.placeholder = "👤 User"
			embed = user_help_embed(self.bot)
		elif choice == 1:
			self.placeholder = "💰 Economy"
			embed = economy_help_embed(self.bot)
		elif choice == 2:
			self.placeholder = "🔑 Game Keys"
			embed = keys_help_embed(self.bot)
		elif choice == 3:
			self.placeholder = "🎲 Bets"
			embed = bets_help_embed(self.bot)
		elif choice == 4:
			self.placeholder = "🎰 Casino"
			embed = casino_help_embed(self.bot)
		elif choice == 5:
			self.placeholder = "📚 Daily Problems"
			embed = daily_problems_help_embed(self.bot)    
		elif choice == 6:
			self.placeholder = "👥 Multiplayer"
			embed = multiplayer_help_embed(self.bot)    
		elif choice == 7:
			self.placeholder = "📦 Miscellaneous"
			embed = misc_help_embed(self.bot)

		# Load new embed into message
		await self.message.edit(embed = embed, view = self.view)