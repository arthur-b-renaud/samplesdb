from pathlib import Path
from typing import List

from db_helper import create_session, get_album, get_artist
from db_models import TrackModel, ArtistModel, AlbumModel


class TrackController:
    def __init__(self, track_model: TrackModel=None):
        self.track_model = track_model
        self.conn = create_session()

    def download(self):
        pass

    def upload(self, filepath, artists: List[ArtistModel], track_model: TrackModel):
        # 1. Upload filepath to s3
        # ...

        # 2. Add url to model
        track_model.mp3_s3_url = "htts://...."


        self.track_model = track_model

    def get_album(self, **kwargs):
        return get_album(session=self.conn, **kwargs)

    def get_artist(self, **kwargs):
        return get_artist(session=self.conn, **kwargs)

    def upload(self, filepath, artists_names: List[str], album_name: str, track_model: TrackModel):
        pass

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


1/0


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