import os
from flask import Flask, render_template, redirect, url_for, session, request
from dotenv import load_dotenv
import requests

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Access environment variables
org_id = os.getenv("ORG_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
api_key = os.getenv("API_KEY")
logout_url = os.getenv("LOGOUT_URL")
# and when we get the session secret key, we encode it into bytes
session_secret_key = os.getenv("SESSION_SECRET_KEY").encode()

# set a secret key for the 'session' object.
# The 'session' object in Flask is what allows us to store information
# specific to a user from one request to the next. This is implemented
# on top of cookies signs the cookies cryptographically. As a result,
# while the user is able to look at the contents of the cookie, they cannot
# modify it, unless they know the secret key used for signing.
# In order to use sessions we must first set a secret key.
app.secret_key = session_secret_key

# Landing Page
@app.route('/')
def landing():
    login_url = f"https://{org_id}.app.neoncrm.com/np/oauth/auth?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
    return render_template('landing.html', login_url=login_url)

# OAuth Callback Route
@app.route('/authorize')
def authorize():
    # first let's pull the 'code' URL query parameter using Flask's 'request'
    # object, which contains the data related to the HTTP request sent by
    # the client's web browser to our Flask application. The 'code' parameter
    # is what NeonCRM sends back following a successful OAuth login by the
    # constituent.
    authorization_code = request.args.get('code')

    # Then we can use the 'requests' Python library to construct and send
    # an HTTP request to NeonCRM using this authorization code, in order
    # to get the access token that represents the constituent's Account id.
    neon_access_token_url = 'https://app.neoncrm.com/np/oauth/token'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'code': authorization_code,
        'grant_type': 'authorization_code'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(neon_access_token_url, data=payload, headers=headers)
    access_token = response.json().get('access_token')

    # Save access token to the session
    session['access_token'] = access_token

    # ---------------- API User Authentication --------------------------
    # Now, let's authenticate ourselves as an API user and get
    # the userSessionId we need to actually pull info from NeonCRM
    # about our constituent (and, to send new info to NeonCRM about them!
    # -------------------------------------------------------------------
    #
    # First, we construct the URL needed to log in
    # neon_api_login_url = f'https://api.neoncrm.com/neonws/services/api/common/login?login.apiKey={api_key}&login.orgid={org_id}'
    neon_api_login_url = f'https://api.neoncrm.com/neonws/services/api/common/login?login.apiKey={api_key}&login.orgid={org_id}'
    #
    # Next, we use the 'requests' library to send the GET request to the API
    api_response = requests.get(neon_api_login_url)
    print(api_response.text)
    #
    # Then we can check the content of the response to our request
    if api_response.status_code == 200:
        # if the request itself (Note: distinct from the login attempt!) was
        # successful, we'll parse the response's JSON data
        api_response_data = api_response.json()
        #
        # before checking to see if the login attempt worked.
        #
        # For context, a successful loginResponse would look something like:
        # "loginResponse": {
        #     "operationResult": "SUCCESS",
        #     "responseMessage": "User logged in.",
        #     "responseDateTime": "2012-12-25T21:26:41.981-06:00",
        #     "userSessionId": "T1356492402097"
        # }
        #
        login_response = api_response_data.get('loginResponse', {})
        operation_result = login_response['operationResult']
        # we'll also make a dictionary of error code descriptions taken from
        # the NeonCRM API documentation
        error_code_descriptions = {
            '1': "An unknown system error. Often, these are generated due to a badly formed API request or a problem in NeonCRM.",
            '2': "Indicates a temporary problem with NeonCRM's servers.",
            '3': "A user session ID must be included with the request. Retrieve a session ID using the Login method.",
            '4': "The provided user session ID is invalid.",
            '5': "The user account associated with this API key does not have sufficient permissions to perform the desired operation."
        }

        if operation_result == 'SUCCESS':
            # if the api login WAS a success, we'll grab the userSessionId
            user_session_id = login_response.get('userSessionId')
            print(user_session_id)
            if user_session_id:
                # and print it out for logging/debugging purposes
                print('Great news! Login worked. User session ID is: ', user_session_id)
            else:
                print("login failed. No user session ID received.")
        else:
            # if the login was not a success, we will print out our terrible news
            print("I am mortified to admit that the api login failed. Maybe someone canceled the atlas user account? The system replied: ", operation_result)
            # if there are specific errors provided, we'll print them out too
            if 'errors' in login_response:
                errors_list = login_response['errors']['error']
                for error in errors_list:
                    error_code = str(error['errorCode'])
                    error_message = error['errorMessage']
                    error_description = error_code_descriptions.get(error_code, "No description available.")
                    print(f"Error code: {error_code}, Message: {error_message}. Description: {error_description}")
    else:
        # if the HTTP request itself to the API failed to connect,
        # we'll admit our problem and print our the status code:
        print('Sadly, could not even connect to the api...', api_response.status_code)
    #
    #
    # ------------------------------------------------------------------------------- #
    # ----------- and that is the end of the API User Authentication block ---------- #
    # ------------------------------------------------------------------------------- #


    return render_template('neon_redirect.html', user=access_token, logout_url=logout_url)

# @app.route('/neon_redirect')
# def neon_redirect(user_id):
#     return render_template('neon_redirect.html', logout_url=logout_url)


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
