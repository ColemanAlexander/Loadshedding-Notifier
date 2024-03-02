# Load shedding Notifier

This is a loadshedding notifier using the ESP API, meant to run in the background. If the allowance is reached, it lets the user know using toast, otherwise the main part of the script runs.
It gets the current schedule, then runs an infinite loop that checks if there is loadshedding today and lets the user know if theres loadshedding in 55 or 15 minutes.
