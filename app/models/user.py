from sqlalchemy import Column, String, TIMESTAMP, text, CheckConstraint
from app.core.database import Base

class UserTable(Base):
    __tablename__ = "user_table"

    user_id = Column(String, primary_key=True, index=True)
    user_username = Column(String, unique=True, nullable=False, index=True)
    user_password = Column(String, nullable=False)

    # Only admin or employee allowed
    role = Column(String, nullable=False)

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )

    __table_args__ = (
        CheckConstraint("role in ('admin', 'employee')", name="role_check"),
    )
