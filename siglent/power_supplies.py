"""Power suppliess.

# SPD3303X
WIP
"""

from .common import MessageResource

from enum import Enum, StrEnum

class RunMode(StrEnum):
    CC = "CC"
    CV = "CV"

class SPD3303X(MessageResource):
    """The class to control a SPD3303X-Series power supply."""

    def __getitem__(self, channel: int):
        """Set the current chanel."""
        assert channel == 1 or channel == 2, "Channel must be either 1 or 2"
        self._resource.query(f"INST CH{channel}")
        return self

    @property
    def current(self) -> float:
        """Get the current of the currently selected channel."""
        return float(self._resource.query("MEAS:CURR?"))

class SPD4000X(MessageResource):
    """
    Class to control an SPD4000X power supply
    """

    supported_models = [
        "SPD4323X",
        "SPD4121X",
        "SPD4306X"
    ]

    def __del__(self):
        """Turn off all channels before disposal"""
        for i in range(1, 5):
            self.channel(i).output = False

    def channel(self, channel: int) -> "Channel":
        """Get the PSU channel from 1 to 4"""
        assert 1 <= channel <= 4, "Valid channels available are 1-4"
        return self.Channel(self, channel)

    class Channel:
        """Channel object from 1 of 4 available channels"""
        def __init__(self, parent: "SPD4000X", n: int):
            self._n = n
            self._parent = parent
            self._resource = parent._resource

        @property
        def voltage(self) -> float:
            """Get the voltage setting for the channel"""
            return float(self._resource.query(f":SOUR:VOLT:SET? CH{self._n}"))

        @voltage.setter
        def voltage(self, volts: float):
            """Set the voltage for the channel"""
            self._resource.write(f":SOUR:VOLT:SET CH{self._n},{volts}")

        @property
        def current(self) -> float:
            """Get the current setting for the channel"""
            return float(self._resource.query(f":SOUR:CURR:SET? CH{self._n}"))

        @current.setter
        def current(self, amps: float):
            """Set the current setting for the channel"""
            self._resource.write(f":SOUR:CURR:SET CH{self._n},{amps}")

        @property
        def ovp(self) -> float:
            """Get the overvoltage protection setting for the channel"""
            return float(self._resource.query(f":SOUR:OVP? CH{self._n}"))

        @ovp.setter
        def ovp(self, volts: float):
            """Set the overvoltage protection setting for the channel"""
            self._resource.write(f":SOUR:OVP CH{self._n},{volts}")

        @property
        def ovp_triggered(self) -> bool:
            """Get whether overvoltage protection has been triggered"""
            return bool(self._resource.query(f":SOUR:OVP:PROT:STAT? CH{self._n}"))

        @property
        def ocp(self) -> float:
            """Get the overcurrent protection setting for the channel"""
            return float(self._resource.query(f":SOUR:OCP? CH{self._n}"))

        @ocp.setter
        def ocp(self, amps: float):
            """Set the overcurrent protection setting for the channel"""
            self._resource.write(f":SOUR:OCP CH{self._n},{amps}")

        @property
        def ocp_triggered(self) -> bool:
            """Get whether overcurrent protection has been triggered"""
            return bool(self._resource.query(f":SOUR:OCP:PROT:STAT? CH{self._n}"))

        def clear_protection(self):
            """Clear the Overcurrent/Overvoltage protection status"""
            self._resource.write(f":SOUR:RESET:PROT CH{self._n}")

        @property
        def output(self) -> bool:
            """Get whether the output is on (true) or off (false)"""
            return bool(self._resource.query(f":SOUR:OUTP:STAT? CH{self._n}"))

        @output.setter
        def output(self, on: bool):
            """Turn the output on (true) or off (false)"""
            self._resource.write(f":SOUR:OUTP:STAT CH{self._n},{1 if on else 0}")

        @property
        def meas_voltage(self) -> float:
            """Get the voltage measurement for the channel"""
            return float(self._resource.query(f":MEAS:VOLT? CH{self._n}"))

        @property
        def meas_current(self) -> float:
            """Get the current measurement for the channel"""
            return float(self._resource.query(f":MEAS:CURR? CH{self._n}"))

        @property
        def meas_power(self) -> float:
            """Get the power measurement for the channel"""
            return float(self._resource.query(f":MEAS:POWER? CH{self._n}"))

        @property
        def run_mode(self) -> RunMode:
            mode = self._resource.query(f"MEAS:RUN:MODE? CH{self._n}")
            if "CV" in mode:
                return RunMode.CV
            elif "CC" in mode:
                return RunMode.CC
            else:
                raise ValueError(f"Unknown run mode response from instrument: {mode}")