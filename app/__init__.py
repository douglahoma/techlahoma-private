import os

from .config import Config
from flask import Flask, session
from flask_session import Session
from dotenv import load_dotenv
from .secretkey import SecretKey
# Load environment variables from .env file
load_dotenv()



app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = SecretKey()

sess = Session()
sess.init_app(app)

from app import views
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
