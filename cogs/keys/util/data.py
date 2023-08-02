from util.json import loadJson, saveJson

def storeGame(user: str, title: str, link: str) -> None:
  data = loadJson(user)
  data[title] = link
  saveJson(data, user)


def getGameList(user: str) -> list[str]:
  data = loadJson(user)
  return list(data.keys())


def removeGames(user: str, games: list[str]) -> None:
  data = loadJson(user)
  for game in games:
    del data[game]
  saveJson(data, user)