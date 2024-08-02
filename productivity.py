# Imports
import json
import time
from datetime import datetime, timedelta
from termcolor import cprint
import random
import threading

# Helper function to round up minutes to multiple of 5
def round_up_to_nearest_five(minutes):
    return ((minutes + 4) // 5) * 5

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
                duration_minutes = (end - start).seconds // 60
                hours, minutes = divmod(duration_minutes, 60)
                print(f" - {start.strftime('%I:%M%p')}: {task} for {hours}h{minutes:02d}m")
            print("")
            
        if task.lower() != 'restart':
            break  # Exit outer loop if not restarting
    return tasks

# Create schedule list from tasks
def get_tasks_schedule(tasks, start_time=None):
    if start_time is None:
        start_time = datetime.now()
    
    scheduled_tasks = []
    unscheduled_tasks = []

    for task, duration, specific_start_time in tasks:
        if specific_start_time:
            scheduled_tasks.append((task, duration, specific_start_time))
        else:
            unscheduled_tasks.append((task, duration))
    
    # Sort scheduled tasks by their start time
    scheduled_tasks.sort(key=lambda x: x[2])

    schedule = []
    current_time = start_time

    # Insert scheduled tasks into the timeline
    for task, duration, specific_start_time in scheduled_tasks:
        if current_time < specific_start_time:
            current_time = specific_start_time
        end_time = current_time + timedelta(minutes=duration)
        schedule.append((task, current_time, end_time))
        current_time = end_time

    # Maintain a list of free time slots
    free_slots = []
    current_time = start_time
    for task, start, end in schedule:
        if current_time < start:
            free_slots.append((current_time, start))
        current_time = end

    free_slots.append((current_time, datetime.max))

    # Fit unscheduled tasks into the gaps between scheduled tasks
    for task, duration in unscheduled_tasks:
        while duration > 0 and free_slots:
            free_start, free_end = free_slots.pop(0)
            available_time = (free_end - free_start).seconds // 60
            task_duration = min(duration, available_time)
            if task_duration <= 2: # Buffer to ensure small free time slots are skipped
                continue
            end_time = round_up_to_nearest_five(free_start + timedelta(minutes=task_duration))
            schedule.append((task, free_start, end_time))
            duration -= task_duration
            if end_time < free_end:
                free_slots.insert(0, (end_time, free_end))
            # else:
            #     print(f"[DEBUG] No remaining free slots to adjust from {end_time.strftime('%I:%M%p')} to {free_end.strftime('%I:%M%p')}")

    # Ensure schedule is sorted by start time
    schedule.sort(key=lambda x: x[1])
    
    return schedule

def display_tasks(schedule, current_index, paused_flag):
    while True:
        if not paused_flag.is_set():
            now = datetime.now()
            current_task, start_time, end_time = schedule[current_index]
            remaining_time = end_time - now
            remaining_minutes = int(remaining_time.total_seconds() // 60)
            remaining_hours, remaining_minutes = divmod(remaining_minutes, 60)

            print('')

            for index, (task, s_time, e_time) in enumerate(schedule):
                duration_minutes = (e_time - s_time).seconds // 60
                hours, minutes = divmod(duration_minutes, 60)
                if index < current_index:
                    # Task is completed
                    cprint(f'{task} @ {s_time.strftime("%I:%M%p")} [Done]', 'white', 'on_green')
                elif index == current_index:
                    # Current task
                    if remaining_minutes < 2 and remaining_hours == 0:
                        cprint(f'{task} < {remaining_hours}h{remaining_minutes:02d}m', 'white', 'on_red', attrs=['blink'])
                    elif remaining_minutes < 5 and remaining_hours == 0:
                        cprint(f'{task} - {remaining_hours}h{remaining_minutes:02d}m', 'white', 'on_light_red')
                    else:
                        cprint(f'{task} - {remaining_hours}h{remaining_minutes:02d}m', 'white', 'on_light_blue')
                else:
                    print(f'{s_time.strftime("%I:%M%p")}: {task} for {hours}h{minutes:02d}m')

            # Random reminder
            list_of_reminders = [
                "I will get a SWE internship for Summer '25.",
                "I will be my best self each day.",
                "I will be a successful SWE.",
                "I will practice LeetCode consistently.",
                "I will work on side projects that inspire me.",
                "My consistency will set me apart.",
                "If I'm doing something, I'm making progress.",
                "Detach from the outcome, focus on the now.",
                "Be who you want to become",
                "Believe in your limitless potential.",
                "Strive for progress, not perfection.",
                "Every day is a new opportunity.",
                "Your hard work will pay off.",
                "Stay focused and determined.",
                "You have the power to create change.",
                "Embrace challenges as opportunities.",
                "Keep pushing forward.",
                "Success is built on consistency.",
                "Your effort today shapes your tomorrow.",
                "Dream big and work hard.",
                "You are stronger than you think.",
                "Remain positive and persistent.",
                "Great things take time.",
                "Be the best version of yourself.",
                "Your attitude determines your direction.",
                "Success is a journey, not a destination.",
                "Every small step counts.",
                "Your dedication is your superpower.",
                "Keep moving forward.",
                "You are capable of amazing things.",
                "Push yourself, because no one else will.",
                "No one's here to save you"
                "Thoughts become actions... Actions become habits.",
                "Don't stop until you're proud.",
                "Work hard and stay humble.",
                "The only thing stopping you is you.",
                "Make today count.",
                "Small steps lead to big changes.",
                "Take the risk or lose the chance.",
                "Success is a state of mind.",
                "Discipline over motivation.",
                "The best way to predict the future is to create it.",
                "Believe you can and you're halfway there.",
                "Focus on the good.",
                "The sky is the limit.",
                "Make it happen.",
                "Don't wait for things to come to you.",
                "Yesterday you said tomorrow",
                "Never say 'I should'.",
                "Don't let your dreams be dreams."
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