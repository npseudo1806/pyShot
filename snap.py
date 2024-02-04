from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash
from flask import make_response
import requests
import json
import os
from datetime import datetime
from datetime import datetime, timezone
import time
import glob
saved_data = {}

# Define the ProgressiveAuthorization class
class ProgressiveAuthorization:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def login(self):
        url = "https://api.progressive.com/onlineaccount/v1/accesstoken"
        headers = {
            "X-PGRIdentifier": "7517e9ca0ac75fa9",
            "User-Agent": "PGRApp/3.89 Android/12 SM-G975U1",
            "api_key": "cDP01Wmyzjt8riiB7nsKNQwieie",
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "Content-Encoding": "gzip",
            "X-PGRCLIENT": "PGR-ANDROID",
            "Content-Type": "application/json; charset=UTF-8",
            "Host": "api.progressive.com",
        }

        data = {
            "keepMeLoggedIn": False,
            "password": self.password,
            "refreshToken": False,
            "userName": self.username
        }

        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return True, response.json()  # Login successful, return True and response data
        else:
            return False, response.text  # Login failed, return False and error message

def get_unix_timestamp(year, month, day):
    """Get Unix timestamp for a specific date."""
    date = datetime(year, month, day, tzinfo=timezone.utc)
    return int(time.mktime(date.timetuple()))

def get_current_unix_timestamp():
    """Get Unix timestamp for the current time."""
    current_time = datetime.now(timezone.utc)
    return int(time.mktime(current_time.timetuple()))

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'BiT-SnapShot-AAP-23'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json  # Get data from fetch request
    username = data['username']
    password = data['password']
    saved_data['driver_name'] = username
    prog_auth = ProgressiveAuthorization(username, password)
    success, response = prog_auth.login()

    if success:
        saved_data['access_token'] = response.get("accessToken", "No access token provided")
        session['access_token'] = response.get("accessToken", "No access token provided")
        session['logged_in'] = True  # Set session variable to keep track of login status
        script_dir = os.path.dirname(os.path.realpath(__file__))
        # Check if a folder exists with the same name as the username
        folder_path = os.path.join(script_dir, username)
        flag = 'Y' if os.path.exists(folder_path) else 'N'

        # Get the timestamp of the last updated file in the folder
        last_updated = None
        if flag == 'Y':
            files = [os.path.join(script_dir, f) for f in os.listdir(script_dir) if os.path.isfile(os.path.join(script_dir, f))]
            if files:
                last_updated = max(os.path.getmtime(file) for file in files)
        
        dt_object = datetime.fromtimestamp(last_updated)
        last_updated = dt_object.strftime('%Y-%m-%d %H:%M:%S.%f')
        print("Already_Registered",flag)
        print("last_updated",last_updated)
        return jsonify(status="success", access_token=session['access_token'], links=response.get("_links", {}),
                       folder_exists=flag,last_updated = last_updated)
    else:
        return jsonify(status="failure", message="Login Failed. Please check your credentials")


@app.route('/getPolicy', methods=['GET'])
def getPolicy():
    # Ensure the access token is current and valid
    authorization_string = f"Bearer {saved_data['access_token']}"

    # Define the URL for the request
    policy_url = "https://api.progressive.com/policypro/v1/account/documents"

    # Define the headers exactly as they are in Postman
    headers = {
        "host": "api.progressive.com",
        "x-prgsessiondatalocation": "BunkerWest",
        "authorization": authorization_string,
        "api_key": "cDP01Wmyzjt8riiB7nsKNQwieie",
        "content-type": "application/json",
        "x-prgaccountsessionid": "1a18b80d-ae47-4751-9d5a-e0b522593b84",
    }

    # Define the parameters
    params = {
        "listType": "Terms"
    }

    try:
        response = requests.get(policy_url, headers=headers, params=params)
        
        if response.status_code == 200:
            response_body = response.json()
            print(response_body)
            account_documents = response_body.get('accountDocuments', [])
            if account_documents:
                saved_data['policy_number'] = account_documents[0].get('policyNumber', 'Not Available')
            else:
                saved_data['policy_number'] = 'Not Available'

            print("policyNumebr",saved_data['policy_number']);
            return jsonify(status="success", data=response_body)
        else:
            print("Failed:", response.text)
            return jsonify(status="failure", message="Failed to retrieve policy documents")
    except requests.exceptions.RequestException as e:
        return jsonify(status="failure", message=str(e))


    

@app.route('/sendCode', methods=['POST'])
def send_code():
    # Extract mobile number from the incoming JSON payload
    data = request.json
    mobileNumber = data['mobileNumber']

    # Define the URL and headers for the request to the external service
    sendcode_url = "https://telematics.api.progressive.com/TelematicsRegistrations/Telematics/MobileDevices/MobileRegistrations/v1/challenge"
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Host": "telematics.api.progressive.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/4.10.0",
        "api_key": "cDP01Wmyzjt8riiB7nsKNQwieie",
        "ADRUM_1": "isMobile:true",
        "ADRUM": "isAjax:true",
    }

    # Set the data payload, including the mobile number as registrationCode
    data = {
        "registrationCode": mobileNumber  # Assuming you want to send the mobile number as the registration code
    }

    try:
        response2 = requests.post(sendcode_url, json=data, headers=headers)
        print("Response Status:", response2.status_code)
        print("Response Headers:", response2.headers)
        print("Response Body:", response2.text)  #

        # Check response status and return the result
        if response2.status_code == 200:
            # print("Success:", response2.json())
            # return jsonify(status="success", data=response2.json())  # Request successful, return True and response data
            return jsonify(status="success")
  
        else:
            print("Failed:", response2.text)
            return jsonify(status="failure", message="Failed to send code")  # Non-200 status code
    except requests.exceptions.RequestException as e:
        return jsonify(status="failure", message=str(e)) 



@app.route('/sendOTP', methods=['POST'])
def send_otp():
    # Extract mobile number from the incoming JSON payload
    data = request.json
    mobileNumber = data['mobileNumber']
    challengeCode = data['challengeCode']
    # Define the URL and headers for the request to the external service
    sendcode_url = "https://telematics.api.progressive.com/TelematicsRegistrations/Telematics/MobileDevices/MobileRegistrations/v1/authenticate"
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Host": "telematics.api.progressive.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/4.10.0",
        "api_key": "cDP01Wmyzjt8riiB7nsKNQwieie",
        "ADRUM_1": "isMobile:true",
        "ADRUM": "isAjax:true",
    }

    # Set the data payload, including the mobile number as registrationCode
    data = {
        "registrationCode": mobileNumber,
        "challengeCode":challengeCode  # Assuming you want to send the mobile number as the registration code
    }

    try:
        response2 = requests.post(sendcode_url, json=data, headers=headers)
        print("Response Status:", response2.status_code)
        print("Response Headers:", response2.headers)
        print("Response Body:", response2.text)  #
        response_body = response2.json() 
        apiToken = response_body.get("apiToken")
        mobileParticipantId = response_body.get("mobileParticipantId")
        firstName = response_body.get("firstName")
        print("apiToken==>",apiToken)
        print("mobileParticipantId==>",mobileParticipantId)
        print("firstName==>",firstName)

        # Check response status and return the result
        if response2.status_code == 200:

            saved_data['apiToken'] = apiToken
            saved_data['mobileParticipantId'] = mobileParticipantId
            saved_data['firstName'] = firstName

            return jsonify(
                status="success",
                apiToken=apiToken,
                mobileParticipantId=mobileParticipantId,
                firstName=firstName
            )
  
        else:
            print("Failed:", response2.text)
            return jsonify(status="failure", message="Failed to send code")  # Non-200 status code
    except requests.exceptions.RequestException as e:
        return jsonify(status="failure", message=str(e)) 


@app.route('/driverId', methods=['POST'])
def driverId():
    # Extract mobile number from the incoming JSON payload
    data = request.json
    apiToken = data['apiToken']
    mobileParticipantId = data['mobileParticipantId']

    print("fetched==>",apiToken)
    print("fetched====>",mobileParticipantId)
    # Define the URL and headers for the request to the external service
    third_url = "https://api-snapshot.cens.io/ubi3/v1/companies/2212aa38-0ada-40a3-ace8-fd1096302d8d/oauth"
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Host": "telematics.api.progressive.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/4.10.0"
    }

    # Set the data payload, including the mobile number as registrationCode
    data = {
        "access_token": saved_data["apiToken"],
        "app_id": "com.phonevalley.progressive",
        "app_version": "3.89",
        "device_model": "SM-G975U1",
        "authorization_server": "a46712ed-a1b1-4748-8de7-7419cf7c671b",
        "device_name": "SM-G975U1",
        "device_type": "ANDROID",
        "install_id": "6b1111b5-9bfa-405e-b01e-659c5c925524",
        "nickname": "SM-G975U1",
        "os_version": "12",
        "user_id":saved_data["mobileParticipantId"]
    }

    try:
        response3 = requests.post(third_url, json=data, headers=headers)
        print("Response Status:", response3.status_code)
        print("Response Headers:", response3.headers)
        print("Response Body:", response3.text)  #
        response_body = response3.json() 
      
        # Check response status and return the result
        if response3.status_code == 200:
            saved_data['device_id'] = response_body.get("device_id")
            saved_data['driver_id'] = response_body.get("driver_id")
            saved_data['access_token'] = response_body.get("access_token")
            saved_data['refresh_token'] = response_body.get("refresh_token")
            saved_data['expires_in'] = response_body.get("expires_in")
            saved_data['token_type'] = response_body.get("token_type")
            saved_data['policy_id'] = response_body.get("policy_id")

            return jsonify(
                status="success"
            )
        else:
            print("Failed:", response3.text)
            return jsonify(status="failure", message="Failed to send code")  # Non-200 status code
    except requests.exceptions.RequestException as e:
        return jsonify(status="failure", message=str(e)) 




@app.route('/driverdetails', methods=['GET'])
def driverdetails():
    # Extract mobile number from the incoming JSON payload
    # Define the URL and headers for the request to the external service
    driver_id = saved_data['driver_id']
    base_url = "https://api-snapshot.cens.io/ubi3/v1/drivers/"
    endpoint = "/enrollment"
    fourth_url = f"{base_url}{driver_id}{endpoint}"

    print(fourth_url)

    #fourth_url = "https://api-snapshot.cens.io/ubi3/v1/drivers/1b9d3b6a-baac-4c53-bd06-58a95f47c773/enrollment"
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Connection": "Keep-Alive",
        "Accept":"*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "okhttp/4.10.0",
        "authorization":saved_data['access_token']
    }


    try:
        response4 = requests.get(fourth_url, headers=headers)
        print("Response Status:", response4.status_code)
        print("Response Headers:", response4.headers)
        print("Response Body:", response4.text)  #
        response_body = response4.json() 
      
        # Check response status and return the result
        if response4.status_code == 200:

            saved_data["Id"]=response_body.get("Id") #an unique id to be used later---Trevor!!
            saved_data["DriverID"]=response_body.get("DriverID") # an new DriverID here different from previous
            saved_data["CompanyID"]=response_body.get("CompanyID")
            saved_data["PolicyID"]=response_body.get("PolicyID")
            saved_data["Created"]=response_body.get("Created")
            saved_data["Updated"]=response_body.get("Updated")
            saved_data["FirstName"]=response_body.get("FirstName")

            # Printing all key-value pairs in the saved_data dictionary
            for key, value in saved_data.items():
                print(f"{key}: {value}")
        
           
            return jsonify(
                status="success"
            )
        else:
            print("Failed:", response4.text)
            return jsonify(status="failure", message="Failed to send code")  # Non-200 status code
    except requests.exceptions.RequestException as e:
        return jsonify(status="failure", message=str(e)) 
    

@app.route('/tripDetails', methods=['GET'])
def tripDetails():
    # Extract mobile number from the incoming JSON payload
    start_time = get_unix_timestamp(2015, 9, 2)
    current_time = get_current_unix_timestamp()

    print("start_time",start_time)
    print("current_time",current_time)
    driver_id = saved_data['driver_id']
    base_url = "https://api-snapshot.cens.io/mobile/v3/driver/"
    # endpoint = "/trips/start/{start_time}/end/{current_time}"
    # fifth_url = f"{base_url}{driver_id}{endpoint}"
    fifth_url = f"{base_url}{driver_id}/trips/start/{start_time}/end/{current_time}"



    print("fifth_url",fifth_url)
    headers = {
        "Accept":"*/*",
        "Accept-Encoding":"gzip, deflate, br",
        "Connection": "Keep-Alive",
        "authorization":saved_data['access_token'],
        "User-Agent": "okhttp/4.10.0",
    }

    print(headers)

    # Set the data payload, including the mobile number as registrationCode

    try:
        response5 = requests.get(fifth_url, headers=headers)
        print("Trip_Response Status:", response5.status_code)
        print("Trip_Response Headers:", response5.headers)
        print("Trip_Response Body:", response5.text)  #
        response_body = response5.json() 
      
        # Check response status and return the result
        if response5.status_code == 200:

            response_body = response5.json() 

            driver_name = saved_data['driver_name'] 

            # Create a directory with the driver's ID
            driver_id_folder = f"./{driver_name}"
            if not os.path.exists(driver_id_folder):
                os.makedirs(driver_id_folder)

            # Format the current date and time
            current_date_time = datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f"map_{current_date_time}.json"

            # Save the response in a JSON file within the created directory
            with open(os.path.join(driver_id_folder, file_name), 'w') as json_file:
                json.dump(response_body, json_file, indent=4)

            return jsonify(status="success")
        else:
            print("Failed:", response5.text)
            return jsonify(status="failure", message="Failed to send code")  # Non-200 status code
    except requests.exceptions.RequestException as e:
        return jsonify(status="failure", message=str(e)) 


@app.route('/tripList')
def tripList():
    user_name =  saved_data['driver_name']
    user_folder_path = os.path.join(user_name)

    # Check if the user's folder exists
    if not os.path.exists(user_folder_path) or not os.path.isdir(user_folder_path):
        return "User folder not found", 404

    # List all JSON files in the user's folder
    json_files = glob.glob(os.path.join(user_folder_path, '*.json'))

    # Find the most recently updated JSON file
    latest_file = None
    latest_mod_time = 0
    for file in json_files:
        mod_time = os.path.getmtime(file)
        if mod_time > latest_mod_time:
            latest_mod_time = mod_time
            latest_file = file

    # Check if any JSON file was found
    if latest_file is None:
        return "No JSON files found for the user", 404

    with open(latest_file, 'r') as file:
        json_data = json.load(file)
        trips = json_data['data']['trips']

        for trip in trips:
            trip['start_time'] = datetime.fromtimestamp(trip['start_time']).strftime('%Y-%m-%d %H:%M:%S')
            trip['end_time'] = datetime.fromtimestamp(trip['end_time']).strftime('%Y-%m-%d %H:%M:%S')
        
        trips.sort(key=lambda x: x['start_time'], reverse=True)

    trips_json = json.dumps(trips)
    print("trips_details",trips_json)
    return jsonify(trips)



@app.route('/tripMap', methods=['POST'])
def tripMap():
    data = request.json
    rowIndex = data['rowIndex']
    with open('map.json', 'r') as file:
        json_data = json.load(file)
        trips = json_data['data']['trips']
        for trip in trips:
            trip['start_time'] = datetime.fromtimestamp(trip['start_time']).strftime('%Y-%m-%d %H:%M:%S')
            trip['end_time'] = datetime.fromtimestamp(trip['end_time']).strftime('%Y-%m-%d %H:%M:%S')
        trips.sort(key=lambda x: x['start_time'], reverse=True)
    
    selected_trip = trips[rowIndex - 1]
    trip_info = {
        "start_time": selected_trip["start_time"],
        "start_location": selected_trip["start_location"],
        "end_location": selected_trip["end_location"],
        "end_time": selected_trip["end_time"],
        "start_latitude": selected_trip["start_latitude"],
        "start_longitude": selected_trip["start_longitude"],
        "end_latitude": selected_trip["end_latitude"],
        "end_longitude": selected_trip["end_longitude"],
        "events": selected_trip.get("events", [])
    }
    print(trip_info)
    return jsonify(trip_info)


# @app.route('/tripdetails',methods=['GET'])
# def index():
#     with open('map.json', 'r') as file:
#         json_data = json.load(file)
#         trips = json_data['data']['trips']

#         for trip in trips:
#             trip['start_time'] = datetime.fromtimestamp(trip['start_time']).strftime('%Y-%m-%d %H:%M:%S')
#             trip['end_time'] = datetime.fromtimestamp(trip['end_time']).strftime('%Y-%m-%d %H:%M:%S')
        
#         trips.sort(key=lambda x: x['start_time'], reverse=True)

#         return render_template('map_view.html', trips=trips)


if __name__ == '__main__':
    app.run(debug=True)


# saved_data = {
#     "Id": "4d7db5e9-8e59-4d7b-91eb-24bab7ed97ad",
#     "DriverID": "09775487-257a-47a1-b22d-8e3b67d2086a",
#     "CompanyID": "2212aa38-0ada-40a3-ace8-fd1096302d8d",
#     "PolicyID": "4294c5d7-1d80-2aae-3e2d-ce4ca8a7ac4e",
#     "ProgramID": None,
#     "FeatureSetID": "MNA",
#     "FleetName": None,
#     "FirstName": "Abdulla",
#     "LastName": None,
#     "Locale": "en-US",
#     "Designation": None,
#     "AgencyID": None,
#     "BirthDate": None,
#     "ZipCode": None,
#     "EnrollmentMode": "UBI",
#     "EnrollmentModeUpdated": None,
#     "DataCollectionStrategy": "ALL",
#     "TrialDurationDays": 0,
#     "RatingRegion": None,
#     "PhoneNumber": "",
#     "EnrollmentDate": None,
#     "ScoreVersion": None,
#     "ScoreProvider": None,
#     "Vehicles": [],
#     "Attributes": [],
#     "Unenrolled": False,
#     "Created": 1694047317.407184,
#     "Updated": 1694047391.709292,
#     "Timestamp": None,
#     "CustomData": {
#         "crashEligibility": "False",
#         "invitationScreenType": "B",
#         "programCode": "1",
#         "ratedDistractedDriving": "True",
#         "showInvitationScreen": "true",
#         "summarizationMethod": "2021",
#         "ubiEligibility": "True"
#     }
# }