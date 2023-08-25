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

import os
import json

def load_json(sub_path: str, cog: str) -> dict[str, str]:
  data = {}
  filePath = f"data/{cog}/{sub_path}.json"
  
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
  
def save_json(data: dict[str, str], sub_path: str, cog: str) -> None:
  filePath = f"data/{cog}/{sub_path}.json"

  with open(filePath, "w") as file:
    json.dump(data, file)