from random import choice

all_minor_tasks = []
all_minor_tasks.append({
    'task-name':"Volunteer Locally",
})
all_minor_tasks.append({
    'task-name':"Visit GreenTeam.org.uk",
})
all_minor_tasks.append({
    'task-name':"Follow Us On Instagram",
})
all_minor_tasks.append({
    'task-name':"Go Outside",
})
all_minor_tasks.append({
    'task-name':"Climb A Hill",
})
all_minor_tasks.append({
    'task-name':"Practice A Skill",
})
all_minor_tasks.append({
    'task-name':"Go Exploring",
})
all_minor_tasks.append({
    'task-name':"Light A Fire",
})
all_minor_tasks.append({
    'task-name':"Survive The Wilderness",
})

def random_task():
    return choice(all_minor_tasks)