from math import e
from bs4 import BeautifulSoup
from utils import get

GRADUS_LINK = "https://gradus.kefo.hu/archive/"
MTMT_LINK = "https://m2.mtmt.hu/gui2/?mode=search&query=publication;labelOrMtid;eq;"


# Data
data_json = []


gradus_soup = BeautifulSoup(get(GRADUS_LINK).text, "html.parser")


# Get issues div
issues_tag = gradus_soup.find("div", id="issues")
year_tags = gradus_soup.select('div[style="float: left; width: 100%;"]')


articles_number = 0

for year_tag in year_tags:

    # Get publication year
    publication_year = year_tag.find("h3", recursive=False).text.strip()

    for volume_info_tag in year_tag.find_all("a"):
        # Split text
        volume_info = volume_info_tag.text.split(":")[0].split("(")[0]
        # Remove unwanted substrings
        volume_info = (
            volume_info.replace("Vol ", "").replace("No ", "").replace(" ", "")
        )

        volume, number = volume_info.split(",")

        # Get volume catalog tag
        volume_catalog_link = GRADUS_LINK + volume_info_tag["href"]
        volume_catalog_soup = BeautifulSoup(
            get(volume_catalog_link).text, "html.parser"
        )
        volume_catalog = volume_catalog_soup.find("div", id="content")

        section = ""

        # Get articles
        for catalog_item in list(
            volume_catalog.select(
                "div#content > .tocSectionTitle, div#content > .tocArticle"
            )
        ):
            if catalog_item.attrs.get("class") == ["tocSectionTitle"]:
                section = catalog_item.text.strip()

            else:
                article_title = catalog_item.find(class_="tocTitle").text
                articles_number += 1
                print(articles_number, ":", article_title, end="\r")
