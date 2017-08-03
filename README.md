# spendenquittungsgenerator (donation receipt generator)

`gen-receipt.py` is a Python script that takes an amount and address as input and generates a PDF/A donation receipt from a LibreOffice templace document, replacing variables in the document.

It is currently optimized for the German legal requirements for donation receipts, e.g. it also converts the Euro amount into (German) words (`823.20 = Achthundertdreiundzwanzig Euro und zwanzig Cent`).

## gen-receipt.py

We need a LibreOffice instance listening on port 2002:

    soffice --accept="socket,host=localhost<Plug>PeepOpenort=2002;urp;" --norestore --nologo --nodefault --headless -env:UserInstallation=file:///tmp/spendenquittungsgenerator

(We use a custom UserInstallation directory to not confuse existing instances; it will be created [and reused]).

Now, we can generate a `new.pdf` based on `templates/simple.odt` with placeholders filled out:

    ./gen-receipt.py amount address [donation_date] [--template TEMPLATE] [--outputfile OUT.PDF]

The only required arguments are the amount (in Euros as float, eg. `100.50`) and address data of the donor (required in Germany) separated by commas and enclosed by quotation marks (eg. `"Walter Tevis, Samsaramstraße 44, 12999 Irgendwo"`). The third, optional argument is the date of the donation (default: current date).

Example:

```bash
❯ ./gen-receipt.py 203.30 "Hans Meier, Apfelstraße 24, 02199 Groden" 3.8.2017          
INFO:root:Validating inputs...
INFO:root:Trying to connect to Libreoffice...
INFO:root:Loading templates/single.odt...
INFO:root:Replacing strings in templates/single.odt
INFO:root:Writing to new.pdf...
```

Options:

* ``--template <template.odt>`` use a different template file as input (default: ``--template templates/single.odt``)
* ``--outputfile <output.pdf>`` write to a different output file (will be overwritten if it exists) (default: ``--outputfile new.pdf``)

## PLACEHOLDERS

Placeholder | Replaced by | Example
--- | --- | ---
_ADDRESSLINE | Address in one line, separated by commas | Walter Tevis, Samsaramstraße 44, 12999 Irgendwo
_ADDRESSBOX | Address as multiple lines separated by newlines | "Walter Tevis\nSamsaramstraße 44\n12999 Irgendwo"
_AMOUNTNUM | Amount in Euros | 203,30 €
_AMOUNTINWORDS | Amount in German words | Zweihundertdrei Euro und dreißig Cent
_DONATIONDATE | Date of donation reception | 3.8.2017

## zahlwort.py: Convert float to amount in German words

```bash
./zahlwort.py 21921.20                                                         
Einundzwanzigtausendneunhunderteinundzwanzig Euro und zwanzig Cent
```

## TODO

* refactor a few things
* cryptographically sign PDFs
