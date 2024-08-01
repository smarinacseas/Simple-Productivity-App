# Imports
import json
import time
from datetime import datetime, timedelta
from termcolor import cprint
import random
import threading

# Function to load tasks from a hard-coded tasks.json file
def load_default_tasks():
    with open('/Users/stefanmarinac/VSCode_Projects/Simple-Productivity-App/tasks.json', 'r') as f:
        tasks = json.load(f)
    return tasks

# Function to load tasks from a hard-coded tasks.json file
def load_default_tasks():
    with open('/path/to/your/tasks.json', 'r') as f:
        tasks = json.load(f)
    return tasks

# Function to get tasks from user input with error correction and restart option
def get_tasks_from_input():
    tasks = []
    initial_prompt = input("Type 'default' to load tasks from tasks.json, 'restart' to restart task input, or press Enter to start entering tasks manually: ").strip().lower()
    
    if initial_prompt == 'default':
        return load_default_tasks()
    if initial_prompt == 'restart':
        print("Restarting task input...\n")
        return get_tasks_from_input()  # Restart input process
    
    while True:
        print("\nEnter your tasks and their durations (in minutes) or specific start times (HH:MMam/pm).")
        print("Press Enter without typing anything to finish.\n")
        while True:
            # Get task name
            task = input("Task: ")
            if task.lower() == 'restart':
                print("Restarting task input...\n")
                break
            if not task:
                return tasks

            # Get task duration or start time
            time_input = input(f"Enter duration in minutes or start time (HH:MMam/pm) for '{task}': ")
            specific_start_time = None
            duration = None

            if time_input:
                try:
                    if 'am' in time_input.lower() or 'pm' in time_input.lower():
                        specific_start_time = datetime.strptime(time_input, '%I:%M%p')
                        current_time = datetime.now()
                        specific_start_time = specific_start_time.replace(year=current_time.year, month=current_time.month, day=current_time.day)
                        duration = int(input(f"Enter duration in minutes for '{task}': "))
                    else:
                        duration = int(time_input)
                except ValueError:
                    print("Enter a valid number or time.")
                    continue
            
            tasks.append((task, duration, specific_start_time))

            # Update and display current schedule
            schedule = get_tasks_schedule(tasks)
            print("Current Tasks:")
            for task, start, end in schedule:
                print(f" - {start.strftime('%I:%M%p')}: {task} for {(end - start).seconds // 60} minutes")
            print("")
            
        if task.lower() != 'restart':
            break  # Exit outer loop if not restarting
    return tasks

# Create schedule list from tasks
def get_tasks_schedule(tasks, start_time=None):
    if start_time is None:
        start_time = datetime.now()
    schedule = []
    remaining_tasks = []

    for task, duration, specific_start_time in tasks:
        if specific_start_time:
            if start_time < specific_start_time:
                while remaining_tasks and start_time < specific_start_time:
                    remaining_task, remaining_duration = remaining_tasks.pop(0)
                    if start_time + timedelta(minutes=remaining_duration) <= specific_start_time:
                        schedule.append((remaining_task, start_time, start_time + timedelta(minutes=remaining_duration)))
                        start_time += timedelta(minutes=remaining_duration)
                    else:
                        overlap_duration = (specific_start_time - start_time).seconds // 60
                        remaining_tasks.insert(0, (remaining_task, remaining_duration - overlap_duration))
                        schedule.append((remaining_task, start_time, specific_start_time))
                        start_time = specific_start_time
            start_time = specific_start_time
        end_time = start_time + timedelta(minutes=duration if duration else 0)
        if schedule and start_time < schedule[-1][2]:
            overlap_duration = (schedule[-1][2] - start_time).seconds // 60
            remaining_tasks.insert(0, (schedule[-1][0] + " (cont)", overlap_duration))
            schedule[-1] = (schedule[-1][0], schedule[-1][1], start_time)
        schedule.append((task, start_time, end_time))
        start_time = end_time

        while remaining_tasks:
            remaining_task, remaining_duration = remaining_tasks.pop(0)
            schedule.append((remaining_task, start_time, start_time + timedelta(minutes=remaining_duration)))
            start_time += timedelta(minutes=remaining_duration)

    return schedule

def display_tasks(schedule, current_index, paused_flag):
    while True:
        if not paused_flag.is_set():
            now = datetime.now()
            current_task, start_time, end_time = schedule[current_index]
            remaining_time = end_time - now
            remaining_minutes = int(remaining_time.total_seconds() // 60)

            print('')

            for index, (task, s_time, e_time) in enumerate(schedule):
                if index < current_index:
                    # Task is completed
                    cprint(f'{task} @ {s_time.strftime("%I:%M%p")} [Done]', 'white', 'on_green')
                elif index == current_index:
                    # Current task
                    if remaining_minutes < 2:
                        cprint(f'{task} < 2m', 'white', 'on_red', attrs=['blink'])
                    elif remaining_minutes < 5:
                        cprint(f'{task} - {remaining_minutes}m', 'white', 'on_light_red')
                    else:
                        cprint(f'{task} - {remaining_minutes}m', 'white', 'on_light_blue')
                else:
                    print(f'{s_time.strftime("%I:%M%p")}: {task}')

            # Random reminder
            list_of_reminders = [
                "I will get a high profile internship for Summer '25.",
                "I will be my best self each day.",
                "If I'm doing something, I'm making progress.",
                "Detach from the outcome, focus on the now.",
                "Be who you want to become"
            ]
            random_reminder = random.choice(list_of_reminders)
            print('* ' + random_reminder)

            # Print message when all tasks have been completed
            if now >= end_time:
                current_index += 1
                if current_index >= len(schedule):
                    cprint('All tasks complete', 'white', 'on_light_green')
                    break

            time.sleep(15)

def main():
    tasks = get_tasks_from_input()
    if not tasks:
        print("No tasks entered. Exiting.")
        return

    start_time = datetime.now()
    schedule = get_tasks_schedule(tasks, start_time)
    current_index = 0
    paused_flag = threading.Event()

    def update_schedule_on_resume():
        nonlocal schedule
        nonlocal current_index
        nonlocal start_time
        nonlocal tasks
        now = datetime.now()
        if current_index < len(schedule):
            remaining_duration = (schedule[current_index][2] - now).total_seconds() / 60
            schedule = get_tasks_schedule(tasks, start_time)
            elapsed = (now - start_time).total_seconds() / 60
            current_index = 0
            while elapsed > 0 and current_index < len(schedule):
                task_duration = (schedule[current_index][2] - schedule[current_index][1]).total_seconds() / 60
                if elapsed >= task_duration:
                    elapsed -= task_duration
                    current_index += 1
                else:
                    schedule[current_index] = (schedule[current_index][0], now, now + timedelta(minutes=task_duration - elapsed))
                    elapsed = 0
            start_time = now

    # Start the display thread
    display_thread = threading.Thread(target=display_tasks, args=(schedule, current_index, paused_flag))
    display_thread.start()

    while display_thread.is_alive():
        user_input = input("Type 'pause' or 'p' to pause, 'resume' or 'r' to resume: ").strip().lower()
        if user_input in ['pause', 'p']:
            paused_flag.set()
            print("Task view paused. Type 'resume' or 'r' to resume.")
        elif user_input in ['resume', 'r']:
            paused_flag.clear()
            update_schedule_on_resume()
            print("Resuming task view.")

if __name__ == "__main__":
    main()