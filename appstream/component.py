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

import sys
import xml.etree.ElementTree as ET

try:
    # Py2.7 and newer
    from xml.etree.ElementTree import ParseError as StdlibParseError
except ImportError:
    # Py2.6 and older
    from xml.parsers.expat import ExpatError as StdlibParseError

from appstream.errors import ParseError, ValidationError

if sys.version_info[0] == 2:
    # Python2 has a nice basestring base class
    string_types = (basestring,)
else:
    # But python3 has distinct types
    string_types = (str, bytes)


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

class Checksum(object):
    def __init__(self):
        """ Set defaults """
        self.kind = 'sha1'
        self.target = None
        self.value = None
        self.filename = None
    def to_xml(self):
        return '        <checksum filename="%s" target="%s" type="sha1">%s</checksum>\n' % (self.filename, self.target, self.value)
    def _parse_tree(self, node):
        """ Parse a <checksum> object """
        if 'filename' in node.attrib:
            self.filename = node.attrib['filename']
        if 'type' in node.attrib:
            self.kind = node.attrib['type']
        if 'target' in node.attrib:
            self.target = node.attrib['target']
        self.value = node.text

class Release(object):
    def __init__(self):
        """ Set defaults """
        self.version = None
        self.description = None
        self.timestamp = 0
        self.checksums = []
        self.location = None
        self.size_installed = 0
        self.size_download = 0
        self.urgency = None

    def get_checksum_by_target(self, target):
        """ returns a checksum of a specific kind """
        for csum in self.checksums:
            if csum.target == target:
                return csum
        return None

    def add_checksum(self, csum):
        """ Add a checksum to a release object """
        for csum_tmp in self.checksums:
            if csum_tmp.target == csum.target:
                self.checksums.remove(csum_tmp)
                break
        self.checksums.append(csum)

    def _parse_tree(self, node):
        """ Parse a <release> object """
        if 'timestamp' in node.attrib:
            self.timestamp = int(node.attrib['timestamp'])
        if 'urgency' in node.attrib:
            self.urgency = node.attrib['urgency']
        if 'version' in node.attrib:
            self.version = node.attrib['version']
            # fix up hex value
            if self.version.startswith('0x'):
                self.version = str(int(self.version[2:], 16))
        for c3 in node:
            if c3.tag == 'description':
                self.description = _parse_desc(c3)
            if c3.tag == 'size':
                if 'type' not in c3.attrib:
                    continue
                if c3.attrib['type'] == 'installed':
                    self.size_installed = int(c3.text)
                if c3.attrib['type'] == 'download':
                    self.size_download = int(c3.text)
            elif c3.tag == 'checksum':
                csum = Checksum()
                csum._parse_tree(c3)
                self.add_checksum(csum)

    def to_xml(self):
        xml = '      <release'
        if self.version:
            xml += ' version="%s"' % self.version
        if self.timestamp:
            xml += ' timestamp="%i"' % self.timestamp
        if self.urgency:
            xml += ' urgency="%s"' % self.urgency
        xml += '>\n'
        if self.size_installed > 0:
            xml += '        <size type="installed">%i</size>\n' % self.size_installed
        if self.size_download > 0:
            xml += '        <size type="download">%i</size>\n' % self.size_download
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
        self.update_contact = None
        self.kind = None
        self.provides = []
        self.name = None
        self.pkgname = None
        self.summary = None
        self.description = None
        self.urls = {}
        self.icons = {}
        self.metadata_license = None
        self.project_license = None
        self.developer_name = None
        self.releases = []
        self.kudos = []

    def to_xml(self):
        xml = '  <component type="firmware">\n'
        if self.id:
            xml += '    <id>%s</id>\n' % self.id
        if self.pkgname:
            xml += '    <pkgname>%s</pkgname>\n' % self.pkgname
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
        for key in self.icons:
            xml += '    <icon type="%s">%s</icon>\n' % (key, self.icons[key]['value'])
        if len(self.releases) > 0:
            xml += '    <releases>\n'
            for rel in self.releases:
                xml += rel.to_xml()
            xml += '    </releases>\n'
        if len(self.kudos) > 0:
            xml += '    <kudos>\n'
            for kudo in self.kudos:
                xml += '      <kudo>%s</kudo>\n' % kudo
            xml += '    </kudos>\n'
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
        if isinstance(xml_data, string_types):
            # Presumably, this is textual xml data.
            try:
                root = ET.fromstring(xml_data)
            except StdlibParseError as e:
                raise ParseError(str(e))
        else:
            # Otherwise, assume it has already been parsed into a tree
            root = xml_data

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
                self.update_contact = c1.text

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

            # <kudos>
            elif c1.tag == 'kudos':
                for c2 in c1:
                    if not c2.tag == 'kudo':
                        continue
                    self.kudos.append(c2.text)

            # <project_license>
            elif c1.tag == 'project_license' or c1.tag == 'licence':
                self.project_license = c1.text

            # <developer_name>
            elif c1.tag == 'developer_name':
                self.developer_name = _join_lines(c1.text)

            # <name>
            elif c1.tag == 'name' and not self.name:
                self.name = _join_lines(c1.text)

            # <pkgname>
            elif c1.tag == 'pkgname' and not self.pkgname:
                self.pkgname = _join_lines(c1.text)

            # <summary>
            elif c1.tag == 'summary' and not self.summary:
                self.summary = _join_lines(c1.text)

            # <description>
            elif c1.tag == 'description' and not self.description:
                self.description = _parse_desc(c1)

            # <url>
            elif c1.tag == 'url':
                key = 'homepage'
                if 'type' in c1.attrib:
                    key = c1.attrib['type']
                self.urls[key] = c1.text

            elif c1.tag == 'icon':
                key = c1.attrib.pop('type', 'unknown')
                c1.attrib['value'] = c1.text
                self.icons[key] = self.icons.get(key, []) + [c1.attrib]
