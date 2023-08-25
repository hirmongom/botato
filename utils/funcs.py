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

from utils.json import load_json, save_json

def make_data(user: str) -> None:
  user_data = {}
  user_data["level"] = 1
  user_data["experience"] = 0
  user_data["xp_probabiliy"] = 5
  user_data["daily_xp"] = 5
  user_data["user_description"] = ""
  user_data["role_name"] = ""
  save_json(user_data, user, "user")

  economy_data = {}
  economy_data["hand_balance"] = 0
  economy_data["bank_balance"] = 100
  economy_data["daily_pay"] = 1
  economy_data["max_withdrawal"] = 2500
  economy_data["withdrawn_money"] = 0
  economy_data["bank_upgrade"] = 0
  economy_data["interest_rate"] = 1
  economy_data["streak"] = 1
  save_json(economy_data, user, "economy")

def make_casino_data(user: str):
  casino_data = {}
  casino_data["blackjack_hands_played"] = 0
  casino_data["blackjack_hands_won"] = 0
  casino_data["total_blackjack_winnings"] = 0
  casino_data["total_casino_winnings"] = 0
  save_json(casino_data, user, "casino")


def save_user_id(user_name: str, user_id: int) -> None:
  user_ids = load_json("user_ids", "other")
  user_ids[user_name] = user_id
  save_json(user_ids, "user_ids", "other")