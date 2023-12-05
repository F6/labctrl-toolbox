# -*- coding: utf-8 -*-

"""__init__.py:
Simple Python API for generic sensor toolbox server.

Usage:

    >>> from toolbox.sensor.api.python import RemoteSensor
    >>> sensor = RemoteSensor("./config.json")
    >>> print(sensor.get_data())
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231205"


from .api import RemoteSensor