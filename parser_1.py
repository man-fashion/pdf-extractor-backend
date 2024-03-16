import io
import os
import re
import string
from PyPDF2 import PdfReader
import pandas as pd
from datetime import datetime,date
from dateutil import relativedelta
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFSyntaxError
import json
import tika
from tika import parser
import dateparser
import fitz

def extract_text_from_pdf(cv_path):
    if not isinstance(cv_path, io.BytesIO):
        with open(cv_path, 'rb') as fh:
            try:
                for page in PDFPage.get_pages(
                        fh,
                        caching=True,
                        check_extractable=False
                ):
                    resource_manager = PDFResourceManager()
                    fake_file_handle = io.StringIO()
                    converter = TextConverter(
                        resource_manager,
                        fake_file_handle,
                        codec='utf-8',
                        laparams=LAParams()
                    )
                    page_interpreter = PDFPageInterpreter(
                        resource_manager,
                        converter
                    )
                    page_interpreter.process_page(page)

                    text = fake_file_handle.getvalue()
                    yield text

                    converter.close()
                    fake_file_handle.close()
            except PDFSyntaxError:
                return
    else:
        try:
            for page in PDFPage.get_pages(
                    cv_path,
                    caching=True,
                    check_extractable=False
            ):
                resource_manager = PDFResourceManager()
                fake_file_handle = io.StringIO()
                converter = TextConverter(
                    resource_manager,
                    fake_file_handle,
                    codec='utf-8',
                    laparams=LAParams()
                )
                page_interpreter = PDFPageInterpreter(
                    resource_manager,
                    converter
                )
                page_interpreter.process_page(page)

                text = fake_file_handle.getvalue()
                yield text

                # close open handles
                converter.close()
                fake_file_handle.close()
        except PDFSyntaxError:
            return

def extract_text(file_path,ext):
    if ext == 'pdf':
        # text = ''
        # pages = 0
        # try:
        #     for page in extract_text_from_pdf(file_path):
        #         text += ' ' + page
        #         pages+=1
        #     return text,pages
        # except Exception:
        #   return text,pages
        text = ''
        pages = 0
        try:
            doc = fitz.open(file_path)
        except Exception:
            # file_path.seek(0)
            # doc = fitz.open(stream = file_path.read(), filetype = ext)
            doc = fitz.open(stream = file_path, filetype = ext)
        try:
            for page in doc:
                text += page.get_text("text", sort=True)
                pages += 1
            return text,pages
        except Exception:
            return text,pages

    else:
        tika.TikaClientOnly = True
        parsed = parser.from_file(file_path)
        try:
            return parsed['content'],parsed['metadata']['xmpTPg:NPages']            # pylint: disable=E1136
        except TypeError:
            return parsed['content'],0
        
def process_pdf_data(pdf_path, pick_up_service_list=["Delhivery", "Xpress Bees", "Pickup", "Ecom Express"]):
    text = extract_text(pdf_path, "pdf")
    bill_text_list = text[0].split("\nCOD")
    res = []

    if bill_text_list:
        for data in bill_text_list:
            try:
                start_index = data.find("Customer Address")
                end_index = data.find("Destination Code")
                result_string = data[start_index:end_index]

                # Split the result string into lines
                lines = result_string.split('\n')

                # Strip leading and trailing whitespaces from each line
                lines = [line.strip() for line in lines]

                # Iterate over pickup service names and remove corresponding lines
                for service_name in pick_up_service_list:
                    lines = [line for line in lines if service_name not in line]

                # Join the modified lines back into a string
                result_string = '\n'.join(lines)

                Lines = result_string.split('\n')
                name = Lines[1].strip()
                address_lines = Lines[2:-1]  # Exclude the first and last lines
                parts = address_lines[-1].split(', ')

                city, state, pincode = parts[0], parts[1], parts[2]
                final_address = "".join(address_lines[:-1])

                address_dict = {
                    "Name": name,
                    "address": final_address,
                    "city": city,
                    "state": state,
                    "pincode": pincode
                }
                res.append(address_dict)
            except Exception as e:
                address_dict = {
                    "Name": "NA",
                    "address": "NA",
                    "city": "NA",
                    "state": "NA",
                    "pincode": "NA"
                }
                res.append(address_dict)

    return res
        
