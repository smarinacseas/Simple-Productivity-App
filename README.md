# Simple-Productivity-App

7/30:

- Operates in Terminal window, executable via shell script and based json-formatted list of tasks and minutes per task (tasks.json file).
- Displays local time of upcoming tasks, time previous tasks were completed, and minutes remaining for current task. Color and blinking added for better visual.

7/31:

- get_tasks_from_input() implemented - Program prompts user for tasks and minutes, rather than using hard-coded JSON file.
- Separated task list display from main method. Implemented pause/resume functionality.
- Allows default schedule to be started from beginning.
- User can specify start time for a specific task before entering duration.

8/1:

- Scheduled tasks are properly prioritized, use of scheduled and unscheduled task lists + dynamic calculation of free time slots during task entry.
- Tasks with only duration specified are proplerly split up to accomodate for scheduled tasks.

Future:

1. Improve UI (ideas: selection instead of manual entry)
