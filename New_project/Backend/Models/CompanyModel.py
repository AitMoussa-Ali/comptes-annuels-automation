from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base
from datetime import date
from sqlalchemy import Date
from datetime import datetime
from sqlalchemy.orm import relationship

class Company(Base):
    
    __tablename__ = "Companies"
    
    company_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4, 
        unique=True,
        nullable=False
    )
    
    company_name : Mapped[str] = mapped_column(
        String(40),
        unique=True,
        nullable=False
    )
    
    company_creation_date : Mapped[date] = mapped_column(
        Date, 
        nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    funds = relationship(
        "Fund", 
        back_populates="company", 
        cascade="all, delete-orphan"
    )