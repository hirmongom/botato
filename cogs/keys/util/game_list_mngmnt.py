import os
import json

def loadJson(user: str) -> dict[str, str]:
    data = {}
    filePath = f"data/{user}.json"
    
    if os.path.isfile(filePath):
        with open(filePath, "r") as file:
            data = json.load(file)
    else:
        data = {}
        
    return data
    
def saveJson(data: dict[str, str], user: str) -> None:
    filePath = f"data/{user}.json"

    with open(filePath, "w") as file:
        json.dump(data, file)


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