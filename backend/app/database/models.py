from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_system: Mapped[str] = mapped_column(String(80), default="CDSCO_LEGACY_PDF")
    source_url: Mapped[str | None] = mapped_column(Text)
    document_url: Mapped[str | None] = mapped_column(Text)
    alert_title: Mapped[str | None] = mapped_column(Text)
    alert_type: Mapped[str] = mapped_column(String(40), index=True)
    publication_date: Mapped[str | None] = mapped_column(String(32), index=True)
    retrieved_at: Mapped[str | None] = mapped_column(String(40))
    original_filename: Mapped[str] = mapped_column(Text)
    local_raw_path: Mapped[str | None] = mapped_column(Text)
    content_hash_sha256: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    mime_type: Mapped[str | None] = mapped_column(String(100))
    page_count: Mapped[int | None] = mapped_column(Integer)
    extraction_status: Mapped[str] = mapped_column(String(40), default="EXTRACTED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    records: Mapped[list["ParsedRegulatoryRecord"]] = relationship(back_populates="source_document")


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_system: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(32))
    parser_version: Mapped[str | None] = mapped_column(String(40))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    records_seen: Mapped[int] = mapped_column(Integer, default=0)
    records_inserted: Mapped[int] = mapped_column(Integer, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, default=0)


class ParsedRegulatoryRecord(Base):
    __tablename__ = "parsed_regulatory_records"
    __table_args__ = (UniqueConstraint("source_document_id", "source_row", name="uq_document_source_row"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_document_id: Mapped[int] = mapped_column(ForeignKey("source_documents.id"), index=True)
    source_page: Mapped[int | None] = mapped_column(Integer)
    source_row: Mapped[int] = mapped_column(Integer)
    source_bbox: Mapped[list | None] = mapped_column(JSON)
    alert_type: Mapped[str] = mapped_column(String(40), index=True)
    raw_drug_name: Mapped[str | None] = mapped_column(Text, index=True)
    raw_batch_number: Mapped[str | None] = mapped_column(Text, index=True)
    raw_manufacturer: Mapped[str | None] = mapped_column(Text, index=True)
    raw_manufacturer_address: Mapped[str | None] = mapped_column(Text)
    raw_manufacturing_date: Mapped[str | None] = mapped_column(String(80))
    raw_expiry_date: Mapped[str | None] = mapped_column(String(80))
    raw_failure_reason: Mapped[str | None] = mapped_column(Text)
    raw_laboratory: Mapped[str | None] = mapped_column(Text)
    raw_authority: Mapped[str | None] = mapped_column(Text)
    raw_remarks: Mapped[str | None] = mapped_column(Text)
    raw_firm_reply: Mapped[str | None] = mapped_column(Text)
    raw_cells: Mapped[list | None] = mapped_column(JSON)
    raw_row_text: Mapped[str] = mapped_column(Text)
    parsed_manufacturing_date: Mapped[str | None] = mapped_column(String(16))
    parsed_expiry_date: Mapped[str | None] = mapped_column(String(16))
    parse_status: Mapped[str] = mapped_column(String(32), index=True)
    parser_name: Mapped[str] = mapped_column(String(80))
    parser_version: Mapped[str] = mapped_column(String(40))
    warnings: Mapped[list | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    source_document: Mapped[SourceDocument] = relationship(back_populates="records")
    manufacturer_alias: Mapped["ManufacturerAlias | None"] = relationship(back_populates="record", uselist=False)
    drug_alias: Mapped["DrugAlias | None"] = relationship(back_populates="record", uselist=False)


class CanonicalManufacturer(Base):
    __tablename__ = "canonical_manufacturers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    canonical_name: Mapped[str] = mapped_column(Text)
    normalized_name: Mapped[str] = mapped_column(Text, unique=True, index=True)
    resolution_status: Mapped[str] = mapped_column(String(32), default="NORMALIZATION_CLUSTER", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    aliases: Mapped[list["ManufacturerAlias"]] = relationship(back_populates="entity", cascade="all, delete-orphan")


class ManufacturerAlias(Base):
    __tablename__ = "manufacturer_aliases"
    __table_args__ = (UniqueConstraint("source_record_id", name="uq_manufacturer_alias_record"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey("canonical_manufacturers.id"), index=True)
    source_record_id: Mapped[int] = mapped_column(ForeignKey("parsed_regulatory_records.id"), index=True)
    source_mention: Mapped[str] = mapped_column(Text)
    display_name: Mapped[str] = mapped_column(Text)
    normalized_mention: Mapped[str] = mapped_column(Text, index=True)
    source_address: Mapped[str | None] = mapped_column(Text)
    normalized_address: Mapped[str | None] = mapped_column(Text)
    match_method: Mapped[str] = mapped_column(String(40))
    match_score: Mapped[float] = mapped_column(Float)
    review_status: Mapped[str] = mapped_column(String(32), default="NAME_EQUALITY_ONLY", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    entity: Mapped[CanonicalManufacturer] = relationship(back_populates="aliases")
    record: Mapped[ParsedRegulatoryRecord] = relationship(back_populates="manufacturer_alias")


class CanonicalDrug(Base):
    __tablename__ = "canonical_drugs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    canonical_name: Mapped[str] = mapped_column(Text)
    normalized_name: Mapped[str] = mapped_column(Text, unique=True, index=True)
    strengths: Mapped[list | None] = mapped_column(JSON)
    dosage_forms: Mapped[list | None] = mapped_column(JSON)
    resolution_status: Mapped[str] = mapped_column(String(32), default="NORMALIZATION_CLUSTER", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    aliases: Mapped[list["DrugAlias"]] = relationship(back_populates="entity", cascade="all, delete-orphan")


class DrugAlias(Base):
    __tablename__ = "drug_aliases"
    __table_args__ = (UniqueConstraint("source_record_id", name="uq_drug_alias_record"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey("canonical_drugs.id"), index=True)
    source_record_id: Mapped[int] = mapped_column(ForeignKey("parsed_regulatory_records.id"), index=True)
    source_mention: Mapped[str] = mapped_column(Text)
    normalized_mention: Mapped[str] = mapped_column(Text, index=True)
    strengths: Mapped[list | None] = mapped_column(JSON)
    dosage_forms: Mapped[list | None] = mapped_column(JSON)
    match_method: Mapped[str] = mapped_column(String(40))
    match_score: Mapped[float] = mapped_column(Float)
    review_status: Mapped[str] = mapped_column(String(32), default="NAME_EQUALITY_ONLY", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    entity: Mapped[CanonicalDrug] = relationship(back_populates="aliases")
    record: Mapped[ParsedRegulatoryRecord] = relationship(back_populates="drug_alias")


class EntityMatch(Base):
    __tablename__ = "entity_matches"
    __table_args__ = (
        UniqueConstraint("entity_type", "pair_key", name="uq_entity_match_pair"),
        Index("ix_entity_match_decision", "entity_type", "decision", "review_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(24))
    pair_key: Mapped[str] = mapped_column(String(129))
    left_mention: Mapped[str] = mapped_column(Text)
    right_mention: Mapped[str] = mapped_column(Text)
    left_normalized: Mapped[str] = mapped_column(Text)
    right_normalized: Mapped[str] = mapped_column(Text)
    match_method: Mapped[str] = mapped_column(String(40))
    match_score: Mapped[float] = mapped_column(Float)
    decision: Mapped[str] = mapped_column(String(24))
    review_status: Mapped[str] = mapped_column(String(32), default="UNREVIEWED")
    evidence: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class WebUsageEvent(Base):
    __tablename__ = "web_usage_events"
    __table_args__ = (Index("ix_usage_type_created", "event_type", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    event_type: Mapped[str] = mapped_column(String(40), index=True)
    entity_type: Mapped[str | None] = mapped_column(String(24))
    entity_id: Mapped[str | None] = mapped_column(String(120))
    query: Mapped[str | None] = mapped_column(Text)
    filters: Mapped[dict | None] = mapped_column(JSON)
    metadata_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
