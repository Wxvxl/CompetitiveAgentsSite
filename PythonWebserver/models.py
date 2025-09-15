from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from dotenv import load_dotenv
from datetime import datetime, timezone
import os

load_dotenv() 
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    users = relationship("User", back_populates="group")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String)
    isAdmin = Column(Boolean, default=False)
    role = Column(String, default="student")
    group_id = Column(Integer, ForeignKey("groups.id"))
    group = relationship("Group", back_populates="users")
    agents = relationship("Agent", back_populates="user")
    
class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    upload_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user = relationship("User", back_populates="agents")