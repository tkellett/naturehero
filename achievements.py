

all_achievements = []
all_achievements.append({
    'achievement-name':"First Task Completed", 
    'achievement-icon':"🏆"}
)

all_achievements.append({
    'achievement-name':"Ten Tasks Completed", 
    'achievement-icon':"🏆🏆"}
)

all_achievements.append({
    'achievement-name':"Volunteering Event", 
    'achievement-icon':"🏆🏆🏆"}
)

def get_achievements(finished_task_query):
    num_completed = 0
    volunteering_events = 0

    for task in finished_task_query:
        if task['status'] == "Completed":
            num_completed += 1
            if "volunteer" in task:
                volunteering_events += 1
    
    result = []
    if volunteering_events >= 1:
        result.append(all_achievements[2])

    if num_completed >= 10:
        result.append(all_achievements[1])
    
    if num_completed >= 1:
        result.append(all_achievements[0])

    percent = int(100.0*len(result)/len(all_achievements))
    return (result,percent)
