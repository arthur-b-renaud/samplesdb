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
class ArtistModel(IdBaseMixin, TimestampBaseMixin):

    __tablename__ = "artist"
    __sa_dataclass_metadata_key__ = "sa"

    full_name: str = field(default=None, metadata={"sa": Column(String)})

    # Relation with ArtistTrack
    artists_tracks: List[ArtistTrackModel] = field(
        default_factory=list,
        metadata={"sa": relationship("ArtistTrackModel", lazy="noload")},
    )


@mapper_registry.mapped
@dataclass
class ArtistTrackModel(IdBaseMixin, TimestampBaseMixin):
    """Many-to-many relation between ArtistModel and TrackModel"""

    __tablename__ = "artist_track"
    __sa_dataclass_metadata_key__ = "sa"

    # Relation with ArtistModel
    artist_ref: int = field(
        default=None,
        metadata={
            "sa": Column(ForeignKey("artist.id", ondelete="CASCADE"), index=True)
        },
    )
    artist: ArtistModel = field(
        default=None,
        metadata={"sa": relationship("ArtistModel", back_populates="artists_tracks")},
    )

    # Relation with Track
    track_ref: int = field(
        default=None,
        metadata={"sa": Column(ForeignKey("track.id", ondelete="CASCADE"), index=True)},
    )
    track: TrackModel = field(
        default=None,
        metadata={"sa": relationship("TrackModel", back_populates="artists_tracks")},
    )


@mapper_registry.mapped
@dataclass
class AlbumModel(IdBaseMixin, TimestampBaseMixin):

    __tablename__ = "album"
    __sa_dataclass_metadata_key__ = "sa"

    title: str = field(default=None, metadata={"sa": Column(String, nullable=False)})

    # Relation with Track
    tracks: List[TrackModel] = field(
        default_factory=list,
        metadata={"sa": relationship("TrackModel", lazy="noload")},
    )


@mapper_registry.mapped
@dataclass
class TrackModel(IdBaseMixin, TimestampBaseMixin):

    __tablename__ = "track"
    __sa_dataclass_metadata_key__ = "sa"

    # Relation with ArtistTrack
    artists_tracks: List[ArtistTrackModel] = field(
        default_factory=list,
        metadata={"sa": relationship("ArtistTrackModel", lazy="noload")},
    )

    # Relation with Album
    album_ref: int = field(
        default=None,
        metadata={"sa": Column(ForeignKey("album.id", ondelete="CASCADE"), index=True)},
    )
    album: AlbumModel = field(
        default=None,
        metadata={"sa": relationship("AlbumModel", back_populates="tracks")},
    )

    title: str = field(default=None, metadata={"sa": Column(String, nullable=False)})

    # Music metadata
    annotation: str = field(default=None, metadata={"sa": Column(String)})
    bpm: int = field(default=None, metadata={"sa": Column(Integer)})
    rates_hz: int = field(default=None, metadata={"sa": Column(Float)})
    bitrate_bps: int = field(default=None, metadata={"sa": Column(Float)})
    nb_channels: int = field(default=None, metadata={"sa": Column(Integer)})
    bit_depth: int = field(default=None, metadata={"sa": Column(Integer)})
    duration_secs: int = field(default=None, metadata={"sa": Column(Integer)})
    styles: List[str] = field(
        default_factory=list, metadata={"sa": Column(ARRAY(String))}
    )
    instruments: List[str] = field(
        default_factory=list, metadata={"sa": Column(ARRAY(String))}
    )
    moods: List[str] = field(
        default_factory=list, metadata={"sa": Column(ARRAY(String))}
    )

    # File storage
    s3_url: str = field(default=None, metadata={"sa": Column(String)})
    s3_etag_hash: str = field(default=None, metadata={"sa": Column(String)})
    wav_etag_hash: str = field(default=None, metadata={"sa": Column(String)})
    wav_s3_url: str = field(default=None, metadata={"sa": Column(String)})
    wav_s3_metadata: Dict = field(default=None, metadata={"sa": Column(JSON)})
    mp3_etag_hash: str = field(default=None, metadata={"sa": Column(String)})
    mp3_s3_url: str = field(default=None, metadata={"sa": Column(String)})
    mp3_s3_metadata: Dict = field(default=None, metadata={"sa": Column(JSON)})