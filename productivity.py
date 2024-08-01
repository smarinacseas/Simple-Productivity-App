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

# Function to get tasks from user input with error correction and restart option
def get_tasks_from_input():
    tasks = {}
    initial_prompt = input("Type 'default' to load tasks from tasks.json, 'restart' to restart task input, or press Enter to start entering tasks manually: ").strip().lower()
    
    if initial_prompt == 'default':
        return load_default_tasks()
    if initial_prompt == 'restart':
        print("Restarting task input...\n")
        return get_tasks_from_input()  # Restart input process
    
    while True:
        print("\nEnter your tasks and their durations (in minutes) or specific start times (HH:MM).")
        print("Press Enter without typing anything to finish.\n")
        tasks.clear()  # Clear the tasks dictionary for restarting
        while True:
            
            # Display current tasks
            if tasks:
                print("Current Tasks:")
                current_time = datetime.now()
                start_time = current_time
                for t, (m, s_time) in tasks.items():
                    if s_time:
                        start_time = s_time
                    end_time = start_time + timedelta(minutes=m if m else 0)
                    start_info = f"{start_time.strftime('%I:%M%p')}: {t} for {m} minutes" if m else f"{start_time.strftime('%I:%M%p')}: {t}"
                    print(f" - {start_info}")
                    start_time = end_time
                print("")

            # Get task name
            task = input("Task: ")
            if task.lower() == 'restart':
                print("Restarting task input...\n")
                break
            if not task:
                return tasks
            
            # Confirm or rename task
            while True:
                confirm_task = input(f"'{task}' OK? (Enter to confirm, or type new name): ")
                if not confirm_task:
                    break
                task = confirm_task

            # Get task duration or start time
            while True:
                time_input = input(f"Enter duration in minutes or start time (HH:MM) for '{task}': ")
                if not time_input:
                    break  # Allow user to skip duration input for now
                try:
                    if ':' in time_input:
                        current_time = datetime.now()
                        entered_time = datetime.strptime(time_input, '%H:%M')
                        # Assume the entered time is today, and adjust if it's in the past
                        entered_time = entered_time.replace(year=current_time.year, month=current_time.month, day=current_time.day)
                        if entered_time < current_time:
                            entered_time += timedelta(hours=12)  # Consider as PM if time has passed
                        start_time = entered_time
                        duration = None
                    else:
                        duration = int(time_input)
                        start_time = None
                except ValueError:
                    print("Enter a valid number or time.")
                    continue

                # Confirm or change duration/start time
                while True:
                    confirm_time = input(f"{time_input} OK? (Enter to confirm, or type new): ")
                    if not confirm_time:
                        break
                    try:
                        if ':' in confirm_time:
                            current_time = datetime.now()
                            entered_time = datetime.strptime(confirm_time, '%H:%M')
                            # Assume the entered time is today, and adjust if it's in the past
                            entered_time = entered_time.replace(year=current_time.year, month=current_time.month, day=current_time.day)
                            if entered_time < current_time:
                                entered_time += timedelta(hours=12)  # Consider as PM if time has passed
                            start_time = entered_time
                            duration = None
                        else:
                            duration = int(confirm_time)
                            start_time = None
                        break
                    except ValueError:
                        print("Enter a valid number or time.")
                        continue

                tasks[task] = (duration, start_time)
                break

        if task.lower() != 'restart':
            break  # Exit outer loop if not restarting
    return tasks

# Create schedule list from tasks
def get_tasks_schedule(tasks, start_time=None):
    if start_time is None:
        start_time = datetime.now()
    schedule = []
    task_start_time = start_time
    for task, (minutes, specific_start_time) in tasks.items():
        if specific_start_time:
            task_start_time = specific_start_time
        end_time = task_start_time + timedelta(minutes=minutes if minutes else 0)
        schedule.append((task, task_start_time, end_time))
        task_start_time = end_time
    return schedule

# Method for displaying tasks, times, and time remaining
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