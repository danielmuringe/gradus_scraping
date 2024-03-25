from urllib.parse import quote
from bs4 import BeautifulSoup
from utils import *


GRADUS_LINK = "https://gradus.kefo.hu/archive/"
MTMT_LINK = "https://m2.mtmt.hu/gui2/?mode=search&query=publication;labelOrMtid;eq;"


# Data
data_json = []


GRADUS_SOUP = BeautifulSoup(get(GRADUS_LINK).text, "html.parser")

PDF_PATH = Path(__file__).parent / "pdf_articles"


# Get issues div
issues_tag = GRADUS_SOUP.find("div", id="issues")
year_tags = GRADUS_SOUP.select('div[style="float: left; width: 100%;"]')


for year_tag in year_tags:

    # Get publication year
    pub_year = year_tag.find("h3", recursive=False).text.strip()

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
                # Get article name
                article_name = catalog_item.find("a")["href"]

                # Download article pdf
                pdf_link = f"{volume_catalog_link}/{article_name}"
                download_pdf(
                    pdf_link,
                    PDF_PATH / f"{pub_year}/{volume}/{number}/{section}/{article_name}",
                )

                article_title = catalog_item.find(class_="tocTitle").text

                authors, doi_link = (
                    catalog_item.find(class_="tocAuthors").text.strip().split("\n")
                )

                authors = authors.strip().split(",")

                doi_link = doi_link
                doi_link_works: bool = False

                try:
                    doi_link_works = get(doi_link).status_code == 200
                except HTTPError as http_error:
                    pass

                mtmt_page_link = f"{MTMT_LINK}{quote(article_title)}"
                mtmt_soup = BeautifulSoup(get(mtmt_page_link).text, "html.parser")

                mtmt_search_tag = mtmt_soup.find(
                    "li",
                    class_="list-item ui-widget-content publication not-selected opened",
                )

                data_json.append(
                    {
                        "Publication Year": pub_year,
                        "Volume": volume,
                        "Number": number,
                        "Section": section,
                        "Article PDF Name": article_name.split(".")[0].strip(),
                        "Original Article Title": article_title,
                        "English Article Title": (article_title),
                        "Authors": authors,
                        "DOI Link": doi_link,
                        "DOI Link Works": doi_link_works,
                        "MTMT Link": doi_link,
                        "MTMT Link Works": doi_link_works,
                    }
                )

                print(article_name.split(".")[0].strip())
                print(pdf_link)
                # print(mtmt_search_tag)
                # print(mtmt_soup)
