import hashlib
import os
from typing import List

import boto3
import magic
from botocore.exceptions import ClientError, NoCredentialsError

from db_helper import create_session, get_album, get_artist
from db_models import TrackModel, ArtistModel
from s3helper import S3Helper
from config import config

# Added for S3 support
s3_helper = S3Helper()


class TrackController:
    def __init__(self, track_model: TrackModel = None):
        self.track_model = track_model
        self.conn = create_session()

    @staticmethod
    def define_s3key(filepath):
        # Compute MD5 hash
        md5_hash = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        md5_hex = md5_hash.hexdigest()

        # Concatenate MD5 hash and file title
        return f"tracks/{md5_hex}---{os.path.basename(filepath)}"

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
            filepath,
            artists: List[ArtistModel],
            track_model: TrackModel,
            s3_helper=None
    ):
        # 1. Upload filepath to s3
        extra_args = {"ACL": "public-read",
                      "ContentType": f"Content-Type: {magic.from_file(filepath, mime=True)}"}
        s3_obj = s3_helper.upload_file(self.define_s3key(filepath), filepath, extra_args=extra_args)

        # 2. Add url to model
        track_model.mp3_s3_url = s3_obj.url
        track_model.title = os.path.basename(filepath)
        self.track_model = track_model

    def __del__(self):
        self.conn.close()


if __name__ == '__main__':
    tc = TrackController()

    with create_session() as conn:
        my_arist_1 = get_artist(full_name="Boris Breja", session=conn)
        my_arist_2 = get_artist(full_name="Patrick Sebastien", session=conn)
        my_album = get_album(title="My AlbumModel", session=conn)

        tc.upload(
            filepath="/path/to/track.mp3",
            artists=[my_arist_1, my_arist_2],
            track_model=TrackModel(title="track.mp3", album=my_album)
        )

    with create_session() as conn:
        query = conn.query(TrackModel)
        track = query.where(TrackModel.id == 1)
        print(track)

1 / 0

#
# class Library:
#     """A high-level class for handling samples
#     """
#     def __init__(self, folder_path):
#         self.folder_path = folder_path
#
#     def sync(self, samples_query):
#         """ Based on a SQL sample query, the query downloads all the file from the database
#         and store it locally in the folder path
#         :return:
#         """
#
#
#     # UPLOAD MUSIC ONLINE ##########################################################################
#     def upload_track_on_s3(self, ):
#         """
#         ---
#         :return:
#         """
#
#     # ORGANISE MUSIC LOCALLY #######################################################################
#     @staticmethod
#     def file_name_formatter():
#         """A formatting tool for storing the music harmoniously in the folder
#         ----
#         :return:
#         """
#
#     def get(self):
#         """Gets a sample
#         ---
#         :return:
#         """
