import os
from flask import Flask, render_template, redirect, url_for, session, request
from dotenv import load_dotenv
import requests
from datetime import datetime

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
# on top of cookies and signs the cookies cryptographically. As a result,
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
                ###! FOR MOCKUP ONLY: And store it in the session (remember, it only lasts 10 minutes)
                session['user_session_id'] = user_session_id

                #######################################################################
                # ------------ Get the Consituent's Information --------------------- #
                # first, construct and make the API call
                consituent_info_url = f"https://api.neoncrm.com/neonws/services/api/account/retrieveIndividualAccount?userSessionId={user_session_id}&accountId={access_token}"
                constituent_info_response = requests.get(consituent_info_url)
                # then, check to see if the API call was successful
                if constituent_info_response.status_code == 200:
                    # if it was, parse it as JSON
                    constituent_data = constituent_info_response.json()
                    # print the response for debugging
                    print(constituent_data)
                    # then grab the data about the account
                    constituent_account_data = constituent_data['retrieveIndividualAccountResponse']['individualAccount']
                    # try to grab the preferred name, but failing that, get the first name
                    constituent_name = constituent_account_data['primaryContact'].get('preferredName', constituent_account_data['primaryContact'].get('firstName'))
                    # print the name for debugging
                    print(f"name: {constituent_name}")
                    # and save the user's name to the session
                    session['constituent_name'] = constituent_name
                    ### Deal with the exception later
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


    return render_template('check_in.html', logout_url=logout_url, name=constituent_name)
















@app.route('/post_checkin', methods=['POST'])
def post_checkin():
    selected_group = request.form.get('selected_group')
    print(selected_group)
    # First, let's create the new Points record in NeonCRM
    # we begin by creating our API request
    # Note ---- we need to double-check that it's okay ------ WE HAVE NOT CODED THAT PART YET
    user_session_id = session['user_session_id']
    access_token = session['access_token']
    # and to include today's date in the name of the record, we'll need to get it
    today = datetime.today()
    formatted_date = today.strftime("%m/%d/%y")
    print(formatted_date)
    checkin_record_name = f'check-in: {selected_group} - {formatted_date}'
    # and format the API request
    checkin_url = f'https://api.neoncrm.com/neonws/services/api/customObjectRecord/createCustomObjectRecord?userSessionId={user_session_id}&customObjectRecord.objectApiName=Points_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=Constituent_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value={access_token}&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=type_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value=check-in&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=subtype_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value={selected_group}&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=name&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value={checkin_record_name}'
    # and post the request
    checkin_response = requests.post(checkin_url)
    #print the raw response for debugging
    print(checkin_response)
    # then, check to see if checkin api call was successful
    if checkin_response.status_code == 200:
        # if it was, parse it as JSON
        checkin_data = checkin_response.json()
        # print it for debugging
        print(checkin_data)
    else:
        print("whoops")
        ##! Fix this later, add error handling

    #######################################################################
    # ------------ Get the Points Info for the Constituent-------------- #
    # first, construct and make the API call
    user_session_id = session['user_session_id']
    access_token = session['access_token']
    points_url = f"https://api.neoncrm.com/neonws/services/api/customObjectRecord/listCustomObjectRecords?userSessionId={user_session_id}&objectApiName=Points_c&customObjectSearchCriteriaList.customObjectSearchCriteria.criteriaField=Constituent_c&customObjectSearchCriteriaList.customObjectSearchCriteria.operator=EQUAL&customObjectSearchCriteriaList.customObjectSearchCriteria.value={access_token}&customObjectOutputFieldList.customObjectOutputField.label=Points Activity&customObjectOutputFieldList.customObjectOutputField.columnName=name&customObjectOutputFieldList.customObjectOutputField.label=Created on&customObjectOutputFieldList.customObjectOutputField.columnName=createTime&customObjectOutputFieldList.customObjectOutputField.label=type&customObjectOutputFieldList.customObjectOutputField.columnName=type_c&customObjectOutputFieldList.customObjectOutputField.label=subtype&customObjectOutputFieldList.customObjectOutputField.columnName=subtype_c"
    points_response = requests.get(points_url)
    # print the raw response for debugging
    print(points_response)
    # then, check to see if points API call was successful
    if points_response.status_code == 200:
        # if it was, parse it as JSON
        points_data = points_response.json()
        # print it for debugging
        print(points_data)
        # Now we'll make a helper function to parse the date from the response records
        def parse_date(date_string):
            return datetime.strptime(date_string, "%m/%d/%y")
        # And then we can extract and transform the points records
        events = []
        for item in points_data["listCustomObjectRecordsResponse"]["searchResults"]["nameValuePairs"]:
            event = {}
            for pair in item["nameValuePair"]:
                if pair["name"] == "type_c":
                    event["type"] = pair["value"]
                elif pair["name"] == "subtype_c":
                    event["subtype"] = pair["value"]
                elif pair["name"] == "createTime":
                    event["date"] = datetime.strptime(pair["value"], "%m/%d/%Y %H:%M:%S").strftime("%m/%d/%y")
            events.append(event)
            # Now we will use our helper function to sort the events list based on the date, in descending order
            # (this would be extremely error-prone if we were trying to sort them by the date strings they now have)
            events.sort(key=lambda x: parse_date(x["date"]), reverse=True)
            # Then we can construct our final dictionary that holds the points total and the array of points records with details
            points_dict = {
                "points": points_data["listCustomObjectRecordsResponse"]["page"]["totalResults"],
                "events": events
            }
            print(points_dict)
    else:
        print("Failed to retrieve any points object records", points_response.status_code)

#### Commenting out this useful block because I am in a rush
# else:
#     # handle case where API call is not successful
#     print(f"Could not retrieve account info. Status code: {constituent_info_response.status_code}")

#     else:
#         print("login failed. No user session ID received.")
# else:
#     # if the login was not a success, we will print out our terrible news
#     print("I am mortified to admit that the api login failed. Maybe someone canceled the atlas user account? The system replied: ", operation_result)
#     # if there are specific errors provided, we'll print them out too
#     if 'errors' in login_response:
#         errors_list = login_response['errors']['error']
#         for error in errors_list:
#             error_code = str(error['errorCode'])
#             error_message = error['errorMessage']
#             error_description = error_code_descriptions.get(error_code, "No description available.")
#             print(f"Error code: {error_code}, Message: {error_message}. Description: {error_description}")
# else:
# # if the HTTP request itself to the API failed to connect,
# # we'll admit our problem and print our the status code:
# print('Sadly, could not even connect to the api...', api_response.status_code)
# #
# #
# ------------------------------------------------------------------------------- #
# ----------- and that is the end of the API User Authentication block ---------- #
# ------------------------------------------------------------------------------- #

    constituent_name = session['constituent_name']

    return render_template('neon_redirect.html', user=access_token, logout_url=logout_url, name=constituent_name, points_dict=points_dict)

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
    return render_template('landing.html')

if __name__ == '__main__':
    app.run(debug=True)
