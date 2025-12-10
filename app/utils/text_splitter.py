class TextSplitter:
    """Utility for chunking text into smaller segments."""

    def split(self, text: str) -> list[str]:
        return text.split("\n")