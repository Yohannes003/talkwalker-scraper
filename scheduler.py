import schedule
import time
import subprocess
import os

# Get the current working directory
current_directory = os.getcwd()

# Define your scraping task
def run_scraper():
    print("Running talkwalker cookies...")
    subprocess.run(["python3", os.path.join(current_directory, "talkwalker cookies.py")])
    print("Running the scraper...")
    subprocess.run(["python3", os.path.join(current_directory, "scraper.py")])

# Run the scraper immediately
run_scraper()

# Schedule the task every 7 days
schedule.every(7).days.do(run_scraper)

# Keep the scheduler running
while True:
    schedule.run_pending()
    time.sleep(1)
