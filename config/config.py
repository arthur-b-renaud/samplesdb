import os

from dotenv import load_dotenv
load_dotenv()

# ========== AWS ================================================================================ #

# Config
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = "eu-west-3"

# S3
S3_BUCKET = "maximix"

# The file which contains checksums of all files of a model. Used to check version of local model.
S3_FOLDER_CHECKSUMS_FILENAME = "s3_checksums.txt"
