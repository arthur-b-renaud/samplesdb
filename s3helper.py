import glob
import itertools
import json
import os
from io import BytesIO
from pathlib import Path
from typing import Any, Generator, List

import aioboto3
import boto3 as boto3
from tqdm import tqdm

from config import config
from libs.AsyncTask import AsyncTask


class S3Helper:
    def __init__(self):
        self.s3_resource = boto3.resource(
            "s3",
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_REGION,
        )
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_REGION,
        )
        self.aioboto3_session = aioboto3.Session(
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_REGION,
        )
        self.stackabot_bucket = self.s3_resource.Bucket(config.S3_BUCKET)

    @staticmethod
    def get_aws_public_url(object_key):
        return (
            f"https://{config.S3_BUCKET}.s3.{config.AWS_REGION}"
            + f".amazonaws.com/{object_key}"
        )

    def upload_file(self, object_key: str, file, extra_args: dict = None):
        """
        Function to upload a file from path, with progress bar
        :param object_key: The destination key in S3
        :param file: Can be either the path of the file or the file content
        :param extra_args: ExtraArgs in upload_fileobj
        """
        if extra_args is None:
            extra_args = {}

        if isinstance(file, str):
            file_size = os.stat(file).st_size
            file_content = open(file, "rb")
        elif isinstance(file, BytesIO):
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            file_content = file
        else:
            raise ValueError(
                "Invalid data type. Supported types are str (file path) and io.StringIO."
            )

        with tqdm(total=file_size, unit="B", unit_scale=True, desc=object_key) as pbar:
            self.s3_client.upload_fileobj(
                file_content,
                config.S3_BUCKET,
                object_key,
                Callback=lambda bytes_transferred: pbar.update(bytes_transferred),
                ExtraArgs=extra_args,
            )
        return {
            "url": self.get_aws_public_url(object_key),
            "bucket": config.S3_BUCKET,
            "region": config.AWS_REGION,
            "key": object_key,
        }

    def get_s3_folder_checksums(self, s3_folder_name: str) -> set:
        """
        Compute checksum of files in a folder in S3
        :param s3_folder_name: The path of the folder in S3
        :return: The list of checksums
        """
        checksums = []
        for obj in self.stackabot_bucket.objects.filter(Prefix=s3_folder_name):
            filename = obj.key[len(s3_folder_name) :]

            if not filename:
                continue
            checksums.append(obj.e_tag[1:-1])
        return set(checksums)

    def check_folder_checksum(self, s3_folder_path: str, local_folder_path: str) -> bool:
        checksum_local_file = os.path.join(local_folder_path, config.S3_FOLDER_CHECKSUMS_FILENAME)
        if not os.path.isfile(checksum_local_file):
            return False
        bucket = self.s3_resource.Bucket(config.S3_BUCKET)
        with open(checksum_local_file) as checksum_file:
            checksum_local = {line.strip() for line in checksum_file}
        checksum_s3 = {
            obj.e_tag[1:-1]
            for obj in bucket.objects.filter(Prefix=s3_folder_path)
            if obj.key[-1] != "/"
        }
        return set(checksum_local) == set(checksum_s3)

    def download_folder(
        self,
        s3_folder_name: str,
        local_destination: str,
        download_checksum: bool = False,
        enable_tqdm: bool = False,
    ) -> None:
        bucket = self.s3_resource.Bucket(config.S3_BUCKET)
        checksums = []
        for obj in bucket.objects.filter(Prefix=s3_folder_name):
            filename = obj.key[len(s3_folder_name) :]
            if not filename:
                continue
            filename = filename[1:] if filename[0] == "/" else filename
            destination_path = os.path.join(local_destination, filename)
            if not os.path.exists(os.path.dirname(destination_path)):
                os.makedirs(os.path.dirname(destination_path))

            # If the download file is a folder and the folder already exists, skip it
            if os.path.exists(destination_path) and os.path.isdir(destination_path):
                continue

            if enable_tqdm:
                file_length = self.s3_client.head_object(
                    Bucket=config.S3_BUCKET, Key=obj.key
                )["ContentLength"]
                with tqdm(file_length, unit="B", unit_scale=True, desc=destination_path) as pbar:
                    self.s3_client.download_file(
                        Bucket=config.S3_BUCKET,
                        Key=obj.key,
                        Filename=destination_path,
                        Callback=lambda bytes_transferred: pbar.update(bytes_transferred),
                    )
            else:
                bucket.download_file(obj.key, destination_path)
            checksums.append(obj.e_tag[1:-1])

        if download_checksum:
            with open(
                os.path.join(local_destination, config.S3_FOLDER_CHECKSUMS_FILENAME),
                "w",
            ) as f:
                for item in checksums:
                    f.write(f"{item}\n")

    def upload_folder(
        self,
        local_folder: str,
        s3_folder_key: str,
        extra_args: dict = None,
        tqdm_desc: str = "Upload folder to S3",
        concurrency: int = 100,
    ) -> None:
        data_list = [
            {
                "s3_key": str(Path(s3_folder_key) / Path(file).relative_to(Path(local_folder))),
                "file_path": file,
                "extra_args": extra_args,
            }
            for file in glob.glob(str(Path(local_folder) / "**/*"))
            if Path(file).is_file()
        ]
        return self.bulk_upload_files(
            data_list=data_list, tqdm_desc=tqdm_desc, concurrency=concurrency
        )

    def list_folder_keys(self, folder_path: str) -> Generator:
        for obj in self.stackabot_bucket.objects.filter(Prefix=folder_path):
            yield obj.key

    def bulk_upload_files(
        self,
        data_list: List[dict],
        tqdm_desc: str = "Bulk upload files to S3",
        concurrency: int = 100,
        enable_get_headers: bool = False,
        skip_if_exists: bool = False,
    ):
        """
        Upload multiple files asynchronously
        :param data_list: The list of files to upload. List of dicts :
            - "s3_key" (str) : The key of the uploaded object in S3
            - "file_path" (str) : The path of the file to upload
            - "extra_args" (dict) : Optional. ExtraArgs in upload_fileobj
            (ex : {'ACL': 'public-read', 'ContentType': 'image/jpeg'})
        :param tqdm_desc: The description of the tqdm bar
        :param concurrency: The maximum concurrency of uploads
        :param enable_get_headers: If true, headers will be fetched for each object
        :param skip_if_exists: If true, upload is skipped if the object already exists
        :return:
        """
        aioboto3_session = self.aioboto3_session
        bucket = self.stackabot_bucket
        aioboto3_session = self.aioboto3_session

        class MyAsyncTask(AsyncTask):
            async def _do_task(self, data: Any):
                async with aioboto3_session.client("s3") as s3:
                    object_exists = False
                    if skip_if_exists:
                        object_exists = await s3.head_object(Bucket=bucket.name, Key=data["s3_key"])
                    if not object_exists:
                        await s3.upload_fileobj(
                            open(data["file_path"], "rb"),
                            config.S3_BUCKET,
                            data["s3_key"],
                            ExtraArgs=data.get("extra_args"),
                        )
                        if enable_get_headers:
                            headers = await s3.head_object(Bucket=bucket.name, Key=data["s3_key"])
                        else:
                            headers = None

                    return {
                        "s3_key": data["s3_key"],
                        "bucket": bucket.name,
                        "headers": headers,
                        "s3_url": S3Helper.get_aws_public_url(data["s3_key"]),
                    }

        # Deduplicate dicts
        key = lambda x: json.dumps(  # noqa E731 do not assign a lambda expression
            x, ensure_ascii=False, default=str, sort_keys=True
        )
        unique_data_list = [
            next(x) for _, x in itertools.groupby(sorted(data_list, key=key), key=key)
        ]

        return MyAsyncTask().apply(
            data_list=unique_data_list,
            tqdm_desc=tqdm_desc,
            concurrency=concurrency,
        )

    def bulk_download_files(
        self,
        data_list: List[dict],
        tqdm_desc: str = "Bulk download files from S3",
        concurrency: int = 10,
        skip_if_file_exists: bool = False,
    ):
        """
        Download multiple files asynchronously
        :param data_list: The list of files to upload. List of dicts :
            - "s3_key" (str) : The key of the object in S3
            - "file_path" (str) : The path of the file to download
        :param tqdm_desc: The description of the tqdm bar
        :param concurrency: The maximum concurrency of downloads
        :param skip_if_file_exists: If True, the function will skip the download if the file already
        exists
        :return:
        """
        aioboto3_session = self.aioboto3_session

        class MyAsyncTask(AsyncTask):
            async def _do_task(self, data: Any):
                async with aioboto3_session.client("s3") as s3:
                    try:
                        await s3.download_file(
                            config.S3_BUCKET,
                            data["s3_key"],
                            data["file_path"],
                        )
                    except: # noqa
                        raise ValueError('Error on Key : "{}"'.format(data["s3_key"]))

        # Deduplicate dicts
        key = lambda x: json.dumps(  # noqa E731 do not assign a lambda expression
            x, ensure_ascii=False, default=str, sort_keys=True
        )
        unique_data_list = [
            next(x) for _, x in itertools.groupby(sorted(data_list, key=key), key=key)
        ]

        # Skip files if already found local
        if skip_if_file_exists:
            unique_data_list = [x for x in unique_data_list if not os.path.isfile(x["file_path"])]

        return MyAsyncTask().apply(
            data_list=unique_data_list,
            tqdm_desc=tqdm_desc,
            concurrency=concurrency,
        )

    def bulk_download_get_headers(
        self,
        s3_keys: List[str],
        tqdm_desc: str = "Bulk get headers from S3",
        concurrency: int = 10,
    ):
        """
        Download multiple files asynchronously
        :param s3_keys: The list of keys to head
        :param tqdm_desc: The description of the tqdm bar
        :param concurrency: The maximum concurrency of downloads
        :return:
        """
        aioboto3_session = self.aioboto3_session

        class MyAsyncTask(AsyncTask):
            async def _do_task(self, s3_key: Any):
                async with aioboto3_session.client("s3") as s3:
                    try:
                        return await s3.head_object(
                            Bucket=config.S3_BUCKET,
                            Key=s3_key,
                        )
                    except:  # noqa
                        raise ValueError("Error occurred on key {} :".format(s3_key))

        return MyAsyncTask().apply(
            data_list=s3_keys,
            tqdm_desc=tqdm_desc,
            concurrency=concurrency,
        )

    def __del__(self):
        self.s3_resource.meta.client.close()
        self.s3_client.close()


if __name__ == "__main__":
    s3_helper = S3Helper()

    extra_args = {"ACL": "public-read", "ContentType": "Content-Type: audio/mpeg"}
    a = s3_helper.upload_file("tracks/test.mp3", '/home/arthur/data/music/full_track_ddim50.mp3', extra_args=extra_args)