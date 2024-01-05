from pathlib import Path

from db_models import TrackModel


class Track(TrackModel):
    def __init__(self, id:int=None, path:Path=None):

    # def upload_to_s3(self, filepath):






class Library:
    """A high-level class for handling samples
    """
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def sync(self, samples_query):
        """ Based on a SQL sample query, the query downloads all the file from the database
        and store it locally in the folder path
        :return:
        """


    # UPLOAD MUSIC ONLINE ##########################################################################
    def upload_track_on_s3(self, ):
        """
        ---
        :return:
        """

    # ORGANISE MUSIC LOCALLY #######################################################################
    @staticmethod
    def file_name_formatter():
        """A formatting tool for storing the music harmoniously in the folder
        ----
        :return:
        """

    def get(self):
        """Gets a sample
        ---
        :return:
        """