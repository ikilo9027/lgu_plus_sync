import os
from datetime import datetime
from pytz import timezone
from dateutil import relativedelta
import time
import shutil


def createDirectory(directory: str):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: Failed to create the directory.")

def deletefolder(directory: str):
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
    except OSError:
        print("Error: Failed to delete the file.")


def expiration_date(file_path: str):
    for folder in os.listdir(file_path):
        now_date = datetime.now(timezone('Asia/Seoul')).strftime("%c")
        create_date = time.ctime(os.path.getctime(f"{file_path}/{folder}"))
        week_later = (datetime.strptime(create_date, "%c") +
                      relativedelta.relativedelta(days=7)).strftime("%c")
        if week_later <= now_date:
            deletefolder(f"{file_path}/{folder}")
