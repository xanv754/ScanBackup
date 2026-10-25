import re


class IxpVendorExtractor:
    """Obtains the vendor of an Ixp interface from its name (RF-003).

    Rules, in order:
    1. `Posicion <letter><digits>` gives that code (`A6`, `B6`).
    2. `Peering Privado <side> - <side>` gives the side that is not `CANTV`; if neither is
       `CANTV`, the last one.
    3. Otherwise, the last word of the name.

    The vendor is returned in uppercase.
    """

    OPERATOR_CANTV = "cantv"
    SIDE_STRIP_CHARS = " )"
    POSITION_PATTERN = re.compile(r"\bposici[oó]n\s+([a-z]\d+)\b", re.IGNORECASE)
    PEERING_PATTERN = re.compile(r"\bpeering\s+privado\s+(.+?)\s+-\s+(.+)$", re.IGNORECASE)
    LAST_WORD_PATTERN = re.compile(r"([^\s()]+)[\s()]*$")

    def extract(self, name: str | None) -> str | None:
        """Return the vendor found in the name, or `None` if the name is empty."""
        if not name or not name.strip():
            return None
        vendor = self._from_position(name) or self._from_peering(name) or self._from_last_word(name)
        return vendor.upper() if vendor else None

    def _from_position(self, name: str) -> str | None:
        """Return the switch position code (`A6`) if the name has one."""
        match = self.POSITION_PATTERN.search(name)
        return match.group(1) if match else None

    def _from_peering(self, name: str) -> str | None:
        """Return the side of a private peering that is not CANTV, without the closing `)`."""
        match = self.PEERING_PATTERN.search(name)
        if match is None:
            return None
        first_side = match.group(1).strip(self.SIDE_STRIP_CHARS)
        second_side = match.group(2).strip(self.SIDE_STRIP_CHARS)
        if first_side.lower() == self.OPERATOR_CANTV:
            return second_side
        if second_side.lower() == self.OPERATOR_CANTV:
            return first_side
        return second_side

    def _from_last_word(self, name: str) -> str | None:
        """Return the last word of the name, without trailing parentheses."""
        match = self.LAST_WORD_PATTERN.search(name)
        return match.group(1) if match else None
