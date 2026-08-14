import re


__all__ = ["NamesResolver"]


class NamesResolver:
    """Generate collision-free copied and enumerated names."""

    copy_suffix: str
    _copy_pattern: re.Pattern

    def __init__(self, copy_suffix: str) -> None:
        """Initialize patterns for a localized copy suffix.

        Args:
            copy_suffix: Text placed inside copied-name parentheses.
        """
        self.copy_suffix = copy_suffix
        self._copy_pattern = re.compile(rf" \({re.escape(copy_suffix)}\)| \({re.escape(copy_suffix)} (\d+)\)$")

    def copy(self, name: str, existing_names: list[str]) -> str:
        """Copy name with suffix and numeration.
        If there are already copied names -> pick max copy number.

        Args:
            name (str): name to copy
            existing_names (list[str]): list of existing names

        Returns:
            str: name copy

        Examples:
            section -> section (копия)
            section (копия) -> section (копия 1)
            section (копия 1) -> section (копия 2)
            section_(копия) -> section_(копия) (копия)
            section (копия 1331 131) -> section (копия 1331 131) (копия)
        """
        copy_found = self._copy_pattern.search(name)
        base_name = "".join(name.rsplit(copy_found.group(0), 1)) if copy_found else name
        max_copy_number = self._find_max_copy_number(base_name=base_name, names=existing_names)
        if not copy_found:
            if max_copy_number is None:
                return f"{name} ({self.copy_suffix})"
            return f"{name} ({self.copy_suffix} {max_copy_number + 1})"
        copy_number = int(copy_found.group(1)) if copy_found.group(1) else 0
        if max_copy_number is None:
            max_copy_number = copy_number
        else:
            max_copy_number = max(max_copy_number, copy_number)
        return f"{base_name} ({self.copy_suffix} {max_copy_number + 1})"

    def _find_max_copy_number(self, base_name: str, names: list[str]) -> int | None:
        """Find max copy number along names for given base name.

        Args:
            base_name (str): base name without copy suffix
            existing_names (list[str]): list of names

        Returns:
            int | None: max copy number if at least 1 copy was found, None otherwise
        """
        name_copy_pattern = re.compile(rf"{re.escape(base_name)} \({re.escape(self.copy_suffix)}(?: (\d+))?\)$")
        max_copy_number: int | None = None
        for name in names:
            copy_found = name_copy_pattern.search(name)
            if not copy_found:
                continue
            current_copy_number = int(copy_found.group(1)) if copy_found.group(1) else 0
            if max_copy_number is None:
                max_copy_number = current_copy_number
            else:
                max_copy_number = max(max_copy_number, current_copy_number)
        return max_copy_number

    @staticmethod
    def get_new_base_name(base_name: str, delimiter: str, names: list[str] | None = None) -> str:
        """Get new name consisted of base name and delimiter, considering existing names.

        Args:
            base_name (str): base of the name
            delimiter (str): delimiter between base and name enumeration
            names (list[str] | None, optional): list of existing names to consider while enumeration.
                Defaults to None.

        Returns:
            str: new base name

        Examples:
            Existing names: [base_1, smth, base_2], -> then new name will be base_3.
        """
        if not names:
            return f"{base_name}{delimiter}1"
        base_name_pattern = re.compile(rf"{re.escape(base_name)}{re.escape(delimiter)}\d+")
        base_names = sorted([name for name in names if base_name_pattern.fullmatch(name)])
        if not base_names:
            return f"{base_name}{delimiter}1"
        last_base_name_index = int(base_names[-1].split(delimiter)[-1])
        return f"{base_name}{delimiter}{last_base_name_index+1}"
