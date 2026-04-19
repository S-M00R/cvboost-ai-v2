from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./cvboost.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


# --------------------
# USERS TABLE
# --------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    analyses = relationship("CVAnalysis", back_populates="owner")


# --------------------
# CV ANALYSIS TABLE
# --------------------
class CVAnalysis(Base):
    __tablename__ = "cv_analysis"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String)
    match_score = Column(Integer)
    missing_skills = Column(Text)
    summary = Column(Text)
    cover_letter = Column(Text)
    created_at = Column(String, default=lambda: str(datetime.now()))

    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="analyses")