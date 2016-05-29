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

from __future__ import print_function

import appstream

def main():

    test_data = """
 Fixes:
- BIOS boot successfully with special food.
- No related beep codes displayed when HDD disabled.

Enhancemets:
- Update Microcode to dave.
- Update TGC function WINS test.
"""
    xml = appstream.utils.import_description(test_data)
    print(xml)
    assert appstream.utils.validate_description(xml)

    test_data = """
1. First version to support Win7 OS.
2. First version to support dock.
"""
    xml = appstream.utils.import_description(test_data)
    print(xml)
    assert appstream.utils.validate_description(xml)

    # parse junk
    app = appstream.Component()
    try:
        app.parse('junk')
    except appstream.ParseError:
        pass

    data = """<?xml version="1.0" encoding="UTF-8"?>
<!-- Copyright 2015 Richard Hughes <richard@hughsie.com> -->
<component type="firmware">
  <id>com.hughski.ColorHug.firmware</id>
  <name>ColorHug Device Update</name>
  <summary>
    Firmware for the Hughski ColorHug Colorimeter
  </summary>
  <description>
    <p>
      Updating 
      adds new features.
    </p>
    <p>
      2nd para.
    </p>
  </description>
  <provides>
    <firmware type="flashed">40338ceb-b966-4eae-adae-9c32edfcc484</firmware>
  </provides>
  <keywords>
    <keyword>one</keyword>
    <keyword>two</keyword>
  </keywords>
  <url type="homepage">http://www.hughski.com/</url>
  <metadata_license>CC0-1.0</metadata_license>
  <project_license>GPL-2.0+</project_license>
  <updatecontact>richard_at_hughsie.com</updatecontact>
  <developer_name>Hughski Limited</developer_name>
  <releases>
    <release version="1.2.4" timestamp="1438454314" date="2016-02-25" urgency="high">
      <size type="installed">123456</size>
      <size type="download">654321</size>
      <checksum target="content" filename="firmware.bin" type="sha1">deadbeef</checksum>
      <description>
        <p>Fixes bugs:</p>
        <ul>
          <li>Fix the RC</li>
          <li>Scale the output</li>
        </ul>
      </description>
    </release>
  </releases>
</component>
"""
    app = appstream.Component()
    app.parse(data)
    app.validate()
    assert app.id == 'com.hughski.ColorHug.firmware', app.id
    assert app.name == 'ColorHug Device Update', app.name
    assert app.summary == 'Firmware for the Hughski ColorHug Colorimeter', app.summary
    assert app.description == '<p>Updating adds new features.</p><p>2nd para.</p>', app.description
    assert app.urls['homepage'] == 'http://www.hughski.com/', app.urls['homepage']
    assert app.metadata_license == 'CC0-1.0', app.metadata_license
    assert app.project_license == 'GPL-2.0+', app.project_license
    assert app.developer_name == 'Hughski Limited', app.developer_name
    tmp = app.get_provides_by_kind('firmware-flashed')[0].value
    assert tmp == '40338ceb-b966-4eae-adae-9c32edfcc484', tmp
    assert len(app.releases) == 1
    assert len(app.keywords) == 2
    for rel in app.releases:
        assert rel.version == '1.2.4', rel.version
        assert rel.timestamp == 1456358400, rel.timestamp
        assert rel.size_installed == 123456, rel.size_installed
        assert rel.size_download == 654321, rel.size_download
        assert rel.description == '<p>Fixes bugs:</p><ul><li>Fix the RC</li><li>Scale the output</li></ul>', rel.description
        assert rel.urgency == 'high', rel.urgency
        assert len(rel.checksums) == 1, len(rel.checksums)
        for csum in rel.checksums:
            assert csum.kind == 'sha1', csum.kind
            assert csum.target == 'content', csum.target
            assert csum.value == 'deadbeef', csum.value
            assert csum.filename == 'firmware.bin', csum.filename

    # add extra information for AppStream file
    rel = app.releases[0]
    rel.location = 'http://localhost:8051/hughski-colorhug-als-3.0.2.cab'

    csum = appstream.Checksum()
    csum.value = 'deadbeef'
    csum.target = 'container'
    csum.filename = 'hughski-colorhug-als-3.0.2.cab'
    rel.add_checksum(csum)

    csum = appstream.Checksum()
    csum.value = 'beefdead'
    csum.target = 'content'
    csum.filename = 'firmware.bin'
    rel.add_checksum(csum)

    # add to store
    store = appstream.Store()
    store.add(app)

    # add new release
    data = """<?xml version="1.0" encoding="UTF-8"?>
<!-- Copyright 2015 Richard Hughes <richard@hughsie.com> -->
<component type="firmware">
  <id>com.hughski.ColorHug.firmware</id>
  <releases>
    <release version="1.2.5" timestamp="1500000000">
      <description><p>This release adds magic®.</p></description>
    </release>
  </releases>
</component>
"""
    app = appstream.Component()
    app.parse(data)
    store.add(app)
    print(store.to_xml().encode('utf-8'))

    store.to_file('/tmp/firmware.xml.gz')

    # sign
    #from signature import Signature
    #ss = Signature()
    #ss.create_detached('firmware.xml.gz')

if __name__ == "__main__":
    main()
