from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from sqlalchemy import (
    JSON, Column, DateTime, ForeignKey, Index, Integer, String, Text, create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, relationship, sessionmaker


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.getenv("CAMPAIGN_DATABASE_URL", f"sqlite:///{PROJECT_ROOT / 'storage' / 'campaigns.db'}")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})


class Base(DeclarativeBase):
    pass


def utc_column() -> Column:
    return Column(DateTime(timezone=True), nullable=False)


class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(String, primary_key=True)
    name = Column(String(200), nullable=False)
    product_name = Column(String(200), nullable=False, index=True)
    status = Column(String(30), nullable=False, default="draft")
    inputs = Column(JSON, nullable=False, default=dict)
    brief = Column(JSON, nullable=False, default=dict)
    approval = Column(JSON, nullable=False, default=dict)
    created_time = utc_column()
    updated_time = utc_column()
    sections = relationship("GeneratedOutput", back_populates="campaign", cascade="all, delete-orphan")
    versions = relationship("OutputVersion", back_populates="campaign", cascade="all, delete-orphan")
    quality_reports = relationship("QualityReport", back_populates="campaign", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="campaign", cascade="all, delete-orphan")
    exports = relationship("Export", back_populates="campaign", cascade="all, delete-orphan")


class CampaignBrief(Base):
    __tablename__ = "campaign_briefs"
    campaign_id = Column(String, ForeignKey("campaigns.id", ondelete="CASCADE"), primary_key=True)
    data = Column(JSON, nullable=False, default=dict)
    updated_time = utc_column()


class GeneratedOutput(Base):
    __tablename__ = "generated_outputs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    section = Column(String(100), nullable=False)
    data = Column(JSON, nullable=False, default=dict)
    status = Column(String(30), nullable=False, default="ready")
    updated_time = utc_column()
    campaign = relationship("Campaign", back_populates="sections")
    __table_args__ = (Index("ix_generated_outputs_campaign_section", "campaign_id", "section", unique=True),)


class OutputVersion(Base):
    __tablename__ = "output_versions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    section = Column(String(100), nullable=False)
    previous_value = Column(JSON, nullable=False)
    source = Column(String(30), nullable=False)
    editor = Column(String(100), nullable=False, default="user")
    created_time = utc_column()
    campaign = relationship("Campaign", back_populates="versions")
    __table_args__ = (Index("ix_output_versions_campaign_section", "campaign_id", "section"),)


class QualityReport(Base):
    __tablename__ = "quality_reports"
    id = Column(String, primary_key=True)
    campaign_id = Column(String, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    data = Column(JSON, nullable=False)
    outdated = Column(Integer, nullable=False, default=0)
    created_time = utc_column()
    campaign = relationship("Campaign", back_populates="quality_reports")


class Asset(Base):
    __tablename__ = "assets"
    id = Column(String, primary_key=True)
    campaign_id = Column(String, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    asset_type = Column(String(30), nullable=False)
    status = Column(String(30), nullable=False, default="ready")
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    metadata_json = Column("metadata", JSON, nullable=False, default=dict)
    created_time = utc_column()
    campaign = relationship("Campaign", back_populates="assets")


class Export(Base):
    __tablename__ = "exports"
    id = Column(String, primary_key=True)
    campaign_id = Column(String, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    format = Column(String(10), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=False)
    package_version = Column(String, nullable=False)
    approval_report_id = Column(String, nullable=True)
    created_time = utc_column()
    campaign = relationship("Campaign", back_populates="exports")


SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Any:
    with Session(engine) as db:
        yield db


def init_db() -> None:
    Path(DATABASE_URL.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(engine)
