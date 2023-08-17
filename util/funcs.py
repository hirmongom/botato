from util.json import save_json

def make_data(user: str) -> None:
  user_data = {}
  user_data["level"] = 1
  user_data["experience"] = 0
  user_data["xp_probabiliy"] = 5
  user_data["daily_xp"] = 5
  user_data["user_description"] = ""
  save_json(user_data, user, "user")

  economy_data = {}
  economy_data["hand_balance"] = 0
  economy_data["bank_balance"] = 100
  economy_data["daily_pay"] = 1
  economy_data["max_withdrawal"] = 500
  economy_data["withdrawn_money"] = 0
  economy_data["bank_upgrade"] = 0
  save_json(economy_data, user, "economy")