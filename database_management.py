from google.auth.transport import requests
from google.cloud import datastore
import json
import google.oauth2.id_token
import datetime

datastore_client = datastore.Client()

def is_user_created(email):
    key = datastore_client.key("User", email)  # "User" is the kind, email is the unique key

    #datastore_client.delete(key)

    if datastore_client.get(key) is None:
        return False
    else:
        return True

def create_user(email, name, DoB, tag={}):
    key = datastore_client.key("User", email)  # "User" is the kind, email is the unique key

    # Create a new entity
    entity = datastore.Entity(key=key)

    # Set entity properties
    entity.update({
        "name": name,
        "dateOfBirth": DoB,
        "xp":0,
        "streak":0,
        "friends":0,

    })

    # Save entity to Datastore
    datastore_client.put(entity)
    print(f"User {name} added successfully!")

    # set starting tasks

    create_task(email, "Romp about the woodlands")

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

def create_task(email, task_name, status = "daily"):
    user_key = datastore_client.key("User", email)  

    task_key = datastore_client.key("User", email, "task")  

    # Create the Task entity
    task = datastore.Entity(key=task_key)

    # Set properties for the Task
    task.update({
        "task_name": task_name,
        "timestamp": datetime.datetime.now(),
        "status": status
    })

    # Save the entity
    datastore_client.put(task)
    print(f"Task '{task_name}' added for user {email}.")
    return task

def create_personal_task(email, task_name):
    user_key = datastore_client.key("User", email)  
    personal_task_key = datastore_client.key("User", email, "task")  

    # Create the Task entity
    personal_task = datastore.Entity(key=personal_task_key)

    # Set properties for the Task
    personal_task.update({
        "task_name": task_name,
        "status": "To do"
    })

    # Save the entity
    datastore_client.put(personal_task)
    print(f"Task '{task_name}' added for user {email}.")



def fetch_tasks(email, limit):
    ancestor = datastore_client.key("User", email)
    query = datastore_client.query(kind="task", ancestor=ancestor)
    #query.order = ["-task_name"]

    query.order = ["-timestamp"]

    tasks = query.fetch(limit=limit)

    return tasks

def fetch_finished_tasks(email, limit):
    ancestor = datastore_client.key("User", email)
    query = datastore_client.query(kind="finished_task", ancestor=ancestor)
    #query.order = ["-task_name"]

    query.order = ["-timestamp"]

    tasks = query.fetch(limit=limit)

    return tasks





