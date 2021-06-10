from time import sleep
from bs4 import BeautifulSoup
from requests import get
from pathlib import Path
from sys import exit

base_url = "https://www.supremecourt.gov.sg"
slug = "/news/supreme-court-judgments/page/1"  # Change this slug if you wish to start on a later page

# Creates a "downloaded_pdfs" dir if it doesn't exist, adds a log in there to indicate last download page.
(Path.cwd() / "downloaded_pdfs").mkdir(exist_ok=True)
download_path = Path.cwd() / "downloaded_pdfs"
(download_path / "download_log.txt").touch(exist_ok=True)

# Goes through the website and goes down the pages, downloads case pdfs until there are no more left
while True:
    current_page = "".join([base_url, slug])
    response = get(current_page)

    # Exits the program if the base + slug yields an invalid response (code 400 and above).
    if not response.ok:
        exit(f"Could not get http response from {current_page}.")
    else:
        print(f"Successfully obtained response from {current_page}.")

    # Uses bs4 to open the webpage into a bs4 HTML object
    soup = BeautifulSoup(response.content, "html.parser")

    # Finds the judgmentblock ul and identifies the stuff to download: this contains all the judgments on the page.
    judgments_block = soup.find("ul", class_="judgmentblock")
    judgments = judgments_block.find_all("div", class_="judgmentpage")

    # Finds all pdf download links in the judgment block
    for judgment in judgments:
        downloads = judgment.find_all("a", class_="pdf-download")

        # Accesses the download links and saves the bytes from the resulting pdf into a new file
        for download in downloads:
            download_slug = download["href"]  # Each a tag only has one href attr, extract it
            download_filename = download_slug.rsplit("/", 1)[1]
            newfile = (download_path / download_filename)
            newfile.touch(exist_ok=True)

            download_url = get("".join([base_url, download_slug]))
            newfile.write_bytes(download_url.content)

            print(f"Successfully extracted case into {newfile}.")
            sleep(5)  # IMPORTANT. Do not remove, it will probably overload the Sup Ct website servers.

    # Prints success message and logs last-downloaded page
    print(f"All cases from page {current_page} extracted. Will attempt to access next page.")
    with open((download_path / "download_log.txt"), "w") as f:
        f.write(f"Last page downloaded: {current_page}.")

    # Updates slug, gets ready for next request
    next_tag = soup.find("a", title="Next")
    slug = next_tag["href"]

    sleep(5)  # IMPORTANT. Do not remove, it will probably overload the Sup Ct website servers.

