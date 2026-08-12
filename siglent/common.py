"""Commom utilities for working with all siglent GPIB devices."""

from pyvisa import ResourceManager, errors
from pyvisa.resources import MessageBasedResource

import time

class MessageResource:
    """Base class for all message-based siglent gpib resources."""

    def __init__(self, visa_address: str, rm: ResourceManager):
        res = rm.open_resource(visa_address)
        if isinstance(res, MessageBasedResource):
            self._resource = res
        else:
            raise TypeError("Selected resource isn't a Message-based resource")

    @property
    def identifier(self) -> str:
        """Get the unique identifier of the deivce."""
        return self._resource.query("*IDN?")

    def reset(self):
        """Reset the instrument to a factory defined condition."""
        self._resource.write("*RST")

    def clear(self):
        """Clear the instrument status byte."""
        self._resource.write("*CLS")

    def block_until_complete(self, timeout_ms=10000):
        """Wait until the previous instrument command completes"""
        start_time = time.time()

        # Save the original timeout to restore it later
        orig_timeout = self._resource.timeout
        
        # Shorten timeout for quick polling loops
        self._resource.timeout = 1000 
        
        while True:
            if (time.time() - start_time) * 1000 > timeout_ms:
                self._resource.timeout = orig_timeout
                raise TimeoutError("Instrument failed to become ready within timeout period.")
                
            try:
                # Query *OPC? to check if operations are done
                response = self._resource.query("*OPC?").strip()
                if response == "1":
                    break
            except (errors.VisaIOError, ConnectionError):
                # Suppress I/O errors while the connection is dropping/reconnecting
                time.sleep(0.5)
                continue
                
        # Restore original instrument timeout
        self._resource.timeout = orig_timeout