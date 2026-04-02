from sqlalchemy import Column, String
from app.core.database import Base

class Nursery(Base):
    __tablename__ = "nursery"

    nursery_id = Column(String, primary_key=True, index=True)
    nursery_name = Column(String, nullable=False)
