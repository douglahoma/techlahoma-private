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
