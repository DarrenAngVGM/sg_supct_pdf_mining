# Takes pdf judgments from the Sup Ct website (only), relies on their file name and format to extract their text.
# Only works for judgments in the most recent (as of 2016) format. OCR fails for the earlier ones.

from pathlib import Path
import PyPDF2
import re
from nltk.tokenize import sent_tokenize
from sys import exit


def ExtractTextIntoDict(pdf_file_path):
    """
    Extracts text from pdf file, into a dict {page no (int): text (str)}. Cleans text by removing extra spaces created
    by OCR. Note: OCR only works for judgments in or after 2016.
    """
    f = pdf_file_path.open(mode="rb")
    reader = PyPDF2.PdfFileReader(f)
    n_pages = reader.getNumPages()

    # Extract all text into a dict, in the format: {page no (int): text (str)}
    text = {page_num: "" for page_num in range(n_pages)}

    for page_num in range(n_pages):
        page = reader.getPage(page_num)
        page_text = page.extractText()

        # Removes all newlines and extra spaces
        page_text = page_text.replace("\n", " ")
        page_text = re.sub("\s+", " ", page_text)
        text[page_num] = page_text

    f.close()
    return text


def FindCitationFromHeader(text):
    """
    Unreported judgments from the Sup Ct website share a header which contains the casename and citation,
    but the order of the words is scrambled when they are OCR'd by PyPDF2 (they appear in the order: {Party 1 v} {
    citation} {Party 2} {pg no}. This function takes a dict of text extracted from the cases (from
    ExtractTextIntroDict()) and uses the header on the last page and tries all pages backwards until the citation is
    found.

    Returns a list in the format: (Party 1, Neutral Citation, Party 2). This will be used to remove the header from
    other pages.
    """
    pg_ptr = len(text.keys()) - 1  # Starts on last page and works backwards
    scrambled_regex = re.compile("(.+) v (\[\d\d\d\d] SG\w\w \d+) (.+) \d+")

    while pg_ptr != -1:
        lastpg_text = text.get(pg_ptr)

        # It's not always possible to find the citation from the header because OCR messes up.
        # Therefore, return False if not possible; the code will still carry on.
        try:
            search_hits = scrambled_regex.match(lastpg_text).groups()
            if len(search_hits) == 3:
                return list(search_hits)

        except AttributeError:
            pass

        pg_ptr -= 1

    print("Could not extract citation from header due to OCR issues. It will appear in the extracted text.")
    return False


def RemoveHeadersFromText(text, cite):
    """
    Takes a dict of text extracted from a case pdf (from ExtractTextIntoDict()) and a list of the parts of the
    citation from the headers (from FindCitationFromHeader()), and removes the header from all pages which have it.

    Returns the dict of text without the headers. If citation could not be found, just return the text as is.
    """
    if cite is not False:
        cite.insert(1, "v")
        header_std_text = " ".join(cite)
        for page in text.keys():
            page_text = text.get(page)
            text[page] = page_text.replace(header_std_text, "")

        return text
    else:
        return text


def FindStartOfText(text):
    """
    Takes a dict of text extracted from a case pdf (from ExtractTextIntoDict()) and returns the page number and
    character position (in a tuple) where the judgment begins. Under the new format, the paragraphs begin with a
    Justice's name followed by a colon (:). This function uses that format to determine the start position of the text.

    If the start point cannot be found, the function returns (0,0), and none of the text will be removed.
    """
    justice_intro = re.compile("J[A-Z]*( .*)?: ")
    for page_num in text.keys():
        page_text = text.get(page_num)
        search_hit = justice_intro.search(page_text)
        if search_hit is not None:
            return page_num, search_hit.end()

    print("Could not find start of judgment.")
    return 0, 0


def PreprocessTextToString(text: dict) -> str:
    """
    Takes a dict of text extracted from a case pdf (from ExtractTextToDict()). Calls FindCitationFromHeader(),
    RemoveHeadersFromText() and FindStartOfText(), and removes all text before the start position.

    Returns a single string of text representing the main body text of the entire judgment.
    """
    text_chunks = list()

    cite = FindCitationFromHeader(text)
    text_no_headers = RemoveHeadersFromText(text, cite)
    start_page, start_pos = FindStartOfText(text_no_headers)

    # Only keep text from pages above the start page. If on start page, only keep text after start position.
    for page_num in text.keys():
        if page_num == start_page:
            text_chunks.append(text.get(page_num)[start_pos:])
        elif page_num > start_page:
            text_chunks.append(text.get(page_num))

    return "".join(text_chunks)


def SentenceTokenizeText(pdf_file_path):
    """
    Reads a pdf of a case from a file_path and returns the main body of the case in a list of sentences. Also removes
    any stray numbers which might appear at the beginning of sentences: these are likely to be page numbers or paragraph
    markers which could not be removed.
    """
    text = ExtractTextIntoDict(pdf_file_path)
    text_string = PreprocessTextToString(text)

    sentences = sent_tokenize(text_string)

    # Find excess bits; once they are found, remove them until the first alpha char is found.
    # Note: This might remove some relevant numbers, such as cash amounts.
    sentences_cleaned = list()
    for sentence in sentences: # Removes extra spaces
        rm_counter = 0
        for char in sentence:
            check = char.isalpha()
            if check is True:  # Once an alphabet is hit, stop checking for more numbers/spaces
                break
            else:
                rm_counter += 1

        sentences_cleaned.append(sentence[rm_counter:])

    return sentences_cleaned


def WriteSentencesToTxtFile(pdf_file_path):
    """
    Reads a pdf of a case from a read_path and returns a .txt file in a new "txt_output" folder, with each sentence of the
    case separated by a newline. Creates the "txt_output" folder if it does not already exist.
    """
    sentences = SentenceTokenizeText(pdf_file_path)

    (Path.cwd() / "txt_output").mkdir(exist_ok=True)
    txt_path = Path.cwd() / "txt_output" / f"{pdf_file_path.name}.txt"
    with open(txt_path, "w", encoding="utf-8-sig") as f:
        for sentence in sentences:
            f.write(sentence + "\n")


# If the program is run standalone, prompt user to choose one file to convert.
if __name__ == "__main__":
    user_valid = None
    for path in Path.cwd().iterdir():
        user_valid = input(f"Is {path.name} the right file (y/n)?\t")

        if user_valid.lower() == "y":
            WriteSentencesToTxtFile(path)
            print(f"Created txt file from {path.name} in the 'txt_output' directory.")
            break

    # If end of loop reached without finding a file, print exit message.
    if user_valid != "y":
        exit("End of dir; could not find the file you were looking for. Please ensure that the file you wish to convert"
             "is in the current working directory.")


