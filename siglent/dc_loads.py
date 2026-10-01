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
        _ = self._resource.write(f":SOUR:FUNC {func}")

    @property
    def current(self) -> float:
        """Get the constant-current setting of the load"""
        return float(self._resource.query(":SOUR:CURR:LEV?"))

    @current.setter
    def current(self, current: float):
        """Set the constant-current setting of the load"""
        _ = self._resource.write(f":SOUR:CURR:LEV {current}")

    @property
    def input(self) -> bool:
        """Get the input state of the load (on or off)"""
        return bool(self._resource.query(":SOUR:INP:STAT?"))

    @input.setter
    def input(self, state: bool):
        """Set the input state of the load (on or off)"""
        _ = self._resource.write(f":SOUR:INP:STAT {"1" if state else "0"}")

    @property
    def meas_voltage(self) -> float:
        """Measure the voltage of the source input"""
        return float(self._resource.query(":MEAS:VOLT?"))
    
    @property
    def meas_current(self) -> float:
        """Measure the current of the source input"""
        return float(self._resource.query("MEAS:CURR?"))

    def __del__(self):
        """Turn off before disposal"""
        self.input = False