import os
from flask import Flask, render_template, redirect, url_for, session
from dotenv import load_dotenv
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load environment variables from .env file
load_dotenv()

# Access environment variables
org_id = os.getenv("ORG_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

# Landing Page
@app.route('/')
def landing():
    login_url = f"https://{org_id}.app.neoncrm.com/np/oauth/auth?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
    return render_template('landing.html', login_url=login_url)

# OAuth Callback Route
@app.route('/authorize')
def authorize():
    authorization_code = requests.args.get('code')
    
    # Make HTTP request to Neon CRM to request the access token
    neon_access_token_url = 'https://app.neoncrm.com/np/oauth/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'code': authorization_code,
        'grant_type': 'authorization_code'
    }
    response = requests.post(neon_access_token_url, data=data)
    access_token = response.json().get('access_token')
    
    # Save access token to the session
    session['access_token'] = access_token
    
    # Redirect to another route
    return redirect(url_for('neon_redirect'))
# Error Page
@app.route('/error')
def error():
    return render_template('error.html')

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

if __name__ == '__main__':
    app.run(debug=True)
