# Imports
import json
import time
from datetime import datetime, timedelta
from termcolor import cprint
import random

# Load tasks from tasks.json
def load_tasks():
    with open('/Users/stefanmarinac/VSCode_Projects/Simple-Productivity-App/tasks.json', 'r') as f:
        tasks = json.load(f)
    return tasks

# Create schedule list from tasks
def get_tasks_schedule(tasks):
    task_start_time = datetime.now()
    schedule = []
    for task, minutes in tasks.items():
        end_time = task_start_time + timedelta(minutes=minutes)
        schedule.append((task, task_start_time, end_time))
        task_start_time = end_time
    return schedule

# Main method
def main():
    tasks = load_tasks()
    schedule = get_tasks_schedule(tasks)
    current_index = 0

    # Running loop until tasks are complete, updates every 15s
    while True:
        now = datetime.now()
        current_task, start_time, end_time = schedule[current_index]
        remaining_time = end_time - now
        remaining_minutes = int(remaining_time.total_seconds() // 60)

        print('')

        for index, (task, s_time, e_time) in enumerate(schedule):
            if index < current_index:
                # Task is completed
                print(f'{task} completed @{s_time.strftime("%I:%M%p")}')
            elif index == current_index:
                # Current task
                if remaining_minutes < 2:
                    cprint(f'{task} < 2m left', 'white', 'on_red', attrs=['blink'])
                elif remaining_minutes < 5:
                    cprint(f'{task} - {remaining_minutes} mins', 'white', 'on_light_red')
                else:
                    cprint(f'{task} - {remaining_minutes} mins', 'white', 'on_light_blue')
            else:
                print(f'{s_time.strftime("%I:%M%p")}: {task}')

        # Random reminder
        list_of_reminders = [
            "I will get a high profile internship for Summer '25.",
            "I will be my best self each day.",
            "If I'm doing something, I'm making progress.",
            "I will become a successful algorithmic trader.",
            "Detach from the outcome, focus on the now."
        ]
        random_reminder = random.choice(list_of_reminders)
        print('*' + random_reminder)

        # Print message when all tasks have been completed
        if now >= end_time:
            current_index += 1
            if current_index >= len(schedule):
                cprint('All tasks complete', 'white', 'on_light_green')
                break
                
        time.sleep(15)

if __name__ == "__main__":
    main()