#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

DEFAULT_TEMPLATE = "template.odt"
DEFAULT_OUTPUT = "new.pdf"
LOGLEVEL = logging.INFO

"""receipt.py

Example:

    ./receipt.py 203 "Hans Meier, Apfelstraße 24, 02199 Groden" 24.2.2014
[2017-08-07 00:20:15,041] INFO [root.cli:110] Validating inputs
[2017-08-07 00:20:15,044] INFO [root.cli:124] Trying to connect to Libreoffice at uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext
[2017-08-07 00:20:15,055] INFO [root.cli:152] Loading template.odt
[2017-08-07 00:20:15,182] INFO [root.cli:162] Replacing strings in template.odt
[2017-08-07 00:20:15,220] INFO [root.cli:172] Writing to new.pdf

 by Moritz Bartl <moritz@headstrong.de>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

LOGFORMAT="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
SOFFICE_URL='uno:socket,host=localhost<Plug>PeepOpenort=2002;urp;StarOffice.ComponentContext'

import string
import getopt
import sys
import uno

import click
import time
import zipfile
import tempfile
import os
import shutil
import locale

import zahlwort

from unohelper import Base, systemPathToFileUrl, absolutize
from os import getcwd
from os.path import splitext
from com.sun.star.beans import PropertyValue
from com.sun.star.uno import Exception as UnoException
from com.sun.star.io import IOException, XOutputStream


class OutputStream(Base, XOutputStream):

    def __init__(self):
        self.closed = 0

    def closeOutput(self):
        self.closed = 1

    def writeBytes(self, seq):
        sys.stdout.write(seq.value)

    def flush(self):
        pass


def findInDoc(doc, searchstring):
    searchDescriptor = doc.createSearchDescriptor()
    searchDescriptor.SearchCaseSensitive = True
    searchDescriptor.SearchString = searchstring
    return doc.findFirst(searchDescriptor)


def replaceInDoc(doc, old, new):
    searchDescriptor = doc.createSearchDescriptor()
    searchDescriptor.SearchCaseSensitive = True
    searchDescriptor.SearchString = old
    found = doc.findFirst(searchDescriptor)
    if not found:
        logging.warn('Placeholder ' + old + ' not found in template document!')
    while found:
        found.String = new
        found = doc.findNext(found.End, searchDescriptor)


@click.command()
@click.argument('amount', type=float)
@click.argument('address')
@click.argument('donation_date', default=time.strftime('%d.%m.%Y'))
@click.option('--template', '-t', type=click.Path(exists=True, file_okay=True, dir_okay=False), default=DEFAULT_TEMPLATE, help="use a different odt template file as input (default: --template " + DEFAULT_TEMPLATE + ".odt)")
@click.option('--outputfile', '-o', type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=True), default=DEFAULT_OUTPUT, help="write to a different output file (will be overwritten if it exists) (default: --outputfile " + DEFAULT_OUTPUT + ")")
@click.option('--soffice-url', '-u', default=SOFFICE_URL, help="LibreOffice connection string (default: --soffice-url " + SOFFICE_URL + ")")
def cli(amount, address, donation_date, template, outputfile, soffice_url):
    """Produces German PDF/A donation receipts from LibreOffice Writer .odt templates. See README.md for usage.

    \b
    AMOUNT           the donation amount in Euro (float; example: 292.20)
    ADDRESS          postal mail address of the donor (example: "Moritz Bartl, Gottschedstrasse 4, 13357 Berlin")
    [DONATION_DATE]  date of donation arrival (example: 24.12.2048)
    """
    retVal = 0
    # validate optional donation date
    logging.info('Validating inputs')
    try:
        donation_datetime = time.strptime(donation_date, '%d.%m.%Y')
    except ValueError:
        raise ValueError("Incorrect data format, should be DD.MM.YYYY")

    donation_date = time.strftime('%d.%m.%Y', donation_datetime)
    amount_words = zahlwort.float2text(amount)
    address_split = address.split(",")
    address_split = list(map(str.strip, address_split))
    addressee = '\n'.join(address_split)
    addressline = ', '.join(address_split)

    try:
        logging.info("Trying to connect to Libreoffice at " + soffice_url)
        filterName = "writer_pdf_Export"
        extension = "pdf"

        ctxLocal = uno.getComponentContext()
        smgrLocal = ctxLocal.ServiceManager

        resolver = smgrLocal.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", ctxLocal)
        ctx = resolver.resolve(soffice_url)
        smgr = ctx.ServiceManager

        desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", ctx)

        cwd = systemPathToFileUrl(getcwd())
        filterData = (
            PropertyValue("SelectPdfVersion", 0, 1, 0),
        )
        outProps = (
            PropertyValue("FilterName", 0, filterName, 0),
            PropertyValue("FilterData", 0, uno.Any("[]com.sun.star.beans.PropertyValue", tuple(filterData)), 0),
            PropertyValue("Overwrite", 0, True, 0),
            PropertyValue("OutputStream", 0, OutputStream(), 0)
        )

        inProps = PropertyValue("Hidden", 0, True, 0),

        logging.info("Loading " + DEFAULT_TEMPLATE)

        fileUrl = absolutize(cwd, systemPathToFileUrl(DEFAULT_TEMPLATE))
        try:
            doc = desktop.loadComponentFromURL(fileUrl, "_blank", 0, inProps)

            if not doc:
                raise UnoException(
                    "Couldn't open stream for unknown reason", None)

            logging.info('Replacing strings in ' + DEFAULT_TEMPLATE)

            replaceInDoc(doc, '_ADDRESSBOX', addressee)

            replaceInDoc(doc, '_ADDRESSLINE', addressline)
            replaceInDoc(doc, '_AMOUNTNUM', locale.currency(amount))
            replaceInDoc(doc, '_AMOUNTINWORDS', amount_words)
            replaceInDoc(doc, '_DONATIONDATE', donation_date)

            destUrl = absolutize(cwd, systemPathToFileUrl(DEFAULT_OUTPUT))
            logging.info("Writing to " + DEFAULT_OUTPUT)
            doc.storeToURL(destUrl, outProps)
        except IOException as e:
            logging.exception("Error during conversion: " + e.Message + "\n")
            retVal = 1
        except UnoException as e:
            logging.exception(
                "Error (" + repr(e.__class__) + ") during conversion:" + e.Message + "\n")
            retVal = 1
        if doc:
            doc.dispose()

    except UnoException as e:
        logging.exception(
            "Error (" + repr(e.__class__) + ") :" + e.Message + "\n")
        retVal = 1

    sys.exit(retVal)

if __name__ == '__main__':
    logging.basicConfig(level=LOGLEVEL,format=LOGFORMAT)
    locale.setlocale(locale.LC_MONETARY, ('de', 'utf-8'))
    cli()
