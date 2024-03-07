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


import logging
import datetime
import re
import csv

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from utils.json import save_json


#***************************************************************************************************
class WebScrapper():
  def __init__(self, logger: logging.Logger, browserPath: str) -> None:
    self.logger = logger
    self.options = Options()
    self.options.add_argument("--headless")
    self.options.binary_location = str(browserPath)
    self.driver = webdriver.Chrome(options = self.options)
    self.logger.info("Started WebScrapper")


#***************************************************************************************************
  def restart_driver(self) -> None:
    self.driver.quit()
    self.driver = webdriver.Chrome(service = self.service, options = self.options)
    self.logger.info("Restarted webdriver")


#***************************************************************************************************
  def get_game_link(self, query: str) -> str:
    query = query.replace(" ", "+")
    query = f"https://clavecd.es/catalog/search-{query}"

    html = BeautifulSoup(requests.get(query).text, "lxml")
    try:
      link = html.find("li", class_ = "search-results-row").find("a").get("href")
    except AttributeError:
      raise Exception()

    return link


#***************************************************************************************************
  def get_game_title(self, link: str) -> str:
    soup = BeautifulSoup(requests.get(link).text, "lxml")

    title = soup.find("div", class_ = "content-box-title").find("span", attrs = {"data-itemprop": "name"}).get_text()
    title = title.replace("\n", "").replace("\t", "")
    return title


#***************************************************************************************************
  def get_game_keys(self, link: str) -> list[str]:
    self.driver.get(link)
    html = self.driver.page_source

    soup = BeautifulSoup(html, "lxml")

    table = soup.find("div", id = "offers_table")
    keys = table.find_all("div", class_ = "offers-table-row x-offer")

    keys_list = []
    for i, key in enumerate(keys):
      if (i == 5 or i == len(keys)):
        break     
      info = "[ " + key.find("div", class_ = "x-offer-edition-region-names offers-infos d-block d-md-none").get_text(separator = " - ") + " ]"
      store = key.find("div", class_ = "x-offer-merchant-title offers-merchant text-truncate").get("title")
      price = key.find("div", class_ = "offers-table-row-cell buy-btn-cell").find("span").get_text()
      keys_list.append(f"\n{info}    {price} {store}")
    return keys_list