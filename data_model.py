from __future__ import annotations

import datetime
from dataclasses import dataclass, field, fields
from typing import Dict, List, Optional, Union

from sqlalchemy import (
    ARRAY,
    JSON,
    Boolean,
    Column,
    Computed,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    types,
)
from sqlalchemy.orm import declarative_mixin, registry, relationship

mapper_registry = registry()
Base = mapper_registry.generate_base()

@declarative_mixin
@dataclass
class IdBaseMixin:
    __sa_dataclass_metadata_key__ = "sa"

    id: int = field(init=False, metadata={"sa": Column(Integer, primary_key=True)})


@declarative_mixin
@dataclass
class TimestampBaseMixin:
    __sa_dataclass_metadata_key__ = "sa"

    created_at: datetime.datetime = field(
        init=False,
        metadata={"sa": Column(DateTime, default=datetime.datetime.utcnow, nullable=False)},
    )
    last_update: datetime.datetime = field(
        init=False,
        metadata={
            "sa": Column(
                DateTime,
                default=datetime.datetime.utcnow,
                onupdate=datetime.datetime.utcnow,
                nullable=False,
            )
        },
    )


@mapper_registry.mapped
@dataclass
class Music(IdBaseMixin, TimestampBaseMixin):

    __tablename__ = "music"
    __sa_dataclass_metadata_key__ = "sa"
    
    s3_url: str = field(default=None, metadata={"sa": Column(String, primary_key=True)})
    annotation: str = field(default=None, metadata={"sa": Column(String)})
    bpm: int = field(default=None, metadata={"sa": Column(Integer)})
