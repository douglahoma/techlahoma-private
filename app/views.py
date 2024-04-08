import os
import requests

from app import app, neoncrm
from flask import render_template, session, request
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

redirect_uri = os.getenv("REDIRECT_URI")
logout_url = os.getenv("LOGOUT_URL")

@app.route('/')
def landing():
    """Gets url to send user credentials and renders app landing page"""
    return render_template(
        'landing.html',
        login_url=neoncrm.API.LOGIN_URL.format(
            os.getenv("ORG_ID"),
            os.getenv("CLIENT_ID"),
            os.getenv("REDIRECT_URI")
        )
    )

# OAuth Callback Route
@app.route('/authorize')
def authorize():

    neoncrm.API.get_session_access(request.args.get('code'))

    # ---------------- API User Authentication --------------------------
    # Now, let's authenticate ourselves as an API user and get
    # the userSessionId we need to actually pull info from NeonCRM
    # about our constituent (and, to send new info to NeonCRM about them!
    # -------------------------------------------------------------------
    # Next, we use the 'requests' library to send the GET request to the API
    api_response = requests.get(
        neoncrm.API.API_LOGIN_URL.format(
            os.getenv("API_KEY"),
            os.getenv("ORG_ID")
        )
    )
    print("about the print the reponse we got from authenticating as an API user")
    print(api_response.text)
    print("just printed the reponse we got from authenticating as an API user")
    #
    # Then we can check the content of the response to our request
    if api_response.status_code == 200:
        # if the request itself (Note: distinct from the login attempt!) was
        # successful, we'll parse the response's JSON data
        print("about the print the json of the reponse we got from authenticating as an API user")
        api_response_data = api_response.json()
        print(api_response_data)
        print("just finished printing the json of the reponse we got from authenticating as an API user")
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
            print("about to print the user_session_id we got back")
            print(user_session_id)
            print("about to print the user_session_id we got back")
            if user_session_id:
                # and print it out for logging/debugging purposes
                print('Great news! Login worked. User session ID is: ', user_session_id)
                ###! FOR MOCKUP ONLY: And store it in the session (remember, it only lasts 10 minutes)
                session['user_session_id'] = user_session_id

                #######################################################################
                # ------------ Get the Consituent's Information --------------------- #
                # first, construct and make the API call
                constituent_info_response = requests.get(
                    neoncrm.API.CONSTITUENT_INFO_URL.format(
                        session['user_session_id'],
                        session['access_token']
                    )
                )
                # then, check to see if the API call was successful
                if constituent_info_response.status_code == 200:
                    # if it was, parse it as JSON
                    constituent_data = constituent_info_response.json()
                    # print the response for debugging
                    print("about to print the consituent account data we got back")
                    print(constituent_data)
                    print("that concludes the printing of the account data")
                    # then grab the data about the account
                    constituent_account_data = constituent_data['retrieveIndividualAccountResponse']['individualAccount']
                    # try to grab the preferred name, but failing that, get the first name
                    constituent_name = constituent_account_data['primaryContact'].get('preferredName', constituent_account_data['primaryContact'].get('firstName'))
                    # print the name for debugging
                    print(f"the constituent's name (preferred name if included) is: {constituent_name}")
                    # and save the user's name to the session
                    session['constituent_name'] = constituent_name
                    ### Deal with the exception later
                    # Now let's get the points records
                    points_records = neoncrm.Constituent.retrieve_user_point_records(session['user_session_id'], session['access_token'])
                    print("now we are about to print the points records for the constituent")
                    print(points_records)
                    print("and that concludes the points records for the constituent")
                    # print(points_records["listCustomObjectRecordsResponse"]["searchResults"]["nameValuePairs"])
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


    return render_template(
        'check_in.html',
        logout_url=os.getenv("LOGOUT_URL"),
        name=constituent_name
    )

@app.route('/post_checkin', methods=['POST'])
def post_checkin():
    selected_group = request.form.get('selected_group')
    print("about to print the group they selected")
    print(selected_group)
    print("that was the group they selected")
    # First, let's create the new Points record in NeonCRM
    # we begin by creating our API request
    # Note ---- we need to double-check that it's okay ------ WE HAVE NOT CODED THAT PART YET
    user_session_id = session['user_session_id']
    access_token = session['access_token']
    # and to include today's date in the name of the record, we'll need to get it
    today = datetime.today()
    formatted_date = today.strftime("%m/%d/%y")
    print(f"about to make a checkin record for {formatted_date}")
    checkin_record_name = f'check-in: {selected_group} - {formatted_date}'
    print(f"we will call the record {checkin_record_name}")
    # and format the API request
    checkin_url = f'https://api.neoncrm.com/neonws/services/api/customObjectRecord/createCustomObjectRecord?userSessionId={user_session_id}&customObjectRecord.objectApiName=Points_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=Constituent_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value={access_token}&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=type_for_api_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value=check-in&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=subtype_for_api_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value={selected_group}&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=name&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value={checkin_record_name}'
    # and post the request
    checkin_response = requests.post(checkin_url)
    #print the raw response for debugging
    print("just submitted the post request to check in to the event. About to print the response code.")
    print(checkin_response)
    print("that was the response code")
    # then, check to see if checkin api call was successful
    if checkin_response.status_code == 200:
        # if it was, parse it as JSON
        checkin_data = checkin_response.json()
        # print it for debugging
        print("about to print the json of the reponse we got back")
        print(checkin_data)
        print("that was the json of the reponse we got back")
    else:
        print("whoops")
        ##! Fix this later, add error handling

    #######################################################################
    # ------------ Get the Points Info for the Constituent-------------- #
    # first, construct and make the API call
    user_session_id = session['user_session_id']
    access_token = session['access_token']
    points_dict = neoncrm.Constituent.retrieve_user_point_records_dictionary(user_session_id, access_token)



    constituent_name = session['constituent_name']

    return render_template('neon_redirect.html', user=session["access_token"], logout_url=logout_url, name=constituent_name, points_dict=points_dict)

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
