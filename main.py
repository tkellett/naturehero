import datetime
from flask import Flask, render_template, request, redirect, jsonify
from google.auth.transport import requests
from google.cloud import datastore
import google.oauth2.id_token
app = Flask(__name__)

from database_management import *

firebase_request_adapter = requests.Request()
datastore_client = datastore.Client()

def store_time(email, dt):
    entity = datastore.Entity(key=datastore_client.key("User", email, "visit"))
    entity.update({"timestamp": dt})

    datastore_client.put(entity)


def fetch_times(email, limit):
    ancestor = datastore_client.key("User", email)
    query = datastore_client.query(kind="visit", ancestor=ancestor)
    query.order = ["-timestamp"]

    times = query.fetch(limit=limit)

    return times

@app.route('/submit-registration', methods=['POST'])
def submit_registration():
    # Get user input from the form
    name = request.form.get('name')
    email = request.form.get('email')
    age = request.form.get('age')

    # Store the data in Firestore
    user_data = {
        'name': name,
        'email': email,
        'age': int(age)
    }

    # Add a new document to the "users" collection
    db.collection('users').add(user_data)

    return redirect('/')

@app.route('/trigger-action', methods=['POST'])
def trigger_action():
    # Get data from the request (if any)
    data = request.json  # For JSON data
    name = data.get('name')
    age = data.get('age')

    # Perform some action (e.g., process data, interact with a database)
    print(f"Received data: Name = {name}, Age = {age}")

    # Return a response (optional)
    return jsonify({"status": "success", "message": "Action triggered successfully!"})

@app.route("/home")
def home():

    error_message = None
    id_token = request.cookies.get("token")
    if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter
                )
                # CHECK IF USER IS REGISTERED
                
                return render_template(
                    "home.html"
                )

            except ValueError as exc:
                # This will be raised if the token is expired or any other
                # verification checks fail.
                error_message = str(exc)
                return redirect("/")
    
    return redirect("/")

@app.route("/")
def root():
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    tasks = None

    if id_token:
        try:
            # Verify the token against the Firebase Auth API. This example
            # verifies the token on each page load. For improved performance,
            # some applications may wish to cache results in an encrypted
            # session store (see for instance
            # http://flask.pocoo.org/docs/1.0/quickstart/#sessions).
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter
            )

            store_time(claims["email"], datetime.datetime.now(tz=datetime.timezone.utc))

            create_task(claims["email"], "test task 123")
            times = fetch_times(claims["email"], 10)
            tasks = fetch_tasks(claims["email"], 10)

        except ValueError as exc:
            # This will be raised if the token is expired or any other
            # verification checks fail.
            error_message = str(exc)

    return render_template(
        "index.html", user_data=claims, error_message=error_message, times=times, tasks=tasks
    )



if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host="127.0.0.1", port=8000, debug=True)