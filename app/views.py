import os
import requests

from . import app, neoncrm
from flask import render_template, session, request, redirect, url_for
from datetime import datetime

redirect_uri = os.getenv("REDIRECT_URI")
# logout_url = os.getenv("LOGOUT_URL")

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

    points_dict = neoncrm.Constituent.retrieve_user_point_records_dictionary(session['user_session_id'], session['access_token'])

    session['points_dict'] = points_dict

    check_in_options = [
    "Atlas Demo Day",
    "SheCodesTulsa",
    "Tulsa Web Devs",
    "Tulsa UX",
    "Tulsa Game Developers",
    "Tulsa Developers Association",
    "Tulsa Agile Practitioners",
    "Tulsa Area Techlahoma",
    "OKC-Sharp",
    "OKC LUGnuts",
    "Oklahoma Game Developers",
    "Oklahoma City Java Users",
    "Oklahoma City Techlahoma",
    "UX Connect OKC",
    "OKC WebDevs",
    "OKC Open Source Hardware",
    "Pythonistas",
    "Salesforce Meetup Group",
    "SheCodesOKC",
]
    if points_dict['eligible_for_checkin'] == True:
        return render_template(
        'check_in.html',
        # logout_url=os.getenv("LOGOUT_URL"),
        name=constituent_name,
        check_in_options=check_in_options
    )
    else:
        return redirect(url_for('dashboard'))


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    # grab all possible incentives and store them in the session
    incentives_list_of_tuples = neoncrm.Constituent.get_incentives(session["user_session_id"])
    session["all_incentives"] = incentives_list_of_tuples
    points_dict = session['points_dict']
    if request.method == 'POST':
        # now let's get ready to post their new checkin event
        selected_group = request.form.get('selected_group')
        if selected_group:
            if points_dict['eligible_for_checkin'] == True:
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
                # and format and send the API request
                checkin_response = requests.post(neoncrm.API.EVENT_CHECKIN_URL.format(user_session_id, access_token, selected_group, checkin_record_name))
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
                    # and let's grab an updated points_dict
                    points_dict = neoncrm.Constituent.retrieve_user_point_records_dictionary(user_session_id, access_token)
                    # and update the points_dict in the session
                    session['points_dict'] = points_dict
                else:
                    print("whoops")
                    ##! Fix this later, add error handling
        linkedin = request.form.get('linkedin')
        if linkedin:
            if points_dict['eligible_for_data_update'] == True:
                print("about to print the linkedin url they gave")
                print(linkedin)
                print("that was the linkedin profile they shared")
                # First, let's create the new Points record in NeonCRM
                # we begin by creating our API request
                # Note ---- we need to double-check that it's okay ------ WE HAVE NOT CODED THAT PART YET
                user_session_id = session['user_session_id']
                access_token = session['access_token']
                # and to include today's date in the name of the record, we'll need to get it
                today = datetime.today()
                formatted_date = today.strftime("%m/%d/%y")
                print(f"about to make a data update Points record for {formatted_date}")
                points_record_name = f'data update: linkedin - {formatted_date}'
                print(f"we will call the record {points_record_name}")
                data_update_subtype = "linkedin"
                # and format and send the API request
                data_update_points_response = requests.post(neoncrm.API.DATA_UPDATE_POINTS_OBJECT_URL.format(user_session_id, access_token, data_update_subtype, points_record_name))
                #print the raw response for debugging
                print("just submitted the post request to check in to the event. About to print the response code.")
                print(data_update_points_response)
                print("that was the response code")
                # then, check to see if checkin api call was successful
                if data_update_points_response.status_code == 200:
                    # if it was, parse it as JSON
                    data_update_points_response_data = data_update_points_response.json()
                    # print it for debugging
                    print("about to print the json of the reponse we got back")
                    print(data_update_points_response_data)
                    print("that was the json of the reponse we got back")
                    # and let's grab an updated points_dict
                    points_dict = neoncrm.Constituent.retrieve_user_point_records_dictionary(user_session_id, access_token)
                    # and update the points_dict in the session
                    session['points_dict'] = points_dict
                    # and now let's push the actual information to the Neon CRM server in the form of a 'data update' object
                    data_update_data_update_record_response = requests.post(neoncrm.API.DATA_UPDATE_DATA_UPDATE_RECORD_CREATION_LINKEDIN_URL.format(user_session_id, access_token, linkedin, points_record_name, data_update_subtype))
                    print("just submitted the post request to add the 'data update' custom object record. About to print the response code.")
                    print(data_update_data_update_record_response)
                    print("that was the response code")
                    # then, check to see if data update object creation api call was successful
                    if data_update_data_update_record_response.status_code == 200:
                        # if it was, parse it as JSON
                        data_update_data_update_record_response_data = data_update_data_update_record_response.json()
                        # print it for debugging
                        print("about to print the json of the reponse we got back")
                        print(data_update_data_update_record_response_data)
                        print("that was the json of the reponse we got back")
                        # and let's grab an updated points_dict
                    else:
                        print("data update record creation failed")
                        ##! Fix this later, add error handling
                else:
                    print("whoops")
                    ##! Fix this later, add error handling

    constituent_name = session['constituent_name']
    incentives = session['list_of_incentives']
    all_incentives_as_a_list_of_tuples_with_points_value_and_name = sorted(incentives)
    # logout_url=os.getenv("LOGOUT_URL")

    return render_template(
        'dashboard.html',
        user=session["access_token"],
        all_incentives_as_a_list_of_tuples_with_points_value_and_name = all_incentives_as_a_list_of_tuples_with_points_value_and_name,
        # logout_url=logout_url,
        name=constituent_name,
        points_total = points_dict['points'],
        next_closest_reward = points_dict['next_closest_reward'],
        points_to_next_reward = points_dict['points_to_next_reward'],
        points_value_of_next_reward = points_dict['points_value_of_next_reward'],
        eligible_for_data_update = points_dict['eligible_for_data_update'],
        next_data_update  = points_dict['next_data_update'],
        next_data_update_points_value = points_dict['next_data_update_points_value'],
        array_of_earned_rewards = points_dict['earned_rewards'],
        array_of_checkin_records = points_dict['events'],
    )


# Error Page
@app.route('/error')
def error():
    return render_template('error.html')

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect("https://techlahoma.app.neoncrm.com/np/logout.do?targetUrl=https://www.techlahoma.org")

@app.route('/my-points')
def account_details():
    return render_template('account_details.html',
    points_dict=session['points_dict'],
    name=session['constituent_name'],
    )

@app.route('/linkedin')
def linkedin_form():
    return render_template('linkedin.html')

if __name__ == '__main__':
    app.run(debug=True)
