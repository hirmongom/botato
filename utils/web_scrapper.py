import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

import logging
import datetime
import re
import csv

from utils.json import save_json


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


  def get_f1_data(self) -> None:
    month_mapping = {
      'Jan': 1,
      'Feb': 2,
      'Mar': 3,
      'Apr': 4,
      'May': 5,
      'Jun': 6,
      'Jul': 7,
      'Aug': 8,
      'Sep': 9,
      'Oct': 10,
      'Nov': 11,
      'Dec': 12
    }
    now = datetime.datetime.now()

    url = f"https://pitwall.app/seasons/{now.year}-formula-1-world-championship"
    html = BeautifulSoup(requests.get(url).text, "lxml")
    sections = html.find_all("div", class_ = "section")

    days = []
    months = []
    races = []
    winners = []    

    # Find the table with the races and winners    
    table = None
    for section in sections:
      h3_element = section.find("h3", class_ = "block-title")
      if h3_element.get_text() == f"{now.year} schedule":
        table = section
        break

    # Get the race date column
    html_dates = table.find_all("td", class_ = "nowrap")
    for date in html_dates:
      split_date = date.get_text().split(" ")
      days.append(re.findall(r"\d+", split_date[1])[0])
      months.append(str(month_mapping[split_date[0]]))

    # Get the race name column
    html_names = table.find_all("td", class_ = "title")
    # Skip the class="minmd title" that it finds
    for i in range(0, len(html_names), 2):
      races.append(html_names[i].get_text(strip = True))

    # Get the race winner column
    pattern = re.compile(r'#\d+\s*(.*)')
    html_winners = table.find_all("td", class_ = "minmd title")
    for winner in html_winners:
      driver_name = winner.get_text(strip = True)
      winners.append(pattern.match(driver_name).group(1) if driver_name != "" else "")

    data = []
    for i in range(len(days)):
      entry = {
        "ix": i,
        "day": days[i],
        "month": months[i],
        "event": races[i],
        "winner": winners[i]
      }
      data.append(entry)

    with open("data/bets/f1/f1_data.csv", mode = "w", newline = "") as file:
      fieldnames = ["ix", "day", "month", "event", "winner"]
      writer = csv.DictWriter(file, fieldnames = fieldnames)

      writer.writeheader()

      for entry in data:
        writer.writerow(entry)
  

  def get_f1_pilots(self) -> None:
    now = datetime.datetime.now()

    url = f"https://pitwall.app/seasons/{now.year}-formula-1-world-championship"
    html = BeautifulSoup(requests.get(url).text, "lxml")
    sections = html.find_all("div", class_ = "section")

    pilots_dir = {}
    for section in sections:
      h3_element = section.find("h3", class_ = "block-title")
      if h3_element.get_text() == f"{now.year} standings":
        pilots = section.find_all("td", class_ = "title")
        for html_pilot in pilots:
          pilot = html_pilot.get_text(strip = True)
          if pilot[0] == "#":
            match = re.match(r"#(\d+)(\D+)", pilot)
            if match:
              number, name = match.groups()
              pilots_dir[number] = name
              save_json(pilots_dir, "f1/f1_choices", "bets")