# Takes a txt file of sentences extracted from a judgment, runs a regex search, returns a csv that indicates all
# matches of the legislation section format.

from pathlib import Path
import re
import pandas as pd


def ExtractTxtIntoSentences(txt_path):
    """
    Takes a pathlib object pointing to a .txt file of sentences, stores in memory as a list of sentences.
    """
    with open(txt_path, "r", encoding="utf-8") as f:
        sentences = f.readlines()

    return sentences


def FindLegisCitations(sentences):
    """
    Takes a list of sentences and finds legislation citations based on a regex formulation of section/article
    numbers. Returns a df with the matches found, tries to also find the statute, and the full sentence matched.
    """
    section_search = re.compile("(([A|a]rticle|[A|a]rt|[S|s]ection| s+) \d+)")
    df = pd.DataFrame(columns=["section_no", "sentence"])

    for sentence in sentences:
        try:
            section_hit = re.search(section_search, sentence).groups()[0]
            df = df.append({"section_no": section_hit, "sentence": sentence}, ignore_index=True)
        except AttributeError:
            pass

    return df


if __name__ == "__main__":
    txt_dir = Path.cwd() / "txt_output"
    main_df = pd.DataFrame(columns=["file", "section_no", "sentence"])

    for txt in txt_dir.glob("*.txt"):
        sentences = ExtractTxtIntoSentences(txt)
        df_to_add = FindLegisCitations(sentences)
        main_name_parts = txt.name.split("-")
        main_name = "_".join([main_name_parts[1], main_name_parts[2], main_name_parts[3]])

        for index, row in df_to_add.iterrows():
            main_df = main_df.append({"file": main_name, "section_no": row["section_no"], "sentence": row["sentence"]},
                                     ignore_index=True)

    main_df.to_csv((Path.cwd() / "section_search.csv"), encoding="utf-8-sig")

