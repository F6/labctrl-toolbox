# -*- coding: utf-8 -*-

"""hardware_config.py:
This module contains a simple hardware mocker that behaves like a real device.
It can be used for testing other modules without actually connected to the device.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20240125"

# standard library
import logging
# third party
import numpy as np
# this package
from .hardware_config import hardware_config

# set up logging
lg = logging.getLogger(__name__)


def mock_data_generator():
    xmin = 0
    xmax = 4 * np.pi
    phases = np.linspace(xmin, xmax, 64)
    while True:
        for i in phases:
            if i > xmax:
                i = xmin
            i = i + 0.5 * np.pi
            x = np.sin(np.linspace(xmin + i, xmax + i, 2048)) + \
                np.random.rand(2048) * 0.2 + 1
            x = x * 10000
            x = np.array(x, dtype=np.int64)
            yield x


class MockedFX2000:
    def __init__(self) -> None:
        lg.info("Setting up mocked FX2000.")
        self.spec_num = 1
        lg.info("Number of spectrometers connected:" + str(self.spec_num))

        self.name = "[!] Mocked FX2000 [!]"
        lg.info("Name of first spectrometer:" + self.name)

        self.serial_num = "1145141919810"
        lg.info("Serial Number of first spectrometer:" + self.serial_num)

        self.pixels = 2048
        lg.info("Pixel Number of first spectrometer:" + str(self.pixels))

        self.wavelengths = np.linspace(185.2, 1302.3, 2048)
        lg.info("Minumum Wavelength:"+str(self.wavelengths[0]))
        lg.info("Maximum Wavelength:"+str(self.wavelengths[-1]))

        self.mocked_data = mock_data_generator()

    def set_boxcar_width(self, n):
        lg.info("Set boxcar width: {n}".format(n=n))

    def set_integration_time(self, t):
        lg.info("Set integration time: {t}ms".format(t=t))

    def set_average_times(self, n):
        print("Set average times:{n}".format(n=n))

    def get_spectrum(self):
        spectrum = next(self.mocked_data)
        return spectrum
