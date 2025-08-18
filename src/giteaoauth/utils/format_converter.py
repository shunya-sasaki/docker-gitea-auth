"""Utility for converting string formats."""


class FormatConverter:
    """A utility class for converting string formats."""

    @staticmethod
    def snake_to_camel(word: str) -> str:
        """Convert snake_case to camelCase."""
        components = word.split("_")
        return components[0] + "".join(x.capitalize() for x in components[1:])
