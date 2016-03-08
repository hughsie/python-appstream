#!/usr/bin/python2
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Richard Hughes <richard@hughsie.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA

import xml.etree.ElementTree as ET

try:
    # Py2.7 and newer
    from xml.etree.ElementTree import ParseError as StdlibParseError
except ImportError:
    # Py2.6 and older
    from xml.parsers.expat import ExpatError as StdlibParseError

from appstream.errors import ParseError

def _join_lines(txt):
    """ Remove whitespace from XML input """
    txt = txt or ''  # Handle NoneType input values
    val = ''
    lines = txt.split('\n')
    for line in lines:
        stripped = line.strip()
        if len(stripped) == 0:
            continue
        val += stripped + ' '
    return val.strip()

def _parse_desc(node):
    """ A quick'n'dirty description parser """
    desc = ''
    for n in node:
        if n.tag == 'p':
            desc += '<p>' + _join_lines(n.text) + '</p>'
        elif n.tag == 'ol' or n.tag == 'ul':
            desc += '<ul>'
            for c in n:
                if c.tag == 'li':
                    desc += '<li>' + _join_lines(c.text) + '</li>'
                else:
                    raise ParseError('Expected <li> in <%s>, got <%s>' % (n.tag, c.tag))
            desc += '</ul>'
        else:
            raise ParseError('Expected <p>, <ul>, <ol> in <%s>, got <%s>' % (node.tag, n.tag))
    return desc

def validate_description(xml_data):
    """ Validate the description for validity """
    try:
        root = ET.fromstring(xml_data)
    except StdlibParseError as e:
        raise ParseError(str(e))
    return _parse_desc(root)

def _import_description_to_list_element(text):
    if len(text) < 5:
        return None
    if text.startswith('- '):
        return text[2:]
    if text[0].isdigit and text[1:3] == '. ':
        return text[3:]
    return None

def _import_description_sentence_case(text):
    return text[0].upper() + text[1:]

def import_description(text):
    """ Convert ASCII text to AppStream markup format """
    xml = ''
    is_in_ul = False
    for line in text.split('\n'):

        # don't include whitespace
        line = line.strip()
        if len(line) == 0:
            continue

        # detected as a list element?
        line_li = _import_description_to_list_element(line)
        if line_li:
            # first list element
            if not is_in_ul:
                xml += '<ul>\n'
                is_in_ul = True
            xml += '<li>' + _import_description_sentence_case(line_li) + '</li>\n'
            continue

        # done with the list
        if is_in_ul:
            xml += '</ul>\n'
            is_in_ul = False

        # regular paragraph
        xml += '<p>' + _import_description_sentence_case(line) + '</p>\n'

    # no trailing paragraph
    if is_in_ul:
        xml += '</ul>\n'

    return xml
