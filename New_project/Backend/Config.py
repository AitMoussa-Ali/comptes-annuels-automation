from os.path import join, dirname 
from dotenv import load_dotenv
import os
dotenv_path=join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


class Config :
    DB_NAME = os.environ.get("DB_NAME")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    