from typing import Protocol

from domain.entities import EmailMessageData


class EmailSender(Protocol):
    def send(self, message: EmailMessageData) -> None:
        pass
