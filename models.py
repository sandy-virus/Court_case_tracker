from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class CaseResult(Base):
    __tablename__ = "case_results"
    id = Column(Integer, primary_key=True, index=True)
    petitioner = Column(String(255))
    respondent = Column(String(255))
    last_hearing = Column(String(50))
    next_hearing = Column(String(50))
    latest_order_url = Column(String(500))


class CaseQuery(Base):
    __tablename__ = "case_queries"
    id = Column(Integer, primary_key=True, index=True)
    case_type = Column(String(50), index=True)
    case_number = Column(String(50), index=True)
    filing_year = Column(String(10), index=True)
    response_html = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Foreign key to CaseResult
    result_id = Column(Integer, ForeignKey("case_results.id"))
    result = relationship("CaseResult")
