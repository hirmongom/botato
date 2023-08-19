from utils.json import load_json, save_json

def store_game(user: str, title: str, link: str) -> None:
  data = load_json(user, "keys")
  data[title] = link
  save_json(data, user, "keys")


def get_game_list(user: str) -> list[str]:
  data = load_json(user, "keys")
  return list(data.keys())


def remove_games(user: str, games: list[str]) -> None:
  data = load_json(user, "keys")
  for game in games:
    del data[game]
  save_json(data, user, "keys")

def get_following_list_size(user: str) -> int:
  data = load_json(user, "keys")
  return len(data.keys())