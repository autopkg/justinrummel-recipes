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
from autopkglib import Processor, ProcessorError

__all__ = ["VMwareFusionGuestToolsURLProvider"]


# variables
VMWARE_BASE_URL = 'https://softwareupdate.vmware.com/cds/vmw-desktop/'
FUSION = 'fusion.xml'
DEFAULT_TOOL = 'com.vmware.fusion.tools.darwin.zip.tar'

class VMwareFusionGuestToolsURLProvider(Processor):
    description = "Provides URL to the latest VMware Fusion update release."
    input_variables = {
        "product_name": {
            "required": True,
            "description": "Default is '%s." % FUSION,
        },
        "guest_tool": {
            "required": True,
            "description": "Default is %s." % DEFAULT_TOOL,
        },
        "base_url": {
            "required": True,
            "description": "Default is '%s." % VMWARE_BASE_URL,
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest VMware Fusion update release.",
        },
    }

    __doc__ = description

    def packages_metadata(self, base_url, guest_tool, product_name):
        request = urllib2.Request(base_url+product_name)
        # print base_url

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
        packages = [s for s in matching if "packages" in s]
        # print packages[0]

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

        try:
            metadataResponse = ElementTree.fromstring(data)
        except ExpatData:
            print "Unable to parse XML data from string"

        return base_url+packages[0].replace("metadata.xml.gz", "")+guest_tool

        # relativePath = metadataResponse.find("bulletin/componentList/component/relativePath")
        #for elem in metadataResponse.findall('bulletin/componentList/component/relativePath'):
            # print elem.text
        #    return base_url+packages[0].replace("metadata.xml.gz", elem.text)

    def main(self):
        # Determine product_name, and base_url.
        product_name = self.env.get("product_name", FUSION)
        base_url = self.env.get("base_url", VMWARE_BASE_URL)
        guest_tool = self.env.get("guest_tool", DEFAULT_TOOL)

        self.env["url"] = self.packages_metadata(base_url, guest_tool, product_name)
        self.output("Found URL %s" % self.env["url"])

if __name__ == "__main__":
    processor = VMwareFusionGuestToolsURLProvider()
    processor.execute_shell()

