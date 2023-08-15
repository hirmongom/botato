from util.json import loadJson, saveJson

def storeGame(user: str, title: str, link: str) -> None:
  data = loadJson(user, "keys")
  data[title] = link
  saveJson(data, user, "keys")


def getGameList(user: str) -> list[str]:
  data = loadJson(user, "keys")
  return list(data.keys())


def removeGames(user: str, games: list[str]) -> None:
  data = loadJson(user, "keys")
  for game in games:
    del data[game]
  saveJson(data, user, "keys")

def getFollowingSize(user: str) -> int:
  data = loadJson(user, "keys")
  return len(data.keys())