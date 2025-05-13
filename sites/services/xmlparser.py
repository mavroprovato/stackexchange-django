"""Contains functions to iterate an XML file.
"""
import pathlib
from collections.abc import Generator

import defusedxml.ElementTree as eT


class XmlFileIterator:
    """The XML file iterator
    """
    def __init__(self, xml_file: pathlib.Path):
        """Create the XML file iterator.

        :param xml_file: The XML file.
        """
        self.xml_file = xml_file

    def __iter__(self) -> Generator[dict]:
        """Iterate over the XML file data.

        :return: Yields the data for each row as a dictionary of the element names to their values.
        """
        tree = eT.iterparse(self.xml_file, events=('start', ))
        for _, elem in tree:
            if elem.tag == 'row':
                yield dict(elem.items())
