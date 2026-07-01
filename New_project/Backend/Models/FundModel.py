from sqlalchemy import  String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base
import enum
from sqlalchemy import Enum, Boolean
from datetime import datetime
from datetime import date
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
# from Models.CompanyModel import Company

class AncientStatus(str, enum.Enum): 
    A = "A"
    N = "N"

class Fund(Base):
    
    __tablename__ = "Funds"
    
    fund_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4, 
        unique=True
    )
    
    fund_name: Mapped[str] = mapped_column(
        String(40),
        unique=True
    )
    
    fund_anciente: Mapped[AncientStatus] = mapped_column(
        Enum(AncientStatus, name="anciente_enum"),
        nullable=False
    ) 
        
    fund_bilingue : Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    fund_creation_date : Mapped[date] = mapped_column(
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
    
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("Companies.company_id"),
        nullable=False
    )
    
    company : Mapped["Company"] = relationship("Company", back_populates="funds")
    
    @property
    def company_name(self) -> str:
        return self.company.company_name if self.company else ""
    
    