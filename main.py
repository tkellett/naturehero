import datetime
from flask import Flask, render_template, request
from google.auth.transport import requests
from google.cloud import datastore
import google.oauth2.id_token
app = Flask(__name__)

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




def create_user(email, name, DoB, tag):
    key = datastore_client.key("User", email)  # "User" is the kind, email is the unique key
    
    # Create a new entity
    entity = datastore.Entity(key=key)

    # Set entity properties
    entity.update({
        "name": name,
        "dateOfBirth": age,
        "XP":0

    })

    # Save entity to Datastore
    datastore_client.put(entity)
    print(f"User {name} added successfully!")

# Example usage
create_user("alice@example.com", "Alice", 25)  






def create_task(email, task_name):
    user_key = datastore_client.key("User", email)  

    task_key = datastore_client.key("User", email, "Task")  

    # Create the Task entity
    task = datastore.Entity(key=task_key)

    # Set properties for the Task
    task.update({
        "task_name": task_name,

        "status": "To do"
    })

    # Save the entity
    datastore_client.put(task)
    print(f"Task '{task_name}' added for user {email}.")



def create_personal_task(email, task_name):
    user_key = datastore_client.key("User", email)  
    personal_task_key = datastore_client.key("User", email, "Task")  

    # Create the Task entity
    personal_task = datastore.Entity(key=personal_task_keytask_key)

    # Set properties for the Task
    personal_task.update({
        "task_name": task_name,
        "status": "To do"
    })

    # Save the entity
    datastore_client.put(personal_task)
    print(f"Task '{task_name}' added for user {email}.")









firebase_request_adapter = requests.Request()
@app.route("/")
def root():
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None

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
            times = fetch_times(claims["email"], 10)

        except ValueError as exc:
            # This will be raised if the token is expired or any other
            # verification checks fail.
            error_message = str(exc)

    return render_template(
        "index.html", user_data=claims, error_message=error_message, times=times
    )



if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)