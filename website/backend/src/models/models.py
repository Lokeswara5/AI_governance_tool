"""Database models."""
from datetime import datetime
from typing import Optional, Dict
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Organization(Base):
    """Organization model."""
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    api_key = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    policies = relationship("Policy", back_populates="organization")
    users = relationship("User", back_populates="organization")

class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    role = Column(String, default="user")  # admin, user
    created_at = Column(DateTime, default=datetime.utcnow)
    organization = relationship("Organization", back_populates="users")

class Policy(Base):
    """Policy model."""
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    version = Column(String)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    organization = relationship("Organization", back_populates="policies")
    analyses = relationship("PolicyAnalysis", back_populates="policy")

class PolicyAnalysis(Base):
    """Policy analysis results."""
    __tablename__ = "policy_analyses"

    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey("policies.id"))
    overall_score = Column(Float, nullable=False)
    is_compliant = Column(Boolean, nullable=False)
    category_scores = Column(JSON)  # Store as JSON
    found_patterns = Column(JSON)  # Store as JSON
    proximity_scores = Column(JSON)  # Store as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    policy = relationship("Policy", back_populates="analyses")