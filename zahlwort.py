#!/usr/bin/env python
# -*- coding: latin-1 -*-

"""zahlwort.py outputs a string that describes a float in German words (Euros)

Example:

    zahlwort.py 21921.20
    > Einundzwanzigtausendneunhunderteinundzwanzig Euro und zwanzig Cent

num2text originally in PHP by Thorsten Rotering <support@rotering-net.de>
 https://rotering-net.de/tut/php-num2text.html

zahlwort.py ported and slightly extended in Python
 by Moritz Bartl <moritz@headstrong.de>

 explicitly licensed under MIT with permission of the original author
 - Thanks Thomas!

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
from math import floor, modf
import click

NUMERALS = [
    'null', 'ein', 'zwei', 'drei', 'vier', 'fünf', 'sechs', 'sieben', 'acht', 'neun',
          'zehn', 'elf', 'zwölf', 'drei~', 'vier~',
          'fünf~', 'sech~', 'sieb~', 'acht~', 'neun~']
TENNER = ['', '', 'zwanzig', 'dreißig', 'vierzig',
          'fünfzig', 'sechzig', 'siebzig', 'achtzig', 'neunzig']
GROUP_SUFFIX = [['', ''], ['tausend', 'tausend'],
                ['e Million ', ' Millionen '], ['e Milliarde ', ' Milliarden ']]
NUMERAL_SIGN = 'minus'
INFIX = 'und'
HUNDREDS_SUFFIX = 'hundert'


def num2text_group(number, group_level=0):
    if (number == 0):
        return ''
    group_number = number % 1000
    res = ''

    if (group_number == 1):
        res = NUMERALS[1] + GROUP_SUFFIX[group_level][0]
    elif (group_number > 1):
        first_digit = floor(group_number / 100)
        if (first_digit):
            res = NUMERALS[first_digit] + HUNDREDS_SUFFIX
        else:
            res = ''

        last_digits = group_number % 100
        second_digit = floor(last_digits / 10)
        third_digit = last_digits % 10

        if (last_digits == 0):
            res += ''
        elif (last_digits == 1):
            res += NUMERALS[1] + 's'
        elif (last_digits <= 19):
            res += NUMERALS[last_digits].replace('~', NUMERALS[10])
        else:
            if (third_digit):
                res += NUMERALS[third_digit] + INFIX
            res += TENNER[second_digit]

        res += GROUP_SUFFIX[group_level][1]

    number = floor(number / 1000)
    group_level += 1

    return num2text_group(number, group_level) + res


def num2text(number):
    prefix = ''
    if (number == 0):
        return NUMERALS[0]  # null
    if (number < 0):
        prefix = NUMERAL_SIGN + ' '  # minus …
    return prefix + num2text_group(abs(number))

    click.echo(zahl)


def float2text(number_float):
    cent, euro = modf(number_float)
    cent = round(cent * 100)
    zahlwort = num2text(int(euro)) + ' Euro'
    if (cent > 0):
        zahlwort += ' und ' + num2text(int(cent)) + ' Cent'
    zahlwort = zahlwort[0].upper() + zahlwort[1:]
    return zahlwort


@click.command()
@click.argument('zahl', type=float)
def cli(zahl):
    click.echo(float2text(zahl))

if __name__ == '__main__':
        cli()
