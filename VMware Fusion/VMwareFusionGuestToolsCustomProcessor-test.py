#!/usr/bin/python
#
# Copyright 2014 Justin Rummel
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import urllib, urllib2, gzip

from xml.etree import ElementTree
from StringIO import StringIO

# variables
base_url = 'https://softwareupdate.vmware.com/cds/vmw-desktop/'
fusion = 'fusion.xml'

# functions
def packages_metadata(base_url, fusion):
    request = urllib2.Request(base_url+fusion)
    print base_url

    try:
        vsus = urllib2.urlopen(request)
    except URLError, e:
        print e.reason

    data = vsus.read()
    # print data

    try:
        metaList = ElementTree.fromstring(data)
    except ExpatData:
        print "Unable to parse XML data from string"

    versions = []
    for metadata in metaList:
        version = metadata.find("version")
        versions.append(version.text)

    versions.sort()
    latest = versions[-1]
    # print latest

    urls = []
    for metadata in metaList:
        url = metadata.find("url")
        urls.append(url.text)

    matching = [s for s in urls if latest in s]
    packages = [s for s in matching if "package" in s]
    print packages[0]

    vsus.close()

    request = urllib2.Request(base_url+packages[0])

    try:
        vLatest = urllib2.urlopen(request)
    except URLError, e:
        print e.reason

    buf = StringIO( vLatest.read())
    f = gzip.GzipFile(fileobj=buf)
    data = f.read()
    # print data

    print base_url+packages[0].replace("metadata.xml.gz", "")

    try:
        metadataResponse = ElementTree.fromstring(data)
    except ExpatData:
        print "Unable to parse XML data from string"

    for elem in metadataResponse.findall('bulletin/componentList/component/relativePath'):
        # print elem.text
        # print packages[0].replace("metadata.xml.gz", elem.text)
        print base_url+packages[0].replace("metadata.xml.gz", elem.text)

packages_metadata(base_url, fusion)
