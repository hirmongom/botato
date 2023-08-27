import discord
from discord.ext import commands


class HelpHandlerSelect(discord.ui.Select):
  def __init__(self, user_id: int, bot_instance: commands.Bot, message = discord.Webhook, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.options = [
      discord.SelectOption(label = "👤 User", value = 0),
      discord.SelectOption(label = "💰 Economy", value = 1),
      discord.SelectOption(label = "🔑 Game Keys", value = 2),
      discord.SelectOption(label = "🎲 Bets", value = 3),
      discord.SelectOption(label = "🎰 Casino", value = 4),
      discord.SelectOption(label = "📦 Miscellaneous", value = 5)
    ]
    self.placeholder = "Choose a category"

    self.user_id = user_id
    self.bot = bot_instance
    self.message = message
    self._view = discord.ui.View()


  async def start(self) -> None:
    embed = self.main_help_embed()
    self._view.add_item(self)

    await self.message.edit(content = None, embed = embed, view = self._view)


  async def callback(self, interaction: discord.Interaction) -> None:
    if interaction.user.id != self.user_id:
        return # User not authorized

    await interaction.response.defer()
    choice = int(self.values[0])

    if choice == 0:
      self.placeholder = "👤 User"
      embed = self.user_help_embed()
    elif choice == 1:
      self.placeholder = "💰 Economy"
      embed = self.economy_help_embed()
    elif choice == 2:
      self.placeholder = "🔑 Game Keys"
      embed = self.keys_help_embed()
    elif choice == 3:
      self.placeholder = "🎲 Bets"
      embed = self.bets_help_embed()
    elif choice == 4:
      self.placeholder = "🎰 Casino"
      embed = self.casino_help_embed()
    elif choice == 5:
      self.placeholder = "📦 Miscellaneous"
      embed = self.misc_help_embed()

    await self.message.edit(embed = embed, view = self.view)


  def main_help_embed(self) -> discord.Embed:
    embed = discord.Embed(
      title = "📚 Bot Help",
      description = "Welcome to the help menu! Use the interface below to navigate through the bot's features.",
      color = discord.Color.light_embed()
    )

    embed.add_field(name = "```👤 User```", value = "Category related to user profiles, experience, and rankings.", inline = False)
    embed.add_field(name = "```💰 Economy```", value = "Category centered around managing your virtual finances within the server.", inline = False)
    embed.add_field(name = "```🔑 Game Keys```", value = "Category centered around tracking game key prices and receiving updates.", inline = False)
    embed.add_field(name = "```🎲 Bets```", value = "Category centered around placing bets on various events.", inline = False)
    embed.add_field(name = "```🎰 Casino```", value = "Category centered around testing your luck and increasing your virtual finances within the server.", inline = False)
    embed.add_field(name = "```📦 Miscellaneous```", value = "Category centered around various utility and fun commands.")
    embed.add_field(name = "", value = "```🔗 Source Code```", inline = False)
    embed.add_field(name = "", value = "[Click here](https://github.com/hmongom/botato)" 
                    " to view the bot's source code on GitHub.", inline = False)
    
    embed.add_field(name = "", value = "", inline = False) # Separator
    embed.set_footer(text = "Useful Assistance | Botato Help", icon_url = self.bot.user.display_avatar.url)

    return embed


  def user_help_embed(self) -> discord.Embed:
      embed = discord.Embed(
        title = "👤 User Category",
        description = "Category related to user profiles, experience, and rankings.",
        color = discord.Color.blue()
      )
      embed.add_field(
        name = "", value = "```📚 How Experience Works 📚```", inline = False
      )
      embed.add_field(
        name = "", 
        value = "- 🌱 **Earning XP:** Interacting with the bot rewards users with XP, which falls within a consistent range.\n"
                "- 📈 **Increasing XP Chances:** The more a user interacts with the bot, the higher their chances of earning XP with each interaction.\n"
                "- 🌞 **Daily XP Opportunities:** Every day, users have specific chances to earn XP, promoting daily engagement.\n"
                "- 📊 **Leveling Mechanics:** As users gather XP, they level up. Each new level requires more XP than the last, making progression challenging yet rewarding.\n"
                "- 🔓 **Benefits of Leveling:** Advanced levels unlock additional features across various bot categories, enhancing the user's experience and capabilities.",
        inline = False
      )

      embed.add_field(
        name = "", value = "```🛠️ Commands 🛠️```", inline = False
      )

      # Profile command
      embed.add_field(
        name = "👥 `/profile [mention]`",
        value = "View your own profile or, optionally, mention a user to check their profile.",
        inline = False
      )
      # Description command
      embed.add_field(
        name = "✏️ `/description [description]`",
        value = "Set a description to show in your profile. Max 64 characters.",
        inline = False
      )
      # Leaderboard command
      embed.add_field(
        name = "🏆 `/leaderboard [category]`",
        value = "Check the leaderboard across different categories.",
        inline = False
      )

      embed.add_field(name = "", value = "", inline = False) # Separator
      embed.set_footer(text = "Useful Assistance | Botato Help", icon_url = self.bot.user.display_avatar.url)

      return embed


  def economy_help_embed(self) -> discord.Embed:
    embed = discord.Embed(
      title = "💰 Economy Category",
      description = "Category centered around managing your virtual finances within the server.",
      color = discord.Color.green()
    )
    
    embed.add_field(
      name = "", value = "```📚 How the Economy Works 📚```", inline = False
    )
    embed.add_field(
      name = "", 
      value = "- 🌞 **Daily Interaction Bonus:** Each day, your first interaction with the bot grants you a variable amount of money influenced by your user level. Consistency pays off!\n"
              "- 🎉 **7-Day Streak Bonus:** Interacting with the bot for 7 consecutive days rewards you with a substantial bonus on your next economy yield.\n"
              "- 📈 **Level Advancements:** As you reach higher levels, you unlock the ability to upgrade your bank.\n"
              "- 💸 **Increased Withdrawal Limit:** Upgrading the bank boosts the maximum amount you can withdraw weekly.\n"
              "- 📊 **Interest Benefits:** With each upgrade, you either initiate or increase the interest rate. This means you earn a percentage of your saved money in the bank every week, passively boosting your balance.\n"
              "- 🔒 **Security:** There's a weekly withdrawal limit for security. Ensure you manage your finances wisely!",
      inline = False
    )
    
    embed.add_field(name = "", value = "```🛠️ Commands 🛠️```", inline = False)
    
    # Bank command
    embed.add_field(
      name = "🏦 `/bank`",
      value = "Check your account balance and perform operations.",
      inline = False
    )
    # Deposit command
    embed.add_field(
      name = "💹 `/deposit [amount]`",
      value = "Deposit a specified amount into your bank.",
      inline = False
    )
    # Withdraw command
    embed.add_field(
      name = "📤 `/withdraw [amount]`",
      value = "Withdraw a specified amount from your bank.",
      inline = False
    )
    # Transfer command
    embed.add_field(
      name = "🔄 `/transfer [amount] [mention]`",
      value = "Transfer a specified amount to another user's bank.",
      inline = False
    )
    # Shop command
    embed.add_field(
      name = "🏪 `/shop`",
      value = "View and purchase items available in the shop.",
      inline = False
    )
    
    embed.add_field(name = "", value = "", inline = False) # Separator
    embed.set_footer(text = "Useful Assistance | Botato Help", icon_url = self.bot.user.display_avatar.url)

    return embed

  
  def keys_help_embed(self) -> discord.Embed:
    embed = discord.Embed(
      title = "🔑 Game Keys Category",
      description = "Category centered around tracking game key prices and receiving updates.",
      color = discord.Color.gold()
    )

    embed.add_field(name = "", value = "```🛠️ Commands 🛠️```", inline = False)
    
    # Keys command
    embed.add_field(
      name = "🔍 `/keys [query]`",
      value = "Search for a game on clavecd.es and get the first 5 prices.",
      inline = False
    )
    # Follow command
    embed.add_field(
      name = "📌 `/follow [game]`",
      value = "Follow a game to easily check key prices.",
      inline = False
    )
    # List command
    embed.add_field(
      name = "📋 `/list`",
      value = "List all games you are following.",
      inline = False
    )
    # Unfollow command
    embed.add_field(
      name = "❌ `/unfollow`",
      value = "Remove one or multiple games from your following list.",
      inline = False
    )
    # Update command
    embed.add_field(
      name = "🔄 `/update`",
      value = "Get the key prices for all the games on your following list.",
      inline = False
    )
    # Autoupdate command
    embed.add_field(
      name = "⏰ `/autoupdate_keys [option]`",
      value = "Enable or disable the weekly autoupdate keys function.",
      inline = False
    )
    
    embed.add_field(name = "", value = "", inline = False) # Separator
    embed.set_footer(text = "Useful Assistance | Botato Help", icon_url = self.bot.user.display_avatar.url)

    return embed


  def bets_help_embed(self) -> discord.Embed:
    embed = discord.Embed(
      title = "🎲 Bets Category",
      description = "Category centered around placing bets on various events.",
      color = discord.Color.fuchsia()
    )
    
    embed.add_field(name = "", value = "```🛠️ Commands 🛠️```", inline = False)
    
    # Bet command
    embed.add_field(
      name = "🎫 `/bet`",
      value = "Check ongoing events and place bets on them.",
      inline = False
    )
    # Create Event command
    embed.add_field(
      name = "📅 `/create_event [day] [month] [year]`",
      value = "(ADMIN) Create a custom event for users to bet on.",
      inline = False
    )
    # Close Event command
    embed.add_field(
      name = "🏁 `/close_event`",
      value = "(ADMIN) Set the winner and close a custom-made bet.",
      inline = False
    )

    embed.add_field(name = "", value = "", inline = False) # Separator
    embed.set_footer(text = "Useful Assistance | Botato Help", icon_url = self.bot.user.display_avatar.url)

    return embed


  def casino_help_embed(self) -> discord.Embed:
    embed = discord.Embed(
      title = "🎰 Casino Category",
      description = "Category centered around testing your luck and increasing your virtual finances within the server.",
      color = discord.Color.red()
    )

    embed.add_field(name = "", value = "```🛠️ Commands 🛠️```", inline = False)

    embed.add_field(
        name = "🃏 `/blackjack [bet amount]`",
        value = "Play blackjack and try to double your bet.",
        inline = False
    )
    embed.add_field(
        name = "🎰 `/roulette`",
        value = "Spin the roulette wheel and place your bet.",
        inline = False
    )
    
    embed.add_field(name = "", value = "", inline = False) # Separator
    embed.set_footer(text = "Useful Assistance | Botato Help", icon_url = self.bot.user.display_avatar.url)

    return embed
    

  def misc_help_embed(self) -> discord.Embed:
    embed = discord.Embed(
        title = "🔧 Miscellaneous Category",
        description = "Category centered around various utility and fun commands.",
        color = discord.Color.orange()
    )

    embed.add_field(name = "", value = "```🛠️ Commands 🛠️```", inline = False)

    embed.add_field(
        name = "🔗 `/git`",
        value = "Check my code in my GitHub repository.",
        inline = False
    )
    embed.add_field(
        name = "🎲 `/roll [rolls] [dice]`",
        value = "Roll a specific dice. You can specify the number of rolls and the type of dice.",
        inline = False
    )
    embed.add_field(
        name = "❓ `/help`",
        value = "Get help and information on the different functionalities provided by the bot.",
        inline = False
    )

    embed.add_field(name = "", value = "", inline = False) # Separator
    embed.set_footer(text = "Useful Assistance | Botato Help", icon_url = self.bot.user.display_avatar.url)

    return embed