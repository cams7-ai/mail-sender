from dataclasses import dataclass


@dataclass(frozen=True)
class EmailMessageData:
    recipient: str
    subject: str
    body: str
