import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

import logging
import datetime
import re


class WebScrapper():
  def __init__(self, logger: logging.Logger, browserPath: str) -> None:
    self.logger = logger
    self.options = Options()
    self.options.add_argument("--headless")
    self.options.binary_location = browserPath
    self.service = Service(executable_path = "./chromedriver/chromedriver")
    self.driver = webdriver.Chrome(service = self.service, options = self.options)
    self.logger.info("Started WebScrapper")


  def restart_driver(self) -> None:
    self.driver.quit()
    self.driver = webdriver.Chrome(service = self.service, options = self.options)
    self.logger.info("Restarted webdriver")


  def get_game_link(self, query: str) -> str:
    query = query.replace(" ", "+")
    query = f"https://clavecd.es/catalog/search-{query}"

    html = BeautifulSoup(requests.get(query).text, "lxml")
    try:
      link = html.find("li", class_ = "search-results-row").find("a").get("href")
    except AttributeError:
      raise Exception()

    return link


  def get_game_title(self, link: str) -> str:
    soup = BeautifulSoup(requests.get(link).text, "lxml")

    title = soup.find("div", class_ = "content-box-title").find("span", attrs = {"data-itemprop": "name"}).get_text()
    title = title.replace("\n", "").replace("\t", "")
    return title


  def get_game_keys(self, link: str) -> str:
    self.driver.get(link)
    html = self.driver.page_source

    soup = BeautifulSoup(html, "lxml")

    table = soup.find("div", id = "offers_table")
    keys = table.find_all("div", class_ = "offers-table-row x-offer")

    content = ""
    for i, key in enumerate(keys):
      if (i == 5 or i == len(keys)):
        break     
      info = "[ " + key.find("div", class_ = "x-offer-edition-region-names offers-infos d-block d-md-none").get_text(separator = " - ") + " ]"
      store = key.find("div", class_ = "x-offer-merchant-title offers-merchant text-truncate").get("title")
      price = key.find("div", class_ = "offers-table-row-cell buy-btn-cell").find("span").get_text()
      content += f"\n{info}    {price} {store}"
    return content


  def scrap_f1(self) -> str:
    now = datetime.datetime.now()

    url = f"https://pitwall.app/seasons/{now.year}-formula-1-world-championship"
    html = BeautifulSoup(requests.get(url).text, "lxml")
    sections = html.find_all("div", class_ = "section")

    # Find the table with the races and winners    
    table = None
    for section in sections:
      h3_element = section.find("h3", class_ = "block-title")
      if h3_element.get_text() == f"{now.year} schedule":
        table = section
        break

    # Get the race date column
    races = []
    html_dates = table.find_all("td", class_ = "nowrap")
    for date in html_dates:
      races.append(date.get_text())

    # Get the race name column
    html_names = table.find_all("td", class_ = "title")
    # Skip the class="minmd title" that it finds
    for i, k in zip(range(0, len(races), 1), range(0, len(html_names), 2)):
      races[i] += f" | {html_names[k].get_text(strip = True)}"

    # Get the race winner column
    pattern = re.compile(r'#\d+\s*(.*)')
    html_winners = table.find_all("td", class_ = "minmd title")
    for i, winner in enumerate(html_winners):
      driver_name = winner.get_text(strip = True)
      if  driver_name == "":
        break
      driver_name = pattern.match(driver_name).group(1)
      races[i] += f" -> {driver_name}"

    # Form response
    response = ""
    for race in races:
      response += race + "\n"

    return response