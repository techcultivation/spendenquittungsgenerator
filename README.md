# spendenquittungsgenerator (donation receipt generator)

`receipt.py` is a Python script that takes an amount and address as input and generates a PDF/A donation receipt from a LibreOffice templace document, replacing variables in the document. It depends on ``python-uno``.

It is currently optimized for the German legal requirements for donation receipts, e.g. it also converts the Euro amount into (German) words (`823.20 = Achthundertdreiundzwanzig Euro und zwanzig Cent`).

Spendenquittungsgenerator: Spendenbescheinigungen für Vereine, Stiftungen usw. aus ODT-Vorlage generieren.

## Install

Might work on MacOSX and even Windows. Currently tested only on Debian.

    git clone REPO_URL
    virtualenv env
    source env/bin/activate
    pip install --editable .

## receipt.py

We need a LibreOffice instance listening on port 2002:

    soffice --accept="socket,host=localhost,port=2002;urp;" --norestore --nologo --nodefault --headless -env:UserInstallation=file:///tmp/spendenquittungsgenerator

(We use a custom UserInstallation directory to not confuse existing instances; it will be created [and reused]).

This repository also contains a systemd service file to run LibreOffice as a daemon under the current user:

    mkdir -p ~/.config/systemd/user
    cp libreoffice-uno.service ~/.config/systemd/user
    systemctl --user enable libreoffice-uno.service
    systemctl --user start libreoffice-uno.service

Now, we can generate a `new.pdf` based on `templates/simple.odt` with placeholders filled out:

```
  > ./receipt.py --help
  Usage: receipt.py [OPTIONS] AMOUNT ADDRESS [DONATION_DATE]

  Produces German PDF/A donation receipts from LibreOffice Writer .odt
  templates. See README.md for usage.

  AMOUNT           the donation amount in Euro (float; example: 292.20)
  ADDRESS          postal mail address of the donor (example: "Moritz Bartl, Gottschedstrasse 4, 13357 Berlin")
  [DONATION_DATE]  date of donation arrival (example: 24.12.2048)

Options:
  -t, --template PATH     use a different odt template file as input (default:
                          --template template.odt.odt)
  -o, --outputfile PATH   write to a different output file (will be
                          overwritten if it exists) (default: --outputfile
                          new.pdf)
  -u, --soffice-url TEXT  LibreOffice connection string (default: --soffice-
                          url uno:socket,host=localhost<Plug>PeepOpenort=2002;
                          urp;StarOffice.ComponentContext)
  --help                  Show this message and exit.

```

The only required arguments are the amount (in Euros as float, eg. `100.50`) and address data of the donor (required in Germany) separated by commas and enclosed by quotation marks (eg. `"Walter Tevis, Samsaramstraße 44, 12999 Irgendwo"`). The third, optional argument is the date of the donation (default: current date).

### Example

```bash
❯ ./receipt.py 203.30 "Hans Meier, Apfelstraße 24, 02199 Groden" 3.8.2017          
[2017-08-07 00:20:15,041] INFO [root.cli:110] Validating inputs
[2017-08-07 00:20:15,044] INFO [root.cli:124] Trying to connect to Libreoffice at uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext
[2017-08-07 00:20:15,055] INFO [root.cli:152] Loading template.odt
[2017-08-07 00:20:15,182] INFO [root.cli:162] Replacing strings in template.odt
[2017-08-07 00:20:15,220] INFO [root.cli:172] Writing to new.pdf
```

Now, for additional greatness, we can digitally sign the PDF -- see notes at the end of this document.

### PLACEHOLDERS

Placeholder | Replaced by | Example
--- | --- | ---
_ADDRESSLINE | Address in one line, separated by commas | Walter Tevis, Samsaramstraße 44, 12999 Irgendwo
_ADDRESSBOX | Address as multiple lines separated by newlines | Walter Tevis\nSamsaramstraße 44\n12999 Irgendwo
_AMOUNTNUM | Amount in Euros | 203,30 €
_AMOUNTINWORDS | Amount in German words | Zweihundertdrei Euro und dreißig Cent
_DONATIONDATE | Date of donation reception | 3.8.2017

## zahlwort.py: Convert float to amount in German words

```bash
./zahlwort.py 21921.20                                                         
Einundzwanzigtausendneunhunderteinundzwanzig Euro und zwanzig Cent
```

## TODO

* additional receipt types (Sachspende, Sammelbescheinigung)

## Digitally sign PDF (notes)

[JSignPDF](http://jsignpdf.sourceforge.net/) by Josef Cacek has not seen any release or activity since 2014, but it works. Almost the last place to get a certificate from seems to be [Comodo](https://www.comodo.com/home/email-security/free-email-certificate.php).

    java -jar JSignPdf.jar -kst PKCS12 -ksf keyfile.p12 -ksp <password> new.pdf
