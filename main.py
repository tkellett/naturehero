import datetime
from flask import Flask, render_template, request, redirect, jsonify
import json
from google.auth.transport import requests
from google.cloud import datastore
import google.oauth2.id_token
app = Flask(__name__)
app.secret_key = 'EXCELLENT_SECRET_KEY'

from database_management import *
from achievements import *
from minor_tasks import *

firebase_request_adapter = requests.Request()
datastore_client = datastore.Client()

def get_lvl_xp(raw_xp):
    xp = raw_xp
    next_level_xp = 100
    level = 1
    while xp > next_level_xp:
        level += 1
        xp -= next_level_xp
        next_level_xp = int(next_level_xp * 1.5)

    return (level, xp / float(next_level_xp))
    

@app.route('/add-task-action', methods=['POST'])
def add_task_test_action():
    id_token = request.cookies.get("token")
    if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter
                )
                #create_task(claims["email"], "test task 123" + str(datetime.datetime.now(tz=datetime.timezone.utc)))
            except:
                pass

def add_streak_xp():
    id_token = request.cookies.get("token")
    if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter
                )
                key = datastore_client.key("User", claims['email'])  # "User" is the kind, email is the unique key

                # Create a new entity
                entity = datastore_client.get(key)
                streak = 0
                if 'streak' in entity:
                    streak = entity['streak']
                xp = 0
                if 'xp' in entity:
                    xp = entity['xp']
                entity['streak'] = streak+1
                entity['xp']= xp + 50

                datastore_client.put(entity)
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

        # Get the entity
        task_entity = client.get(task_key)
        
        if not task_entity:
            return jsonify({"error": "Task not found"}), 404
        
        # Update the entity
        task_entity['status'] = "Completed"
        task_entity['timestamp'] = datetime.datetime.now()

        id_token = request.cookies.get("token")
        if id_token:
                try:
                    claims = google.oauth2.id_token.verify_firebase_token(
                        id_token, firebase_request_adapter
                    )

                    task_key = datastore_client.key("User", claims['email'], "finished_task")  
                    fin_task = datastore.Entity(key=task_key)

                    # Set properties for the Task
                    fin_task.update({
                        "task_name": task_entity['task_name'],
                        "timestamp": datetime.datetime.now(),
                        "status": "Completed"
                    })

                    # Save the entity
                    datastore_client.put(fin_task)
                except:
                    pass

        # Overwrite the entity
        client.delete(task_entity)
        add_streak_xp()
        
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
                finished_task_query = fetch_finished_tasks(claims['email'], 7)

                completed_tasks = []
                daily_tasks = []
                special_tasks = []
                for task in task_query:
                    task_entry = make_task_entry(task)

                    if task['status'] == "Completed":
                        pass #completed_tasks.append(task_entry)
                    elif task['status'] == "Special":
                        special_tasks.append(task_entry)
                    else:
                        daily_tasks.append(task_entry)
                for task in finished_task_query:
                    task_entry = make_task_entry(task)
                    completed_tasks.append(task_entry)
                
                while len(daily_tasks) < 4:
                    task = create_task(claims['email'], random_task()['task-name'])
                    daily_tasks.append(make_task_entry(task))
            
                # CHECK IF USER IS REGISTERED
                if is_user_created(claims['email']):
                    key = datastore_client.key("User", claims['email'])  # "User" is the kind, email is the unique key

                    # Create a new entity
                    entity = datastore_client.get(key)
                    xp = entity['xp'] if 'xp' in entity else 0
                    level, progress = get_lvl_xp(xp)
                    
                    return render_template(
                        "home.html", xp_value = progress*100.0, level = level, daily_tasks=daily_tasks,special_tasks=special_tasks,completed_tasks=completed_tasks
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

                fin_task_query = fetch_finished_tasks(claims['email'], 999)

                achievements, completion_percent = get_achievements(fin_task_query)

                #achievements = []
                #achievements.append({"achievement-name":"dummy achievement", "achievement-icon":"🏆"})

                # CHECK IF USER IS REGISTERED
                if is_user_created(claims['email']):
                    key = datastore_client.key("User", claims['email'])  # "User" is the kind, email is the unique key
                    # Create a new entity
                    entity = datastore_client.get(key)
                    
                    user_data={
                        "name":entity['name'],
                        "email":claims['email'],
                        "streak":entity['streak'] if 'streak' in entity else 0,
                        "questions_percent":str(completion_percent),
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