from pathlib import Path
import PyPDF2
from googletrans import Translator
from requests import RequestException, get as request_get
from requests import HTTPError


def get(url, stream_=False):
    response = request_get(url, stream=stream_)
    response.raise_for_status()
    return response


def translate(text):
    translator = Translator()
    detected_language = translator.detect(text).lang

    if detected_language != "en":  # Check if language is not English
        translated_text = translator.translate(text, dest="en").text
        return translated_text
    else:
        return text


def get_num_pages(pdf_path):
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfFileReader(file)
            num_pages = reader.numPages
            return num_pages
    except FileNotFoundError:
        print(f"File {pdf_path} not found.")
        return None


def download_pdf(url, folder_path):
    try:
        # Create the folder if it doesn't exist
        folder_path = Path(folder_path)
        folder_path.parent.mkdir(
            parents=True, exist_ok=True
        )  # Create parent directories if needed

        # Get the filename from the URL (consider using urllib.parse for complex URLs)
        filename = Path(url).name

        # Check if the file already exists
        filepath = folder_path.parent / filename
        if filepath.exists():
            print(f"PDF already exists: {filepath}")
            return False

        # Download the file
        print(url)
        response = get(url, stream_=True)
        response.raise_for_status()  # Raise an exception for unsuccessful download

        # Save the file
        with filepath.open("wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        print(f"PDF downloaded successfully: {filepath}")
        return True

    except RequestException as e:
        print(f"Error downloading PDF: {e}")
        return False


def is_valid_text(text):
    allowed_chars = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZűőúöóÖŐÚŰEgyed "
    )
    return all(char in allowed_chars for char in text)
