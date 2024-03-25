from bs4 import BeautifulSoup
from pathlib import Path
from requests import get
from urllib.parse import quote
import PyPDF2
from bs4 import BeautifulSoup
from pathlib import Path
from requests import get
from urllib.parse import quote
import PyPDF2


# Open the PDF file
pdf_path = "/home/dan/Projects/Gigs/gradus_scraping/2023_2_ECO_002_Kasznar (1).pdf"
with open(pdf_path, "rb") as file:
    # Create a PDF reader object
    pdf_reader = PyPDF2.PdfReader(file)

    # Get the first page of the PDF
    first_page = pdf_reader.pages[0]

    # Extract the text from the first page and remove leading/trailing whitespace
    text = first_page.extract_text()

    print(text.split("\n"))
