# -*- coding: utf-8 -*-

"""__init__.py:
Simple Python API for shutter toolbox server.

Usage:

    >>> from toolbox.shutter.api.python import RemoteShutter
    >>> shutter = RemoteShutter("./config.json")

"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231115"


from .api import RemoteShutter