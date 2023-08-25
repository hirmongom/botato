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
import argparse


from utils.json import load_json, save_json

valid_cog_names = ["economy", "user", "casino"]

parser = argparse.ArgumentParser()
parser.add_argument("--cog", required = True, choices = valid_cog_names, help = "Cog where you want to add a field to its data")
parser.add_argument("--field", required = True, type = str, help = "Field you want to add")
parser.add_argument("--data", required = True,  help = "Data used to fill the field")
args = parser.parse_args()

if args.data.isdigit():
  default = int(args.data)
else:
  default = args.data

for file in os.listdir(f"data/{args.cog}"):
  if file !=  ".gitkeep":
    file = file[:-5]
    print(f"Filling {args.cog}/{file}.json with data[{args.field}] = {default}")
    data = load_json(file, args.cog)
    data[args.field] = default
    save_json(data, file, args.cog)

print("Operation complete")