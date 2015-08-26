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

from errors import ParseError, ValidationError

def _parse_desc(node):
    """ A quick'n'dirty description parser """
    lines = ET.tostring(node[0]).split('\n')
    desc = ''
    for line in lines:
        new_ln = line.strip()
        if len(desc) > 0 and desc[-1] != '>':
            if len(new_ln) > 0 and new_ln[0] != '<':
                new_ln = ' ' + new_ln
        desc += new_ln
    return desc

class Checksum(object):
    def __init__(self):
        """ Set defaults """
        self.kind = 'sha1'
        self.target = None
        self.value = None
        self.filename = None
    def to_xml(self):
        return '        <checksum filename="%s" target="%s" type="sha1">%s</checksum>\n' % (self.filename, self.target, self.value)

class Release(object):
    def __init__(self):
        """ Set defaults """
        self.version = None
        self.description = None
        self.timestamp = 0
        self.checksums = []
        self.location = None

    def add_checksum(self, csum):
        """ Add a checksum to a release object """
        self.checksums.append(csum)

    def _parse_tree(self, node):
        """ Parse a <release> object """
        if 'timestamp' in node.attrib:
            self.timestamp = int(node.attrib['timestamp'])
        if 'version' in node.attrib:
            self.version = node.attrib['version']
        for c3 in node:
            if c3.tag == 'description':
                self.description = _parse_desc(c3)

    def to_xml(self):
        xml = '      <release version="%s" timestamp="%i">\n' % (self.version, self.timestamp)
        if self.location:
            xml += '        <location>%s</location>\n' % self.location
        for csum in self.checksums:
            xml += csum.to_xml()
        if self.description:
            xml += '        <description>%s</description>\n' % self.description
        xml += '      </release>\n'
        return xml

class Provide(object):
    def __init__(self):
        """ Set defaults """
        self.kind = None
        self.value = None
    def _parse_tree(self, node):
        """ Parse a <provide> object """
        if node.tag == 'firmware':
            if 'type' in node.attrib and node.attrib['type'] == 'flashed':
                self.kind = 'firmware-flashed'
            self.value = node.text.lower()

class Component(object):
    """ A quick'n'dirty MetaInfo parser """

    def __init__(self):
        """ Set defaults """
        self.id = None
        self.kind = None
        self.provides = []
        self.name = None
        self.summary = None
        self.description = None
        self.urls = {}
        self.metadata_license = None
        self.project_license = None
        self.developer_name = None
        self.releases = []

    def to_xml(self):
        xml = '  <component type="firmware">\n'
        if self.id:
            xml += '    <id>%s</id>\n' % self.id
        if self.name:
            xml += '    <name>%s</name>\n' % self.name
        if self.summary:
            xml += '    <summary>%s</summary>\n' % self.summary
        if self.developer_name:
            xml += '    <developer_name>%s</developer_name>\n' % self.developer_name
        if self.description:
            xml += '    <description>%s</description>\n' % self.description
        for key in self.urls:
            xml += '    <url type="%s">%s</url>\n' % (key, self.urls[key])
        if len(self.releases) > 0:
            xml += '    <releases>\n'
            for rel in self.releases:
                xml += rel.to_xml()
            xml += '    </releases>\n'
        if len(self.provides) > 0:
            xml += '    <provides>\n'
            for p in self.provides:
                xml += '      <firmware type="flashed">%s</firmware>\n' % p.value
            xml += '    </provides>\n'
        xml += '  </component>\n'
        return xml

    def add_release(self, release):
        """ Add a release object if it does not already exist """
        for r in self.releases:
            if r.version == release.version:
                return
        self.releases.append(release)

    def add_provide(self, provide):
        """ Add a provide object if it does not already exist """
        for p in self.provides:
            if p.value == provide.value:
                return
        self.provides.append(provide)

    def get_provides_by_kind(self, kind):
        """ Returns an array of provides of a certain kind """
        provs = []
        for p in self.provides:
            if p.kind == kind:
                provs.append(p)
        return provs

    def validate(self):
        """ Parse XML data """
        if not self.id or len(self.id) == 0:
            raise ValidationError('No <id> tag')
        if not self.name or len(self.name) == 0:
            raise ValidationError('No <name> tag')
        if not self.summary or len(self.summary) == 0:
            raise ValidationError('No <summary> tag')
        if not self.description or len(self.description) == 0:
            raise ValidationError('No <description> tag')
        if self.kind == 'firmware':
            if len(self.provides) == 0:
                raise ValidationError('No <provides> tag')
            if len(self.releases) == 0:
                raise ValidationError('No <release> tag')
        if not self.metadata_license or len(self.metadata_license) == 0:
            raise ValidationError('No <metadata_license> tag')
        if self.metadata_license not in ['CC0-1.0']:
            raise ValidationError('Invalid <metadata_license> tag')
        if not self.project_license or len(self.project_license) == 0:
            raise ValidationError('No <project_license> tag')
        if not self.developer_name or len(self.developer_name) == 0:
            raise ValidationError('No <developer_name> tag')

        # verify release objects
        for rel in self.releases:
            if not rel.version or len(rel.version) == 0:
                raise ValidationError('No version in <release> tag')
            if rel.timestamp == 0:
                raise ValidationError('No timestamp in <release> tag')

    def parse(self, xml_data):
        """ Parse XML data """

        # parse tree
        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError as e:
            raise ParseError(str(e))

        # get type
        if 'type' in root.attrib:
            self.kind = root.attrib['type']

        # parse component
        for c1 in root:

            # <id>
            if c1.tag == 'id':
                self.id = c1.text

            # <updatecontact>
            elif c1.tag == 'updatecontact' or c1.tag == 'update_contact':
                continue

            # <metadata_license>
            elif c1.tag == 'metadata_license':
                self.metadata_license = c1.text

            # <releases>
            elif c1.tag == 'releases':
                for c2 in c1:
                    if c2.tag == 'release':
                        rel = Release()
                        rel._parse_tree(c2)
                        self.add_release(rel)

            # <provides>
            elif c1.tag == 'provides':
                for c2 in c1:
                    prov = Provide()
                    prov._parse_tree(c2)
                    self.add_provide(prov)

            # <project_license>
            elif c1.tag == 'project_license' or c1.tag == 'licence':
                self.project_license = c1.text

            # <developer_name>
            elif c1.tag == 'developer_name':
                self.developer_name = c1.text

            # <name>
            elif c1.tag == 'name' and not self.name:
                self.name = c1.text

            # <summary>
            elif c1.tag == 'summary' and not self.summary:
                self.summary = c1.text

            # <description>
            elif c1.tag == 'description' and not self.description:
                self.description = _parse_desc(c1)

            # <url>
            elif c1.tag == 'url':
                key = 'homepage'
                if 'type' in c1.attrib:
                    key = c1.attrib['type']
                self.urls[key] = c1.text
