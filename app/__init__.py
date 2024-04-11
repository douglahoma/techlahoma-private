from .secretkey import SecretKey
from .config import Config
from flask import Flask
from flask_session import Session

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = SecretKey()

sess = Session()
sess.init_app(app)

from . import views
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
