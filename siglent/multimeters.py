"""
Multimeters

# SDM3000X
Tested on:
- SDM3065X

"""

from enum import Enum
from typing import List

from .common import MessageResource

class Measurement(Enum):
    """
    Valid measurement types for the SDM3000X multimeters
    """
    DCV = "VOLT:DC"
    ACV = "VOLT:AC"
    DCI = "CURR:DC"
    ACI = "CURR:AC"
    RES = "RES"
    CONT = "CONT"
    DIODE = "DIOD"
    CAP = "CAP"
    TEMP = "TEMP"
    FREQ = "FREQ"

class SDM3000X(MessageResource):

    @property
    def sample_count(self) -> int:
        """
        Get the current sample count
        """
        return int(self._resource.query(":SAMP:COUN?"))

    @sample_count.setter
    def sample_count(self, count: int):
        """
        Set the sample count
        """
        self._resource.write(f":SAMP:COUN {count}")

    @property
    def measurement(self) -> Measurement:
        # CONF? will return <Meas> <Range>,<Resolution> on the 3065X
        conf = self._resource.query(":CONF?")
        # Switch based on measurement mode
        if "VOLT:AC" in conf:
            return Measurement.ACV
        elif "CURR:AC" in conf:
            return Measurement.ACI
        elif "VOLT" in conf:
            return Measurement.DCV
        elif "CURR" in conf:
            return Measurement.DCI
        elif "CONT" in conf:
            return Measurement.CONT
        elif "DIOD" in conf:
            return Measurement.DIODE
        elif "CAP" in conf:
            return Measurement.CAP
        elif "FREQ" in conf:
            return Measurement.FREQ
        elif "TEMP" in conf:
            return Measurement.TEMP
        else:
            raise ValueError(f"Unknown instrument config {conf}")

    @measurement.setter
    def measurement(self, meas: Measurement):
        self._resource.write(f":CONF:{meas}")

    @property
    def trigger_count(self) -> int:
        return int(self._resource.query("TRIG:COUN?"))

    @trigger_count.setter
    def trigger_count(self, count: int):
        self._resource.write(f"TRIG:COUN {count}")
        
    @property
    def value(self) -> float:
        # Read the current measurement
        return float(self._resource.query("READ?"))