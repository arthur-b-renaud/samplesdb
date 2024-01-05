from typing import List, Tuple

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, joinedload

from config.alembic_config import DB_URI
from db_models import ArtistModel, TrackModel, ArtistTrackModel, AlbumModel

engine = create_engine(
    DB_URI,
    client_encoding="utf8",
    pool_size=50,
    # Ping the DB before sending the query (cf https://stackoverflow.com/a/66515677)
    pool_pre_ping=True,
)
create_session = sessionmaker(bind=engine, autocommit=False)


def create_artist(session: Session, artist: ArtistModel) -> ArtistModel:
    session.add(artist)
    session.commit()
    return artist


def get_artist(
        session: Session,
        full_name: str = None,
        artist_id: int = None,
) -> ArtistModel:
    query = session.query(ArtistModel)
    if full_name is not None:
        query = query.where(ArtistModel.full_name == full_name)
    if artist_id is not None:
        query = query.where(ArtistModel.id == artist_id)

    artists = query.all()
    if len(artists) > 1:
        raise ValueError("There is more than one artist.")
    if len(artists) == 0:
        raise ValueError("There no artist.")
    return artists[0]


def create_album(session: Session, album: AlbumModel) -> AlbumModel:
    session.add(album)
    session.commit()
    return album


def get_album(
        session: Session,
        title: str = None,
        album_id: int = None,
) -> AlbumModel:
    query = session.query(AlbumModel)
    if title is not None:
        query = query.where(AlbumModel.title == title)
    if album_id is not None:
        query = query.where(AlbumModel.id == album_id)

    albums = query.all()
    if len(albums) > 1:
        raise ValueError("There is more than one album.")
    if len(albums) == 0:
        raise ValueError("There no album.")
    return albums[0]


def create_samples(
    session: Session,
    tracks_and_artists: List[Tuple[TrackModel, List[ArtistModel]]],
) -> List[TrackModel]:
    """
    Create multiple Samples
    :param session: the connexion to the database
    :param tracks_and_artists: List of tuples with TrackModels and ArtistModels of each track. Example:
    >>> tracks_and_artists = [
    >>>     (
    >>>         TrackModel(title="Dark serviettes", album=my_album),     # TrackModel #1
    >>>         [my_arist_1, my_arist_2],                           # ArtistModels for the TrackModel #1
    >>>     ),
    >>>     (
    >>>         TrackModel(title="Deep chenille", album=my_album),       # TrackModel #2
    >>>         [my_arist_1, my_arist_2],                           # ArtistModels for the TrackModel #2
    >>>     ),
    >>> ]

    :return:
    """
    completed_tracks = []
    # For each TrackModel and each ArtistModel, create a relation many-to-many ArtistTrackModel
    for track, artists in tracks_and_artists:
        completed_track = track
        completed_track.artists_tracks = []
        for artist in artists:
            completed_track.artists_tracks.append(ArtistTrackModel(
                artist=artist,
                track=track,
            ))
        completed_tracks.append(completed_track)

    session.add_all(completed_tracks)
    session.commit()

    return completed_tracks


def get_track(
        session: Session,
        title: str = None,
        track_id: int = None,
) -> TrackModel:
    query = session.query(TrackModel)
    if title is not None:
        query = query.where(TrackModel.title == title)
    if track_id is not None:
        query = query.where(TrackModel.id == track_id)

    tracks = (
        query
        .options(joinedload(TrackModel.artists_tracks))
        .all()
    )
    if len(tracks) > 1:
        raise ValueError("There is more than one track.")
    if len(tracks) == 0:
        raise ValueError("There no track.")
    return tracks[0]


if __name__ == "__main__":
    # Create artist
    # with create_session() as conn:
    #     new_artist_1 = create_artist(artist=ArtistModel(full_name="Patrick Sebastien"), session=conn)
    #     new_artist_2 = create_artist(artist=ArtistModel(full_name="Boris Breja"), session=conn)

    # Get artist
    # with create_session() as conn:
    #     created_artist_1 = get_artist(full_name="Patrick Sebastien", session=conn)
    #     created_artist_2 = get_artist(artist_id=2, session=conn)

    # Create album
    # with create_session() as conn:
    #     new_album = create_album(album=AlbumModel(title="My AlbumModel"), session=conn)

    # Get album
    # with create_session() as conn:
    #     created_album = get_album(title="My AlbumModel", session=conn)
    #     print(created_album)

    # Create tracks
    # with create_session() as conn:
    #     my_arist_1 = get_artist(full_name="Boris Breja", session=conn)
    #     my_arist_2 = get_artist(full_name="Patrick Sebastien", session=conn)
    #
    #     my_album = get_album(title="My AlbumModel", session=conn)
    #
    #     my_samples = [
    #         (
    #             TrackModel(title="Dark serviettes", album=my_album),
    #             [my_arist_1, my_arist_2],
    #         ),
    #         (
    #             TrackModel(title="Deep chenille", album=my_album),
    #             [my_arist_1, my_arist_2],
    #         ),
    #     ]
    #
    #     created_samples = create_samples(
    #         session=conn,
    #         tracks_and_artists=my_samples,
    #     )
    #
    #     print(created_samples)

    # Get track
    with create_session() as conn:
        my_track = get_track(title="Dark serviettes", session=conn)
        print("TrackModel:", my_track)
        print("ArtistModels:", [artist_track.artist for artist_track in my_track.artists_tracks])
        print("AlbumModel:", my_track.album)

