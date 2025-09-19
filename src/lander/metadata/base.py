"""Base class for metadata formatters."""

from abc import ABC, abstractmethod
from typing import List, Optional, Union


class MetaTagFormatterBase(ABC):
    """A base class for generating HTML meta tags."""

    def __str__(self) -> str:
        """Create the metadata tags."""
        return self.as_html()

    @property
    @abstractmethod
    def tag_attributes(self) -> List[str]:
        """The names of class properties that create tags."""
        raise NotImplementedError

    def as_html(self) -> str:
        """Create the metadata HTML tags."""
        tags: List[str] = []
        for prop in self.tag_attributes:
            self.extend_not_none(tags, getattr(self, prop))
        return "\n".join(tags) + "\n"

    @staticmethod
    def extend_not_none(
        entries: List[str], new_item: Optional[Union[str, List[str]]]
    ) -> None:
        """Extend a list with new items if they are not None."""
        if new_item is None:
            return
        if isinstance(new_item, list):
            entries.extend(new_item)
        else:
            entries.append(new_item)
