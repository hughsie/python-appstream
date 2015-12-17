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
