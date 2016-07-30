#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import io
import re
from datetime import timedelta, date

import PyPDF2
import requests


def request(URL, session=requests.Session()):
    while (True):
        # Silly try-retry method for trying to account for networking
        # errors
        try:
            response = session.get(URL)
            return (response.content)
        except Exception as API_error:
            print(API_error)
            continue
        break


def buildurl(jornal, date, page):
    return ("http://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?"
            "jornal={}&pagina={}&data={}&captchafield=firistAccess"
            .format(jornal, page, date))


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def getfull(date, session=requests.Session()):
    full_text = ""
    counter = 1
    while True:
        try:
            url = buildurl(1, date, counter)
            pdf_content = io.BytesIO(request(url, session))
            pdf_reader = PyPDF2.PdfFileReader(pdf_content)
            page_obj = pdf_reader.getPage(0)
            full_text += page_obj.extractText()
            print("", end="\r")
            print("----Got {} pages.".format(counter), flush=True, end="")
            counter += 1
        except PyPDF2.utils.PdfReadError:
            break
    return full_text


with requests.Session() as line:
    with open("diarios.txt", "a+") as f:

        start_date = date(2016, 1, 1)
        end_date = date(2016, 7, 30)

        for single_date in daterange(start_date, end_date):
            diario_date = single_date.strftime("%d/%m/%Y")
            print(diario_date)
            f.write(getfull(diario_date, line))
            print("")
        f.seek(0)
        foo = re.findall(r"\d{2}[.]\d{3}[.]\d{3}/\d{4}-\d{2}", f.read())
    with open("results.txt", "a+") as f:
        cnpjs = {x: foo.count(x) for x in foo}
        print("{} CNPJs".format(len(cnpjs)))
        print("{} CNPJs".format(len(cnpjs)), file=f)
        for w in sorted(cnpjs, key=cnpjs.get, reverse=True):
            print(w, cnpjs[w])
            print(w, cnpjs[w], file=f)
