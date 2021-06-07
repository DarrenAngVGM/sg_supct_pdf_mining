# sg_supct_pdf_mining
Breaking down PDF judgments from the Singapore Supreme Court website into machine-readable text files!

This Python program works on PDF judgments downloaded from the Supreme Court website (https://www.supremecourt.gov.sg/news/supreme-court-judgments). It contains functions that can extract text from the PDFs, clean out the unnecessary information (to the best extent possible), as well as to break the text down into sentences.

Unfortunately, this program only works on judgments published in the latest format, as the optical character recognition (OCR) package I have used cannot recognise the words in the pre-2016 judgments. To my knowledge, judgments in the latest format are those which have been issued and published in 2016 and after.

~

NOTE:

To my knowledge and my best efforts, this program has been written in compliance of the Supreme Court website's Terms of Use (https://www.supremecourt.gov.sg/terms-of-use, retrieved 7 June 2021). While this program was mainly written for the purposes of an empirical legal research project I was embarking on, my hope in making it public was to contribute in some small way to the legal tech charge in Singapore. On that note, I am happy to take this program down or make this repository private upon request, in the event that it might interfere with the State's interests in any way.

If you wish to use this program, your attention is drawn to clause 6 of the Supreme Court website's Terms of Use. Any intellectual property subsisting in the PDF judgments downloaded from the Supreme Court website belongs to the Supreme Court (see cl 1). The usual principles of fair dealing (soon to be fair use, and the computational data analysis exception) apply.
