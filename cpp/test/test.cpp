/* @copyright   This file is part of the "Botato" project.
 * 
 *              Every file is free software: you can redistribute it and/or modify
 *              it under the terms of the GNU General Public License as published by
 *              the Free Software Foundation, either version 3 of the License, or
 *              (at your option) any later version.
 * 
 *              These files are distributed in the hope that they will be useful,
 *              but WITHOUT ANY WARRANTY; without even the implied warranty of
 *              MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 *              GNU General Public License for more details.
 * 
 *              You should have received a copy of the GNU General Public License
 *              along with the "Botato" project. If not, see <http://www.gnu.org/licenses/>.
 */

#include <iostream>
#include <string>

extern "C" {
const char* hello_cpp() {
  return "Hello, from C++";
}
}