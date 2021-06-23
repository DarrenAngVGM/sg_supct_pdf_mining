"""
Runs through the Sup Ct website judgments page, downloads all full judgment PDFs and keeps a log of the casenames,
citations and filenames of the judgments extracted. Will not extract a judgment if it already exists in the
"downloaded_pdfs" folder.
"""

from time import sleep
from datetime import date
from bs4 import BeautifulSoup
from requests import get
from pathlib import Path
from sys import exit
import pandas as pd
import re

base_url = "https://www.supremecourt.gov.sg"
slug = "/news/supreme-court-judgments/page/1"  # Change this slug if you wish to start on a later page

# Creates a "downloaded_pdfs" dir if it doesn't exist, adds a log in there to indicate last download page.
(Path.cwd() / "downloaded_pdfs").mkdir(exist_ok=True)
download_path = Path.cwd() / "downloaded_pdfs"

# Creates a df to log the keywords, casenames, citations, and filenames
log_df = pd.DataFrame(columns=["casename", "keywords", "citation", "filename"])

# Goes through the website and goes down the pages, downloads case pdfs until there are no more left
while True:
    current_page = "".join([base_url, slug])
    response = get(current_page)

    # Exits the program if the base + slug yields an invalid response (code 400 and above).
    if not response.ok:
        exit(f"Bad http response from {current_page}.")
    else:
        print(f"Successfully obtained response from {current_page}.")

    # Uses bs4 to open the webpage into a bs4 HTML object
    soup = BeautifulSoup(response.content, "html.parser")

    # Finds the judgmentblock ul and finds all the individual judgmentpage elements under them
    judgments_block = soup.find("ul", class_="judgmentblock")
    judgments = judgments_block.find_all("div", class_="judgmentpage")

    # For each judgmentpage div (stores one judgment), extract case data (PART 1) and pdf file (PART 2)
    for judgment in judgments:

        # Create dict to append to log_df
        log_row = {
            "casename": None,
            "keywords": None,
            "citation": None,
            "filename": None
        }

        # PART 1: CASE DATA
        # Finds the case data, which is stored in the "text" div class
        text_block = judgment.find("div", class_="text")

        # Each text div has 5 elements: index 1 contains keywords, index 2 contains casename, index 3 contains citation
        text_contents = text_block.contents
        keywords_tag, casename_str, citation_tag = text_contents[1], text_contents[2], text_contents[3]

        # Keywords: is a bs4 Tag; remove additional spaces from beginning and end
        try:
            keywords_lsplit = keywords_tag.text.split("[", 1)[1]
            keywords_rsplit = keywords_lsplit.rsplit("]", 1)[0]
            log_row["keywords"] = "[" + keywords_rsplit + "]"
        except IndexError:
            log_row["keywords"] = keywords_tag.text

        # Casename: is a bs4 NavigableString; remove extra spaces at beginning and end
        log_row["casename"] = re.search("\s\s+(.*)\s\s+", casename_str).groups()[0]  # Captures casename as only group

        # Citation: is a bs4 Tag; extract from first li tag
        log_row["citation"] = citation_tag.find("li").text

        # PART 2: PDF DOWNLOADS (AND PDF FILENAMES)
        # Finds all pdf download links in the judgment block
        download = judgment.find("a", class_="pdf-download")

        # Accesses the download link and saves the bytes from the resulting pdf into a new file
        download_slug = download["href"]  # Each anchor tag only has one href attr, extract it
        log_row["filename"] = download_filename = download_slug.rsplit("/", 1)[1]
        newfile = (download_path / download_filename)

        if not newfile.is_file():
            newfile.touch(exist_ok=True)
            download_url = get("".join([base_url, download_slug]))
            newfile.write_bytes(download_url.content)
            print(f"Successfully extracted case into {newfile} and updated case log.")

            sleep(5)  # IMPORTANT. Do not remove, it will probably overload the Sup Ct website servers.
        else:
            print(f"File at {newfile} already exists.")

        # Updates the log and prints a success message
        log_df = log_df.append(log_row, ignore_index=True)
        last_page_num = slug.rsplit("/", 1)[1]
        date_now = date.today().strftime("%m%d%y")

        # Saves the log to a csv, removes the earlier csv if it exists
        log_df.to_csv(f"download log {date_now} - last accessed page no {last_page_num}.csv", encoding="utf-8-sig")
        (Path.cwd() / f"download log {date_now} - last accessed page no {int(last_page_num) - 1}.csv").unlink(
            missing_ok=True)

    # Prints success message and logs last-downloaded page
    print(f"All cases from page {current_page} extracted. Will attempt to access next page.")

    # Updates slug, gets ready for next request
    next_tag = soup.find("a", title="Next")
    slug = next_tag["href"]
    sleep(5)
