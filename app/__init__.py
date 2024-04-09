import os

from .config import Config
from .secretkey import SecretKey
from flask import Flask
from flask_session import Session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = SecretKey()

sess = Session()
sess.init_app(app)

# When testing locally just make sure you don't have the DOMAIN key defined
# in the version of the .env file you're using and everyone should be okay.
if (not os.getenv("DOMAIN")):
    os.environ["REDIRECT_URI"] = "{}{}".format(
        os.getenv("DEBUG_DOMAIN"),
        os.getenv("REDIRECT_URI")
    )

from app import views
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)