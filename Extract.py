from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTChar, LTTextBox
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextContainer, LTChar, LTTextLineHorizontal, LTAnno
from pdfminer.high_level import extract_pages
import json
def is_digit(char):
    return char.isdigit()

def extract_font_info(layout):
    max_font_size = 0  # Variable to store the largest font size

    for lt_obj in layout:
        if isinstance(lt_obj, LTTextBox):
            for text_line in lt_obj:
                for character in text_line:
                    if isinstance(character, LTChar):
                        current_char = character.get_text()

                        # Skip digit characters
                        if is_digit(current_char):
                            continue

                        current_font_size = character.size

                        # Update max_font_size if the current font size is larger
                        if current_font_size > max_font_size:
                            max_font_size = current_font_size

    return max_font_size

def font_size(path):
    with open(path, 'rb') as fp:
        parser = PDFParser(fp)
        document = PDFDocument(parser)

    # Check if the document allows text extraction. If not, abort.
    #if not document.is_extractable:
        #raise PDFTextExtractionNotAllowed

    # Create a PDF resource manager object that stores shared resources.
        rsrcmgr = PDFResourceManager()

    # Create a PDF device object.
        device = PDFDevice(rsrcmgr)

    # BEGIN LAYOUT ANALYSIS
    # Set parameters for analysis.
        laparams = LAParams()

    # Create a PDF page aggregator object.
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)

    # Create a PDF interpreter object.
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        total_pages = len(list(PDFPage.create_pages(document)))
        start_page = int(total_pages * 0.5)
        end_page = int(total_pages * 0.6)

        largest_font_size = 0  # Variable to store the largest font size across all pages

        for page_number, page in enumerate(PDFPage.create_pages(document)):
            if start_page <= page_number < end_page:
                interpreter.process_page(page)
                layout = device.get_result()
                current_page_max_font_size = extract_font_info(layout)

            # Update largest_font_size if the current page's max font size is larger
                if current_page_max_font_size > largest_font_size:
                    largest_font_size = current_page_max_font_size

    return largest_font_size
def extract_pdf(path):
    temp_pdf = []
    temp_dict = {}
    page_data = ""  # Initialize page_data
    largest_font_size = font_size(path)

    for page_layout in extract_pages(path):
        for element in page_layout:      # extracting the pages
            if isinstance(element, LTTextContainer):
                for text_line in element: # extracting the lines in pages
                    if isinstance(text_line, LTTextLineHorizontal):
                        for chr in text_line:
                            if isinstance(chr, LTChar):
                            # Check for bold, italic, and hyperlink

                                if (chr.size >= largest_font_size):
                                    if len(page_data) > 0:
                                        temp_dict['data'] = page_data
                                        temp_pdf.append(temp_dict)
                                        temp_dict = {}
                                    temp_dict["title"] = text_line.get_text()
                                    page_data = ""
                                    has_content_started = True
                                    break
                                elif (chr.size < largest_font_size):
                                    page_data += text_line.get_text()
                                    break

    out_file = open("/content/openai/results/Geo.json", "w", encoding='utf-8')  # Add encoding='utf-8'
    json.dump(temp_pdf, out_file, indent=6, ensure_ascii=False)  # Add ensure_ascii=False
    out_file.close()




if __name__=="__main__":
    extract_pdf("/content/sample_data/Eco.pdf")
