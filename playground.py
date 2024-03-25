from bs4 import BeautifulSoup
from pathlib import Path
from requests import get
from urllib.parse import quote


soup = BeautifulSoup(
    get(
        f"https://m2.mtmt.hu/gui2/?mode=search&query=publication;labelOrMtid;eq;{quote('First')}"
    ).text,
    "html.parser",
)


print(soup)
