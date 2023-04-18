# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2022 Neradoc
#
# SPDX-License-Identifier: MIT
"""
`mcp23017_scanner`
================================================================================

Scan a matrix keyboard with an API modelled after the keypad module


* Author(s): Neradoc

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

"""

from digitalio import DigitalInOut, Pull
from supervisor import ticks_ms

try:
    # Only used for typing
    from typing import Tuple, Optional, Iterable, Set
    from microcontroller import Pin
except ImportError:
    pass

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/Neradoc/CircuitPython_mcp23017_scanner.git"


class Event:
    """
    A key transition event.

    :param int key_number: the key number
    :param bool pressed: ``True`` if the key was pressed; ``False`` if it was released.
    :param int timestamp: The time in milliseconds that the keypress occurred in the
                          `supervisor.ticks_ms` time system.  If specified as None,
                          the current value of `supervisor.ticks_ms` is used.
    """

    def __init__(self, key: int, pressed: bool, timestamp: int = None):
        self.key_number = key
        """The key number."""
        self.timestamp = timestamp or ticks_ms()
        """The timestamp."""
        self.pressed = pressed
        """True if the event represents a key down (pressed) transition.
        The opposite of released."""

    @property
    def released(self) -> bool:
        """True if the event represents a key up (released) transition.
        The opposite of pressed."""
        return not self.pressed

    def __eq__(self, other: object) -> bool:
        """Two Event objects are equal if their key_number and pressed/released values
        are equal. Note that this does not compare the event timestamps."""
        return self.key_number == other.key_number and self.pressed == other.pressed

    def __hash__(self) -> int:
        """Returns a hash for the Event, so it can be used in dictionaries, etc..
        Note that as events with different timestamps compare equal,
        they also hash to the same value."""
        return self.key_number << 1 + int(self.pressed)


class EventQueue:
    """
    A queue of Event objects, filled by a scanner.
    """

    def __init__(self):  # , max_events=64):
        self._outq = []
        self._inq = []

    def append(self, event: Event) -> None:
        """Append an event at the end of the queue"""
        self._inq.append(event)

    def get(self) -> Event:
        """
        Return the next key transition event.
        Return None if no events are pending.
        """
        if self._outq:
            return self._outq.pop()
        if len(self._inq) == 1:
            return self._inq.pop()
        if self._inq:
            self._outq = list(reversed(self._inq))
            self._inq.clear()
            return self._outq.pop()
        return None

    def get_into(self, event: Event) -> bool:
        """
        Store the next key transition event in the supplied event, if available,
        and return True. If there are no queued events, do not touch event
        and return False.
        Note: in python this does not optimize to avoid allocating.
        """
        next_event = self.get()
        if next_event:
            event.key_number = next_event.key_number
            event.timestamp = next_event.timestamp
            event.pressed = next_event.pressed
            return True
        return False

    def clear(self) -> None:
        """Clear any queued key transition events."""
        self._outq.clear()
        self._inq.clear()

    def __bool__(self) -> bool:
        """
        True if len() is greater than zero.
        This is an easy way to check if the queue is empty.
        """
        return len(self) > 0

    def __len__(self) -> int:
        """
        Return the number of events currently in the queue.
        Used to implement len().
        """
        return len(self._outq) + len(self._inq)


class McpScanner:
    """
    Base class for MCP scanners.

    .. property:: events

        The `EventQueue` associated with this Scanner. (read-only)
    """

    def __init__(
        self,
        mcp: any,
        irq: Optional[Pin] = None,
    ):
        self._key_count = 0
        self.mcp = mcp
        self.keys_state = set()
        self.events = EventQueue()
        self.irq = None
        if irq:
            self.irq = DigitalInOut(irq)
            self.irq.switch_to_input(Pull.UP)

    @property
    def key_count(self) -> int:
        """The number of keys that are being scanned. (read-only)"""
        return self._key_count

    def _scan_pins(self) -> Set[int]:  # pylint:disable=no-self-use
        return Set()

    def update(self) -> None:
        """
        Run the scan and create events in the event queue.
        """
        timestamp = ticks_ms()
        # scan the matrix, find Neo
        current_state = self._scan_pins()
        # use set algebra to find released and pressed keys
        released_keys = self.keys_state - current_state
        pressed_keys = current_state - self.keys_state
        # create the events into the queue
        for key in released_keys:
            self.events.append(Event(key, False, timestamp))
        for key in pressed_keys:
            self.events.append(Event(key, True, timestamp))
        # end
        self.keys_state = current_state

    def reset(self) -> None:
        """
        Reset the internal state of the scanner to assume that all keys are now
        released. Any key that is already pressed at the time of this call will
        therefore cause a new key-pressed event to occur on the next scan.
        """
        self.events.clear()
        self.keys_state.clear()

    def deinit(self) -> None:
        """Release the IRQ pin"""
        if self.irq:
            self.irq.deinit()
            self.irq = None
        # TODO: reset the mcp configuration

    def __enter__(self) -> "McpScanner":
        """No-op used by Context Managers."""
        return self

    def __exit__(self, type_er, value, traceback) -> None:
        """Automatically deinitializes when exiting a context."""
        self.deinit()


class McpMatrixScanner(McpScanner):
    """
    Class to scan a matrix of keys connected to the MCP chip.

    Columns are on port A and inputs.
    Rows are on port B and outputs.
    """

    def __init__(
        self,
        mcp: any,
        row_pins: Iterable[int],
        column_pins: Iterable[int],
        irq: Optional[Pin] = None,
    ):
        super().__init__(mcp, irq)
        self._key_count = len(column_pins) * len(row_pins)
        self.columns = column_pins
        self.rows = row_pins
        # set port A to output (columns)
        mcp.iodira = 0x00
        # set port B to input (rows) all pull ups
        mcp.iodirb = 0xFF
        mcp.gppub = 0xFF
        # set interrupts
        if irq:
            # TODO: configure mcp based on row and column numbers
            #       to leave the other pins free to use ?
            mcp.interrupt_enable = 0xFF00
            mcp.default_value = 0xFFFF
            # compare input to default value (1) or previous value (0)
            mcp.interrupt_configuration = 0xFF00
            mcp.io_control = 0x44  # Interrupt as open drain and mirrored
            mcp.clear_ints()

    def _scan_pins(self) -> Set[int]:
        """Scan the matrix and return the list of keys down"""
        pressed = set()
        num_cols = len(self.columns)
        for scan_column in self.columns:
            # set all outputs to 1 on port A except the scan_column
            self.mcp.gpioa = 0xFF - (1 << scan_column)
            if self.irq is None or not self.irq.value:
                # read the input
                inputs = self.mcp.gpiob
                if inputs:
                    # adds (columns,row) if the row is 0 too
                    for row in self.rows:
                        if (inputs >> row) & 1 == 0:
                            pressed.add(scan_column + num_cols * row)
        # set back port A to default
        self.mcp.gpioa = 0xFF
        return pressed

    def key_number_to_row_column(self, key_number: int) -> Tuple[int]:
        """Convert key number to row, column"""
        row = key_number // len(self.columns)
        column = key_number % len(self.columns)
        return (row, column)

    def row_column_to_key_number(self, row: int, column: int) -> int:
        """Convert row, column to key number"""
        return row * len(self.columns) + column


class McpKeysScanner(McpScanner):
    """
    Class to scan a key per pin of the MCP chip.

    Pins 0-7 are on port A. Pins 8-15 are on port B.
    """

    def __init__(
        self,
        mcp: any,
        pins: Iterable[int],
        irq: Optional[Pin] = None,
    ):
        super().__init__(mcp, irq)
        self._key_count = len(pins)
        self.pins = pins
        self.pin_bits = sum(1 << x for x in pins)
        # set port A and B to input all pull ups
        mcp.iodir = 0xFFFF & self.pin_bits
        mcp.gppu = 0xFFFF & self.pin_bits
        # set interrupts
        if irq:
            # set interrupts
            mcp.interrupt_enable = 0xFFFF & self.pin_bits
            mcp.default_value = 0xFFFF & self.pin_bits
            # compare input to default value (1) or previous value (0)
            mcp.interrupt_configuration = 0xFFFF & self.pin_bits
            mcp.io_control = 0x44  # Interrupt as open drain and mirrored
            mcp.clear_ints()

    def _scan_pins(self) -> Set[int]:
        """Scan the buttons and return the list of keys down"""
        pressed = set()
        inputs = self.mcp.gpio & self.pin_bits
        for pin in self.pins:
            if inputs & (1 << pin) == 0:
                pressed.add(pin)
        return pressed
