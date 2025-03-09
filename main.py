import datetime
from flask import Flask, render_template, request, redirect, jsonify
import json
from google.auth.transport import requests
from google.cloud import datastore
import google.oauth2.id_token
import uuid
app = Flask(__name__)
app.secret_key = 'EXCELLENT_SECRET_KEY'

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

@app.route('/add-task-action', methods=['POST'])
def add_task_test_action():
    id_token = request.cookies.get("token")
    if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter
                )
                create_task(claims["email"], "test task 123" + str(datetime.datetime.now(tz=datetime.timezone.utc)))
            except:
                pass

@app.route('/complete-task-action', methods=['POST'])
def complete_task_action():
    client = datastore.Client()
    data = request.json
    
    try:
        # Parse the key information
        key_info = json.loads(data.get('key_info'))
        
        # Reconstruct the hierarchical key
        parent_key = client.key(key_info['parent_kind'], key_info['parent_name'])
        task_key = client.key(key_info['kind'], key_info['id'], parent=parent_key)

        vals = client.get(task_key)

        # Get the entity
        task_entity = client.get(task_key)
        
        if not task_entity:
            return jsonify({"error": "Task not found"}), 404
        
        # Update the entity
        task_entity['status'] = "Completed"

        # Delete the entity
        client.put(task_entity)
        
        return jsonify({"message": "Task deleted successfully"})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400
    
@app.route('/delete-task-action', methods=['POST'])
def delete_task_action():
    client = datastore.Client()
    data = request.json
    
    try:
        # Parse the key information
        key_info = json.loads(data.get('key_info'))
        
        # Reconstruct the hierarchical key
        parent_key = client.key(key_info['parent_kind'], key_info['parent_name'])
        task_key = client.key(key_info['kind'], key_info['id'], parent=parent_key)
        
        # Delete the entity
        client.delete(task_key)
        
        return jsonify({"message": "Task deleted successfully"})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400

@app.route('/complete-registration-action', methods=['POST'])
def complete_registration_action():
    # Get data from the request (if any)
    data = request.json  # For JSON data
    name = data.get('name')
    dob = data.get('dob')

    id_token = request.cookies.get("token")
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter
            )
            if not is_user_created(claims['email']):
                create_user(claims['email'], name, dob, {})
                return jsonify({"status": "success", "message": "Action triggered successfully!"})
            else:                
                return jsonify({"status": "failure", "message": "Action triggered successfully!"})
        except:
            pass

    # Return a response (optional)
    return jsonify({"status": "failure", "message": "Action triggered unsuccessfully!"})

@app.route("/social")
def social():
    error_message = None
    id_token = request.cookies.get("token")
    if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter
                )
                feeditems = []
                feeditems.append({
                    'name':'Hakan',
                    "achievement-name":'Sleep In For 16 Hours',
                    "level-badge":"SSR"
                })
                # CHECK IF USER IS REGISTERED
                if is_user_created(claims['email']):
                    return render_template(
                        "social.html", feeditems = feeditems
                    )
                else:
                    return render_template(
                        "registration.html"
                    )

            except ValueError as exc:
                # This will be raised if the token is expired or any other
                # verification checks fail.
                error_message = str(exc)
                return redirect("/")
    
    return redirect("/")

def make_task_entry(entity):
    key_info = {
        'parent_kind': entity.key.parent.kind,
        'parent_name': entity.key.parent.name,  # Using name since your User key uses name
        'kind': entity.key.kind,
        'id': entity.key.id
    }
    task_entry = {
        "task-icon":"A",
        "task-name":entity['task_name'],
        "key_info": json.dumps(key_info)
    }
    return task_entry

@app.route("/home")
def home():
    error_message = None
    id_token = request.cookies.get("token")
    if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter
                )
                task_query = fetch_tasks(claims['email'], 50)

                completed_tasks = []
                daily_tasks = []
                special_tasks = []
                for task in task_query:
                    task_entry = make_task_entry(task)

                    if task['status'] == "Completed":
                        completed_tasks.append(task_entry)
                    elif task['status'] == "Special":
                        special_tasks.append(task_entry)
                    else:
                        daily_tasks.append(task_entry)
                
                while len(daily_tasks) < 7:
                    task = create_task(claims['email'], "Test Task")
                    daily_tasks.append(make_task_entry(task))
            
                # CHECK IF USER IS REGISTERED
                if is_user_created(claims['email']):
                    return render_template(
                        "home.html", xp_value = 75, level = 5, daily_tasks=daily_tasks,special_tasks=special_tasks,completed_tasks=completed_tasks
                    )
                else:
                    return render_template(
                        "registration.html"
                    )

            except ValueError as exc:
                # This will be raised if the token is expired or any other
                # verification checks fail.
                error_message = str(exc)
                return redirect("/")
    
    return redirect("/")

@app.route("/profile")
def profile():
    error_message = None
    id_token = request.cookies.get("token")
    if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter
                )

                achievements = []
                achievements.append({"achievement-name":"dummy achievement", "achievement-icon":"🏆"})

                # CHECK IF USER IS REGISTERED
                if is_user_created(claims['email']):
                    key = datastore_client.key("User", claims['email'])  # "User" is the kind, email is the unique key
                    # Create a new entity
                    entity = datastore_client.get(key)

                    user_data={
                        "name":entity['name'],
                        "email":claims['email'],
                        "streak":"dummy 5",
                        "questions_percent":"20",
                        "friends_number":"6"
                    }
                    return render_template(
                        "profile.html", achievements=achievements, user_data=user_data
                    )
                else:
                    return render_template(
                        "registration.html"
                    )

            except ValueError as exc:
                # This will be raised if the token is expired or any other
                # verification checks fail.
                error_message = str(exc)
                return redirect("/")
    
    return redirect("/")


@app.route("/logout")
def logout():
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

            #return redirect("home")

            #store_time(claims["email"], datetime.datetime.now(tz=datetime.timezone.utc))

            #create_task(claims["email"], "test task 123")
            #times = fetch_times(claims["email"], 10)
            #tasks = fetch_tasks(claims["email"], 10)

        except ValueError as exc:
            # This will be raised if the token is expired or any other
            # verification checks fail.
            error_message = str(exc)

    return render_template(
        "index.html", user_data=claims, error_message=error_message, logout_path="yes"
    )

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

            #return redirect("home")

            #store_time(claims["email"], datetime.datetime.now(tz=datetime.timezone.utc))

            #create_task(claims["email"], "test task 123" + str(datetime.datetime.now(tz=datetime.timezone.utc)))

            #times = fetch_times(claims["email"], 10)
            #tasks = fetch_tasks(claims["email"], 10)

        except ValueError as exc:
            # This will be raised if the token is expired or any other
            # verification checks fail.
            error_message = str(exc)

    return render_template(
        "index.html", user_data=claims, error_message=error_message, logout_path="no"
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