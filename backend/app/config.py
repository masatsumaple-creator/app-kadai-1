import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "mysql+pymysql://user:password@localhost:3306/kakeibo"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
