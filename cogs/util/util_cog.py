import os
from dotenv import load_dotenv

import discord
from discord import app_commands
from discord.ext import commands

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

load_dotenv()
browserPath = os.getenv('BROWSERPATH')

class Util(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name = "keys",
        description = "Queries for a game in clavecd.es and returns the first 5 prices")
    async def keys(self, interaction: discord.Interaction, query: str):
        print(f">> |keys| from {interaction.user.name}#{interaction.user.discriminator} with query |{query}|")
        query = query.replace(" ", "+")
        query = f"https://clavecd.es/catalog/search-{query}"

        html = BeautifulSoup(requests.get(query).text, "lxml")
        try:
            link = html.find("li", class_ = "search-results-row").find("a").get("href")
        except AttributeError:
            await interaction.response.send_message("No results found")
            return

        await interaction.response.defer()

        options = Options()
        options.add_argument("--headless")
        options.binary_location = browserPath
        service = Service(executable_path = "./chromedriver/chromedriver.exe")
        driver = webdriver.Chrome(service = service, options = options)

        #sometimes the command returns nothing, gotta add a wait for element
        driver.get(link)
        html = driver.page_source
        driver.quit()

        soup = BeautifulSoup(html, "lxml")

        title = soup.find("div", class_ = "content-box-title").find("span", attrs = {"data-itemprop": "name"}).get_text()
        title = title.replace("\n", "").replace("\t", "")

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

        await interaction.followup.send(f"{title}\n{query}\n{content}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Util(bot))