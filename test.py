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

import appstream

def main():

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
  <summary>Firmware for the Hughski ColorHug Colorimeter</summary>
  <description>
    <p>
      Updating the firmware on your ColorHug device improves performance and
      adds new features.
    </p>
  </description>
  <provides>
    <firmware type="flashed">40338ceb-b966-4eae-adae-9c32edfcc484</firmware>
  </provides>
  <url type="homepage">http://www.hughski.com/</url>
  <metadata_license>CC0-1.0</metadata_license>
  <project_license>GPL-2.0+</project_license>
  <updatecontact>richard_at_hughsie.com</updatecontact>
  <developer_name>Hughski Limited</developer_name>
  <releases>
    <release version="1.2.4" timestamp="1438454314">
      <description>
        <p>
          This release adds support for verifying the firmware
          contents using fwupd.
        </p>
      </description>
    </release>
  </releases>
</component>
"""
    app = appstream.Component()
    app.parse(data)
    app.validate()
    print ("ID:                  %s" % app.id)
    print ("GUID:                %s" % app.get_provides_by_kind('firmware-flashed')[0].value)
    print ("Name:                %s" % app.name)
    print ("Summary:             %s" % app.summary)
    print ("Description:         %s" % app.description)
    print ("Homepage:            %s" % app.urls['homepage'])
    print ("Metadata License:    %s" % app.metadata_license)
    print ("Project License:     %s" % app.project_license)
    print ("Developer Name:      %s" % app.developer_name)
    for rel in app.releases:
        print ("Release Version:     %s" % rel.version)
        print ("Release Timestamp:   %s" % rel.timestamp)
        print ("Release Description: %s" % rel.description)

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
      <description><p>This release adds magic.</p></description>
    </release>
  </releases>
</component>
"""
    app = appstream.Component()
    app.parse(data)
    store.add(app)
    print store.to_xml()

    store.to_file('/tmp/firmware.xml.gz')

    # sign
    #from signature import Signature
    #ss = Signature()
    #ss.create_detached('firmware.xml.gz')

if __name__ == "__main__":
    main()
