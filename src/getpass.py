# OVerload getpass.getpass() to check an environment variable instead.

import os

def getpass(prompt='Password: ', stream=None):
    """
    Overload getpass() to grab API_KEY from environment.
    """
    return os.environ["API_KEY"]


    
