from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Model


class TaskOrm(Model):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[Optional[str]]
