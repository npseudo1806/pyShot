# PyShot: Flask Web Application for Snapshot Forensics

PyShot is a Flask-based web application designed for interacting with the Progressive Insurance API to retrieve and visualize trip data. This application provides functionalities like user authentication, policy retrieval, sending OTPs, and trip details fetching.

## Features
- User authentication with Progressive Insurance API.
- Fetching and displaying policy documents.
- Sending OTP to mobile numbers for verification.
- Retrieving and visualizing trip details and timelines.
- Saving and listing trip data as JSON files.
- Interactive map visualization using Google Maps API.

## Setup and Installation

### Prerequisites
- Python 3.x
- Flask
- Requests library

### Installation Steps
1. Clone the repository: git clone [https://github.com/rahmanonik18/snapshot_forensic]
2. Navigate to the cloned repository: cd snapshot_forensic
3. pip install flask requests
4. Set up a Google Maps API key (replace `YOUR_API_KEY` with your actual API key): export GOOGLE_MAPS_API_KEY=YOUR_API_KEY
5. Add your Google Maps API key to the HTML file in the script tag for the Maps API.

### Running the Application
1. Start the Flask server: python snap.py
2. Access the web application at `http://localhost:5000/` in your web browser.

## Usage
- **Login**: Enter your username and password to authenticate with the Progressive API.
- **Snapshot Registration**: Send OTPs to a mobile number and verify them for snapshot registration.
- **Trip Details**: Fetch and display trip details including start and end locations, times, and phone usage.
- **Account Information**: Retrieve policy information and account details.
- **Map Visualization**: Visualize trip routes and events on an interactive map.

## File Structure
- `snap.py`: Main Python file containing the Flask application and all backend functionalities.
- `templates/index.html`: HTML file for the frontend interface.
- `static/`: Directory containing CSS and JavaScript files (if any).

