import uuid

from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class UserData(Base):
    __tablename__ = "users_data"

    user_id: Mapped[str] = mapped_column(
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )
    graph_blob: Mapped[bytes] = mapped_column(nullable=False)
