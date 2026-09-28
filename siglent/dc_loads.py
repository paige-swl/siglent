"""
DC electronic loads
"""

from .common import MessageResource
from enum import Enum, StrEnum

class LoadFunction(StrEnum):
    ConstantCurrent = "CURRENT"
    ConstantVoltage = "VOLTAGE"
    ConstantResistance = "RESISTANCE"
    ConstantPower = "POWER"
    LED = "LED"

class SDL1000X(MessageResource):
    """Class to control an SDL1000X electronic load"""

    @property
    def function(self) -> LoadFunction:
        """Get the functional mode of the load"""
        return LoadFunction(self._resource.query(":SOUR:FUNC?"))

    @function.setter
    def function(self, func: LoadFunction):
        """Set the functional mode of the load"""
        self._resource.write(f":SOUR:FUNC {func}")

    