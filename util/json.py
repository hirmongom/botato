import os
import json

def load_json(user: str, cog: str) -> dict[str, str]:
  data = {}
  filePath = f"data/{cog}/{user}.json"
  
  if not os.path.isfile(filePath):
    with open(filePath, "w") as file:
      json.dump(data, file)
      file.close()
          
  with open(filePath, "r") as file:
    try:
      data = json.load(file)
    except json.decoder.JSONDecodeError:
      data = {}

  return data
  
def save_json(data: dict[str, str], user: str, cog: str) -> None:
  filePath = f"data/{cog}/{user}.json"

  with open(filePath, "w") as file:
    json.dump(data, file)