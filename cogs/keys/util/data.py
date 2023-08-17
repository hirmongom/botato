from util.json import load_json, save_json

def storeGame(user: str, title: str, link: str) -> None:
  data = load_json(user, "keys")
  data[title] = link
  save_json(data, user, "keys")


def getGameList(user: str) -> list[str]:
  data = load_json(user, "keys")
  return list(data.keys())


def removeGames(user: str, games: list[str]) -> None:
  data = load_json(user, "keys")
  for game in games:
    del data[game]
  save_json(data, user, "keys")

def getFollowingSize(user: str) -> int:
  data = load_json(user, "keys")
  return len(data.keys())