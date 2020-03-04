from sys import argv, exit
import importlib
from os import getenv

if __name__ == "__main__":
    scheduler_module = getenv('ENGAGE_SCHEDULER')
    scheduler = importlib.import_module(scheduler_module)
    scheduler.run()
    
