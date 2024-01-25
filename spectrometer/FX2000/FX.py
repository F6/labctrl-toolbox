# -*- coding: utf-8 -*-

"""FX.py:
This module provides the FX2000 class to wrap the IdeaOptics FX2000 
spectrometer .NET libraries.

NOTE: This library is only a minimal wrapper loader, do not use this library
directly, use spectrometer.py instead for more comprehensive sanity checks,
thread safety checks, return data formatting, unit conversion, and data calibration.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20240125"


# std libs
import logging
import os
# third party
import clr
# set up logging
lg = logging.getLogger(__name__)


# Add dll reference (pythonnet)
# Because we are loading the application from other root directory, we
# can either add path of this directory to PATH temporarily, or use absolute path
# for the dll.
# clr.AddReference('IdeaOptics')
DLL_PATH = os.path.join(
    os.path.dirname(__file__), 'IdeaOptics.dll')
clr.AddReference(DLL_PATH)
from IdeaOptics import Wrapper


class FX2000:
    def __init__(self) -> None:
        self.wrapper = Wrapper()
        
        # get number of connected spectrometers
        self.spec_num = self.wrapper.OpenAllSpectrometers() 
        lg.info("Number of spectrometers connected:" + str(self.spec_num))

        # get name of first spectrometer
        self.name = self.wrapper.getName(0)
        lg.info("Name of first spectrometer:" + self.name)

        # get serial number of first spectrometer
        self.serial_num = self.wrapper.getSerialNumber(0)
        lg.info("Serial Number of first spectrometer:" + self.serial_num)

        # get pixel number of first spectrometer
        self.pixels = self.wrapper.getNumberOfPixels(0)
        lg.info("Pixel Number of first spectrometer:" + str(self.pixels))

        # get wavelengths
        self.wavelengths = list(self.wrapper.getWavelengths(0))
        lg.info("Minumum Wavelength:"+str(self.wavelengths[0]))
        lg.info("Maximum Wavelength:"+str(self.wavelengths[-1]))

        # detect if the spectrometer supports TEC cooling
        istec = self.wrapper.isTECControl(0)
        if istec:
            lg.info("The spectrometer supports TEC cooling")
            # set cooling temperature
            self.wrapper.setDetectorSetPointCelsius(0,-10)
            lg.info("Set detector temperature to -10 degree Celsius")
            # get temperature
            temp = self.wrapper.getFeatureControllerBoardTemperature(0)
            lg.info("Current temperature:" + str(temp))
        else:
            lg.info("The spectrometer does not support TEC cooling")

    def set_boxcar_width(self, n):
        self.wrapper.setBoxcarWidth(0,n)
        lg.info("Set boxcar width: {n}".format(n=n))

    def set_integration_time(self, t):
        # set integration time, unit=ms
        self.wrapper.setIntegrationTime(0,t)
        lg.info("Set integration time: {t}ms".format(t=t))

    def set_average_times(self, n):
        # set average times
        self.wrapper.setScansToAverage(0,n)
        print("Set average times:{n}".format(n=n))

    def get_spectrum(self):
        specs = list(self.wrapper.getSpectrum(0))
        return specs

