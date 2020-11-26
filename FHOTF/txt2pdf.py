#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''Bigrement inspiré de https://github.com/baruchel/txt2pdf

Copyright (c) 2014 Thomas Baruchel
Copyright (c) 2017 Fredrik de Vibe

Usage :

from txt2pdf import *

pdf_creator = PDFCreator()

pdf_creator.generate('mon_text.txt')

'''

#TODO : revoir que l'on puisse excecuter plusieurs fois generate!!!
#Oui alors supprimer tout mon bazard avec filename et output!

import reportlab.lib.pagesizes
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import units
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re
import sys
import os


class Margins(object):
    def __init__(self, right, left, top, bottom):
        self._right = right
        self._left = left
        self._top = top
        self._bottom = bottom

    @property
    def right(self):
        return self._right * units.cm

    @property
    def left(self):
        return self._left * units.cm

    @property
    def top(self):
        return self._top * units.cm

    @property
    def bottom(self):
        return self._bottom * units.cm

    def adjustLeft(self, width):
        self._left -= width / units.cm


class PDFCreator(object):
    appName = "txt2pdf (version 1.0)"

    def __init__(self, filename = None, \
                font = 'Courier', \
                font_size = 10.0, \
                extra_vertical_space = 0.0, \
                kerning = 0.0, \
                media = 'A4', \
                minimum_page_length = 10, \
                landscape = False, \
                margin_left = 2.0, \
                margin_right = 2.0, \
                margin_top = 2.0, \
                margin_bottom = 2.0, \
                output = None, \
                author = '', \
                title = '', \
                quiet = False, \
                subject = '', \
                keywords = '', \
                break_on_blanks = False,
                encoding = 'utf8', \
                page_numbers = None, \
                line_numbers = None):
        self.filename = filename
        pageWidth, pageHeight = reportlab.lib.pagesizes.__dict__[media]
        if landscape:
            pageWidth, pageHeight = reportlab.lib.pagesizes.landscape(
                (pageWidth, pageHeight))
        self.author = author
        self.title = title
        self.keywords = keywords
        self.subject = subject
        self.output = output
        self.minimum_page_length  = minimum_page_length
        output = self.get_output()
        self.canvas = Canvas(output, pagesize=(pageWidth, pageHeight))
        self.canvas.setCreator(self.appName)
        if len(author) > 0:
            self.canvas.setAuthor(author)
        if len(title) > 0:
            self.canvas.setTitle(title)
        if len(subject) > 0:
            self.canvas.setSubject(subject)
        if len(keywords) > 0:
            self.canvas.setKeywords(keywords)
        self.fontSize = font_size
        if font not in ('Courier'):
            self.font = 'myFont'
            pdfmetrics.registerFont(TTFont('myFont', font))
        else:
            self.font = font
        self.kerning = kerning
        self.margins = Margins(margin_right, margin_left, margin_top, margin_bottom)
        self.leading = (extra_vertical_space + 1.2) * self.fontSize
        self.linesPerPage = int(
            (self.leading + pageHeight
             - self.margins.top - self.margins.bottom - self.fontSize) / self.leading)
        self.lppLen = len(str(self.linesPerPage))
        fontWidth = self.canvas.stringWidth(
            ".", fontName=self.font, fontSize=self.fontSize)
        self.lineNumbering = line_numbers
        if self.lineNumbering:
            self.margins.adjustLeft(fontWidth * (self.lppLen + 2))
        contentWidth = pageWidth - self.margins.left - self.margins.right
        self.charsPerLine = int(
            (contentWidth + self.kerning) / (fontWidth + self.kerning))
        self.top = pageHeight - self.margins.top - self.fontSize
        self.verbose = not quiet
        self.breakOnBlanks = break_on_blanks
        self.encoding = encoding
        self.pageNumbering = page_numbers
        if self.pageNumbering:
            self.pageNumberPlacement = \
               (pageWidth / 2, self.margins.bottom / 2)

    def _process(self, data):
        flen = os.fstat(data.fileno()).st_size
        lineno = 0
        read = 0
        for line in data:
            lineno += 1
            if sys.version_info.major == 2:
                read += len(line)
                yield flen == \
                    read, lineno, line.decode(self.encoding).rstrip('\r\n')
            else:
                read += len(line.encode(self.encoding))
                yield flen == read, lineno, line.rstrip('\r\n')

    def _readDocument(self, filename):
        with open(filename, 'r') as data:
            for done, lineno, line in self._process(data):
                if len(line) > self.charsPerLine:
                    self._scribble(
                        "Warning: wrapping line %d in %s" %
                        (lineno + 1, filename))
                    while len(line) > self.charsPerLine:
                        yield done, line[:self.charsPerLine]
                        line = line[self.charsPerLine:]
                yield done, line

    def _newpage(self):
        textobject = self.canvas.beginText()
        textobject.setFont(self.font, self.fontSize, leading=self.leading)
        textobject.setTextOrigin(self.margins.left, self.top)
        textobject.setCharSpace(self.kerning)
        if self.pageNumbering:
            self.canvas.drawString(
                self.pageNumberPlacement[0],
                self.pageNumberPlacement[1],
                str(self.canvas.getPageNumber()))
        return textobject

    def _scribble(self, text):
        if self.verbose:
            sys.stderr.write(text + os.linesep)

    def generate(self, filename = None):
        if filename is None:
            filename = self.filename
        self.canvas._filename = self.get_output(filename)
        assert filename, "Error : filename not defined."
        self._scribble(
            "Writing '%s' with %d characters per "
            "line and %d lines per page..." %
            (filename, self.charsPerLine, self.linesPerPage)
        )
        if self.breakOnBlanks:
            pageno = self._generateBob(self._readDocument(filename))
        else:
            pageno = self._generatePlain(self._readDocument(filename))
        self._scribble("PDF document: %d pages" % pageno)
        return self.canvas._filename

    def _generatePlain(self, data):
        pageno = 1
        lineno = 0
        page = self._newpage()
        for _, line in data:
            lineno += 1
            # Handle form feed characters.
            (line, pageBreakCount) = re.subn(r'\f', r'', line)
            if pageBreakCount > 0 and lineno >= self.minimum_page_length:
                for _ in range(pageBreakCount):
                    self.canvas.drawText(page)
                    self.canvas.showPage()
                    lineno = 0
                    pageno += 1
                    page = self._newpage()
                    if self.minimum_page_length > 0:
                        break

            page.textLine(line)

            if lineno == self.linesPerPage:
                self.canvas.drawText(page)
                self.canvas.showPage()
                lineno = 0
                pageno += 1
                page = self._newpage()
        if lineno > 0:
            self.canvas.drawText(page)
        else:
            pageno -= 1
        self.canvas.save()
        return pageno

    def _writeChunk(self, page, chunk, lineno):
        if self.lineNumbering:
            formatstr = '%%%dd: %%s' % self.lppLen
            for index, line in enumerate(chunk):
                page.textLine(
                    formatstr % (lineno - len(chunk) + index + 1, line))
        else:
            for line in chunk:
                page.textLine(line)

    def _generateBob(self, data):
        pageno = 1
        lineno = 0
        page = self._newpage()
        chunk = list()
        for last, line in data:
            if lineno == self.linesPerPage:
                self.canvas.drawText(page)
                self.canvas.showPage()
                lineno = len(chunk)
                pageno += 1
                page = self._newpage()
            lineno += 1
            chunk.append(line)
            if last or len(line.strip()) == 0:
                self._writeChunk(page, chunk, lineno)
                chunk = list()
        if lineno > 0:
            self.canvas.drawText(page)
            self.canvas.showPage()
        else:
            pageno -= 1
        if len(chunk) > 0:
            page = self._newpage()
            self.canvas.drawText(page)
            self.canvas.showPage()
            pageno += 1
        self.canvas.save()
        return pageno

    def get_output(self, filename = None):
        '''Renvoie le fichier de sortie
        '''
        if self.output:
            output = self.output
        else:
            if filename is None:
                filename = self.filename
            if filename:
                l_filename = filename.split('.')
                if l_filename[-1].lower()=='txt':
                    l_filename = l_filename[:-1]
                output = '.'.join(l_filename) + '.pdf'
            else:
                output = 'output.pdf'
        return output
