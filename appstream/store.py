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

import gzip

import xml.etree.ElementTree as ET

try:
    # Py2.7 and newer
    from xml.etree.ElementTree import ParseError as StdlibParseError
except ImportError:
    # Py2.6 and older
    from xml.parsers.expat import ExpatError as StdlibParseError

from appstream.errors import ParseError
from appstream.component import Component

class Store(object):
    """ A quick'n'dirty store """
    def __init__(self, origin=None):
        """ Set defaults """
        self.origin = origin
        self.components = {}

    def to_xml(self):
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        if len(self.components) == 0:
            return '<components version="0.9" origin="%s"/>\n' % self.origin
        xml += '<components version="0.9" origin="%s">\n' % self.origin
        for app_id in self.components:
            xml += self.components[app_id].to_xml()
        xml += '</components>\n'
        return xml

    def to_file(self, filename):
        """ Save the store to disk """

        # save compressed file
        xml = self.to_xml()
        f = gzip.open(filename, 'wb')
        try:
            f.write(xml.encode('utf-8'))
        finally:
            f.close()

    def from_file(self, filename):
        """ Open the store from disk """
        with gzip.open(filename, 'rb') as f:
            self.parse(f.read())

    def get_component(self, app_id):
        """ Finds an application from the store """
        if not app_id in self.components:
            return None
        return self.components[app_id]

    def get_components(self):
        """ Returns all the applications from the store """
        components = []
        for app_id in self.components:
            components.append(self.components[app_id])
        return components

    def add(self, component):
        """ Add component to the store """

        # if already exists, just add the release objects
        old = self.get_component(component.id)
        if old:
            old.releases.extend(component.releases)
            return
        self.components[component.id] = component

    def parse(self, xml_data):
        """ Parse XML data """

        # parse tree
        try:
            root = ET.fromstring(xml_data)
        except StdlibParseError as e:
            raise ParseError(str(e))

        self.origin = root.attrib['origin']

        for child in root:
            component = Component()
            component.parse(child)
            self.components[component.id] = component
