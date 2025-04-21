import enum


class ChannelStatus(str, enum.Enum):
    open = "open"
    private = "private"


class ActionType(str, enum.Enum):
    comment = "comment"
    reaction = "reaction"
    view = "view"


class ToneType(str, enum.Enum):
    positive = "positive"
    negative = "negative"
    critical = "critical"
    question = "question"