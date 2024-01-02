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
        metadata={
            "sa": Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
        },
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
class Artist(IdBaseMixin, TimestampBaseMixin):

    __tablename__ = "artist"
    __sa_dataclass_metadata_key__ = "sa"

    full_name: str = field(default=None, metadata={"sa": Column(String)})

    # Relation with ArtistSample
    artists_samples: List[ArtistSample] = field(
        default_factory=list,
        metadata={"sa": relationship("ArtistSample", lazy="noload", cascade="merge")},
    )


@mapper_registry.mapped
@dataclass
class ArtistSample(IdBaseMixin, TimestampBaseMixin):
    """Many-to-many relation between Artist and Sample"""

    __tablename__ = "artist_sample"
    __sa_dataclass_metadata_key__ = "sa"

    # Relation with Artist
    artist_ref: int = field(
        default=None,
        metadata={
            "sa": Column(ForeignKey("artist.id", ondelete="SET NULL"), index=True)
        },
    )
    artist: Artist = field(
        default=None,
        metadata={"sa": relationship("Artist", back_populates="artists_samples")},
    )

    # Relation with Sample
    sample_ref: int = field(
        default=None,
        metadata={
            "sa": Column(ForeignKey("sample.id", ondelete="SET NULL"), index=True)
        },
    )
    sample: Artist = field(
        default=None,
        metadata={"sa": relationship("Sample", back_populates="artists_samples")},
    )


@mapper_registry.mapped
@dataclass
class Sample(IdBaseMixin, TimestampBaseMixin):

    __tablename__ = "sample"
    __sa_dataclass_metadata_key__ = "sa"

    # Relation with ArtistSample
    artists_samples: List[ArtistSample] = field(
        default_factory=list,
        metadata={"sa": relationship("ArtistSample", lazy="noload", cascade="merge")},
    )

    title: str = field(default=None, metadata={"sa": Column(String)})
    album_title: str = field(default=None, metadata={"sa": Column(String)})

    # Music metadata
    annotation: str = field(default=None, metadata={"sa": Column(String)})
    bpm: int = field(default=None, metadata={"sa": Column(Integer)})
    rates_khz: float = field(default=None, metadata={"sa": Column(Float)})
    bitrate_kbps: float = field(default=None, metadata={"sa": Column(Float)})
    nb_channels: int = field(default=None, metadata={"sa": Column(Integer)})
    bit_depth: int = field(default=None, metadata={"sa": Column(Integer)})
    duration_secs: int = field(default=None, metadata={"sa": Column(Integer)})

    # File storage
    wav_s3_url: str = field(default=None, metadata={"sa": Column(String)})
    wav_s3_metadata: Dict = field(default=None, metadata={"sa": Column(JSON)})
    mp3_s3_url: str = field(default=None, metadata={"sa": Column(String)})
    mp3_s3_metadata: Dict = field(default=None, metadata={"sa": Column(JSON)})
