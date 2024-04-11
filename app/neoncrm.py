"""
Namespace module defining all direct interactions with NeonCRM:

Think of this as a book, with the classes as chapters, and properties and
methods as sections and subsections. It might look a little unwieldy, but
ultimately we want to be able to access th url to get an oath token with
'NeonCRM.API.ACCESS_TOKEN_URL' and have a clear unambiguous trail of
breadcrums leading us back to where it's defined in the source code.
"""

import os
import requests
import random
from datetime import datetime

from flask import session

class API:
    """INTERFACE CLASS REPRESENTING NEONCRM AND HOW WE INTERACT WITH IT"""

    LOGIN_URL = "https://{}.app.neoncrm.com/np/oauth/auth?response_type=code&client_id={}&redirect_uri={}"
    ACCESS_TOKEN_URL = 'https://app.neoncrm.com/np/oauth/token'
    API_LOGIN_URL = "https://api.neoncrm.com/neonws/services/api/common/login?login.apiKey={}&login.orgid={}"
    CONSTITUENT_INFO_URL = "https://api.neoncrm.com/neonws/services/api/account/retrieveIndividualAccount?userSessionId={}&accountId={}"
    # incentives url takes user_session_id
    INCENTIVES_URL = "https://api.neoncrm.com/neonws/services/api/customObjectRecord/listCustomObjectRecords?userSessionId={}&objectApiName=Incentives_c&customObjectOutputFieldList.customObjectOutputField.label=Incentive&customObjectOutputFieldList.customObjectOutputField.columnName=name&customObjectOutputFieldList.customObjectOutputField.label=Points Needed&customObjectOutputFieldList.customObjectOutputField.columnName=Points_Needed_c"
    POINTS_URL = "https://api.neoncrm.com/neonws/services/api/customObjectRecord/listCustomObjectRecords?userSessionId={}&objectApiName=Points_c&customObjectSearchCriteriaList.customObjectSearchCriteria.criteriaField=Constituent_c&customObjectSearchCriteriaList.customObjectSearchCriteria.operator=EQUAL&customObjectSearchCriteriaList.customObjectSearchCriteria.value={}&customObjectOutputFieldList.customObjectOutputField.label=Points Activity&customObjectOutputFieldList.customObjectOutputField.columnName=name&customObjectOutputFieldList.customObjectOutputField.label=Created on&customObjectOutputFieldList.customObjectOutputField.columnName=createTime&customObjectOutputFieldList.customObjectOutputField.label=point_type&customObjectOutputFieldList.customObjectOutputField.columnName=point_type_c&customObjectOutputFieldList.customObjectOutputField.label=point_subtype&customObjectOutputFieldList.customObjectOutputField.columnName=point_subtype_c&customObjectOutputFieldList.customObjectOutputField.label=Points Awarded&customObjectOutputFieldList.customObjectOutputField.columnName=Points_Awarded_c&page.pageSize=200"
    # event checkin url requires these arguments: user_session_id, access_token, selected_group, checkin_record_name
    EVENT_CHECKIN_URL = "https://api.neoncrm.com/neonws/services/api/customObjectRecord/createCustomObjectRecord?userSessionId={}&customObjectRecord.objectApiName=Points_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=Constituent_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value={}&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=type_for_api_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value=check-in&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=subtype_for_api_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value={}&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=name&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value={}"
    # event checkin url requires these arguments: user_session_id, access_token, data update subtype, record name
    DATA_UPDATE_POINTS_OBJECT_URL = "https://api.neoncrm.com/neonws/services/api/customObjectRecord/createCustomObjectRecord?userSessionId={}&customObjectRecord.objectApiName=Points_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=Constituent_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value={}&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=type_for_api_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value=data update&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=subtype_for_api_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value={}&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=name&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value={}"
    # linkedin data update custom object creation url requires these arguments: user_session_id, access_token, linkedin username/url, record name, update subtype
    DATA_UPDATE_DATA_UPDATE_RECORD_CREATION_LINKEDIN_URL = "https://api.neoncrm.com/neonws/services/api/customObjectRecord/createCustomObjectRecord?userSessionId={}&customObjectRecord.objectApiName=Data_Updates_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=Constituent_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value={}&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=linkedin_URL_or_username_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value={}&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=name&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value={}&customObjectRecord.customObjectRecordDataList.customObjectRecordData.name=update_type_c&customObjectRecord.customObjectRecordDataList.customObjectRecordData.value={}"
    ERROR_CODE_DESCRIPTION = {
        '1': "An unknown system error. Often, these are generated due to a badly formed API request or a problem in NeonCRM.",
        '2': "Indicates a temporary problem with NeonCRM's servers.",
        '3': "A user session ID must be included with the request. Retrieve a session ID using the Login method.",
        '4': "The provided user session ID is invalid.",
        '5': "The user account associated with this API key does not have sufficient permissions to perform the desired operation."
    }

    @classmethod
    def get_session_access(cls, authorization) -> None:
        """SENDS HTTP REQUEST USING AUTHORIZATION CODE TO GET access token representing constituent Account id."""
        request_payload = {
            'client_id': os.getenv("CLIENT_ID"),
            'client_secret': os.getenv("CLIENT_SECRET"),
            'redirect_uri': os.getenv("REDIRECT_URI"),
            'code': authorization,
            'grant_type': 'authorization_code'
        }
        request_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(
            cls.ACCESS_TOKEN_URL,
            data=request_payload,
            headers=request_headers
        )
        session['access_token'] = (response.json().get('access_token'))
        # print the access_token for debugging
        print(session['access_token'])

    @classmethod
    def get_consituent_info(cls):
        cls.attempt_api_login()

        if (cls.login_sucessful()):
            pass

    @classmethod
    def attempt_api_login(cls) -> None:
        """
        Attempts to login to the api and stores whatever login response was
        given as a key in the server's cache. It's extremely important to save
        the entire response and then just get the parts of it we want as we need
        them.
        """
        api_response = requests.get(
            cls.API_LOGIN_URL.format(
                os.getenv("API_KEY"),
                os.getenv("ORG_ID")
            )
        )
        if (api_response.status_code == 200):
            session["login_response"] = (
                api_response.json().get(
                    'loginResponse', {}
                )
            )
        else:
            raise ConnectionError()

    @staticmethod
    def login_sucessful():
        """VERIFIES THAT THE ATTEMPT TO LOGIN THE USER WAS SUCESSFUL"""
        return (
            session.get('loginResponse', {})
                .get('operationResult', "") == 'SUCCESS'
        )

    @staticmethod
    def retrieve_user_session_id():
        """
        Retrieves the value of userSessionId from the last login response
        stored in the server cache. Will eventually perform the check to see
        if ten minutes have passed and ask for a new one.
        """
        return (
            session.get("login_response", {})
                .get('userSessionId', "")
        )

class Constituent:

    @classmethod
    def retrieve_user_point_records(cls, user_session_id, access_token):
        """
        retrieves all the point records associated with a given user
        """
        print(API.POINTS_URL.format(user_session_id, access_token))
        return requests.get(API.POINTS_URL.format(user_session_id, access_token)).json()

    @classmethod
    def get_incentives(cls, user_session_id):
        """
        returns a list of tuples of the format (points required (num), name of reward) for all the incentives
        """
        incentives_response = requests.get(API.INCENTIVES_URL.format(user_session_id)).json()
        incentives_list = []
        for item in incentives_response["listCustomObjectRecordsResponse"]["searchResults"]["nameValuePairs"]:
            points_needed = 0
            name = ""
            for pair in item["nameValuePair"]:
                if pair["name"] == "Points_Needed_c":
                    points_needed = int(pair["value"])
                elif pair["name"] == "name":
                    name = pair["value"]
            incentives_list.append((points_needed, name))
        print(incentives_list)
        session['list_of_incentives'] = incentives_list
        return (incentives_list)

    @classmethod
    def retrieve_user_point_records_dictionary(cls, user_session_id, access_token):
        # first, construct and make the API call
        points_response = requests.get(API.POINTS_URL.format(user_session_id, access_token))
        # then, check to see if points API call was successful
        if points_response.status_code == 200:
            # if it was, parse it as JSON
            points_data = points_response.json()
            # Now we'll make a helper function to parse the date from the response records
            def parse_date(date_string):
                return datetime.strptime(date_string, "%m/%d/%y")
            points_dict = {}
            events = []
            # possible_data_updates = ['linkedin', 'employment', 'cell', 'profile']
            # edited: many possible data updates removed pending approval by executive director
            possible_data_updates = ['linkedin']
            eligible_for_checkin = True
            eligible_for_data_update = True
            for item in points_data["listCustomObjectRecordsResponse"]["searchResults"]["nameValuePairs"]:
                event = {}
                for pair in item["nameValuePair"]:
                    if pair["name"] == "point_type_c":
                        event["type"] = pair["value"]
                    elif pair["name"] == "point_subtype_c":
                        event["subtype"] = pair["value"]
                    elif pair["name"] == "Points_Awarded_c":
                        event["awarded"] = int((pair["value"]))
                    elif pair["name"] == "createTime":
                        event["date"] = datetime.strptime(pair["value"], "%m/%d/%Y %H:%M:%S").strftime("%m/%d/%y")
                events.append(event)
            # Now we will use our helper function to sort the events list based on the date, in descending order
            events.sort(key=lambda x: parse_date(x["date"]), reverse=True)
            # We'll grab a formatted date of today to check for multiple check-ins
            today_date = datetime.now().strftime("%m/%d/%y")
            # Then we can construct our final dictionary that holds the points total and the array of points records
            total_points = 0
            for item in events:
                # add the point to the constituent's points earned total
                total_points += item['awarded']
                # and if it is a data update, remove it from the ones they are eligible for
                if event['subtype'] in possible_data_updates:
                    possible_data_updates.remove(event['subtype'])
                # and we'll check the date against today to remove the possibility for double check-ins
                if event['date'] == today_date:
                    # if we find it, we'll flip the appropriate switch:
                    if event['type'] == 'check-in':
                        eligible_for_checkin = False
                    elif event['type'] == 'data-update':
                        eligible_for_data_update = False
            points_dict = {
                "points": total_points,
                "events": events
            }
            print(points_dict)
            # now let's get incentive data
            incentives = cls.get_incentives(user_session_id)
            earned_rewards = []
            next_closest_reward = None
            points_to_next_reward = None
            points_value_of_next_reward = None
            # Iterate through the list of rewards
            for points_needed, reward_name in sorted(incentives):
                if points_dict['points'] >= points_needed:
                    earned_rewards.append(reward_name)
                else:
                    # If next_closest_reward is None, it means we've found the first reward
                    # the constituent has not yet earned, which is our next closest reward.
                    if next_closest_reward is None:
                        next_closest_reward = reward_name
                        points_value_of_next_reward = points_needed
                        points_to_next_reward = points_needed - points_dict['points']
                    # Once we've found the next closest reward, we can break out of the loop
                    break
            points_dict['earned_rewards'] = earned_rewards
            points_dict['next_closest_reward'] = next_closest_reward
            points_dict['points_to_next_reward'] = points_to_next_reward
            if points_value_of_next_reward is None:
                # of there is no next reward, put the value of the highest possible reward
                # in 'points_value_of_next_reward'
                # (at the request of the front-end designer)
                sorted_incentives = sorted(incentives)
                points_value_of_next_reward = sorted_incentives[-1][0]
            points_dict['points_value_of_next_reward'] = points_value_of_next_reward
            next_data_update = ""
            if possible_data_updates:
                # if any possible data updates haven't been done, pick the next one at random
                next_data_update = random.choice(possible_data_updates)
            if not possible_data_updates:
                # and if there are none left, then they are not eligible for a data update
                eligible_for_data_update = False
            next_data_update_points_value = None
            if next_data_update:
                    if next_data_update == 'cell' or next_data_update == 'profile':
                        next_data_update_points_value = 10
                    else:
                        next_data_update_points_value = 5
            points_dict['next_data_update'] = next_data_update
            points_dict['next_data_update_points_value'] = next_data_update_points_value
            points_dict['eligible_for_checkin'] = eligible_for_checkin
            points_dict['eligible_for_data_update'] = eligible_for_data_update
            print("about to print the points dict")
            print(points_dict)
            print("just printed the points dict")
            return (points_dict)
        else:
            print("Failed to retrieve any points object records", points_response.status_code)
            return ({})


class PointsEvent:
    pass
