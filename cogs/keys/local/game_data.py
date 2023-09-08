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