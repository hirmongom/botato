import os
import json

def storeKey(user: str, title: str, link: str):
    data = {}
    filePath = f"data/{user}.json"
    
    if os.path.isfile(filePath):
        with open(filePath, "r") as file:
            data = json.load(file)

    data[title] = link

    with open(filePath, "w") as file:
        json.dump(data, file)