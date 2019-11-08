import enum
from dataclasses import dataclass
from typing import Optional


class ItemType(enum.Enum):
    CHANNEL = "channel"
    PLAYLIST = "playlist"

    @classmethod
    def from_(cls, value):
        if isinstance(value, cls):
            return value

        if value == "ItemType.CHANNEL":
            return cls.CHANNEL
        elif value == "ItemType.PLAYLIST":
            return cls.PLAYLIST
        else:
            raise ValueError(f"Invalid item type: {value}")


@dataclass
class Thumbnail:
    url: str
    width: Optional[int]
    height: Optional[int]


@dataclass
class SearchItem:
    id: str
    title: str
    description: str
    thumbnail: Thumbnail
    channel_title: str
    item_type: ItemType
