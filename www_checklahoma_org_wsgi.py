from pathlib import Path
from dotenv import load_dotenv

ENV_FILE = f"{Path.home()}/.env"

load_dotenv(dotenv_path=ENV_FILE)

# import flask app but need to call it "application" for WSGI to work
from app import app as application  # noqa