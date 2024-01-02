from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config.alembic_config import DB_URI
from db_models import Artist, Sample, ArtistSample

engine = create_engine(
    DB_URI,
    client_encoding="utf8",
    pool_size=50,
    # Ping the DB before sending the query (cf https://stackoverflow.com/a/66515677)
    pool_pre_ping=True,
)
create_session = sessionmaker(bind=engine, autocommit=False)


def create_artist(session: Session, artist: Artist) -> Artist:
    session.add(artist)
    session.commit()
    return artist


def get_artist(
    session: Session,
    full_name: str = None,
    artist_id: int = None,
) -> Artist:
    query = session.query(Artist)
    if full_name is not None:
        query = query.where(Artist.full_name == full_name)
    if artist_id is not None:
        query = query.where(Artist.id == artist_id)

    artists = query.all()
    if len(artists) > 1:
        raise ValueError("There is more than one artist.")
    if len(artists) == 0:
        raise ValueError("There no artist.")
    return artists[0]


def create_samples(
    session: Session,
    samples: List[Sample],
    artists: List[Artist],
) -> List[Sample]:
    # For each Sample and each Artist, create a relation many-to-many ArtistSample
    for idx, sample in enumerate(samples):
        samples[idx].artists_samples = []
        for artist in artists:
            samples[idx].artists_samples.append(ArtistSample(
                artist=artist,
                sample=sample,
            ))

    session.add_all(samples)
    session.commit()

    return samples


if __name__ == "__main__":
    # Create artist
    with create_session() as conn:
        created_artist = create_artist(artist=Artist(full_name="Patrick Sebastien"), session=conn)

    # Get artist
    with create_session() as conn:
        created_artist_1 = get_artist(full_name="Boris Breja", session=conn)
        created_artist_2 = get_artist(artist_id=3, session=conn)

    # Create samples
    with create_session() as conn:
        my_arist_1 = get_artist(full_name="Boris Breja", session=conn)
        my_arist_2 = get_artist(full_name="Patrick Sebastien", session=conn)

        my_samples = [
            Sample(title="Dark serviettes"),
            Sample(title="Deep chenille"),
        ]

        created_samples = create_samples(
            session=conn,
            samples=my_samples,
            artists=[my_arist_1, my_arist_2],
        )

        print(created_samples)
