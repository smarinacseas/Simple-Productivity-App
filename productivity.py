# Imports
import json
import time
from datetime import datetime, timedelta
from termcolor import cprint
import random

# Function to get tasks from user input with error correction
def get_tasks_from_input():
    tasks = {}
    print("Enter your tasks and their durations (in minutes). Press Enter without typing anything to finish.")
    while True:
        # Get task name
        task = input("Task name: ")
        if not task:
            break
        # Confirm or rename task
        while True:
            confirm_task = input(f"Entered task name is '{task}'. Press Enter to confirm or type new name to rename: ")
            if not confirm_task:
                break
            task = confirm_task

        # Get task duration
        while True:
            minutes = input(f"Minutes for '{task}': ")
            if not minutes:
                break  # Allow user to skip duration input for now
            if not minutes.isdigit():
                print("Please enter a valid number for minutes.")
                continue

            # Confirm or change duration
            while True:
                confirm_minutes = input(f"Entered duration for '{task}' is {minutes} minutes. Press Enter to confirm or type new duration to change: ")
                if not confirm_minutes:
                    break
                if not confirm_minutes.isdigit():
                    print("Please enter a valid number for minutes.")
                    continue
                minutes = confirm_minutes
                break
            break

        # Add task to dictionary
        tasks[task] = int(minutes) if minutes else 0
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
    tasks = get_tasks_from_input()
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
                cprint(f'{task} completed @{s_time.strftime("%I:%M%p")}', 'white', 'on_green')
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
            # "I will become a successful algorithmic trader.",
            "Detach from the outcome, focus on the now.",
            "Be who you want to become"
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