import os
import json

def loadJson(user: str) -> dict[str, str]:
  data = {}
  filePath = f"data/keys/{user}.json"
  
  if not os.path.isfile(filePath):
    with open(filePath, "w") as file:
      file.close()
          
  with open(filePath, "r") as file:
    try:
      data = json.load(file)
    except json.decoder.JSONDecodeError:
      data = {}

  return data
  
def saveJson(data: dict[str, str], user: str) -> None:
  filePath = f"data/keys/{user}.json"

  with open(filePath, "w") as file:
    json.dump(data, file)