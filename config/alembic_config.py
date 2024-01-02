import os

from dotenv import load_dotenv

load_dotenv()

DB_URI = (
    f"postgresql://"
    f"{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
    f"@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
)