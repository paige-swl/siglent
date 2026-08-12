"""
Oscilloscopes

# SDS2000X
Tested on:
- SDS2354X
"""

from enum import Enum, StrEnum
from typing import List

from .common import MessageResource

class TriggerMode(StrEnum):
    AUTO = "AUTO"
    NORMAL = "NORM"
    SINGLE = "SING"
    FORCE = "FTRIG"

class BandwidthLimit(StrEnum):
    BW_FULL = "FULL"
    BW_20M = "20M"
    BW_200M = "200M"

class ChannelType(StrEnum):
    ANALOG = "C"
    ZOOMED = "Z"
    FUNCTION = "F"
    MEMORY = "M"
    DIGITAL = "D"
    ZOOMED_DIGITAL = "ZD"
    REFERENCE = "REF"

class ChannelCoupling(StrEnum):
    DC = "DC"
    AC = "AC"
    GROUND = "GND"

class ChannelUnit(StrEnum):
    AMPS = "A"
    VOLTS = "V"

class SDSMeasurementMode(StrEnum):
    SIMPLE = "SIMP"
    ADVANCED = "ADV"

class AdvancedMeasurementType(StrEnum):
    PEAKPEAK = "PKPK"
    MAX = "MAX"
    MIN = "MIN"
    AMPLITUDE = "AMPL"
    TOP = "TOP"
    BASE = "BASE"
    LEVEL_X = "LEVELX"
    CYCLE_MEAN = "CMEAN"
    MEAN = "MEAN"
    STDDEV = "STDEV"
    CYCLE_STDDEV = "VSTD"
    RMS = "RMS"
    CYCLE_RMS = "CRMS"
    MEDIAN = "MEDIAN"
    CYCLE_MEDIAN = "CMEDIAN"
    OVERSHOOT_FALLING = "OVSN"
    OVERSHOOT_RISING = "OSVP"
    OVERSHOOT_PRE_FALLING = "FPRE"
    OVERSHOOT_PRE_RISING = "RPRE"
    PERIOD = "PER"
    FREQUENCY = "FREQ"
    TIME_MAX = "TMAX"
    TIME_MIN = "TMIN"
    POSITIVE_WIDTH = "PWID"
    NEGATIVE_WIDTH = "NWID"
    DUTY_CYCLE = "DUTY"
    DUTY_CYCLE_NEGATIVE = "NDUTY"
    # TODO: add the rest there's like two more pages

class SDS2000X(MessageResource):

    supported_models = [
        "SDS2102X",
        "SDS2104X",
        "SDS2204X",
        "SDS2354X",
        "SDS2204X",
        "SDS2354X",
        "SDS2504X"
    ]

    # ----- Timebase Configuration -----

    @property
    def time_scale(self) -> float:
        """Get the current timebase in s/div"""
        return float(self._resource.query(":TIM:SCAL?"))

    @time_scale.setter
    def time_scale(self, timebase: float):
        """Set the current timebase in s/div"""
        self._resource.write(f":TIM:SCAL {timebase}")

    # ----- Channel Configuration -----

    def channel(self, channel: int) -> "Channel":
        """Get the channel number from the scope"""
        assert 1 <= channel <= 4, "Channels are 1-4"
        return self.Channel(self, channel)

    class Channel:
        """Channel object from 1 of 4 available channels"""
        def __init__(self, parent: "SDS2000X", n: int):
            self._n = n
            self._parent = parent
            self._resource = parent._resource

        @property
        def enabled(self) -> bool:
            """Get the channel on/off state"""
            return int(self._resource.query(f":CHAN{self._n}:SWIT?")) == "ON"

        @enabled.setter
        def enabled(self, enabled: bool):
            """Set the channel on/off state"""
            self._resource.write(f":CHAN{self._n}:SWIT {"ON" if enabled else "OFF"}")

        @property
        def scale(self) -> float:
            """Get the channel scale in Volts/Div"""
            return float(self._resource.query(f":CHAN{self._n}:SCAL?"))

        @scale.setter
        def scale(self, volts_div: float):
            """Set the channel scale in Volts/Div"""
            self._resource.write(f":CHAN{self._n}:SCAL {volts_div}")

        @property
        def probe(self) -> int:
            """Get the channel probe attenuation (x:1)"""
            return int(self._resource.query(":CHAN{self._n}:PROB?"))

        @probe.setter
        def probe(self, atten: int):
            """Set the channel probe attenuation (x:1)"""
            self._resource.write(f":CHAN{self._n}:PROB VAL,{atten}")

        @property
        def bandwidth_limit(self) -> BandwidthLimit:
            """Get the channel bandwidth limit"""
            bwl = self._resource.query(f":CHAN{self._n}:BWL?")
            if "20M" in bwl:
                return BandwidthLimit.BW_20M
            elif "200M" in bwl:
                return BandwidthLimit.BW_200M
            elif "FULL" in bwl:
                return BandwidthLimit.BW_FULL
            else:
                raise ValueError(f"Unable to parse channel bandwidth limit {bwl}")

        @bandwidth_limit.setter
        def bandwidth_limit(self, bw: BandwidthLimit):
            """Set the channel bandwidth limit"""
            self._resource.write(f":CHAN{self._n}:BWL {bw}")


        @property
        def coupling(self) -> ChannelCoupling:
            """Get the channel coupling mode"""
            return ChannelCoupling(self._resource.query(f":CHAN{self._n}:COUP?"))

        @coupling.setter
        def coupling(self, coupling: ChannelCoupling):
            """Set the channel coupling mode"""
            self._resource.write(f":CHAN{self._n}:COUP {coupling}")

        @property
        def unit(self) -> ChannelUnit:
            """Get the channel units"""
            return ChannelUnit(self._resource.query(f":CHAN{self._n}:UNIT?"))

        @unit.setter
        def unit(self, unit: ChannelUnit):
            """Set the channel units"""
            self._resource.write(f":CHAN{self._n}:UNIT {unit}")

        @property
        def offset(self) -> float:
            """Get the channel offset in volts"""
            return float(self._resource.query(f":CHAN{self._n}:OFFS?"))

        @offset.setter
        def offset(self, offset: float):
            """Set the channel offset in volts"""
            self._resource.write(f":CHAN{self._n}:OFFS {offset}")

    # ----- Measurement Mode -----

    @property
    def measure(self) -> bool:
        """Get the state of the measurement mode"""
        return self._resource.query(":MEAS?").strip() == "ON"

    @measure.setter
    def measure(self, enabled: bool):
        """Set the state of measurement mode on or off"""
        self._resource.write(f":MEAS {"ON" if enabled else "OFF"}")

    @property
    def measure_mode(self) -> SDSMeasurementMode:
        """Get the measurement mode of the scope (simple or advanced)"""
        return SDSMeasurementMode(self._resource.query(":MEAS:MODE?").strip())

    @measure_mode.setter
    def measure_mode(self, mode: SDSMeasurementMode):
        """Set the measurement mode of the scope (simple or advanced)"""
        self._resource.write(f":MEAS:MODE {mode}")

    # ----- Advanced Measurements -----

    def clear_advanced_meas(self):
        """Clear all advanced measurements"""
        self._resource.write(":MEAS:ADV:CLE")

    def advanced_measurement(self, n: int) -> "AdvancedMeasurement":
        """Get the advanced measurement object based on its index"""
        assert 1 <= n <= 12, "Advanced measurement indexes are 1-12"
        return self.AdvancedMeasurement(self, n)

    class AdvancedMeasurement:
        """An instance of an advanced measurement"""

        def __init__(self, parent: "SDS2000X", n: int):
            self._n = n
            self._parent = parent
            self._resource = parent._resource

        @property
        def enabled(self) -> bool:
            """Get the measurement enabled state"""
            return self._resource.query(f":MEAS:ADV:P{self._n}?") == "ON"

        @enabled.setter
        def enabled(self, enabled: bool):
            """Set the measurement enabled state"""
            self._resource.write(f":MEAS:ADV:P{self._n} {"ON" if enabled else "OFF"}")

        @property
        def meas_type(self) -> AdvancedMeasurementType:
            """Get the measurement type"""
            return AdvancedMeasurementType(self._resource.query(f":MEAS:ADV:P{self._n}:TYPE?"))

        @meas_type.setter
        def meas_type(self, meas_type: AdvancedMeasurementType):
            """Set the measurement type"""
            self._resource.write(f":MEAS:ADV:P{self._n}:TYPE {meas_type}")

        @property
        def source1(self) -> tuple[ChannelType, int] | None:
            """Get the channel for the measurement's first (primary) source (0 = none)"""
            src = self._resource.query(f":MEAS:ADV:P{self._n}:SOUR1?")
            # Stars mean nothing
            if "***" in src:
                return None
            # Channel type is the first letter
            chan_type = ChannelType(src[0])
            # Channel number is the remaining digits
            chan_number = int(src[1:])
            # Return
            return (chan_type, chan_number)

        @source1.setter
        def source1(self, source_cfg: tuple[ChannelType, int]):
            """Set the channel for the measurement's first (primary) source"""
            chan_type = source_cfg[0]
            n = source_cfg[1]
            self._resource.write(f":MEAS:ADV:P{self._n}:SOUR1 {chan_type}{n}")

        @property
        def source2(self) -> tuple[ChannelType, int] | None:
            """Get the channel for the measurement's secondary source (0 = none)"""
            src = self._resource.query(f":MEAS:ADV:P{self._n}:SOUR2?")
            # Stars mean nothing
            if "***" in src:
                return None
            # Channel type is the first letter
            chan_type = ChannelType(src[0])
            # Channel number is the remaining digits
            chan_number = int(src[1:])
            # Return
            return (chan_type, chan_number)

        @source2.setter
        def source2(self, chan_type: ChannelType, n: int):
            """Set the channel for the measurement's secondary source"""
            self._resource.write(f":MEAS:ADV:P{self._n}:SOUR2 {chan_type}{n}")

        @property
        def value(self) -> float:
            """Get the current value of the measurement"""
            return float(self._resource.query(f":MEAS:ADV:P{self._n}:VAL?"))