from pathlib import Path
import PyPDF2
from googletrans import Translator
from requests import RequestException, get as request_get
from requests import HTTPError
from time import sleep


def get(url, stream_=False):

    passed = False
    wait = 0
    response = None

    while not passed:
        try:
            response = request_get(url, stream=stream_)
            response.raise_for_status()
            passed = True
            wait = 0
        except (RequestException, HTTPError):
            wait += 5
            wait %= 60
        finally:
            sleep(wait)

    return response


def translate(text):
    translator = Translator()
    detected_language = translator.detect(text).lang

    bad_characters = []

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


def is_potential_heading(text, font_size_threshold=None, font_name="Helvetica-Bold"):
    """
    Checks if the text has characteristics of a heading based on font size and style (heuristics).

    Args:
        text (str): The text content to analyze.
        font_size_threshold (int, optional): Minimum font size for heading (defaults to None).
        font_name (str, optional): Expected font name for headings (defaults to "Helvetica-Bold").

    Returns:
        bool: True if the text is a potential heading, False otherwise.
    """
    if not text:
        return False  # Empty text can't be a heading

    try:
        # Access font information (might not be available for all PDFs)
        with open("your_pdf_file.pdf", "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            page = pdf_reader.getPage(
                0
            )  # Access the first page (adjust for specific needs)
            font = page.extract_font(text)
            if font:
                return (
                    font_size_threshold is None
                    or font.get("FontSize") >= font_size_threshold
                ) and font.get("FontName") == font_name
            else:
                # Font information unavailable, consider using other heuristics or returning False
                return False

    except Exception as e:
        print(f"Error accessing font information: {e}")
        return False  # Handle errors gracefully, consider alternative approaches


def get_page_info(pdf_path):

    info = {}

    pdf_reader = PyPDF2.PdfReader(pdf_path)
    pdf_pages = pdf_reader.pages

    # Get opening page
    i = 0
    while i < len(pdf_pages):
        page = pdf_pages[i]
        text = page.extract_text()

        # Check if pdf page contains the word Összefoglalás
        if "Összefoglalás" in text:
            if "Összefoglalás" in text.split("\n")[-1]:
                info["opening"] = i + 2
            else:
                info["opening"] = i + 1
            break

        i += 1

    # Get closing page
    i = len(pdf_pages)
    while i > 0:
        page = pdf_pages[i - 1]
        text = page.extract_text()

        # Check if pdf page contains the word Irodalomjegyzék
        if "Irodalomjegyzék" in text:
            if "Irodalomjegyzék" in text.split("\n")[0]:
                info["closing"] = i - 1
            else:
                info["closing"] = i
            break

        i -= 1

    return info
