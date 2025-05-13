"""Contains functions to iterate an XML file.
"""
import pathlib
from collections.abc import Generator

import defusedxml.ElementTree as eT


def get_data(xml_file: pathlib.Path) -> Generator[dict]:
    """Iterate over the XML file data.

    :return: Yields the data for each row as a dictionary of the element names to their values.
    """
    tree = eT.iterparse(xml_file, events=('start', ))
    for _, elem in tree:
        if elem.tag == 'row':
            yield dict(elem.items())
