# -*- coding: utf-8 -*-

"""__init__.py:
Simple Python API for linear stage toolbox server.

Usage:

    >>> from toolbox.linear_stage.api.python import RemoteLinearStage
    >>> linear_stage = RemoteLinearStage("./config.json")
    >>> linear_stage.set_absolute_position(114.514, "mm")

"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231115"


from .api import RemoteLinearStage