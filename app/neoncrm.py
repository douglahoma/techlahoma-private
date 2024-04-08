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

from flask import session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class API:
    """INTERFACE CLASS REPRESENTING NEONCRM AND HOW WE INTERACT WITH IT"""
    BASE_URL = "https://api.neoncrm.com"
    LOGIN_URL = "https://{}.app.neoncrm.com/np/oauth/auth?response_type=code&client_id={}&redirect_uri={}"
    ACCESS_TOKEN_URL = 'https://app.neoncrm.com/np/oauth/token'
    API_LOGIN_URL = "https://api.neoncrm.com/neonws/services/api/common/login?login.apiKey={}&login.orgid={}"
    CONSTITUENT_INFO_URL = "https://api.neoncrm.com/neonws/services/api/account/retrieveIndividualAccount?userSessionId={}&accountId={}"
    POINTS_URL = "https://api.neoncrm.com/neonws/services/api/customObjectRecord/listCustomObjectRecords?userSessionId{}fb571bdff4adb31a36475b5f8af6c386&objectApiName=Points_c&customObjectSearchCriteriaList.customObjectSearchCriteria.criteriaField=Constituent_c&customObjectSearchCriteriaList.customObjectSearchCriteria.operator=EQUAL&customObjectSearchCriteriaList.customObjectSearchCriteria.value={}&customObjectOutputFieldList.customObjectOutputField.label=Points Activity&customObjectOutputFieldList.customObjectOutputField.columnName=name&customObjectOutputFieldList.customObjectOutputField.label=Created on&customObjectOutputFieldList.customObjectOutputField.columnName=createTime&customObjectOutputFieldList.customObjectOutputField.label=point_type&customObjectOutputFieldList.customObjectOutputField.columnName=point_type_c&customObjectOutputFieldList.customObjectOutputField.label=point_subtype&customObjectOutputFieldList.customObjectOutputField.columnName=point_subtype_c&customObjectOutputFieldList.customObjectOutputField.label=Points Awarded&customObjectOutputFieldList.customObjectOutputField.columnName=Points_Awarded_c&page.pageSize=200"
    ERROR_CODE_DESCRIPTION = {
        '1': "An unknown system error. Often, these are generated due to a badly formed API request or a problem in NeonCRM.",
        '2': "Indicates a temporary problem with NeonCRM's servers.",
        '3': "A user session ID must be included with the request. Retrieve a session ID using the Login method.",
        '4': "The provided user session ID is invalid.",
        '5': "The user account associated with this API key does not have sufficient permissions to perform the desired operation."
    }

    @classmethod
    def perform_query(cls, url: str, method: function, **kwargs):
        """Perform a query to the NeonCRM API --
        
        Routing all of our interactions with the API through here allows us
        to streamline how we handle errors, exceptions, and even connection
        problems. The use of keyworld arguments will be critical in making sure
        all of this can happen in one function where we can pass all of the
        relevant parameters here:
        1. URL/I of whatever we're trying to use
        2. requests method we need to use, get, put, etc.
        3. The other arguments we need to feed into the method.
        """
        pass

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
    """Object model representing a single Constituent in the NeonCRM system:

    1. Much of what we're doing is handled quite nicely by treating certain
    data as managed attributes of this Constituent object. The thing about
    the userSessionId expiring every ten minutes is pretty much the EXACT thing
    that getter methods were invented for in OOP.
    https://realpython.com/python-property/

    2. 80-90% of the overall meat of the seperate neoncrm module will ultimately
    need to end up bound in this class, as either class attributes or instance
    attributes. BY NO MEANS EVERTHING THOUGH!--which I explain above. There are
    still things where we are dealing with the API itself and not the data for
    this or that Constituent or even Constituents, per se, which is how you tell
    it goes in this class instead of that one.
    """
    def __init__(self):
        self._account_id = ""
        self._usid = {}
        self._info = {}
        self._points_records = {}

    @property
    def account_id(self):
        """Returns the value of the account_id property as string"""
        return self._account_id

    @account_id.setter
    def account_id(self, authorization: str):
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
            API.ACCESS_TOKEN_URL,
            data=request_payload,
            headers=request_headers
        )
        self._account_id = (
            response.json().get('access_token')
        )

    @property
    def usid(self):
        """We can handle storage of the 'userSessionId' through a little bit
        of tomfoolery --
        
        1. Because we're going to need to access the information contained in
        the value of responseDateTime later in order to perform the check to
        see if our userSessionId has expired. Just store it in a dictionary!
        2. Eventually this method will need to perform the check to see if the
        usid has expired, if so, renew the login.
        3. At the time of writing I am only 85-90% sure this will work exactly
        as I'm describing but there is no good reason not to at leas try it and
        see what happens.
        """
        return self._usid.get('userSessionId')
    
    @usid.setter
    def usid(self, authorization: str):
        """Code corresponding to roughly lines 65-115 in the version of app.py
        that's currently in the repo in the 'old' directory. How exactly this
        will work is not super duper certain ATM, though -- ideally this is
        supposed to be a read-only perorty outside of the class"""
        self._usid = authorization

    @classmethod
    def retrieve_user_point_records(cls, user_session_id, access_token):
        """
        retrieves all the point records associated with a given user
        """
        return requests.get(API.POINTS_URL.format(user_session_id, access_token)).json()

class PointsEvent:
    pass
