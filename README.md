# Simple-Productivity-App

7/30:

- Operates in Terminal window, executable via shell script and based json-formatted list of tasks and minutes per task (tasks.json file).
- Displays local time of upcoming tasks, time previous tasks were completed, and minutes remaining for current task. Color and blinking added for better visual.

7/31:

- get_tasks_from_input() implemented - Program prompts user for tasks and minutes, rather than using hard-coded JSON file.
- Separated task list display from main method. Implemented pause/resume functionality.
- Allows default schedule to be started from beginning
- User can specify start time for a specific task before entering duration

Future:

1. Prioritize scheduled tasks, then fill in tasks with specified duration in empty time slots
