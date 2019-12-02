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

from __future__ import absolute_import, print_function

import gzip
from distutils.version import LooseVersion
from xml.etree import ElementTree
from xml.parsers.expat import ExpatError

from autopkglib import URLGetter, ProcessorError

__all__ = ["VMwareFusionURLProvider"]


# variables
VMWARE_BASE_URL = "https://softwareupdate.vmware.com/cds/vmw-desktop/"
FUSION = "fusion.xml"
DEFAULT_MAJOR_VERSION = "11"


class VMwareFusionURLProvider(URLGetter):
    """Processor class."""

    description = "Provides URL to the latest VMware Fusion update release."
    input_variables = {
        "product_name": {
            "required": False,
            "description": "Default is '%s'." % FUSION,
        },
        "base_url": {
            "required": False,
            "description": "Default is '%s." % VMWARE_BASE_URL,
        },
        "major_version": {
            "required": False,
            "description": "Default is '%s." % DEFAULT_MAJOR_VERSION,
        },
    }
    output_variables = {
        "url": {"description": "URL to the latest VMware Fusion update release."},
        "version": {
            "description": "Version to the latest VMware Fusion update release."
        },
    }

    __doc__ = description

    def core_metadata(self, base_url, product_name, major_version):
        """Given a base URL, product name, and major version, produce the
        product download URL and latest version.
        """

        vsus = self.download(base_url + product_name, text=True)
        # self.output("Metadata fetch result: {}".format(vsus), verbose_level=2)

        try:
            metaList = ElementTree.fromstring(vsus)
        except ExpatError:
            raise ProcessorError("Unable to parse XML data from string.")

        versions = []
        for metadata in metaList:
            version = metadata.find("version")
            if major_version == "latest" or major_version == version.text.split(".")[0]:
                versions.append(version.text)
        if len(versions) == 0:
            raise ProcessorError(
                "Could not find any versions for the "
                "major_version '%s'." % major_version
            )
        versions.sort(key=LooseVersion)
        latest_version = versions[-1]

        urls = []
        for metadata in metaList:
            url = metadata.find("url")
            urls.append(url.text)

        matching = [s for s in urls if latest_version in s]
        core = [s for s in matching if "core" in s]
        self.output("Core value: {}".format(core), verbose_level=2)
        self.output("URL: {}".format(base_url + core[0]))
        vLatest = self.download(base_url + core[0], text=False)
        print("***vLatest: {}".format(vLatest))
        # buf = StringIO(vLatest.read())
        # f = gzip.GzipFile(fileobj=buf)
        # data = f.read()
        # # print(data)
        try:
            with gzip.open(vLatest, "rb") as f:
                data = f.read()
        except Exception as e:
            raise ProcessorError(e)

        try:
            metadataResponse = ElementTree.fromstring(data)
        except ExpatError:
            raise ProcessorError("Unable to parse XML data from string.")

        relativePath = metadataResponse.find(
            "bulletin/componentList/component/relativePath"
        )
        return (
            base_url + core[0].replace("metadata.xml.gz", relativePath.text),
            latest_version,
        )

    def main(self):
        """Main process."""

        # Gather input variables
        product_name = self.env.get("product_name", FUSION)
        base_url = self.env.get("base_url", VMWARE_BASE_URL)
        major_version = self.env.get("major_version", DEFAULT_MAJOR_VERSION)

        # Look up URL and set output variables
        self.env["url"], self.env["version"] = self.core_metadata(
            base_url, product_name, major_version
        )
        self.output("Found URL: %s" % self.env["url"])
        self.output("Found Version: %s" % self.env["version"])


if __name__ == "__main__":
    processor = VMwareFusionURLProvider()
    processor.execute_shell()
