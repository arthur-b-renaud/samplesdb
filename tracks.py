import hashlib
import json
import os
from typing import List

import boto3
import magic
from botocore.exceptions import ClientError, NoCredentialsError

from config import config
from db_helper import create_session, get_album, get_artist, create_tracks
from db_models import TrackModel, ArtistModel, AlbumModel
from libs.audio_properties import get_audio_properties
from s3helper import S3Helper


class TrackManager:
    def __init__(self, track_model: TrackModel = None, file_path: str=None):
        self.file_path = file_path
        self.track_model = track_model
        self.conn = create_session()

    @staticmethod
    def define_s3key(file_path, album_name='UNKNOWN_ALBUM', artists_names:List=None):
        # Compute MD5 hash
        md5_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        md5_hex = md5_hash.hexdigest()
        artists_names = '_'.join(artists_names) if artists_names else 'UNKNOWN_ARTIST'
        # Concatenate MD5 hash and file title
        return f"tracks/{md5_hex}---{artists_names}-{album_name}-{os.path.basename(file_path)}"

    def download(self, s3_file_key, local_file_path):
        try:
            s3 = boto3.client('s3')
            s3.download_file(config.S3_BUCKET, s3_file_key, local_file_path)
        except NoCredentialsError:
            raise ValueError("Credentials not available")
        except ClientError as e:
            raise Exception(f"An error occurred: {e}")
        finally:
            del s3

    def upload(
            self,
            file_path,
            artists: List[ArtistModel],
            album: AlbumModel,
            track_model: TrackModel,
            s3_helper=None,
            conn=None
    ):
        # 1. Upload file_path to s3
        extra_args = {"ACL": "public-read",
                      "ContentType": f"Content-Type: {magic.from_file(file_path, mime=True)}"}
        s3_obj = s3_helper.upload_file(self.define_s3key(file_path), file_path, extra_args=extra_args)

        # 2. Add url to model
        track_model.s3_url = s3_obj['url']
        headers = s3_helper.bulk_download_get_headers([s3_obj['key']])
        track_model.s3_etag_hash = headers[0]['ETag'][1:-1]
        track_model.s3_metadata = json.dumps(headers[0], sort_keys=True, default=str)

        # 3. Populate the model
        track_model.title = os.path.basename(file_path)
        track_model.album = album
        audio_props = get_audio_properties(file_path)
        track_model.bpm = audio_props['bpm']
        track_model.rates_hz = audio_props['rates_hz']
        track_model.bitrate_bps = audio_props['bitrate_bps']
        track_model.nb_channels = audio_props['nb_channels']
        track_model.bit_depth = audio_props['bit_depth']
        track_model.duration_secs = audio_props['duration_secs']
        self.track_model = track_model

        # Upload to database
        new_track = [(self.track_model, artists)]
        created_samples = create_tracks(
            session=conn,
            tracks_and_artists=new_track,
        )
        print(created_samples)

    def __del__(self):
        self.conn.close()


if __name__ == '__main__':
    s3_helper = S3Helper()
    self = tm = TrackManager()

    with create_session() as conn:
        my_arist_1 = get_artist(full_name="Boris Breja", session=conn)
        my_arist_2 = get_artist(full_name="Patrick Sebastien", session=conn)
        my_album = get_album(title="My AlbumModel", session=conn)

        tm.upload(
            file_path="/home/arthur/data/music/full_track_ddim50.mp3",
            artists=[my_arist_1, my_arist_2],
            album=my_album,
            track_model=TrackModel(),
            s3_helper=s3_helper,
            conn=conn
        )

    with create_session() as conn:
        query = conn.query(TrackModel)
        track = query.where(TrackModel.id == 1)
        print(track)

