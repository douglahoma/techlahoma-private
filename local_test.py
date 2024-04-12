#!/usr/bin/python3

from dotenv import load_dotenv

load_dotenv()

from app import app

app.run(host="0.0.0.0", port=5000, debug=True)