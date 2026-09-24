"""
Multimeters

# SDM3000X
Tested on:
- SDM3065X

"""

from enum import Enum, StrEnum
from typing import List

from .common import MessageResource

from statistics import fmean

class SDMMeasurement(Enum):
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

class SDMDCCurrentRange(StrEnum):
    I_200uA = "0.0002"
    I_2mA = "0.002"
    I_20mA = "0.02"
    I_200mA = "0.2"
    I_2A = "2.0"
    I_10A = "10.0"

class SDM3000X(MessageResource):

    supported_models = [
            "SDM3065X"
        ]

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
    def measurement(self) -> SDMMeasurement:
        # CONF? will return <Meas> <Range>,<Resolution> on the 3065X
        conf = self._resource.query(":CONF?")
        # Switch based on measurement mode
        if "VOLT:AC" in conf:
            return SDMMeasurement.ACV
        elif "CURR:AC" in conf:
            return SDMMeasurement.ACI
        elif "VOLT" in conf:
            return SDMMeasurement.DCV
        elif "CURR" in conf:
            return SDMMeasurement.DCI
        elif "CONT" in conf:
            return SDMMeasurement.CONT
        elif "DIOD" in conf:
            return SDMMeasurement.DIODE
        elif "CAP" in conf:
            return SDMMeasurement.CAP
        elif "FREQ" in conf:
            return SDMMeasurement.FREQ
        elif "TEMP" in conf:
            return SDMMeasurement.TEMP
        else:
            raise ValueError(f"Unknown instrument config {conf}")

    @measurement.setter
    def measurement(self, meas: SDMMeasurement):
        self._resource.write(f":CONF:{meas.value}")

    @property
    def trigger_count(self) -> int:
        return int(self._resource.query("TRIG:COUN?"))

    @trigger_count.setter
    def trigger_count(self, count: int):
        self._resource.write(f"TRIG:COUN {count}")
        
    @property
    def value(self) -> float:
        """Read the current measurement from the instrument, averaging if multiple samples are returned"""
        # Init trigger
        self._resource.write("INIT")
        # Wait
        self.block_until_complete()
        # Read the current measurement
        resp = self._resource.query("FETCH?")
        # Split by commas
        meas = [float(num) for num in resp.split(',')]
        # Average and return
        return fmean(meas)

    @property
    def dci_range(self) -> SDMDCCurrentRange:
        val = float(self._resource.query("SENS:CURR:DC:RANG?"))
        # Convert to string and strip any trailing zeroes unless it's >1
        str_val = f"{val:}".rstrip("0").rstrip('.') if val % 1 != 0 else f"{val:.1f}"
        # Parse into enum
        return SDMDCCurrentRange(str_val)

    @dci_range.setter
    def dci_range(self, range: SDMDCCurrentRange):
        # Write
        self._resource.write(f"SENS:CURR:DC:RANG {range.value}")