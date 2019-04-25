#!/usr/bin/env python
#-*- coding: UTF-8 -*-

"""
Requires inkscape and ghostscript
"""

from itertools import izip
from subprocess import Popen, PIPE, STDOUT
import csv
import os
import locale
import sys
from codecs import open
import tempfile



def basename(path):
    return os.path.splitext(os.path.basename(path))[0]


def which(command):
    return "".join(
        Popen(['which', command], stdout=PIPE).stdout.readlines()).strip()


def main():
    if len(sys.argv) != 3:
        print """Se debe invocar el comando de esta manera:
            combinar svgfile csvfile"""
        return 1
    else:
        svgfile = sys.argv[1]
        csvfile = sys.argv[2]
        finalfile = "%s - %s.pdf" % (basename(svgfile), basename(csvfile))
        original = "\n".join(open(svgfile, "r", "utf8").readlines())

    lista = [row for row in csv.reader(open(csvfile), delimiter=';')]
    header = [word.decode("utf8") for word in lista.pop(0)]
    lista = [[word.decode("utf8").title() for word in row] for row in lista]

    lista.sort()

    pdflist = []
    svglist = []

    try:
        locale.localeconv()['thousands_sep'] = '.'
    except locale.Error:
        print "Configue una localización compatible con el sistema"
        return 2


    print("Combinando campos, generando páginas")
    last = ""
    for fila in lista:
        copia = original
        registro = dict(izip(header, fila))

        svgfile = tempfile.mktemp(".svg")
        svglist.append(svgfile)
        pdffile = tempfile.mktemp(".pdf")
        pdflist.append(pdffile)

        for key, value in registro.iteritems():
            if value.isdigit():
                value = locale.format("%d", int(value), True)

            copia = copia.replace("%%%s%%" % key, value.strip())

        file = open(svgfile, "w", "utf8")
        file.write(copia)
        file.close()

        proc = Popen([which("inkscape"), '-zC', '-d', '180', '-A', pdffile,
            svgfile], stdout=PIPE)
        proc.wait()

        if proc.returncode != 0:
            return returncode

        now = round((float(len(pdflist)) / len(lista) * 100))
        if now != last:
            last = now
            sys.stdout.write("%2d%% " % now)
            sys.stdout.flush()

    print("\nCombinando, páginas en documento final")
    proc = Popen([which("gs"), "-q", "-dNOPAUSE", "-dBATCH",
        "-sDEVICE=pdfwrite", "-sOutputFile=%s" % finalfile] + pdflist)
    proc.wait()

    if proc.returncode != 0:
        return proc.returncode
    else:
        print("Generado el documento %s" % finalfile)


if __name__ == "__main__":
    exit(main())
