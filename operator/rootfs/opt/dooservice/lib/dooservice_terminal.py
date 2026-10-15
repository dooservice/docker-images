"""Escape sequences in what a terminal program prints, read byte by byte: no patterns.

CSI is ESC [ with parameter and intermediate bytes and one final byte; OSC is ESC ] up
to BEL or the string terminator, and so are DCS, SOS, PM and APC (ESC P, X, ^, _); any
other is ESC, its intermediate bytes and one more.
A sequence cut at the end of the buffer runs to its end, as it would once the rest arrives.
"""

from __future__ import annotations

from dooservice_constants import (
    BEL,
    CONTROL_STRING_OPENS,
    CSI_OPEN,
    ESC,
    HYPERLINK,
    OSC_OPEN,
    SECURE_URL,
    STRING_TERMINATOR,
)


class TerminalText:
    @staticmethod
    def csi_end(data: bytes, start: int) -> int:
        index = start + 2
        while index < len(data) and 0x30 <= data[index] <= 0x3F:
            index += 1
        while index < len(data) and 0x20 <= data[index] <= 0x2F:
            index += 1
        return index + 1 if index < len(data) and 0x40 <= data[index] <= 0x7E else index

    @staticmethod
    def escape_end(data: bytes, start: int) -> int:
        index = start + 1
        while index < len(data) and 0x20 <= data[index] <= 0x2F:
            index += 1
        if index < len(data) and data[index] == ESC:
            return index
        return min(index + 1, len(data))

    @staticmethod
    def osc_end(data: bytes, start: int) -> tuple[int, int, bool]:
        """Where its body ends, where the sequence ends, and whether it was terminated."""
        index = start + 2
        while index < len(data):
            if data[index] == BEL:
                return index, index + 1, True
            if data[index] == ESC:
                closed = index + 1 < len(data) and data[index + 1] == STRING_TERMINATOR
                return index, index + 2 if closed else index, closed
            index += 1
        return index, index, False

    @classmethod
    def pieces(cls, data: bytes):
        """Each run of text as `(None, text)`, each terminated OSC as `(body, b"")`; other sequences dropped."""
        index, text_start = 0, 0
        while index < len(data):
            if data[index] != ESC:
                index += 1
                continue
            if text_start < index:
                yield None, data[text_start:index]
            following = data[index + 1] if index + 1 < len(data) else None
            if following == OSC_OPEN:
                body_end, ends, closed = cls.osc_end(data, index)
                if closed:
                    yield data[index + 2 : body_end], b""
                index = max(ends, index + 1)
            elif following in CONTROL_STRING_OPENS:
                index = max(cls.osc_end(data, index)[1], index + 2)
            elif following == CSI_OPEN:
                index = cls.csi_end(data, index)
            else:
                index = cls.escape_end(data, index)
            text_start = index
        if text_start < len(data):
            yield None, data[text_start:]

    @classmethod
    def plain(cls, data: bytes) -> bytes:
        return b"".join(text for body, text in cls.pieces(data) if body is None)

    @classmethod
    def readable(cls, data: bytes) -> bool:
        """Whether output carries text for a person, not only questions to the terminal."""
        return any(byte > 0x20 for byte in cls.plain(data))

    @classmethod
    def links(cls, data: bytes) -> list[bytes]:
        """The https targets of OSC 8 hyperlinks, in order."""
        found = []
        for body, _ in cls.pieces(data):
            if body is None or not body.startswith(HYPERLINK):
                continue
            _, separator, target = body[len(HYPERLINK) :].partition(b";")
            if separator and target.startswith(SECURE_URL):
                found.append(target)
        return found
