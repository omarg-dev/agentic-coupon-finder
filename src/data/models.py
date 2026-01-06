from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship
from .database import Base 

class Website(Base):
    __tablename__ = "websites"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True, nullable=False) # MUST be unique
    is_shop = Column(Boolean, default=False)
    
    # Audit fields
    created_at = Column(DateTime, server_default=func.now())
    last_scraped = Column(DateTime, nullable=True)

    coupons = relationship("Coupon", back_populates="website", cascade="all, delete-orphan") 
    # cascade="all, delete-orphan": If you delete a Website, delete its coupons too.

class Coupon(Base):
    __tablename__ = "coupons"
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"), nullable=False)
    
    code = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    
    # Status
    is_working = Column(Boolean, default=None) 
    last_tested = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


    website = relationship("Website", back_populates="coupons")

    # CONSTRAINT: A specific code can only exist ONCE per website.
    __table_args__ = (
        UniqueConstraint('website_id', 'code', name='_website_code_uc'),
    )

class TestLog(Base):
    __tablename__ = "test_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"))
    timestamp = Column(DateTime, server_default=func.now())
    
    status = Column(String)  # "SUCCESS", "FAILED", "PARTIAL"
    message = Column(String) # e.g., "Login pop-up blocked path"
    
    # Optional screenshot path for debugging
    screenshot_path = Column(String, nullable=True) 
    
    website = relationship("Website")